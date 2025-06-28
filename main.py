### 📄 main.py (TCP Server)
```python
import socket
import threading
from flask import Flask, request
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
PORT = int(os.getenv("TCP_PORT", 39051))
FLASK_PORT = int(os.getenv("FLASK_PORT", 5000))
lock_connections = {}

@app.route("/open/<imei>", methods=["POST"])
def open_lock(imei):
    conn = lock_connections.get(imei)
    if conn:
        try:
            msg = f"*CMDR,OM,{imei},000000000000,L0,0,1234#"
            conn.sendall(msg.encode())
            return "Kilit açıldı", 200
        except:
            return "Kilit açma başarısız", 500
    return "Cihaz bağlı değil", 404

def handle_client(conn, addr):
    imei = None
    try:
        while True:
            data = conn.recv(1024)
            if not data:
                break
            msg = data.decode(errors="ignore").strip()
            print(f"[{addr}] <<< {msg}")
            if msg.startswith("*CMDR"):
                parts = msg.split(",")
                if len(parts) > 2:
                    imei = parts[2]
                    lock_connections[imei] = conn
    finally:
        if imei in lock_connections:
            del lock_connections[imei]
        conn.close()


def tcp_server():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(("0.0.0.0", PORT))
        s.listen()
        print(f"[TCP] Dinleniyor: 0.0.0.0:{PORT}")
        while True:
            conn, addr = s.accept()
            print(f"[+] Kilit bağlandı: {addr}")
            threading.Thread(target=handle_client, args=(conn, addr), daemon=True).start()

if __name__ == "__main__":
    threading.Thread(target=tcp_server, daemon=True).start()
    print(f"[+] Flask API çalışıyor: 0.0.0.0:{FLASK_PORT}")
    app.run(host="0.0.0.0", port=FLASK_PORT)
```
