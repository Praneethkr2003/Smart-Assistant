import os
import asyncio
import dateparser
from dotenv import load_dotenv
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder, CommandHandler, ContextTypes, CallbackQueryHandler,
    ConversationHandler, MessageHandler, filters
)
from gmail import fetch_and_store_study_emails_for_user, get_email_by_id, get_gmail_service_for_user
from calendar_manager import get_calendar_service_for_user, create_calendar_event
from scraper import get_attendance
import firebase_admin
from firebase_admin import credentials, firestore

load_dotenv()
FIREBASE_CREDENTIALS = os.getenv("FIREBASE_CREDENTIALS")
if not FIREBASE_CREDENTIALS:
    raise ValueError("FIREBASE_CREDENTIALS not set in environment variables.")
# Initialize Firebase app if not already initialized
if not firebase_admin._apps:
    cred = credentials.Certificate(FIREBASE_CREDENTIALS)
    firebase_admin.initialize_app(cred)
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
if not TELEGRAM_TOKEN:
    raise ValueError("TELEGRAM_TOKEN not set in environment variables.")

def escape_html(text):
    """Escape HTML special characters for Telegram messages."""
    if not isinstance(text, str):
        text = str(text)
    return text.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Send a welcome message and basic instructions."""
    await update.effective_message.reply_text(
        "👋 Welcome to the Smart Assistant Bot!\n\nUse /login to connect your Google account."
    )

async def login(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Initiate Google OAuth login for the user."""
    user_id = update.effective_user.id
    await update.effective_message.reply_text(
        "🔐 Starting Google login process...\n\nA browser window will open. Please complete the Google login and grant access.\nWhen done, return to Telegram."
    )
    try:
        from auth import start_local_server_auth_flow, save_credentials
        loop = asyncio.get_event_loop()
        creds = await loop.run_in_executor(None, start_local_server_auth_flow)
        save_credentials(user_id, creds)
        await update.effective_message.reply_text(
            "✅ Google account connected successfully! You can now use Gmail and Calendar features."
        )
    except Exception as e:
        await update.effective_message.reply_text(f"❌ Error during Google login: {e}")

