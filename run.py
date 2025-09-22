from flask import Flask, request, jsonify
from app.utils.whatsapp_utils import send_message
from app.services.business_service import calculate_invoice, calculate_multi_invoice
from openai import OpenAI
import os

app = Flask(__name__)

# Load environment variables
VERIFY_TOKEN = os.getenv("VERIFY_TOKEN", "ADORABLINDSTOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# Initialize OpenAI client
openai_client = OpenAI(api_key=OPENAI_API_KEY)

def ask_openai(message_text):
    """Send customer message to OpenAI Assistant and return reply."""
    response = openai_client.chat.completions.create(
        model="gpt-4o-mini",   # cost-effective fast model
        messages=[
            {"role": "system", "content": "You are Adora Blinds Assistant AI. You help customers with blinds, curtains, wallpapers, roller blinds pricing, and home decor."},
            {"role": "user", "content": message_text}
        ]
    )
    return response.choices[0].message.content


@app.route("/webhook", methods=["GET"])
def verify():
    """Webhook verification with Meta (for initial setup)."""
    mode = request.args.get("hub.mode")
    token = request.args.get("hub.verify_token")
    challenge = request.args.get("hub.challenge")

    if mode == "subscribe" and token == VERIFY_TOKEN:
        return challenge, 200
    return "Forbidden", 403


@app.route("/webhook", methods=["POST"])
def webhook():
    """Main webhook to handle incoming WhatsApp messages."""
    data = request.get_json()
    try:
        message = data["entry"][0]["changes"][0]["value"]["messages"][0]
        from_number = message["from"]
        text = message.get("text", {}).get("body", "").strip()

        reply = ""

        if text.lower().startswith("order"):
            # Process order requests
            order_text = text.replace("order", "").strip()
            if "," in order_text:
                reply = calculate_multi_invoice(order_text)
            else:
                parts = order_text.split("x")
                if len(parts) == 3:
                    width, height, pcs = float(parts[0]), float(parts[1]), int(parts[2])
                    reply = calculate_invoice(width, height, pcs)
                else:
                    reply = "❌ Invalid format. Use: order 2.5x3.5x1 OR multiple: order 2.5x3.5x1,1.5x1.0x2"
        else:
            # Forward all other messages to OpenAI
            reply = ask_openai(text)

        send_message(from_number, reply)

    except Exception as e:
        print("Error:", e)

    return jsonify({"status": "success"}), 200


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 3000))
    app.run(host="0.0.0.0", port=port)
