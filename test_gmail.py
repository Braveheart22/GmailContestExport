from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
import os
import pickle

# Gmail read-only permission
SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']

creds = None

# Load saved token if it exists
if os.path.exists('token.pickle'):
    with open('token.pickle', 'rb') as token:
        creds = pickle.load(token)

# If no valid credentials, log in
if not creds:
    flow = InstalledAppFlow.from_client_secrets_file(
        'credentials.json',
        SCOPES
    )

    creds = flow.run_local_server(port=0)

    # Save token for future runs
    with open('token.pickle', 'wb') as token:
        pickle.dump(creds, token)

# Connect to Gmail API
service = build('gmail', 'v1', credentials=creds)

# Get Gmail profile info
profile = service.users().getProfile(userId='me').execute()

print("\nSUCCESS!")
print(f"Connected to: {profile['emailAddress']}")
print(f"Total messages: {profile['messagesTotal']}")