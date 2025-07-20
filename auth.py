import os
from google_auth_oauthlib import flow as google_flow
from google_auth_oauthlib.flow import InstalledAppFlow

SCOPES = [
    'openid',
    'https://www.googleapis.com/auth/userinfo.email',
    'https://www.googleapis.com/auth/userinfo.profile',
    'https://www.googleapis.com/auth/gmail.readonly',
    'https://www.googleapis.com/auth/calendar',
]

CLIENT_SECRET_FILE = os.getenv('CLIENT_SECRET_FILE', 'client_secret.json')

def start_local_server_auth_flow():
    """
    Initiates Google OAuth flow using local server. Returns the credentials object after auth.
    """
    flow = InstalledAppFlow.from_client_secrets_file(
        CLIENT_SECRET_FILE,
        SCOPES
    )
    creds = flow.run_local_server(port=0)
    return creds

def save_credentials(user_id, creds, storage_dir='user_tokens'):
    """
    Save user credentials to a file (or Firebase in production).
    """
    os.makedirs(storage_dir, exist_ok=True)
    token_path = os.path.join(storage_dir, f'{user_id}_token.json')
    with open(token_path, 'w') as token_file:
        token_file.write(creds.to_json())
    return token_path

def load_credentials(user_id, storage_dir='user_tokens'):
    token_path = os.path.join(storage_dir, f'{user_id}_token.json')
    if os.path.exists(token_path):
        from google.oauth2.credentials import Credentials
        return Credentials.from_authorized_user_file(token_path, SCOPES)
    return None