import os
from azure.communication.email import EmailClient
from dotenv import load_dotenv
import uuid

load_dotenv() 

ACS_CONNECTION_STRING = os.getenv("ACS_CONNECTION_STRING")
SENDER_ADDRESS = os.getenv("SENDER_ADDRESS")
RECIPIENT_ADDRESS = os.getenv("RECIPIENT_ADDRESS")

conversation_id = f"conv-{uuid.uuid4().hex[:8]}"

client = EmailClient.from_connection_string(ACS_CONNECTION_STRING)
message_id = f"<{uuid.uuid4().hex}@carclinch.com>"

result = client.begin_send({
    "senderAddress": SENDER_ADDRESS,
    "recipients": {"to": [{"address": RECIPIENT_ADDRESS}]},
    "replyTo": [{"address": "carclinch-dev@outlook.com"}],  # replies go to the Logic App mailbox
    "headers": {
        "Message-ID": message_id
    },
    "content": {
        "subject": f"Test inbound reply flow [REF:{conversation_id}]",  # REF tag for threading
        "plainText": "Please reply to this email to test inbound handling."
    }
})

print("Message ID (ACS):", result.result()['id'])
print("Custom Message-ID header:", message_id)
print("Conversation ID:", conversation_id)
print(f"Reply to this email from {RECIPIENT_ADDRESS} to trigger the Logic App")