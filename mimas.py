#!/usr/bin/env python
# -*- coding: utf-8 -*-

import argparse
import os
import email
from email import policy
import bitstream
import berkeleydbstore
import base91
import gmail
import utils
from email.utils import parsedate_to_datetime
from email.utils import format_datetime
from dateutil import parser
from datetime import datetime, timezone
import unidecode
import sys
import tempfile
import subprocess

# mimas list inbox | archive | outbox | sent | trash | drafts | all
# mimas read id
# mimas unread id
# mimas search query
# mimas move id folder
# mimas reply id
# mimas new
# mimas send
# mimas receive
# 

ps = berkeleydbstore.BerkeleyDBStore("mimas.db3")

# Create main parser
parser = argparse.ArgumentParser(description="Mimas command-line interface")
subparsers = parser.add_subparsers(dest="command", required=True)

list_parser = subparsers.add_parser("list", help="List messages in folder")
list_parser.add_argument("folder", type=str, help="Destination folder")

read_parser = subparsers.add_parser("read", help="Read message and mark as read")
read_parser.add_argument("id", type=int, help="Message ID")

show_parser = subparsers.add_parser("show", help="Show message, do not mark as read")
show_parser.add_argument("id", type=int, help="Message ID")

search_parser = subparsers.add_parser("search", help="Search messages")
search_parser.add_argument("query", type=str, help="Search string")

move_parser = subparsers.add_parser("move", help="Move message to a folder")
move_parser.add_argument("id", type=int, help="Message ID")
move_parser.add_argument("folder", type=str, help="Destination folder")

new_parser = subparsers.add_parser("reply", help="Reply to a message")
new_parser.add_argument("id", type=int, help="Message ID")

new_parser = subparsers.add_parser("new", help="Create a new message")

send_parser = subparsers.add_parser("send", help="Send messages")
send_parser.add_argument("max_size", type=int, help="Max Size Of Response")

receive_parser = subparsers.add_parser("receive", help="Receive new messages")

# Parse arguments
args = parser.parse_args()

# Handle commands
if args.command == "list":
    folder_path =  args.folder
    if not os.path.exists(os.path.join(utils.EMAIL_FOLDERS_ROOT,folder_path)):
        if folder_path == "all":
            folders = ["inbox", "archive", "outbox", "sent", "trash", "drafts"]
            messages = []
            for folder in folders:
                folder = os.path.join(utils.EMAIL_FOLDERS_ROOT, folder)
                if not os.path.exists(folder):
                    continue
                for filename in os.listdir(folder):
                    if filename.endswith(".eml"):
                        file_path = os.path.join(folder, filename)
                        with open(file_path, "r") as file:
                            msg = email.message_from_file(file, policy=policy.default)
                            date = parsedate_to_datetime(msg["Date"]) if msg["Date"] else None
                            messages.append((date, folder, filename, msg["Subject"]))
            # Sort messages by date in descending order
            messages.sort(key=lambda x: x[0], reverse=True)

            for date, folder, filename, subject in messages:
                print(f"{date.strftime('%Y-%m-%d %H:%M:%S')} - {folder}/{filename} - {subject}")
            print("Listing messages in all folders.")
        else:
            print(f"Folder '{folder_path}' does not exist.")
        sys.exit(1)
    else:
        messages = []
        for filename in os.listdir(os.path.join(utils.EMAIL_FOLDERS_ROOT,folder_path)):
            if filename.endswith(".eml"):
                file_path = os.path.join(os.path.join(utils.EMAIL_FOLDERS_ROOT,folder_path), filename)
                with open(file_path, "r") as file:
                    msg = email.message_from_file(file, policy=policy.default)
                    date = parsedate_to_datetime(msg["Date"]) if msg["Date"] else None
                    messages.append((date, filename, msg["Subject"]))

        # Sort messages by date in descending order
        messages.sort(key=lambda x: x[0], reverse=True)

        for date, filename, subject in messages:
            print(f"{date.strftime('%Y-%m-%d %H:%M:%S')} - {filename} - {subject}")
    
