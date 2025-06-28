import socket
import threading
from flask import Flask, jsonify
import datetime
import os

app = Flask(__name__)

connected_locks = {}

def handle_client(client_socket, addr):
    print(f"[+] Kilit bağlandı: {addr}")
    while True:
        try:
            data = client_socket.recv(1024).decode(errors="ignore")
            if not data:
                break
            print(f"[{addr}] <<< {data.strip()}")
            imei = None

            if data.startswith("*CMDR") and "OM" in data:
                parts = data.split(",")
                if len(parts) > 2:
                    imei = parts[2]
                    connected_locks[imei] = client_socket

        except Exception as e:
            print(f"[!] Hata ({addr}): {e}")
            break
    print(f"[-] Kilit ayrıldı: {addr}")
    client_socket.close()

@app.route("/")
def index():
    return jsonify({"status": "TCP sunucu çalışıyor", "bagli_kilit_sayisi": len(connected_locks)})

@app.route("/lock/<imei>/open")
def open_lock(imei):
    return send_command(imei, "L0,0,1234,{}".format(int(datetime.datetime.utcnow().timestamp())))

@app.route("/lock/<imei>/close")
def close_lock(imei):
    return send_command(imei, "L1,0,1234,{}".format(int(datetime.datetime.utcnow().timestamp())))

def send_command(imei, command_body):
    client_socket = connected_locks.get(imei)
    if not client_socket:
        return jsonify({"error": "Cihaz bağlı değil"}), 404
    timestamp = datetime.datetime.utcnow().strftime("%y%m%d%H%M%S")
    cmd = f"0xFFFF*CMDS,OM,{imei},{timestamp},{command_body}#\n"
    try:
        client_socket.send(cmd.encode())
        print(f">> Gönderildi: {cmd.strip()}")
        return jsonify({"success": True, "command": cmd.strip()})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

def tcp_server():
    tcp_port = int(os.environ.get("TCP_PORT", 39051))
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(("0.0.0.0", tcp_port))
    server.listen(5)
    print(f"[TCP] Dinleniyor: 0.0.0.0:{tcp_port}")
    while True:
        client_socket, addr = server.accept()
        client_handler = threading.Thread(target=handle_client, args=(client_socket, addr))
        client_handler.start()

if __name__ == "__main__":
    threading.Thread(target=tcp_server, daemon=True).start()
    app.run(host="0.0.0.0", port=int(os.environ.get("FLASK_PORT", 5000)))