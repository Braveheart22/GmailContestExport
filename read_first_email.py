import pickle
import base64
from googleapiclient.discovery import build

LABEL_ID = "Label_6083117079229242213"

with open("token.pickle", "rb") as token:
    creds = pickle.load(token)

service = build("gmail", "v1", credentials=creds)

# Get first message under label
results = service.users().messages().list(
    userId="me",
    labelIds=[LABEL_ID],
    maxResults=1
).execute()

messages = results.get("messages", [])

if not messages:
    print("No messages found.")
    exit()

msg_id = messages[0]["id"]

message = service.users().messages().get(
    userId="me",
    id=msg_id,
    format="full"
).execute()

payload = message["payload"]

body_data = None

# Try direct body first
if "data" in payload.get("body", {}):
    body_data = payload["body"]["data"]

# Otherwise search parts
elif "parts" in payload:
    for part in payload["parts"]:
        if part["mimeType"] == "text/plain":
            body_data = part["body"].get("data")
            break

if body_data:
    decoded_body = base64.urlsafe_b64decode(body_data).decode("utf-8")

    print("\nEMAIL BODY:\n")
    print(decoded_body)

else:
    print("Could not find email body.")