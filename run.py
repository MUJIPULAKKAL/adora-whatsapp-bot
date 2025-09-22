from flask import Flask, request, jsonify
from app.utils.whatsapp_utils import send_message
from app.services.business_service import calculate_invoice, calculate_multi_invoice
from openai import OpenAI
import os

app = Flask(__name__)

# Environment variables
VERIFY_TOKEN = os.getenv("VERIFY_TOKEN", "ADORABLINDSTOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
ASSISTANT_ID = os.getenv("ASSISTANT_ID")

# Initialize OpenAI client
openai_client = OpenAI(api_key=OPENAI_API_KEY)

# Store conversation threads (per user for memory)
user_threads = {}

def ask_assistant(user_id, message_text):
    """Send a message to OpenAI Assistant with memory per user"""
    try:
        # Create a thread if not exists
        if user_id not in user_threads:
            thread = openai_client.beta.threads.create()
            user_threads[user_id] = thread.id

        # Add user message
        openai_client.beta.threads.messages.create(
            thread_id=user_threads[user_id],
            role="user",
            content=message_text
        )

        # Run the assistant (sync with auto-polling)
        run = openai_client.beta.threads.runs.create_and_poll(
            thread_id=user_threads[user_id],
            assistant_id=ASSISTANT_ID
        )

        if run.status == "completed":
            messages = openai_client.beta.threads.messages.list(
                thread_id=user_threads[user_id]
            )
            return messages.data[0].content[0].text.value

        return "⚠️ Sorry, the assistant could not complete your request."

    except Exception as e:
        print("Assistant Error:", e)
        return "⚠️ Error: Could not connect to Assistant."


@app.route("/webhook", methods=["GET"])
def verify():
    """Webhook verification for Meta"""
    mode = request.args.get("hub.mode")
    token = request.args.get("hub.verify_token")
    challenge = request.args.get("hub.challenge")

    if mode == "subscribe" and token == VERIFY_TOKEN:
        return challenge, 200
    return "Forbidden", 403


@app.route("/webhook", methods=["POST"])
def webhook():
    """Main webhook to handle incoming WhatsApp messages"""
    data = request.get_json()
    try:
        message = data["entry"][0]["changes"][0]["value"]["messages"][0]
        from_number = message["from"]
        text = message.get("text", {}).get("body", "").strip()

        reply = ""

        if text.lower().startswith("order"):
            # Handle roller blind orders
            order_text = text.replace("order", "").strip()
            if "," in order_text:
                reply = calculate_multi_invoice(order_text)
            else:
                parts = order_text.split("x")
                if len(parts) == 3:
                    width, height, pcs = float(parts[0]), float(parts[1]), int(parts[2])
                    reply = calculate_invoice(width, height, pcs)
                else:
                    reply = "❌ Invalid format. Use: order 2.5x3.5x1 OR multiple orders."
        else:
            # Use OpenAI Assistant for other queries
            reply = ask_assistant(from_number, text)

        send_message(from_number, reply)

    except Exception as e:
        print("Webhook Error:", e)

    return jsonify({"status": "success"}), 200


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 3000))
    app.run(host="0.0.0.0", port=port)
