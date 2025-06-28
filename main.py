import socket
import threading
from flask import Flask, request, jsonify
import datetime
import os

TCP_PORT = int(os.getenv("TCP_PORT", 39051))
FLASK_PORT = int(os.getenv("FLASK_PORT", 5000))

clients = {}
app = Flask(__name__)

@app.route('/')
def index():
    return "TCP Server Çalışıyor!", 200

@app.route('/send/<imei>/<command>', methods=['POST'])
def send_command(imei, command):
    for conn, data in clients.items():
        if data["imei"] == imei:
            try:
                conn.sendall((command + '\n').encode())
                return jsonify({"status": "success", "message": f"Komut gönderildi: {command}"}), 200
            except Exception as e:
                return jsonify({"status": "error", "message": str(e)}), 500
    return jsonify({"status": "error", "message": "IMEI bulunamadı"}), 404

def handle_client(conn, addr):
    imei = None
    with conn:
        print(f"[+] Kilit bağlandı: {addr}")
        while True:
            try:
                data = conn.recv(1024)
                if not data:
                    break
                message = data.decode(errors='ignore').strip()
                print(f"[{addr}] <<< {message}")

                parts = message.split(",")
                if len(parts) > 2:
                    imei = parts[2]
                    clients[conn] = {"addr": addr, "imei": imei}

            except Exception as e:
                print(f"[-] Hata: {e}")
                break
        print(f"[-] Kilit ayrıldı: {addr}")
        if conn in clients:
            del clients[conn]

def start_tcp_server():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(("0.0.0.0", TCP_PORT))
    server.listen()
    print(f"[TCP] Dinleniyor: 0.0.0.0:{TCP_PORT}")

    while True:
        conn, addr = server.accept()
        thread = threading.Thread(target=handle_client, args=(conn, addr), daemon=True)
        thread.start()

if __name__ == "__main__":
    threading.Thread(target=start_tcp_server, daemon=True).start()
    print(f"[+] Flask API çalışıyor: 0.0.0.0:{FLASK_PORT}")
    app.run(host="0.0.0.0", port=FLASK_PORT)
