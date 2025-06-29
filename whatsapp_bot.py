from flask import Flask, request
import requests
import json
from gemini_utils import generate_response
from zoho_leads import get_or_create_lead

app = Flask(__name__)

VERIFY_TOKEN = "Tamil_Agent_Bot"
WHATSAPP_API_URL = "https://graph.facebook.com/v18.0/693360950535870/messages"
ACCESS_TOKEN = "EAAJZBBNLdXv8BOzCjxiEo4uivEzIFMMAbmMZAI0sPq9xdcHcOHDWsSkpHCBQ6APRXKkfgM2hZA9AGkCRxuHnsvH1POuloBDy2rQXwnxiAW6ZClGU6RgYOAJa4ETY25erICX4rvq7By2BmjNZA6xx4wV3MJDWkrxXLBCX1PFZA2JcUZAVw5FTwV1sOJKWQLEE6CjZAwf51CYCRDoYuthJXUxgqOte9tzvs3ZC0dGOYVlZBESF8rWQZDZD"

# Session storage (very basic)
user_sessions = {}

# Send WhatsApp message
def send_whatsapp_message(recipient_id, message):
    if len(message) > 4096:
        message = message[:4090] + "..."  # Truncate long messages

    headers = {
        "Authorization": f"Bearer {ACCESS_TOKEN}",
        "Content-Type": "application/json"
    }
    data = {
        "messaging_product": "whatsapp",
        "to": recipient_id,
        "type": "text",
        "text": {"body": message}
    }
    response = requests.post(WHATSAPP_API_URL, headers=headers, json=data)
    print("📤 WhatsApp API status:", response.status_code)
    print("📨 Response:", response.text)

# Webhook verification
@app.route("/webhook", methods=["GET"])
def verify():
    mode = request.args.get("hub.mode")
    token = request.args.get("hub.verify_token")
    challenge = request.args.get("hub.challenge")
    if mode == "subscribe" and token == VERIFY_TOKEN:
        return challenge
    return "Verification failed", 403

# Webhook for incoming messages
@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.get_json()
    print("📥 Incoming message:", json.dumps(data, indent=2))

    entry = data.get("entry", [])[0]
    changes = entry.get("changes", [])[0]
    value = changes.get("value", {})
    messages = value.get("messages", [])
    if not messages:
        print("⚠️ No 'messages' key found (probably a delivery status update). Skipping.")
        return "OK", 200

    message = messages[0]
    sender_id = message["from"]
    text = message["text"]["body"].strip().lower()

    # Get or create user session
    session = user_sessions.get(sender_id, {"step": "start"})
    step = session["step"]

    # RESET COMMAND
    if text in ["reset", "restart"]:
        user_sessions[sender_id] = {"step": "start"}
        send_whatsapp_message(sender_id, "🔄 Reset complete. Please type *hi* to start again.")
        return "OK", 200

    try:
        # Step: Welcome
        if step == "start":
            contact = value.get("contacts", [])[0]
            name = contact.get("profile", {}).get("name", "User")
            response = get_or_create_lead(sender_id, name)
            print("📄 Zoho response text:", response)
            session["step"] = "chatting"
            user_sessions[sender_id] = session
            send_whatsapp_message(sender_id, "👋 Hello! I’m your virtual assistant. How can I help you today?")
            return "OK", 200

        # Step: Chatting with Gemini
        elif step == "chatting":
            response_text = generate_response(text)
            if not response_text:
                raise Exception("Empty response from Gemini")
            reply = response_text[:4090] + "..." if len(response_text) > 4096 else response_text
            send_whatsapp_message(sender_id, reply)
            return "OK", 200

    except Exception as e:
        print("❌ Error:", e)
        send_whatsapp_message(sender_id, "⚠️ Sorry, something went wrong. Please try again.")
        return "OK", 200

    return "OK", 200

if __name__ == "__main__":
    app.run(debug=True)
