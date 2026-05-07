import pickle
import base64
import re
import pandas as pd
import os
from email.message import EmailMessage
from google_auth_oauthlib.flow import InstalledAppFlow

from googleapiclient.discovery import build

SCOPES = [
    "https://www.googleapis.com/auth/gmail.readonly",
    "https://www.googleapis.com/auth/gmail.send"
]
BACKUP_RECIPIENT = "Maryellen@LoopLoc.com"
OUTPUT_FILE = "2026_Gift_Contest.xlsx"
LABEL_ID = "Label_6083117079229242213"

# ---------------------------------------
# CONNECT TO GMAIL
# ---------------------------------------

creds = None

if os.path.exists("token.pickle"):
    with open("token.pickle", "rb") as token:
        creds = pickle.load(token)

if not creds or not creds.valid:
    flow = InstalledAppFlow.from_client_secrets_file(
        "credentials.json",
        SCOPES
    )
    creds = flow.run_local_server(port=0)

    with open("token.pickle", "wb") as token:
        pickle.dump(creds, token)

service = build("gmail", "v1", credentials=creds)

# ---------------------------------------
# GET ALL MESSAGES
# ---------------------------------------

messages = []
next_page_token = None

while True:
    request = service.users().messages().list(
        userId="me",
        labelIds=[LABEL_ID],
        maxResults=500,
        pageToken=next_page_token
    )

    results = request.execute()

    messages.extend(results.get("messages", []))

    next_page_token = results.get("nextPageToken")

    if not next_page_token:
        break

print(f"\nFound {len(messages)} contest email(s).\n")

# ---------------------------------------
# HELPER FUNCTION
# ---------------------------------------

def extract_field(pattern, text):
    match = re.search(pattern, text, re.IGNORECASE)

    if match:
        return match.group(1).strip()

    return ""

# ---------------------------------------
# PROCESS EMAILS
# ---------------------------------------

rows = []

for msg in messages:

    message = service.users().messages().get(
        userId="me",
        id=msg["id"],
        format="full"
    ).execute()

    headers = message.get("payload", {}).get("headers", [])
    submission_date = next((h["value"] for h in headers if h["name"].lower() == "date"), "")

    payload = message["payload"]

    body_data = None

    # Direct body
    if "data" in payload.get("body", {}):
        body_data = payload["body"]["data"]

    # Multipart email
    elif "parts" in payload:
        for part in payload["parts"]:
            if part["mimeType"] in ["text/plain", "text/html"]:
                body_data = part["body"].get("data")
                if body_data:
                    break

    if not body_data:
        continue

    decoded_body = base64.urlsafe_b64decode(body_data).decode("utf-8")

    # ---------------------------------------
    # EXTRACT FIELDS
    # ---------------------------------------

    first_name = extract_field(r"First Name:\s*</b>(.*?)<", decoded_body)
    last_name = extract_field(r"Last Name:\s*</b>(.*?)<", decoded_body)
    email = extract_field(r"Email Address:\s*</b>(.*?)<", decoded_body)
    phone = extract_field(r"Phone number:\s*</b>(.*?)<", decoded_body)
    address = extract_field(r"Address:\s*</b>(.*?)<", decoded_body)
    city_state_zip = extract_field(r"City, State, Zip:\s*</b>(.*?)<", decoded_body)
    requirements = extract_field(r"Do you meet all of the requirements\?\s*</b>(.*?)<", decoded_body)

    rows.append({
        "Submission Date": submission_date,
        "First Name": first_name,
        "Last Name": last_name,
        "Email": email,
        "Phone": phone,
        "Address": address,
        "City/State/Zip": city_state_zip,
        "Requirements": requirements
    })

# ---------------------------------------
# EXPORT TO EXCEL
# ---------------------------------------

df = pd.DataFrame(rows)

df.to_excel(OUTPUT_FILE, index=False)

# ---------------------------------------
# EMAIL BACKUP COPY
# ---------------------------------------

def send_backup_email(service, recipient, attachment_path, entry_count):
    message = EmailMessage()

    message["To"] = recipient
    message["From"] = "me"
    message["Subject"] = "2026 Gift Contest Daily Export"

    message.set_content(
        f"""Good morning,

Attached is the latest 2026 Gift Contest export.

Total entries exported: {entry_count}

This is an automated backup email.
"""
    )

    with open(attachment_path, "rb") as file:
        file_data = file.read()

    message.add_attachment(
        file_data,
        maintype="application",
        subtype="vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        filename=attachment_path
    )

    encoded_message = base64.urlsafe_b64encode(message.as_bytes()).decode()

    create_message = {
        "raw": encoded_message
    }

    service.users().messages().send(
        userId="me",
        body=create_message
    ).execute()


send_backup_email(
    service=service,
    recipient=BACKUP_RECIPIENT,
    attachment_path=OUTPUT_FILE,
    entry_count=len(rows)
)

print(f"Backup email sent to {BACKUP_RECIPIENT}")

print(f"\nSUCCESS!")
print(f"Exported {len(rows)} entries to:")
print(OUTPUT_FILE)