# /done is no longer needed with local server flow, but keep for compatibility
async def done(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.effective_message.reply_text("ℹ️ Login is now completed automatically after browser authentication. If you have issues, use /login again.")

from telegram import InlineKeyboardButton, InlineKeyboardMarkup

async def fetch_emails(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    await update.effective_message.reply_text("📬 Checking your Gmail for study-related emails...")
    try:
        loop = asyncio.get_event_loop()
        study_emails = await loop.run_in_executor(None, fetch_and_store_study_emails_for_user, user_id, 10)
        if study_emails:
            await update.effective_message.reply_text(f"Found {len(study_emails)} study-related emails. Displaying as tasks:")
            for idx, e in enumerate(study_emails, 1):
                subject = escape_html(e.get('subject', 'No Subject'))
                sender = escape_html(e.get('from', 'Unknown'))
                snippet = escape_html(e.get('snippet', '')[:200])
                msg = f"📚 <b>Task {idx}</b>\n<b>Subject:</b> {subject}\n<b>From:</b> {sender}\n<b>Snippet:</b> {snippet}"
                keyboard = InlineKeyboardMarkup([
                    [
                        InlineKeyboardButton("Expand Content", callback_data=f"expand_{e.get('id','')}"),
                        InlineKeyboardButton("Create Calendar Event", callback_data=f"calendar_{e.get('id','')}"),
                        InlineKeyboardButton("Ignore", callback_data=f"ignore_{e.get('id','')}")
                    ]
                ])
                await update.effective_message.reply_text(
                    msg,
                    reply_markup=keyboard,
                    parse_mode='HTML'
                )
        else:
            await update.effective_message.reply_text("No study-related emails found in your recent Gmail.")
    except Exception as e:
        await update.effective_message.reply_text(f"❌ Error: {e}")

from telegram.ext import CallbackQueryHandler

async def handle_email_action(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    data = query.data
    await query.answer()
    user_id = query.from_user.id
    if data.startswith("expand_"):
        # Do not remove buttons so user can take multiple actions
        email_id = data[len("expand_"):]
        try:
            # Fetch Gmail service and email content
            loop = asyncio.get_event_loop()
            service = await loop.run_in_executor(None, get_gmail_service_for_user, user_id)
            email = await loop.run_in_executor(None, get_email_by_id, user_id, email_id)
            msg = f"<b>Subject:</b> {escape_html(email.get('subject',''))}\n<b>From:</b> {escape_html(email.get('from',''))}\n<b>Snippet:</b> {escape_html(email.get('snippet',''))}"
            await query.message.reply_text(msg, parse_mode='HTML')
        except Exception as e:
            await query.message.reply_text(f"❌ Error expanding email: {e}")
    elif data.startswith("calendar_"):
        email_id = data[len("calendar_"):]
        try:
            loop = asyncio.get_event_loop()
            email = await loop.run_in_executor(None, get_email_by_id, user_id, email_id)
            service = await loop.run_in_executor(None, get_calendar_service_for_user, user_id)
            # For demo, just create event for now+1h
            from datetime import datetime, timedelta
            now = datetime.now()
            event_data = {
                'summary': email.get('subject', 'Study Event'),
                'description': email.get('snippet', ''),
                'start_datetime': now + timedelta(minutes=5),
                'end_datetime': now + timedelta(minutes=65),
                'user_id': user_id
            }
            event = await loop.run_in_executor(None, create_calendar_event, service, event_data)
            if event:
                await query.message.reply_text("✅ Calendar event created!")
            else:
                await query.message.reply_text("❌ Failed to create calendar event.")
        except Exception as e:
            await query.message.reply_text(f"❌ Error creating calendar event: {e}")
    elif data.startswith("ignore_"):
        await query.edit_message_reply_markup(reply_markup=None)
        await query.message.reply_text("✅ This email has been ignored.")
    else:
        await query.message.reply_text("Unknown action.")

async def remind(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    args = context.args
    if not args:
        await update.effective_message.reply_text("Usage: /remind <reminder text> at <date/time>. Example: /remind Submit assignment at 2025-07-21 18:30")
        return
    text = ' '.join(args)
    if ' at ' not in text:
        await update.effective_message.reply_text("Please specify the reminder in the format: <reminder text> at <date/time>")
        return
    reminder_text, time_str = text.rsplit(' at ', 1)
    dt = dateparser.parse(time_str, settings={'PREFER_DATES_FROM': 'future'})
    if not dt:
        await update.effective_message.reply_text("Couldn't parse the date/time. Please try again with a clearer format.")
        return
    # Store reminder in Firestore
    db = firestore.client()
    db.collection('reminders').add({
        'user_id': user_id,
        'reminder_text': reminder_text.strip(),
        'remind_at': dt,
        'notified': False
    })
    await update.effective_message.reply_text(f"⏰ Reminder set for {dt.strftime('%Y-%m-%d %H:%M')}! You'll get a Telegram notification.")

from telegram.ext import ConversationHandler, MessageHandler, filters

ATTEND_ID, ATTEND_PWD = range(2)

async def attendance_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.effective_message.reply_text("Please enter your Student ID:")
    return ATTEND_ID

async def attendance_id(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['attend_id'] = update.message.text.strip()
    await update.effective_message.reply_text("Now enter your password:")
    return ATTEND_PWD

async def attendance_pwd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = context.user_data.get('attend_id')
    password = update.message.text.strip()
    await update.effective_message.reply_text("⏳ Fetching your attendance, please wait...")
    loop = asyncio.get_event_loop()
    result = await loop.run_in_executor(None, get_attendance, user_id, password)
    # Telegram message max length is 4096 chars
    for chunk in [result[i:i+4000] for i in range(0, len(result), 4000)]:
        await update.effective_message.reply_text(chunk)
    return ConversationHandler.END

async def attendance_cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.effective_message.reply_text("Attendance check cancelled.")
    return ConversationHandler.END

async def reminder_notifier(app):
    while True:
        try:
            db = firestore.client()
            import datetime
            now = datetime.datetime.now()
            reminders = db.collection('reminders').where('remind_at', '<=', now).where('notified', '==', False).stream()
            for doc in reminders:
                data = doc.to_dict()
                user_id = data.get('user_id')
                reminder_text = data.get('reminder_text', 'Reminder!')
                # Send Telegram notification
                try:
                    await app.bot.send_message(chat_id=user_id, text=f"⏰ Reminder: {reminder_text}")
                except Exception as e:
                    print(f"Failed to send reminder to {user_id}: {e}")
                # Mark as notified
                db.collection('reminders').document(doc.id).update({'notified': True})
        except Exception as e:
            print(f"Reminder notifier error: {e}")
        await asyncio.sleep(60)

if __name__ == "__main__":
    import datetime
    from telegram.ext import Application
    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("login", login))
    app.add_handler(CommandHandler("done", done))
    app.add_handler(CommandHandler("fetch_emails", fetch_emails))
    app.add_handler(CommandHandler("remind", remind))
    attendance_handler = ConversationHandler(
        entry_points=[CommandHandler("attendance", attendance_start)],
        states={
            ATTEND_ID: [MessageHandler(filters.TEXT & ~filters.COMMAND, attendance_id)],
            ATTEND_PWD: [MessageHandler(filters.TEXT & ~filters.COMMAND, attendance_pwd)],
        },
        fallbacks=[CommandHandler("cancel", attendance_cancel)],
    )
    app.add_handler(attendance_handler)
    app.add_handler(CallbackQueryHandler(handle_email_action))
    print("🤖 Smart Assistant Telegram Bot is running...")

    async def post_init(application):
        # Start reminder notifier background task
        asyncio.create_task(reminder_notifier(application))
    app.post_init = post_init

    app.run_polling()