#!/usr/bin/env python
# -*- coding: utf-8 -*-

import argparse

# mimas inbox | archive | outbox | sent | trash | drafts | all
# mimas read id
# mimas unread id
# mimas search query
# mimas move id folder
# mimas reply id
# mimas new
# mimas send
# mimas receive

# Create main parser
parser = argparse.ArgumentParser(description="Mimas command-line interface")
subparsers = parser.add_subparsers(dest="command", required=True)

list_parser = subparsers.add_parser("inbox", help="List messages in  Inbox")
list_parser = subparsers.add_parser("archive", help="List messages in  Archive")
list_parser = subparsers.add_parser("outbox", help="List messages in  Outbox")
list_parser = subparsers.add_parser("sent", help="List messages in  Sent")
list_parser = subparsers.add_parser("trash", help="List messages in  Trash")
list_parser = subparsers.add_parser("drafts", help="List messages in  Drafts")
list_parser = subparsers.add_parser("all", help="List all messages")

read_parser = subparsers.add_parser("read", help="Read message and mark as read")
read_parser.add_argument("query", type=int, help="Search string")

unread_parser = subparsers.add_parser("unread", help="Mark message as unread")
unread_parser.add_argument("query", type=int, help="Search string")

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
    print(f"Listing messages in folder: {args.folder or 'inbox'}")
    
elif args.command == "search":
    print(f"Searching for messages containing: {args.query}")
elif args.command == "new":
    print("Creating a new message...")
elif args.command == "reply":
    print(f"Replying to message ID: {args.id}")
elif args.command == "read":
    print(f"Reading message ID: {args.id}")
elif args.command == "unread":
    print(f"Marking message ID {args.id} as unread")
elif args.command == "show":
    print(f"Showing message ID: {args.id}")
elif args.command == "send":
    print("Sending messages...")
elif args.command == "receive":
    print("Receiving new messages...")
