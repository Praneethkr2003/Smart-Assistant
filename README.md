<<<<<<< HEAD
# Smart Assistant Telegram Bot

A privacy-focused productivity assistant bot for students, built on Python and Telegram. Integrates Gmail, Google Calendar, AI-powered content expansion, reminders, attendance monitoring, and more—all via chat. No web dashboard required.

---

## Features

- **Google OAuth Login:** Secure device flow for Telegram users (no web interface needed).
- **Gmail Integration:** Fetches and classifies study-related emails using Gemini AI (with BERT fallback).
- **AI Content Expansion:** Expands email content using Gemini or Hugging Face API.
- **Google Calendar:** Create/view events, sync study tasks as calendar events.
- **Reminders:** Set custom reminders and receive Telegram notifications (background delivery).
- **Attendance Monitoring:** Check attendance using the official API endpoint (no scraping).
- **Firebase Firestore:** Secure storage for emails, reminders, and user data.
- **Inline Actions:** Interactive buttons for email actions (expand, create event, ignore, etc.).
- **Privacy-first:** No sensitive tokens in code, all secrets loaded from environment variables.

---

## Setup Instructions

### 1. Clone the Repository
```bash
git clone <your-repo-url>
cd <project-folder>
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Environment Variables
Create a `.env` file in the project root with the following (see `.env.example`):

```env
TELEGRAM_TOKEN=your-telegram-bot-token
FIREBASE_CREDENTIALS=path/to/your/firebase-key.json
HF_API_KEY=your-huggingface-api-key
CLIENT_SECRET_FILE=path/to/google-client-secret.json
```

- **Never commit your `.env` or secret files to git!**

### 4. Firebase Setup
- Create a Firebase project and download the service account key JSON.
- Enable Firestore in Native mode.

### 5. Google APIs Setup
- Enable Gmail and Calendar APIs in Google Cloud Console.
- Download `client_secret.json` and set `CLIENT_SECRET_FILE` in `.env`.

---

## Running the Bot
```bash
python bot.py
```

The bot will start polling Telegram for messages. Use `/start` to begin.

---

## Telegram Commands
- `/start` — Welcome message and help
- `/login` — Start Google OAuth login
- `/fetch_emails` — Fetch and display study-related emails
- `/remind` — Set a custom reminder (natural language supported)
- `/attendance` — Check your attendance (requires student ID/password)

---

## Project Structure
- `bot.py` — Main Telegram bot logic and command handlers
- `auth.py` — Google OAuth device flow for Telegram users
- `gmail.py` — Gmail API integration and email classification
- `calendar_manager.py` — Google Calendar integration (user-specific)
- `content_expander.py` — AI-powered content expansion (Gemini & BERT fallback)
- `scraper.py` — Attendance API integration
- `utils.py` — Shared utilities
- `user_tokens/` — Per-user Google OAuth tokens (auto-created)

---

## Security & Privacy
- **No hardcoded secrets:** All tokens/keys are loaded from environment variables.
- **User tokens:** Stored locally per Telegram user (not in code).
- **Attendance credentials:** Never stored; only used for API call.
- **.env:** Always keep your `.env` and service keys private.

---

## Contributing
Pull requests and issues are welcome! Please redact any secrets before sharing logs or code.

---

## License
MIT License

---

## Acknowledgments
- [python-telegram-bot](https://python-telegram-bot.org/)
- [Google Cloud APIs](https://console.cloud.google.com/)
- [Firebase](https://firebase.google.com/)
- [Gemini AI](https://ai.google.dev/gemini-api)
- [Hugging Face](https://huggingface.co/)

---


=======
# Smart Assistant Telegram Bot

A privacy-focused productivity assistant bot for students, built on Python and Telegram. Integrates Gmail, Google Calendar, AI-powered content expansion, reminders, attendance monitoring, and more—all via chat. No web dashboard required.

---

## Features

- **Google OAuth Login:** Secure device flow for Telegram users (no web interface needed).
- **Gmail Integration:** Fetches and classifies study-related emails using Gemini AI (with BERT fallback).
- **AI Content Expansion:** Expands email content using Gemini or Hugging Face API.
- **Google Calendar:** Create/view events, sync study tasks as calendar events.
- **Reminders:** Set custom reminders and receive Telegram notifications (background delivery).
- **Attendance Monitoring:** Check attendance using the official API endpoint (no scraping).
- **Firebase Firestore:** Secure storage for emails, reminders, and user data.
- **Inline Actions:** Interactive buttons for email actions (expand, create event, ignore, etc.).
- **Privacy-first:** No sensitive tokens in code, all secrets loaded from environment variables.

---

## Setup Instructions

### 1. Clone the Repository
```bash
git clone <your-repo-url>
cd <project-folder>
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Environment Variables
Create a `.env` file in the project root with the following (see `.env.example`):

```env
TELEGRAM_TOKEN=your-telegram-bot-token
FIREBASE_CREDENTIALS=path/to/your/firebase-key.json
HF_API_KEY=your-huggingface-api-key
CLIENT_SECRET_FILE=path/to/google-client-secret.json
```

- **Never commit your `.env` or secret files to git!**

### 4. Firebase Setup
- Create a Firebase project and download the service account key JSON.
- Enable Firestore in Native mode.

### 5. Google APIs Setup
- Enable Gmail and Calendar APIs in Google Cloud Console.
- Download `client_secret.json` and set `CLIENT_SECRET_FILE` in `.env`.

---

## Running the Bot
```bash
python bot.py
```

The bot will start polling Telegram for messages. Use `/start` to begin.

---

## Telegram Commands
- `/start` — Welcome message and help
- `/login` — Start Google OAuth login
- `/fetch_emails` — Fetch and display study-related emails
- `/remind` — Set a custom reminder (natural language supported)
- `/attendance` — Check your attendance (requires student ID/password)

---

## Project Structure
- `bot.py` — Main Telegram bot logic and command handlers
- `auth.py` — Google OAuth device flow for Telegram users
- `gmail.py` — Gmail API integration and email classification
- `calendar_manager.py` — Google Calendar integration (user-specific)
- `content_expander.py` — AI-powered content expansion (Gemini & BERT fallback)
- `scraper.py` — Attendance API integration
- `utils.py` — Shared utilities
- `user_tokens/` — Per-user Google OAuth tokens (auto-created)

---

## Security & Privacy
- **No hardcoded secrets:** All tokens/keys are loaded from environment variables.
- **User tokens:** Stored locally per Telegram user (not in code).
- **Attendance credentials:** Never stored; only used for API call.
- **.env:** Always keep your `.env` and service keys private.

---

## Contributing
Pull requests and issues are welcome! Please redact any secrets before sharing logs or code.

---

## License
MIT License

---

## Acknowledgments
- [python-telegram-bot](https://python-telegram-bot.org/)
- [Google Cloud APIs](https://console.cloud.google.com/)
- [Firebase](https://firebase.google.com/)
- [Gemini AI](https://ai.google.dev/gemini-api)
- [Hugging Face](https://huggingface.co/)

---

_Last updated: July 20, 2025_

>>>>>>> e54266c (Fix calendar sync and Gmail auth bugs)
