import socket
import threading
from flask import Flask, request, jsonify
import os
from datetime import datetime
import time

TCP_PORT = int(os.getenv("TCP_PORT", 39051))
FLASK_PORT = int(os.getenv("FLASK_PORT", 8000))

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
                # === L0 komutu için özel format ===
                if command == "L0":
                    now = datetime.utcnow()
                    zaman_str = now.strftime("%y%m%d%H%M%S")  # örn: 240628153012
                    epoch = int(time.time())  # Unix zaman
                    user_id = 1234  # sabit kullanıcı ID (gerekirse değiştirilebilir)

                    komut_str = f"*CMDS,OM,{imei},{zaman_str},L0,0,{user_id},{epoch}#\n"
                    mesaj = b'\xFF\xFF' + komut_str.encode()
                    print(f"[API] Gönderilen L0 komutu: {komut_str.strip()}")
                else:
                    mesaj = (command + '\n').encode()
                    print(f"[API] Özel olmayan komut gönderildi: {command}")

                conn.sendall(mesaj)
                return jsonify({"status": "success", "message": f"Komut gönderildi: {command}"}), 200

            except Exception as e:
                print(f"[API] Komut gönderme hatası: {e}")
                return jsonify({"status": "error", "message": str(e)}), 500

    print(f"[API] IMEI bulunamadı: {imei}")
    return jsonify({"status": "error", "message": "IMEI bulunamadı"}), 404

@app.route('/open/<imei>', methods=['POST'])
def open_lock(imei):
    print(f"[API] /open çağrıldı, IMEI: {imei}")
    return send_command(imei, "L0")

def handle_client(conn, addr):
    imei = None
    with conn:
        print(f"[TCP] Kilit bağlandı: {addr}")
        while True:
            try:
                data = conn.recv(1024)
                if not data:
                    break
                message = data.decode(errors='ignore').strip()
                print(f"[TCP] {addr} <<< {message}")

                parts = message.split(",")
                if len(parts) > 2:
                    imei = parts[2]
                    clients[conn] = {"addr": addr, "imei": imei}
                    print(f"[TCP] IMEI kaydedildi: {imei}")

            except Exception as e:
                print(f"[TCP] Hata: {e}")
                break
        print(f"[TCP] Kilit ayrıldı: {addr}")
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