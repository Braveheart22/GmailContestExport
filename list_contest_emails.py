import pickle
from googleapiclient.discovery import build

LABEL_ID = "Label_6083117079229242213"

with open("token.pickle", "rb") as token:
    creds = pickle.load(token)

service = build("gmail", "v1", credentials=creds)

results = service.users().messages().list(
    userId="me",
    labelIds=[LABEL_ID],
    maxResults=10
).execute()

messages = results.get("messages", [])

print(f"\nFound {len(messages)} message(s) in this first batch.\n")

for msg in messages:
    message = service.users().messages().get(
        userId="me",
        id=msg["id"],
        format="metadata",
        metadataHeaders=["Subject", "From", "Date"]
    ).execute()

    headers = message.get("payload", {}).get("headers", [])

    subject = next((h["value"] for h in headers if h["name"] == "Subject"), "")
    sender = next((h["value"] for h in headers if h["name"] == "From"), "")
    date = next((h["value"] for h in headers if h["name"] == "Date"), "")

    print("Subject:", subject)
    print("From:", sender)
    print("Date:", date)
    print("-" * 50)