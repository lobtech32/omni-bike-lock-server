import socket
import threading
from flask import Flask, request, jsonify
import os
from datetime import datetime

app = Flask(__name__)

device_data = {
    "online": False,
    "last_message": "",
    "last_seen": "",
    "voltage": None,
}

clients = []

def send_command(command):
    for c in clients:
        try:
            c.sendall(command.encode())
        except:
            pass

@app.route("/send_l0", methods=["POST"])
def send_l0():
    data = request.get_json()
    if not data or "address" not in data:
        return jsonify({"status": "error", "message": "Eksik veri"}), 400
    send_command("*CMDR,OM,862205059210023,000000000000,L0,0,1234,1751022197#")
    return jsonify({"status": "ok"})

@app.route("/locks")
def get_status():
    return jsonify([{
        "imei": "862205059210023",
        "online": device_data["online"],
        "last_message": device_data["last_message"],
        "last_seen": device_data["last_seen"],
        "voltage": device_data["voltage"],
    }])

def start_tcp_server():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(('0.0.0.0', 39051))  # Cihaz buraya bağlanıyor
    server.listen()

    print("TCP Sunucu dinleniyor: 0.0.0.0:39051")
    while True:
        client, addr = server.accept()
        print(f"Yeni bağlantı: {addr}")
        clients.append(client)

        def handle_client(c):
            while True:
                try:
                    data = c.recv(1024)
                    if not data:
                        break
                    msg = data.decode(errors="ignore").strip()
                    print(f"{addr} mesajı: {msg}")
                    device_data["online"] = True
                    device_data["last_message"] = msg
                    device_data["last_seen"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

                    if ",Q0," in msg:
                        try:
                            volt = msg.split(",Q0,")[1].replace("#", "")
                            device_data["voltage"] = volt
                        except:
                            pass

                except:
                    break

        threading.Thread(target=handle_client, args=(client,), daemon=True).start()

threading.Thread(target=start_tcp_server, daemon=True).start()

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    print(f"Flask API başlatıldı: 0.0.0.0:{port}")
    app.run(host="0.0.0.0", port=port)
