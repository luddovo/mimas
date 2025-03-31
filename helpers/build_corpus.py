import mailbox
from email.utils import parseaddr
from email.header import decode_header
import sys

def decode_email_subject(subject):
    decoded_parts = decode_header(subject)
    decoded_subject = ""

    for part, encoding in decoded_parts:
        if isinstance(part, bytes):
            # Decode using the provided encoding, defaulting to utf-8
            encoding = encoding if encoding and encoding.lower() != "unknown-8bit" else "utf-8"
            decoded_subject += part.decode(encoding, errors="ignore")
        else:
            decoded_subject += part  # If already a string, just append it

    return decoded_subject

def extract_email_data(mbox_path):
    mbox = mailbox.mbox(mbox_path)
    
    sys.stderr.write(f"Number of messages: {len(mbox)}\n")

    # Iterate through the MBOX messages
    for message in mbox:
        # Extract "From", "To", and "Subject"
        from_field = message.get("From")
        to_field = message.get("To")
        subject_field = message.get("Subject")
        if subject_field:
            subject_field = decode_email_subject(message.get("Subject"))
        
        # Extract the text body (ignoring HTML or attachments)
        body = ""
        if message.is_multipart():
            # Iterate through the parts of the multipart message
            for part in message.walk():
                # Check if the part is text/plain (ignore text/html and attachments)
                if part.get_content_type() == "text/plain":
                    charset = part.get_content_charset() or "utf-8"
                    body = part.get_payload(decode=True).decode(charset, errors='ignore')
                    break
        else:
            # If not multipart, get the payload directly
            try:
                body = message.get_payload(decode=True).decode(message.get_content_charset(), errors='ignore')
            except:
                body = message.get_payload(decode=True).decode("utf-8", errors='ignore')
        
        # Clean up "From" and "To" to get just the email addresses
        from_email = parseaddr(from_field)[1]
        to_email = parseaddr(to_field)[1] if to_field else None

        # save the extracted info


        # Print the extracted information
        print(f"{from_email}␀{to_email}␀{subject_field}␀{body[:200]}")
# Provide the path to your MBOX file
mbox_path = "shebang.mbox"
extract_email_data(mbox_path)
