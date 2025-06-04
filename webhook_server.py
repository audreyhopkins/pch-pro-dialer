from flask import Flask, request, jsonify
from pyngrok import ngrok
from dotenv import load_dotenv
import csv
import os
from datetime import datetime

# Load environment variables
load_dotenv()

# Flask setup
app = Flask(__name__)
os.makedirs("logs", exist_ok=True)

# Log file paths
TRANSCRIPT_LOG = "logs/transcripts.csv"
CALLS_LOG = "logs/calls_log.csv"

# Initialize log files
if not os.path.isfile(TRANSCRIPT_LOG):
    with open(TRANSCRIPT_LOG, 'w', newline='', encoding='utf-8') as f:
        csv.writer(f).writerow(["timestamp", "role", "transcript", "call_id"])

if not os.path.isfile(CALLS_LOG):
    with open(CALLS_LOG, 'w', newline='', encoding='utf-8') as f:
        csv.writer(f).writerow(["timestamp", "call_id", "status"])

# Webhook route
@app.route('/webhook/vapi', methods=['POST'])
def handle_webhook():
    message = request.json.get('message', {})
    call_id = message.get('call', {}).get('id', 'unknown')
    msg_type = message.get('type', '')

    if msg_type == 'status-update':
        log_status(call_id, message.get('call', {}).get('status', 'unknown'))
    elif msg_type == 'transcript':
        log_transcript(message.get('role', 'unknown'), message.get('transcript', ''), call_id)
    elif msg_type == 'tool-calls':
        return handle_tool_call(message)

    return jsonify({"received": True}), 200

# Logging helpers
def log_status(call_id, status):
    with open(CALLS_LOG, 'a', newline='', encoding='utf-8') as f:
        csv.writer(f).writerow([datetime.now(), call_id, status])

def log_transcript(role, transcript, call_id):
    with open(TRANSCRIPT_LOG, 'a', newline='', encoding='utf-8') as f:
        csv.writer(f).writerow([datetime.now(), role, transcript, call_id])

# Tool call handler
def handle_tool_call(message):
    results = []

    for tool in message.get("toolCallList", []):
        name = tool.get("name")
        args = tool.get("arguments", {})
        tool_id = tool.get("id")
        response = "No handler for this tool."

        if name == "verify_identity":
            response = f"{args.get('full_name', 'User')} has been verified successfully."
        elif name == "calculate_tax":
            try:
                amount = float(args.get("prize_amount", 0))
                tax = round(amount * 0.24, 2)
                response = f"Calculated tax is ${tax}."
            except Exception:
                response = "Unable to calculate tax."
        elif name == "send_payment_link":
            response = f"Payment link sent to {args.get('phone', 'unknown')}."
        elif name == "log_claim_attempt":
            response = "Claim attempt logged."
        elif name == "transfer_call":
            response = "Transferring to a human agent."

        results.append({"toolCallId": tool_id, "result": response})

    return jsonify({"results": results}), 200

# Start ngrok
def start_ngrok(port):
    ngrok.set_auth_token(os.getenv("NGROK_AUTHTOKEN"))
    subdomain = os.getenv("NGROK_SUBDOMAIN")
    public_url = ngrok.connect(addr=port, subdomain=subdomain)
    print(f"🚀 Webhook running at: {public_url}/webhook/vapi")
    print("🔁 No need to update the Vapi dashboard again.")
    return public_url

# Launch webhook + ngrok
def run_webhook():
    start_ngrok(5000)
    app.run(port=5000, debug=False)
