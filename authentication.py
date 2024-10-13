import pickle
import os

from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow

SCOPES = ['https://www.googleapis.com/auth/gmail.modify']
CREDENTIALS_FILE = 'credentials_oauth.json'
TOKEN_FILE = 'token.pickle'

def authenticate_gmail():
    print("Authenticating to Gmail API...")
    creds = None

    # Load existing token if available
    if os.path.exists(TOKEN_FILE):
        with open(TOKEN_FILE, 'rb') as token:
            creds = pickle.load(token)

    # If there are no valid credentials, perform the OAuth flow
    if not creds or not creds.valid:
        flow = InstalledAppFlow.from_client_secrets_file(CREDENTIALS_FILE, SCOPES)
        creds = flow.run_local_server(port=8080)
        with open(TOKEN_FILE, 'wb') as token:
            pickle.dump(creds, token)

    service = build('gmail', 'v1', credentials=creds)
    print("Authentication successful.")
    return service

def fetch_emails(service):
    print("Fetching emails...")
    results = service.users().messages().list(userId='me', maxResults=10).execute()
    messages = results.get('messages', [])

    for msg in messages:
        message = service.users().messages().get(userId='me', id=msg['id']).execute()
        snippet = message.get('snippet', '')
        print(f"Email ID: {msg['id']} - Snippet: {snippet}")

if __name__ == '__main__':
    service = authenticate_gmail()
    fetch_emails(service)
