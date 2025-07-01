from flask import Flask, request, jsonify
import requests
import os
from gemini_utils import generate_with_gemini
from ollama_utils import ask_ollama
from zoho_leads import search_lead_by_phone, create_lead

app = Flask(__name__)

# === Configuration ===
VERIFY_TOKEN = os.getenv("ZOHO_VERIFY_TOKEN")
WHATSAPP_TOKEN = os.getenv("ZOHO_WHATSAPP_TOKEN")
PHONE_NUMBER_ID =os.getenv("WHATSAPP_PHONE_NUMBER_ID")

# VERIFY_TOKEN = "Tamil_Agent_Bot"
# WHATSAPP_API_URL = "https://graph.facebook.com/v18.0/693360950535870/messages"
# ACCESS_TOKEN = "EAAJZBBNLdXv8BOwZCdx0sjZBWII1piapHhqy56gqN6b9NQQzvp2lBr7pEP3vZA3kaJ0ePaYSL9qDA2mavlNwqR21m50jfv1qXedfTPUt15vObdLnBFbvI5TTbNOwajpBd2yDUgCgCbAq8u6FjGH54cZCq3eyZCzoZAuQlz3Cc38fjpMXE8vamGvEX8NUucbivnqhzsZAH7xtJSRvZBEL7tjWeHXQOAx2pHXPZCZB6eiUQoUMfehcwZDZD"


# === In-memory session store ===
session_memory = {}  # user_id -> list of message dicts
user_models = {}     # user_id -> model choice ("gemini" or "ollama")
user_info = {}       # user_id -> {'name': str, 'email': str, 'stage': str}

# @app.route("/", methods=["GET"], endpoint="verify")
@app.route("/webhook", methods=["GET"])
def verify():
    if request.args.get("hub.mode") == "subscribe" and request.args.get("hub.verify_token") == VERIFY_TOKEN:
        return request.args.get("hub.challenge"), 200
    return "Unauthorized", 403

# @app.route("/", methods=["POST"])
@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.get_json()
    print("📩 Incoming data:", data)

    try:
        entry = data["entry"][0]["changes"][0]["value"]
        if "messages" in entry:
            phone = entry["messages"][0]["from"]
            msg = entry["messages"][0]["text"]["body"].strip()

            print(f"✅ Message entry found\n📱 From: {phone} | Message: {msg}")

            # Handle model switch
            if msg.lower().startswith("/model"):
                model_choice = msg.split(" ")[-1].lower()
                if model_choice in ["gemini", "ollama"]:
                    user_models[phone] = model_choice
                    send_whatsapp_message(phone, f"✅ Model changed to: {model_choice.capitalize()}")
                else:
                    send_whatsapp_message(phone, "❌ Invalid model. Use: /model gemini or /model ollama")
                return "ok", 200

            # Handle reset
            if msg.lower() in ["/reset", "reset", "clear"]:
                session_memory[phone] = []
                user_info.pop(phone, None)
                send_whatsapp_message(phone, "🧠 Memory reset. Start a new legal query.")
                return "ok", 200

            # Check if user info exists
            if phone not in user_info:
                print(f"🔍 Searching lead with phone {phone}...")
                lead = search_lead_by_phone(phone)
                if lead:
                    name = lead.get("Full_Name") or lead.get("Last_Name", "User")
                    user_info[phone] = {"name": name, "email": lead.get("Email"), "stage": "done"}
                    send_whatsapp_message(phone, f"👋 Hi {name}, welcome back! Ask your question.")
                else:
                    user_info[phone] = {"stage": "ask_name"}
                    send_whatsapp_message(phone, "👋 Welcome! What's your full name?")
                return "ok", 200

            # Handle lead creation steps
            stage = user_info[phone].get("stage")
            if stage == "ask_name":
                user_info[phone]["name"] = msg
                user_info[phone]["stage"] = "ask_email"
                send_whatsapp_message(phone, "📧 Great! Now please share your email address.")
                return "ok", 200
            elif stage == "ask_email":
                user_info[phone]["email"] = msg
                name = user_info[phone]["name"]
                email = user_info[phone]["email"]
                create = create_lead(name, email, phone)
                if create:
                    user_info[phone]["stage"] = "done"
                    send_whatsapp_message(phone, f"✅ Thanks {name}! You’re now registered. Ask your legal question.")
                else:
                    send_whatsapp_message(phone, "❌ Failed to save your info. Please try again later.")
                return "ok", 200

            # Main chat flow with LLM
            history = session_memory.setdefault(phone, [])
            history.append({"role": "user", "content": msg})
            formatted = "\n".join(f"{m['role'].capitalize()}: {m['content']}" for m in history[-4:])

            model_choice = user_models.get(phone, "gemini")
            if model_choice == "gemini":
                reply_text = generate_with_gemini(prompt=msg, context=formatted)
            else:
                reply_text = ask_ollama(msg, context=formatted)

            history.append({"role": "bot", "content": reply_text})
            send_whatsapp_message(phone, reply_text)

    except Exception as e:
        print("❌ Error handling message:", e)

    return "ok", 200

def send_whatsapp_message(recipient_id, message_text):
    url = f"https://graph.facebook.com/v18.0/{PHONE_NUMBER_ID}/messages"
    headers = {
        "Authorization": f"Bearer {WHATSAPP_TOKEN}",
        "Content-Type": "application/json"
    }
    payload = {
        "messaging_product": "whatsapp",
        "to": recipient_id,
        "type": "text",
        "text": {"body": message_text}
    }
    r = requests.post(url, headers=headers, json=payload)
    print("📤 Sent:", r.status_code, r.text)

if __name__ == "__main__":
    app.run(port=5000)