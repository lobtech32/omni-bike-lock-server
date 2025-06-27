from flask import Flask, request
import requests
import os

app = Flask(__name__)
TCP_SERVER_URL = os.getenv("TCP_SERVER_URL", "http://localhost:5000")

@app.route("/open/<device_id>", methods=["POST"])
def open_lock(device_id):
    # TCP server ile iletişim API’sı yoksa, TCP servera direkt erişemeyiz.
    # En iyisi TCP server bir API sunar, ya da Redis gibi bir ortak depoya yazılır.
    return {"status": "not_implemented"}, 501

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.getenv("FLASK_PORT", 8000)))