elif args.command == "search":
    folders = ["inbox", "archive", "outbox", "sent", "trash", "drafts"]
    matching_messages = []

    for folder in folders:
        folder_path = os.path.join(utils.EMAIL_FOLDERS_ROOT, folder)
        if not os.path.exists(folder_path):
            continue
        for filename in os.listdir(os.path.join(utils.EMAIL_FOLDERS_ROOT, folder)):
            if filename.endswith(".eml"):
                file_path = os.path.join(utils.EMAIL_FOLDERS_ROOT, folder, filename)
                with open(file_path, "r") as file:
                    msg = email.message_from_file(file, policy=policy.default)
                    if args.query.lower() in msg.as_string().lower():
                        date = parser.parse(msg["Date"])
                        matching_messages.append((date, folder, filename, msg["Subject"]))

    # Sort matching messages by date in descending order
    matching_messages.sort(key=lambda x: x[0], reverse=True)

    for date, folder, filename, subject in matching_messages:
        print(f"{date.strftime('%Y-%m-%d %H:%M:%S')} - {folder}/{filename} - {subject}")
    print(f"Searching for messages containing: {args.query}")
elif args.command == "move":
    # Locate the email in the current folder
    folders = ["inbox", "archive", "outbox", "sent", "trash", "drafts"]
    for folder in folders:
        folder_path = os.path.join(utils.EMAIL_FOLDERS_ROOT, folder)
        if not os.path.exists(folder_path):
            continue
        for filename in os.listdir(folder_path):
            if filename.endswith(".eml"):
                file_path = os.path.join(folder_path, filename)
                with open(file_path, "r") as file:
                    msg = email.message_from_file(file, policy=policy.default)
                    if msg["X-Mimas-Id"] == str(args.id):
                        # Move the file to the destination folder
                        destination_folder = os.path.join(utils.EMAIL_FOLDERS_ROOT, args.folder)
                        os.makedirs(destination_folder, exist_ok=True)
                        new_file_path = os.path.join(destination_folder, filename)
                        os.rename(file_path, new_file_path)
                        print(f"Message ID {args.id} moved from folder '{folder}' to folder '{destination_folder}'.")
                        break
        else:
            continue
        break
    else:
        print(f"Message ID {args.id} not found in any folder.")
        sys.exit(1)
elif args.command == "new":
    # Create a new message
    # Ask for recipient and subject
    recipient = input("Enter recipient: ")
    subject = input("Enter subject: ")

    # Open vi to compose the message
    with tempfile.NamedTemporaryFile(suffix=".txt", delete=False) as temp_file:
        temp_file_path = temp_file.name

    subprocess.call(["vi", temp_file_path])

    # Read the composed message
    with open(temp_file_path, "r") as temp_file:
        body = temp_file.read()

    # Save the message in the outbox folder
    outbox_folder = os.path.join(utils.EMAIL_FOLDERS_ROOT, "outbox")
    os.makedirs(outbox_folder, exist_ok=True)

    # assign mimas-id to the messsage
    last_id = ps.get("last-msg-id")
    if not last_id:
        last_id = (1 << utils.ID_LENGTH) -1
    mimas_id = int(last_id) - 1
    ps.set("last-msg-id", str(mimas_id))


    email_message = email.message.EmailMessage()
    email_message["To"] = recipient
    email_message["Subject"] = subject
    email_message["Date"] = format_datetime(datetime.now(timezone.utc))
    email_message["X-Mimas-Id"] = str(mimas_id)
    email_message.set_content(body)

    file_path = os.path.join(outbox_folder, f"{email_message['X-Mimas-Id']}.eml")
    with open(file_path, "w") as file:
        file.write(email_message.as_string())

    print(f"Message saved to outbox: {file_path}")
elif args.command == "reply":
    # Locate the email in the inbox folder
    inbox_folder = os.path.join(utils.EMAIL_FOLDERS_ROOT, "inbox")
    for filename in os.listdir(inbox_folder):
        if filename.endswith(".eml"):
            file_path = os.path.join(inbox_folder, filename)
            with open(file_path, "r") as file:
                msg = email.message_from_file(file, policy=policy.default)
                if msg["X-Mimas-Id"] == str(args.id):
                    # Open vi to compose the reply
                    with tempfile.NamedTemporaryFile(suffix=".txt", delete=False) as temp_file:
                        temp_file.write(msg.as_string().encode())  # Insert original message
                        temp_file_path = temp_file.name

                    subprocess.call(["vi", temp_file_path])

                    # Read the composed message
                    with open(temp_file_path, "r") as temp_file:
                        body = temp_file.read()

                    # Save the reply message in the outbox folder
                    outbox_folder = os.path.join(utils.EMAIL_FOLDERS_ROOT, "outbox")
                    os.makedirs(outbox_folder, exist_ok=True)

                    # assign mimas-id to the messsage
                    last_id = ps.get("last-msg-id")
                    if not last_id:
                        last_id = (1 << utils.ID_LENGTH) - 1
                    mimas_id = int(last_id) - 1
                    ps.set("last-msg-id", str(mimas_id))

                    email_message = email.message.EmailMessage()
                    email_message["To"] = msg["From"]
                    email_message["Date"] = format_datetime(datetime.now(timezone.utc))
                    email_message["Subject"] = f"Re: {msg['Subject']}"
                    email_message["X-Mimas-Id"] = str(mimas_id)
                    email_message["X-Mimas-Reply-Id"] = msg["X-Mimas-Id"]
                    email_message.set_content(body)

                    reply_file_path = os.path.join(outbox_folder, f"{email_message['X-Mimas-Id']}.eml")
                    with open(reply_file_path, "w") as file:
                        file.write(email_message.as_string())

                    print(f"Reply saved to outbox: {reply_file_path}")
                    break
    else:
        print(f"Message ID {args.id} not found in inbox.")
        sys.exit(1)
    print(f"Replying to message ID: {args.id}")
