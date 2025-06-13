from flask import Flask, request, jsonify
import requests
import csv
import os

app = Flask(__name__)

CSV_PATH = "asa24_credentials.csv"  # assumes it's uploaded with your code
REDCAP_API_URL = "https://research.unisa.edu.au/redcap/api/"
REDCAP_API_TOKEN = "1A6E8C4C359F939B423353774E9D126D"

@app.route("/", methods=["POST"])
def handle_det():
    data = request.form
    record_id = data.get("record")

    if not record_id:
        return "No record ID received", 400

    print(f"🔔 Data Entry Trigger received for record #{record_id}")

    # Load available credentials
    with open(CSV_PATH, newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        credentials = list(reader)

    record_index = int(record_id) - 1

    if record_index >= len(credentials):
        return f"No more credentials available for record #{record_id}", 400

    cred = credentials[record_index]

    # Upload credentials to REDCap
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
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))