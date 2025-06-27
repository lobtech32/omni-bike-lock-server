import socket
import threading
import time
from flask import Flask, request, jsonify
from werkzeug.serving import make_server
import os

clients = {}
lock_status = {}

app = Flask(__name__)

def handle_client(conn, addr):
    print(f"Yeni bağlantı: {addr}")
    clients[addr] = conn
    lock_status[addr] = {
        "connected": True,
        "last_seen": time.strftime("%Y-%m-%d %H:%M:%S"),
        "voltage": None,
        "location": None
    }
    try:
        while True:
            data = conn.recv(1024)
            if not data:
                break
            message = data.decode().strip()
            print(f"{addr} mesajı: {message}")
            lock_status[addr]["last_seen"] = time.strftime("%Y-%m-%d %H:%M:%S")
            if message.startswith("Q0"):
                parts = message.split()
                if len(parts) > 1:
                    lock_status[addr]["voltage"] = parts[1]
    except Exception as e:
        print(f"{addr} bağlantı hatası: {e}")
    finally:
        print(f"Bağlantı kapandı: {addr}")
        lock_status[addr]["connected"] = False
        conn.close()
        if addr in clients:
            del clients[addr]

def start_tcp_server():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(('0.0.0.0', 5000))
    server.listen(5)
    print("TCP Sunucu dinleniyor: 0.0.0.0:5000")
    while True:
        conn, addr = server.accept()
        thread = threading.Thread(target=handle_client, args=(conn, addr))
        thread.start()

@app.route("/locks", methods=["GET"])
def get_locks():
    response = []
    for addr, status in lock_status.items():
        response.append({
            "address": f"{addr[0]}:{addr[1]}",
            "connected": status["connected"],
            "last_seen": status["last_seen"],
            "voltage": status["voltage"],
            "location": status["location"]
        })
    return jsonify(response)

@app.route("/send_l0", methods=["POST"])
def send_l0():
    data = request.get_json()
    address_str = data.get("address")
    if not address_str:
        return jsonify({"error": "address gerekli"}), 400
    try:
        ip, port = address_str.split(":")
        addr = (ip, int(port))
        if addr in clients:
            clients[addr].sendall(b"L0\n")
            return jsonify({"status": "ok", "message": f"L0 gönderildi → {address_str}"})
        else:
            return jsonify({"status": "fail", "message": "Kilit bağlı değil"}), 404
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

class FlaskThread(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        port = int(os.environ.get("PORT", 8000))  # Railway ne port verirse onu kullan
        self.server = make_server('0.0.0.0', port, app)
        self.ctx = app.app_context()
        self.ctx.push()

    def run(self):
        print("Flask API başlatıldı")
        self.server.serve_forever()

    def shutdown(self):
        self.server.shutdown()

if __name__ == "__main__":
    flask_thread = FlaskThread()
    flask_thread.start()
    start_tcp_server()
