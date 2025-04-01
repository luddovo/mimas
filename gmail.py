from googleapiclient.discovery import build
from google.oauth2 import service_account
import base64
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

# Path to your Service Account JSON key file
SERVICE_ACCOUNT_FILE = 'oauth2.json'

# Gmail API Scopes
SCOPES = ['https://www.googleapis.com/auth/gmail.send','https://www.googleapis.com/auth/gmail.readonly','https://www.googleapis.com/auth/gmail.modify']

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

def get_unread_emails(service, after_date):
    """Retrieve unread emails in the inbox since after_date."""

    # Search query for unread emails in inbox from the last 10 days
    query = f"is:unread in:inbox after:{after_date}"

    # Fetch unread messages
    results = service.users().messages().list(userId='me', q=query).execute()
    messages = results.get('messages', [])

    if not messages:
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
            header_name = header['name'].lower()
            if header_name == 'from':
                email_data["from"] = header['value']
            if header_name == 'subject':
                email_data["subject"] = header['value']
            if header_name == 'date':
                email_data["date"] = header['value']

        email_list.append(email_data)

    return email_list

def mark_message_as_read(service, message_id):
    """Mark a Gmail message as read by removing the 'UNREAD' label."""
    try:
        service.users().messages().modify(
            userId='me',
            id=message_id,
            body={'removeLabelIds': ['UNREAD']}
        ).execute()
        return True

    except:
        return False

def send_reply(service, message_id, reply_text):
    """Send a reply to the given message, handling the Reply-To header."""

    # Get the original message
    message = service.users().messages().get(userId='me', id=message_id).execute()

    # Extract headers
    headers = message['payload']['headers']
    
    # Check for Reply-To header, otherwise fallback to From header
    to_address = None
    for header in headers:
        if header['name'].lower() == 'reply-to':
            to_address = header['value']
            break
    if not to_address:
        for header in headers:
            if header['name'].lower() == 'from':
                to_address = header['value']
                break

    if not to_address:
        raise("Unable to determine recipient email address.")
        return

    # Find the subject in headers, if it does not exist, set it to an empty string
    subject = ""
    for header in headers:
        if header['name'].lower() == 'subject':
            subject = header['value']
            break

    # Create the reply message
    reply_message = create_message('me', to_address, 'Re: ' + subject, reply_text)

    # Send the reply
    send_message = service.users().messages().send(userId='me', body=reply_message).execute()
    
    return send_message['id']

def send_email(service, to, subject, text):
    """Send an email and return the message ID."""
    try:
        # Create the email message
        message = MIMEText(text)
        message['to'] = to
        message['subject'] = subject
        raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode()

        # Send the email
        sent_message = service.users().messages().send(
            userId='me',
            body={'raw': raw_message}
        ).execute()

        return sent_message['id']

    except:
        return None

def get_message(service, message_id):
    """Retrieve a message and return the message ID, From, Subject, and the plain text or raw body."""

    # Get the message
    message = service.users().messages().get(userId='me', id=message_id).execute()

    # Extract message details
    message_id = message['id']
    payload = message['payload']
    headers = payload['headers']

    # Get the "From" and "Subject" headers
    from_address = None
    subject = None
    for header in headers:
        if header['name'] == 'From':
            from_address = header['value']
        elif header['name'] == 'Subject':
            subject = header['value']

    # Try to extract the plain text or raw body from 'parts' or 'body'
    body = ''
    if 'parts' in payload:
        # Check for plain text or HTML part
        for part in payload['parts']:
            if part['mimeType'] == 'text/plain':
                body = base64.urlsafe_b64decode(part['body']['data']).decode('utf-8')
                break
            elif part['mimeType'] == 'text/html':
                body = base64.urlsafe_b64decode(part['body']['data']).decode('utf-8')
                break
    elif 'body' in payload and 'data' in payload['body']:
        # If there's no 'parts', we check the raw body
        body = base64.urlsafe_b64decode(payload['body']['data']).decode('utf-8')

    # Return the message details
    return {
        'message_id': message_id,
        'from': from_address,
        'subject': subject,
        'body': body
    }

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
