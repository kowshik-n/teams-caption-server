from flask import Flask, request, jsonify
import re
import datetime
import os
import requests
import urllib.parse

app = Flask(__name__)

# ==============================
# CONFIG
# ==============================

API_KEY = os.getenv("API_KEY")  # Set in Render dashboard
WHATSAPP_NUMBER = os.getenv("WHATSAPP_NUMBER")
WHATSAPP_APIKEY = os.getenv("WHATSAPP_APIKEY")

LOG_FILE = "captions_log.txt"
CODE_REGEX = re.compile(r"\b(\d{3,6})\b")

KEYWORDS = [
    "attendance",
    "attendence",
    "attendance code",
    "enter the code",
    "submit your attendance",
    "mark your attendance",
    "fill the attendance",
    "note down this code",
    "write this code",
    "the code is",
    "enter the number",
    "attendance number",
    "attendance pin",
    "provide the code",
    "put the code"
]

# ==============================
# HELPERS
# ==============================

def contains_keyword(text):
    text_low = text.lower()
    for kw in KEYWORDS:
        if kw in text_low:
            return kw
    return None

def send_whatsapp_message(message):
    try:
        msg = urllib.parse.quote(message)
        url = f"https://api.callmebot.com/whatsapp.php?phone={WHATSAPP_NUMBER}&apikey={WHATSAPP_APIKEY}&text={msg}"
        requests.get(url)
        print("📲 WhatsApp alert sent!")
    except:
        print("WhatsApp error")

def append_log(line):
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(line + "\n")

# ==============================
# CORS
# ==============================

@app.after_request
def add_cors_headers(response):
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Headers'] = 'Content-Type, x-api-key'
    response.headers['Access-Control-Allow-Methods'] = 'POST, OPTIONS'
    return response

# ==============================
# MAIN ROUTE
# ==============================

@app.route("/caption", methods=["POST", "OPTIONS"])
def caption():

    # Preflight
    if request.method == "OPTIONS":
        return '', 200

    # Security check
    key = request.headers.get("x-api-key")
    if key != API_KEY:
        return "Unauthorized", 401

    data = request.get_json(force=True)
    text = data.get("text", "").strip()

    if not text:
        return jsonify({"status": "empty"}), 400

    tstamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    line = f"[{tstamp}] {text}"
    print(line)
    append_log(line)

    # Keyword alert
    kw = contains_keyword(text)
    if kw:
        alert = f"⚠️ Attendance alert phrase detected: '{kw}'\n{text}"
        send_whatsapp_message(alert)

    # Code detection alert
    match = CODE_REGEX.search(text)
    if match:
        code = match.group(1)
        send_whatsapp_message(f"🔢 Attendance Code Detected: {code}")

    return jsonify({"status": "ok"})


# ==============================
# RENDER START
# ==============================

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
