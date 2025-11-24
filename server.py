from flask import Flask, request, jsonify, make_response
import re
import threading
import time
import pyperclip
import datetime
import os

app = Flask(__name__)

LOG_FILE = "captions_log.txt"
CODE_REGEX = re.compile(r"\b(\d{3,6})\b")

def append_log(line):
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(line + "\n")

# ---- ADD THIS ----
@app.after_request
def add_cors_headers(response):
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Headers'] = 'Content-Type'
    response.headers['Access-Control-Allow-Methods'] = 'POST, GET, OPTIONS'
    return response
# -------------------

@app.route("/caption", methods=["POST", "OPTIONS"])
def caption():
    if request.method == "OPTIONS":
        return '', 200

    data = request.get_json(force=True)
    text = data.get("text", "").strip()
    ts = data.get("ts")
    src_url = data.get("url", "")

    if not text:
        return jsonify({"status":"empty"}), 400

    tstamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    out = f"[{tstamp}] {text}"
    print(out)
    append_log(out)

    m = CODE_REGEX.search(text)
    if m:
        code = m.group(1)
        print("🔥 CODE DETECTED:", code)
        append_log(f"[CODE] {tstamp} {code}")
        try:
            pyperclip.copy(code)
            print("(Copied code to clipboard)")
        except:
            pass

    return jsonify({"status":"ok"})

if __name__ == "__main__":
    print("Starting caption receiver on http://0.0.0.0:5000")
    if not os.path.exists(LOG_FILE):
        open(LOG_FILE, "w", encoding="utf-8").close()
    app.run(host="0.0.0.0", port=5000)