elif args.command == "read":
    # Locate the email in the inbox folder
    inbox_folder = os.path.join(utils.EMAIL_FOLDERS_ROOT, "inbox")
    archive_folder = os.path.join(utils.EMAIL_FOLDERS_ROOT, "archive")
    os.makedirs(archive_folder, exist_ok=True)
    for filename in os.listdir(inbox_folder):
        if filename.endswith(".eml"):
            file_path = os.path.join(inbox_folder, filename)
            with open(file_path, "r") as file:
                msg = email.message_from_file(file, policy=policy.default)
                if msg["X-Mimas-Id"] == str(args.id):
                    # Print the message
                    print(msg.as_string())
                    # Add the X-Marked-Read header
                    msg["X-Marked-Read"] = "pending"
                    # Move the file to the archive folder
                    new_file_path = os.path.join(archive_folder, filename)
                    with open(new_file_path, "w") as archive_file:
                        archive_file.write(msg.as_string())
                    os.remove(file_path)
                    break
elif args.command == "show":
    # Locate the email in the inbox folder
    inbox_folder = os.path.join(utils.EMAIL_FOLDERS_ROOT, "inbox")
    for filename in os.listdir(inbox_folder):
        if filename.endswith(".eml"):
            file_path = os.path.join(inbox_folder, filename)
            with open(file_path, "r") as file:
                msg = email.message_from_file(file, policy=policy.default)
                if msg["X-Mimas-Id"] == str(args.id):
                    # Print the message without marking it as read
                    print(msg.as_string())
                    break
elif args.command == "send":
    # bitstream
    bso = bitstream.Bitstream()
    # get all messages from outbox
    outbox_folder = os.path.join(utils.EMAIL_FOLDERS_ROOT, "outbox")
    outbox_emails = []

    for filename in os.listdir(outbox_folder):
        if filename.endswith(".eml"):  # Assuming emails are stored as .eml files
            with open(os.path.join(outbox_folder, filename), "r") as file:
                msg = email.message_from_file(file, policy=policy.default)
                email_data = {
                    "recipient": utils.decode_email_address(msg["To"]),
                    "subject": utils.decode_email_subject(msg["Subject"]),
                    "id": int(msg["X-Mimas-Id"]),
                    "reply-id": int(msg["X-Mimas-Reply-Id"]) if msg["X-Mimas-Reply-Id"] else None,
                    "body": msg.get_body(preferencelist=("plain")).get_content() if msg.is_multipart() else msg.get_payload()
                }
                outbox_emails.append(email_data)

    for email_data in outbox_emails:
        # add to bitstream
        # reply
        if email_data["reply-id"]:
            bso.write_fixed_width(utils.CMD_REPLY, utils.CMD_LENGTH)
            bso.write_fixed_width(email_data["id"], utils.ID_LENGTH)
            bso.write_fixed_width(email_data["reply-id"], utils.ID_LENGTH)
        # send
        else:
            bso.write_fixed_width(utils.CMD_SEND, utils.CMD_LENGTH)
            bso.write_fixed_width(email_data["id"], utils.ID_LENGTH)
            bso.write_huffman_string(utils.str_encode(email_data["recipient"]))
            bso.write_huffman_string(utils.str_encode(email_data["subject"]))
        # body in both cases
        bso.write_huffman_string(utils.str_encode(email_data["body"]))

    # get marked read messages
    archive_folder = os.path.join(utils.EMAIL_FOLDERS_ROOT, "archive")
    marked_read_emails = []
    for filename in os.listdir(archive_folder):
        if filename.endswith(".eml"):  # Assuming emails are stored as .eml files
            with open(os.path.join(archive_folder, filename), "r") as file:
                msg = email.message_from_file(file, policy=policy.default)
                if msg["X-Marked-Read"] == "pending":
                    email_data = {
                        "id": msg["X-Mimas-Id"],
                    }
                    marked_read_emails.append(email_data)

    for email_data in marked_read_emails:
        bso.write_fixed_width(utils.CMD_MARK_READ, utils.CMD_LENGTH)
        bso.write_fixed_width(int(email_data["id"]), utils.ID_LENGTH)

    # request new messages
    bso.write_fixed_width(utils.CMD_CHECK_MAIL, utils.CMD_LENGTH)
    # get last mail check time
    last_mail_check = ps.get("last-mail-check")
    if not last_mail_check:
        last_mail_check = 0
    bso.write_fixed_width(int(last_mail_check), utils.DATE_LENGTH)
    # get max size
    max_size = args.max_size
    bso.write_fixed_width(max_size, utils.MAX_SIZE_LENGTH)

    # write out the bitstream
    out = base91.encode(bso.export())
    sys.stdout.write(out)
