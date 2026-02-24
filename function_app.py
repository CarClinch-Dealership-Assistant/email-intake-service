import azure.functions as func
import logging
import os
from dotenv import load_dotenv
import re

app = func.FunctionApp()
load_dotenv()

def extract_conversation_id(subject: str):
    match = re.search(r'\[REF:(.+?)\]', subject)
    return match.group(1) if match else None

# this function is triggered by the Logic App via HTTP POST when a new reply arrives
# the Logic App monitors an M365 mailbox (carclinch-dev@outlook.com) and forwards replies here
# the Reply-To header on outbound ACS emails should be set to that mailbox address
@app.route(route="inbound-email", methods=["POST"])
def handle_inbound_email(req: func.HttpRequest) -> func.HttpResponse:
    logging.info("Inbound email received")

    try:
        data = req.get_json()
    except ValueError:
        return func.HttpResponse("Invalid JSON", status_code=400)

    sender = data.get("from")
    recipient = data.get("to")
    subject = data.get("subject")
    has_attachments = data.get("hasAttachments", False)
    conversation_id = extract_conversation_id(subject)

    # body is passed directly from the Logic App
    body_text = data.get("bodyText")
    body_html = data.get("bodyHtml")

    logging.info(
        "Inbound email | From: %s | Subject: %s | ConversationId: %s",
        sender, subject, conversation_id
    )

    # later: store to DB, enqueue, etc.
    process_reply(
        conversation_id=conversation_id,
        sender=sender,
        subject=subject,
        body_text=body_text,
        in_reply_to=data.get("inReplyTo"),  # customer's InternetMessageId, used to thread our reply
        has_attachments=has_attachments,
    )

    # Logic App expects a 200 back to confirm successful processing
    return func.HttpResponse("OK", status_code=200)


def process_reply(conversation_id, sender, subject, in_reply_to, body_text, has_attachments):
    # gonna make sure i can intake properly
    logging.info("Processing reply to message: %s | ConversationId: %s", in_reply_to, conversation_id)