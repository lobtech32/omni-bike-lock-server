import socket
import threading
import datetime
from flask import Flask, jsonify, request
import os
from dotenv import load_dotenv

load_dotenv()
TCP_PORT = int(os.getenv("TCP_PORT", 39051))
FLASK_PORT = int(os.getenv("FLASK_PORT", 5000))

app = Flask(__name__)
lock_connections = {}
lock = threading.Lock()

def handle_client(conn, addr):
    imei = None
    with conn:
        print(f"[+] Kilit bağlandı: {addr}")
        try:
            while True:
                data = conn.recv(1024)
                if not data:
                    break
                message = data.decode(errors="ignore").strip()
                print(f"[{addr}] <<< {message}")
                if "*CMDR" in message:
                    parts = message.split(",")
                    if len(parts) >= 4:
                        imei = parts[2]
                        with lock:
                            lock_connections[imei] = conn
        except Exception as e:
            print(f"[!] Hata: {e}")
        finally:
            print(f"[-] Kilit ayrıldı: {addr}")
            with lock:
                if imei in lock_connections:
                    del lock_connections[imei]

def tcp_server():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(("0.0.0.0", TCP_PORT))
    server.listen()
    print(f"[TCP] Dinleniyor: 0.0.0.0:{TCP_PORT}")
    while True:
        conn, addr = server.accept()
        threading.Thread(target=handle_client, args=(conn, addr), daemon=True).start()

@app.route("/open/<imei>", methods=["POST"])
def open_lock(imei):
    with lock:
        conn = lock_connections.get(imei)
    if conn:
        try:
            ts = int(datetime.datetime.utcnow().timestamp())
            command = f"*CMDR,OM,{imei},000000000000,L0,0,1234,{ts}#"
            conn.sendall(command.encode())
            print(f">> Kilit açılıyor: {command}")
            return jsonify({"ok": True}), 200
        except Exception as e:
            return jsonify({"error": str(e)}), 500
    return jsonify({"error": "Cihaz bağlı değil"}), 404

if __name__ == "__main__":
    threading.Thread(target=tcp_server, daemon=True).start()
    print(f"[+] Flask API çalışıyor: 0.0.0.0:{FLASK_PORT}")
    app.run(host="0.0.0.0", port=FLASK_PORT)