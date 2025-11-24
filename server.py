from flask import Flask, request, jsonify
import re
import datetime
import os
from twilio.rest import Client

app = Flask(__name__)

# ========================
# CONFIG FROM ENV
# ========================
API_KEY = os.getenv("API_KEY")
TWILIO_SID = os.getenv("TWILIO_SID")
TWILIO_AUTH = os.getenv("TWILIO_AUTH")
WHATSAPP_FROM = "whatsapp:+14155238886"
WHATSAPP_TO = os.getenv("WHATSAPP_TO")

client = Client(TWILIO_SID, TWILIO_AUTH)

LOG_FILE = "captions_log.txt"

CODE_REGEX = re.compile(r"\b(\d{3,6})\b")

KEYWORDS = [
    "attendance",
    "attendence",
    "enter the code",
    "attendance code",
    "submit your attendance",
    "mark your attendance",
    "fill the attendance",
    "the code is"
]

# ========================
# HELPERS
# ========================

def contains_keyword(text):
    t = text.lower()
    for kw in KEYWORDS:
        if kw in t:
            return kw
    return None

def send_whatsapp(msg):
    try:
        client.messages.create(
            from_=WHATSAPP_FROM,
            body=msg,
            to=f"whatsapp:{WHATSAPP_TO}"
        )
        print("📲 WhatsApp alert sent!")
    except Exception as e:
        print("❌ WhatsApp error:", e)

def append_log(text):
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(text + "\n")

# ========================
# CORS
# ========================
@app.after_request
def cors(resp):
    resp.headers["Access-Control-Allow-Origin"] = "*"
    resp.headers["Access-Control-Allow-Headers"] = "Content-Type, x-api-key"
    resp.headers["Access-Control-Allow-Methods"] = "POST, OPTIONS"
    return resp

# ========================
# MAIN ROUTE
# ========================
@app.route("/caption", methods=["POST", "OPTIONS"])
def caption():

    if request.method == "OPTIONS":
        return "", 200

    # authentication
    if request.headers.get("x-api-key") != API_KEY:
        return "Unauthorized", 401

    data = request.get_json()
    text = data.get("text", "").strip()

    if not text:
        return jsonify({"status": "empty"}), 400

    ts = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_line = f"[{ts}] {text}"
    print(log_line)
    append_log(log_line)

    # detect keyword
    kw = contains_keyword(text)
    if kw:
        send_whatsapp(f"⚠️ Attendance Hint Detected: '{kw}'\n{text}")

    # detect code
    match = CODE_REGEX.search(text)
    if match:
        code = match.group(1)
        send_whatsapp(f"🔢 Attendance Code Detected: {code}")

    return jsonify({"status": "ok"})

# ========================
# START
# ========================
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
