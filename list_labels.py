import pickle
from googleapiclient.discovery import build

# Load saved credentials
with open("token.pickle", "rb") as token:
    creds = pickle.load(token)

# Connect to Gmail API
service = build("gmail", "v1", credentials=creds)

# Get all Gmail labels
results = service.users().labels().list(userId="me").execute()
labels = results.get("labels", [])

print("\nGmail Labels:\n")

for label in labels:
    print(f"{label['name']} --> {label['id']}")