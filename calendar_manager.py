import os
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials
from firebase_admin import firestore
from auth import load_credentials
from datetime import datetime, timedelta

SCOPES = ['https://www.googleapis.com/auth/calendar']


def get_calendar_service_for_user(user_id, storage_dir='user_tokens'):
    """
    Returns a Google Calendar API service for a specific Telegram user.
    Loads credentials from user_tokens/{user_id}_token.json.
    """
    creds = load_credentials(user_id, storage_dir)
    if not creds:
        raise Exception("No calendar credentials found for this user. Please /login first.")
    return build('calendar', 'v3', credentials=creds)


def create_calendar_event(service, event_data):
    """
    Creates a calendar event using the provided Google Calendar API service and event data dict.
    event_data should include: summary, start_datetime, end_datetime, description, and optionally location.
    Returns the created event object.
    """
    event = {
        'summary': event_data.get('summary', 'Study Event'),
        'description': event_data.get('description', ''),
        'start': {
            'dateTime': event_data['start_datetime'].isoformat(),
            'timeZone': event_data.get('timezone', 'Asia/Kolkata'),
        },
        'end': {
            'dateTime': event_data['end_datetime'].isoformat(),
            'timeZone': event_data.get('timezone', 'Asia/Kolkata'),
        },
    }
    if 'location' in event_data:
        event['location'] = event_data['location']
    created_event = service.events().insert(calendarId='primary', body=event).execute()
    # Optionally, store event in Firestore for tracking
    db = firestore.client()
    db.collection('calendar_events').add({
        'user_id': event_data.get('user_id'),
        'event_id': created_event.get('id'),
        'summary': event.get('summary'),
        'created_at': datetime.utcnow()
    })
    return created_event
