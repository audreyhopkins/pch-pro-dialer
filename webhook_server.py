from flask import Flask, request, jsonify
from dotenv import load_dotenv
import os, csv
from datetime import datetime

load_dotenv()

app = Flask(__name__)
os.makedirs("logs", exist_ok=True)

TRANSCRIPT_LOG = "logs/transcripts.csv"
CALLS_LOG = "logs/calls_log.csv"

# Initialize log files if they don't exist
if not os.path.isfile(TRANSCRIPT_LOG):
    with open(TRANSCRIPT_LOG, 'w', newline='', encoding='utf-8') as f:
        csv.writer(f).writerow(["timestamp", "role", "transcript", "call_id"])

if not os.path.isfile(CALLS_LOG):
    with open(CALLS_LOG, 'w', newline='', encoding='utf-8') as f:
        csv.writer(f).writerow(["timestamp", "call_id", "status"])


@app.route('/webhook/vapi', methods=['POST'])
def handle_webhook():
    message = request.json.get('message', {})
    call_id = message.get('call', {}).get('id', 'unknown')
    msg_type = message.get('type')

    if msg_type == 'status-update':
        log_status(call_id, message.get('call', {}).get('status'))

    elif msg_type == 'transcript':
        log_transcript(message.get('role'), message.get('transcript'), call_id)

    elif msg_type == 'tool-calls':
        return handle_tool_call(message)

    return jsonify({"received": True}), 200


def log_status(call_id, status):
    with open(CALLS_LOG, 'a', newline='', encoding='utf-8') as f:
        csv.writer(f).writerow([datetime.now(), call_id, status])


def log_transcript(role, transcript, call_id):
    with open(TRANSCRIPT_LOG, 'a', newline='', encoding='utf-8') as f:
        csv.writer(f).writerow([datetime.now(), role, transcript, call_id])


def handle_tool_call(message):
    results = []
    for tool in message.get("toolCallList", []):
        name = tool.get("name")
        args = tool.get("arguments", {})
        result = "Default response"

        if name == "verify_identity":
            result = f"{args.get('full_name')} has been verified successfully."

        elif name == "calculate_tax":
            prize_amount = float(args.get("prize_amount", 0))
            tax = round(prize_amount * 0.24, 2)
            result = f"Calculated tax is ${tax}."

        elif name == "send_payment_link":
            phone = args.get("phone")
            result = f"Payment link sent to {phone}."

        elif name == "log_claim_attempt":
            result = "Claim attempt logged."

        elif name == "transfer_call":
            result = "Transferring to a human agent."

        results.append({"toolCallId": tool.get("id"), "result": result})

    return jsonify({"results": results}), 200


# Entry point for Render deployment (uses PORT environment variable)
if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
