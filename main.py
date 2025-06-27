import socket
import threading
import os
from flask import Flask, request
from dotenv import load_dotenv

load_dotenv()

TCP_PORT = int(os.getenv("TCP_PORT", 39051))
HTTP_PORT = int(os.getenv("FLASK_PORT", 5000))
connections = {}

app = Flask(__name__)

def handle_client(conn, addr):
    try:
        data = conn.recv(1024).decode().strip()
        if data.startswith("ID:"):
            device_id = data.split(":",1)[1]
            connections[device_id] = conn
            print(f"[+] Kilit cihazı bağlandı: {device_id} @ {addr}")
        else:
            conn.close()
            return
        while True:
            data = conn.recv(1024)
            if not data:
                break
            print(f"[{device_id}] <<< {data.decode().strip()}")
    except Exception as e:
        print("HATA:", e)
    finally:
        if 'device_id' in locals():
            connections.pop(device_id, None)
            print(f"[-] {device_id} bağlantısı kesildi")
        conn.close()

def tcp_server():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(("0.0.0.0", TCP_PORT))
    server.listen()
    print(f"[TCP] Dinleniyor: 0.0.0.0:{TCP_PORT}")
    while True:
        conn, addr = server.accept()
        threading.Thread(target=handle_client, args=(conn, addr), daemon=True).start()

@app.route("/open/<device_id>", methods=["POST"])
def open_lock(device_id):
    if device_id in connections:
        try:
            connections[device_id].sendall(b"L0\n")
            return {"status": "success", "message": f"Kilit {device_id} açıldı"}
        except Exception as e:
            return {"status": "error", "message": str(e)}, 500
    return {"status": "error", "message": "Cihaz bağlı değil"}, 404

if __name__ == "__main__":
    threading.Thread(target=tcp_server, daemon=True).start()
    app.run(host="0.0.0.0", port=HTTP_PORT)
