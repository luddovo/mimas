import os
import base64
import datetime
from googleapiclient.discovery import build
from google.oauth2 import service_account
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

# Path to your Service Account JSON key file
SERVICE_ACCOUNT_FILE = 'oauth2.json'

# Gmail API Scopes
SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']

# Email of the user to impersonate
USER_TO_IMPERSONATE = 'ludek@chovanec.com'

def authenticate_service_account():
    """Authenticate and create a service object using the Service Account."""
    credentials = service_account.Credentials.from_service_account_file(
        SERVICE_ACCOUNT_FILE,
        scopes=SCOPES
    )

    # Impersonate the user
    credentials = credentials.with_subject(USER_TO_IMPERSONATE)

    # Build the Gmail API service
    service = build('gmail', 'v1', credentials=credentials)
    return service
def get_unread_emails(service):
    """Retrieve unread emails in the inbox from the past 10 days."""
    # Calculate the date 10 days ago
    ten_days_ago = (datetime.datetime.utcnow() - datetime.timedelta(days=10)).strftime('%Y/%m/%d')

    # Search query for unread emails in inbox from the last 10 days
    query = f"is:unread in:inbox after:{ten_days_ago}"

    # Fetch unread messages
    results = service.users().messages().list(userId='me', q=query).execute()
    messages = results.get('messages', [])

    if not messages:
        print("No unread emails found in the last 10 days.")
        return []

    email_list = []
    
    for message in messages:
        msg = service.users().messages().get(userId='me', id=message['id']).execute()
        
        email_data = {
            "id": msg['id'],
            "snippet": msg.get("snippet", ""),  # Preview text of the email
            "from": "",
            "subject": "",
            "date": ""
        }

        # Extract headers (From, Subject, Date)
        for header in msg['payload']['headers']:
            if header['name'] == 'From':
                email_data["from"] = header['value']
            if header['name'] == 'Subject':
                email_data["subject"] = header['value']
            if header['name'] == 'Date':
                email_data["date"] = header['value']

        email_list.append(email_data)

    return email_list

# Authenticate and get the Gmail service object
service = authenticate_service_account()

# Fetch and print unread emails
unread_emails = get_unread_emails(service)

if unread_emails:
    print("\nUnread Emails in Inbox (Past 10 Days):\n")
    for email in unread_emails:
        print(f"From: {email['from']}")
        print(f"Subject: {email['subject']}")
        print(f"Date: {email['date']}")
        print(f"Snippet: {email['snippet']}")
        print("=" * 50)