elif args.command == "receive":
    def new_message(bsi):
        # read id
        id = bsi.read_fixed_width(utils.ID_LENGTH)
        # read date
        date = bsi.read_fixed_width(utils.DATE_LENGTH)
        # read from
        from_ = bsi.read_huffman_string()
        # read subject
        subject = bsi.read_huffman_string()
        # read body
        body = bsi.read_huffman_string()
        # Save the message in e-mail format to the inbox folder
        inbox_folder = os.path.join(utils.EMAIL_FOLDERS_ROOT, "inbox")
        os.makedirs(inbox_folder, exist_ok=True)
        email_message = email.message.EmailMessage()
        email_message["From"] = from_
        email_message["Subject"] = subject
        email_message["Date"] = datetime.fromtimestamp(int(date)).strftime("%a, %d %b %Y %H:%M:%S %z")
        email_message["X-Mimas-Id"] = str(id)
        email_message.set_content(body)
        file_path = os.path.join(inbox_folder, f"{id}.eml")
        with open(file_path, "w") as file:
            file.write(email_message.as_string())
    def marked_read(bsi):
        # read id
        id = bsi.read_fixed_width(utils.ID_LENGTH)
        # Locate the email in the archive folder and update its status
        archive_folder = os.path.join(utils.EMAIL_FOLDERS_ROOT, "archive")
        for filename in os.listdir(archive_folder):
            if filename.endswith(".eml"):
                file_path = os.path.join(archive_folder, filename)
                with open(file_path, "r") as file:
                    msg = email.message_from_file(file, policy=policy.default)
                    if msg["X-Mimas-Id"] == id and msg["X-Marked-Read"] == "pending":
                        msg["X-Marked-Read"] = "confirmed"
                        with open(file_path, "w") as updated_file:
                            updated_file.write(msg.as_string())
                        break
    def confirm_sent(bsi):
        # read id
        id = bsi.read_fixed_width(utils.ID_LENGTH)
        # Move the message from the outbox to the sent folder
        outbox_folder = os.path.join(utils.EMAIL_FOLDERS_ROOT, "outbox")
        sent_folder = os.path.join(utils.EMAIL_FOLDERS_ROOT, "sent")
        os.makedirs(sent_folder, exist_ok=True)
        for filename in os.listdir(outbox_folder):
            if filename.endswith(".eml"):
                file_path = os.path.join(outbox_folder, filename)
                with open(file_path, "r") as file:
                    msg = email.message_from_file(file, policy=policy.default)
                    if msg["X-Mimas-Id"] == id:
                    # Move the file
                        new_file_path = os.path.join(sent_folder, filename)
                        os.rename(file_path, new_file_path)
                        break
    # read the bitstream
    data = sys.stdin.read()
    bsi = bitstream.Bitstream(base91.decode(data))
    ps.set("last-mail-check", str(bsi.read_fixed_width(utils.DATE_LENGTH)))

    resp_map = {
        utils.RESP_MESSAGE: new_message,
        utils.RESP_MARKED_READ: marked_read,
        utils.RESP_SENT: confirm_sent
    }

    while True:
        try:
            resp = bsi.read_fixed_width(utils.CMD_LENGTH)
            # run handler
            resp_map[resp](bsi)
        except IndexError:
            break
