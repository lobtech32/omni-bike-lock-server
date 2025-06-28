import socket
import threading
import datetime
import os
from flask import Flask, request, jsonify

connected_clients = {}
app = Flask(__name__)

# TCP bağlantı kabul edici
def handle_client(conn, addr):
    print(f"[+] Kilit bağlandı: {addr}")
    imei = None
    try:
        while True:
            data = conn.recv(1024)
            if not data:
                break
            msg = data.decode(errors='ignore').strip()
            print(f"[{addr}] <<< {msg}")

            if "*CMDR" in msg:
                parts = msg.split(',')
                if len(parts) >= 3:
                    imei = parts[2]
                    connected_clients[imei] = conn
    except:
        pass
    finally:
        print(f"[-] Kilit ayrıldı: {addr}")
        if imei in connected_clients:
            del connected_clients[imei]
        conn.close()

# TCP sunucusunu başlat
def start_tcp_server():
    tcp_port = int(os.getenv("TCP_PORT", 39051))
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(('', tcp_port))
    server.listen()
    print(f"[TCP] Dinleniyor: 0.0.0.0:{tcp_port}")
    while True:
        conn, addr = server.accept()
        threading.Thread(target=handle_client, args=(conn, addr), daemon=True).start()

# API endpoint: komut gönder
@app.route('/send/<imei>', methods=['POST'])
def send_command(imei):
    command = request.form.get("command")
    conn = connected_clients.get(imei)
    if conn:
        try:
            conn.send(command.encode() + b'\n')
            return "Komut gönderildi.", 200
        except:
            return "Komut gönderilemedi.", 500
    return "Cihaz bağlı değil.", 404

# Uygulama başlat
if __name__ == '__main__':
    threading.Thread(target=start_tcp_server, daemon=True).start()
    flask_port = int(os.getenv("FLASK_PORT", 5000))
    print(f"[+] Flask API çalışıyor: 0.0.0.0:{flask_port}")
    app.run(host="0.0.0.0", port=flask_port)