from flask import Flask, request, jsonify
from app.utils.whatsapp_utils import send_message
from app.services.business_service import calculate_invoice, calculate_multi_invoice
import os

app = Flask(__name__)

@app.route("/webhook", methods=["GET"])
def verify():
    verify_token = os.getenv("VERIFY_TOKEN", "ADORABLINDSTOKEN")
    mode = request.args.get("hub.mode")
    token = request.args.get("hub.verify_token")
    challenge = request.args.get("hub.challenge")

    if mode == "subscribe" and token == verify_token:
        return challenge, 200
    return "Forbidden", 403


@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.get_json()
    try:
        message = data["entry"][0]["changes"][0]["value"]["messages"][0]
        from_number = message["from"]
        text = message.get("text", {}).get("body", "").lower()

        reply = "❌ Invalid request."

        if text.startswith("order"):
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

        send_message(from_number, reply)

    except Exception as e:
        print("Error:", e)

    return jsonify({"status": "success"}), 200


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 3000))
    app.run(host="0.0.0.0", port=port)
