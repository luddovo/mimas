import os
import base64
from googleapiclient.discovery import build
from google.oauth2 import service_account
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

# Path to your Service Account JSON key file
SERVICE_ACCOUNT_FILE = 'oauth2.json'

# Gmail API Scopes
SCOPES = ['https://www.googleapis.com/auth/gmail.send']

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

def create_message(sender, to, subject, body):
    """Create an email message."""
    message = MIMEMultipart()
    message['to'] = to
    message['from'] = sender
    message['subject'] = subject

    msg_body = MIMEText(body, 'plain')
    message.attach(msg_body)

    # Encode the message in base64
    raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode()

    return {'raw': raw_message}

def send_message(service, user_id, message):
    """Send the email message using Gmail API."""
    try:
        message = service.users().messages().send(userId=user_id, body=message).execute()
        print(f"Message sent successfully! Message ID: {message['id']}")
    except Exception as error:
        print(f"An error occurred: {error}")

# Authenticate and get the Gmail service object
service = authenticate_service_account()

# Create a message to send
message = create_message(
    sender='your-service-account@your-project-id.iam.gserviceaccount.com', 
    to='ludek@chovanec.com', 
    subject='Test Email', 
    body='This is a test email sent via the Gmail API using Service Account authentication.'
)

# Send the email
send_message(service, 'me', message)

