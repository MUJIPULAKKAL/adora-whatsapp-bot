# Adora Blinds WhatsApp Bot

## Setup
1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Copy `.env.example` to `.env` and fill in your WhatsApp Cloud API credentials.

3. Run the bot:
   ```bash
   python run.py
   ```

4. Use ngrok to expose port 3000:
   ```bash
   ngrok http 3000
   ```

5. Set webhook URL in Meta Developer dashboard to your ngrok URL + `/webhook`.

6. Test in WhatsApp:
   - Send: `order 2.5x3.5x1`
   - Bot replies with an invoice.
