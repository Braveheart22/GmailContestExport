import pickle
import base64
import re
import pandas as pd

from googleapiclient.discovery import build

LABEL_ID = "Label_6083117079229242213"

# ---------------------------------------
# CONNECT TO GMAIL
# ---------------------------------------

with open("token.pickle", "rb") as token:
    creds = pickle.load(token)

service = build("gmail", "v1", credentials=creds)

# ---------------------------------------
# GET ALL MESSAGES
# ---------------------------------------

results = service.users().messages().list(
    userId="me",
    labelIds=[LABEL_ID],
    maxResults=500
).execute()

messages = results.get("messages", [])

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

output_file = "2026_Gift_Contest.xlsx"

df.to_excel(output_file, index=False)

print(f"\nSUCCESS!")
print(f"Exported {len(rows)} entries to:")
print(output_file)