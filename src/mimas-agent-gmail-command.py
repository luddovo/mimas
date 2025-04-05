import gmail
import sys
import email, base91
import utils
import subprocess

# Read the raw email from stdin
raw_email = sys.stdin.read()

# Parse the email
parsed_email = email.message_from_string(raw_email)

# Extract the "From", "Subject", and "Body"
email_from = parsed_email.get("From")
email_subject = parsed_email.get("Subject")

email_from = utils.decode_email_address(email_from)
email_subject = utils.decode_email_subject(email_subject)

# Extract the body
if parsed_email.is_multipart():
    for part in parsed_email.walk():
        if part.get_content_type() == "text/plain" and not part.get("Content-Disposition"):
            email_body = part.get_payload(decode=True).decode(part.get_content_charset())
            break
else:
    email_body = parsed_email.get_payload(decode=True).decode(parsed_email.get_content_charset() or "ascii")

    # Check if the subject contains the words "mimas message" (case insensitive)
    if "mimas command" in email_subject.lower():

        # Decode the email body

        # Run the external script and send email_body to its stdin
        process = subprocess.Popen(
            ["bin/python", "/home/ludd/work/mimas/src/mimas-agent.py"],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )

        stdout, stderr = process.communicate(input=email_body)
        return_code = process.returncode

        gmail_service = gmail.authenticate_service_account()

        # Check if the process was successful
        if return_code == 0:
            gmail.send_email(
                service=gmail_service,
                to=email_from,
                subject="Mimas Response",
                text=stdout
            )
        else:
            # Handle the error case
            gmail.send_email(
                service=gmail_service,
                to=email_from,
                subject="Mimas Error",
                text=stderr
            )
            pass
