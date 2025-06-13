from dotenv import load_dotenv
load_dotenv()
import os

from flask import Flask, request, jsonify
import requests
import csv

app = Flask(__name__)

# ✅ Correct way to load environment variables
CSV_PATH = os.getenv("CSV_PATH")
REDCAP_API_URL = os.getenv("REDCAP_API_URL")
REDCAP_API_TOKEN = os.getenv("REDCAP_API_TOKEN")

@app.route("/", methods=["POST"])
def handle_det():
    data = request.form
    record_id = data.get("record")

    if not record_id:
        return "No record ID received", 400

    print(f"🔔 Data Entry Trigger received for record #{record_id}")

    # Load credentials from CSV
    with open(CSV_PATH, newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        credentials = list(reader)

    record_index = int(record_id) - 1

    if record_index >= len(credentials):
        return f"No more credentials available for record #{record_id}", 400

    cred = credentials[record_index]

    # Prepare data to upload to REDCap
    upload_data = [
        {
            "record_id": record_id,
            "asa24_id": cred["asa24_id"],
            "asa24_password": cred["asa24_password"],
            "asa24_credentials_hidden_complete": "2"
        }
    ]

    response = requests.post(REDCAP_API_URL, data={
        "token": REDCAP_API_TOKEN,
        "content": "record",
        "format": "json",
        "type": "flat",
        "data": str(upload_data).replace("'", '"')
    })

    print(f"✅ Assigned ASA24 credentials: ID={cred['asa24_id']}, Password={cred['asa24_password']}")
    print(f"📬 REDCap response: {response.status_code} - {response.text}")

    return jsonify({"status": "success"}), 200

if __name__ == "__main__":
    # ✅ Render expects host='0.0.0.0' and dynamic port from env
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))