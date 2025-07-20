import os
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials
from firebase_admin import firestore
from auth import load_credentials

# Scopes for Gmail API
SCOPES = [
    'https://www.googleapis.com/auth/gmail.readonly',
]

def get_gmail_service_for_user(user_id, storage_dir='user_tokens'):
    """
    Returns a Gmail API service for a specific Telegram user.
    Loads credentials from user_tokens/{user_id}_token.json.
    """
    creds = load_credentials(user_id, storage_dir)
    if not creds:
        raise Exception("No credentials found for this user. Please /login first.")
    return build('gmail', 'v1', credentials=creds)

def fetch_and_store_study_emails_for_user(user_id, max_results=10):
    """
    Fetches recent emails for the user, filters for study-related ones, and stores them in Firestore.
    Returns a list of dicts with email details.
    """
    service = get_gmail_service_for_user(user_id)
    db = firestore.client()
    results = service.users().messages().list(userId='me', maxResults=max_results, q='').execute()
    messages = results.get('messages', [])
    emails = []
    for msg in messages:
        msg_id = msg['id']
        msg_detail = service.users().messages().get(userId='me', id=msg_id, format='full').execute()
        headers = msg_detail.get('payload', {}).get('headers', [])
        subject = next((h['value'] for h in headers if h['name'] == 'Subject'), '')
        sender = next((h['value'] for h in headers if h['name'] == 'From'), '')
        snippet = msg_detail.get('snippet', '')
        # Simple keyword filter for study-related emails
        if any(kw in subject.lower() for kw in ['assignment', 'exam', 'project', 'class', 'lecture', 'homework', 'study']):
            email_data = {
                'id': msg_id,
                'subject': subject,
                'from': sender,
                'snippet': snippet
            }
            emails.append(email_data)
            db.collection('emails').document(f'{user_id}_{msg_id}').set(email_data)
    return emails

def get_email_by_id(user_id, email_id):
    """
    Retrieves a single email's details by ID from Firestore (if available) or Gmail API.
    """
    db = firestore.client()
    doc = db.collection('emails').document(f'{user_id}_{email_id}').get()
    if doc.exists:
        return doc.to_dict()
    # If not in Firestore, fetch from Gmail
    service = get_gmail_service_for_user(user_id)
    msg_detail = service.users().messages().get(userId='me', id=email_id, format='full').execute()
    headers = msg_detail.get('payload', {}).get('headers', [])
    subject = next((h['value'] for h in headers if h['name'] == 'Subject'), '')
    sender = next((h['value'] for h in headers if h['name'] == 'From'), '')
    snippet = msg_detail.get('snippet', '')
    return {
        'id': email_id,
        'subject': subject,
        'from': sender,
        'snippet': snippet
    }