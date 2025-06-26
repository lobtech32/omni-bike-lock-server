import os
import socket
import threading
from datetime import datetime
from flask import Flask

OM_MANUFACTURER_CODE = os.getenv("OM_MANUFACTURER_CODE", "OM")
OM_LOCK_IMEI = os.getenv("OM_LOCK_IMEI", "862205059210023")
PORT = int(os.getenv("PORT", "5000"))  # Bu PORT Railway tarafından sağlanır
TCP_PORT = PORT + 1  # TCP sunucu bu portta dinler

def calc_timestamp():
    return datetime.utcnow().strftime("%y%m%d%H%M%S")

def build_tcp_command(cmd_type: str, *params) -> bytes:
    ts = calc_timestamp()
    parts = ["*CMDS", OM_MANUFACTURER_CODE, OM_LOCK_IMEI, ts, cmd_type] + list(params)
    cmd_str = "0xFFFF" + ",".join(parts) + "#\n"
    return cmd_str.encode()

def handle_client(conn, addr):
    print(f"[+] Kilit bağlandı: {addr}")
    try:
        conn.sendall(build_tcp_command("Q0", "0", "80"))
        conn.sendall(build_tcp_command("H0", "0", "412", "28", "80"))
        user_id = "1234"
        op_ts = str(int(datetime.utcnow().timestamp()))
        conn.sendall(build_tcp_command("L0", "0", user_id, op_ts))
        while True:
            data = conn.recv(1024)
            if not data:
                break
            print(f"[{addr}] <<< {data.decode(errors='ignore').strip()}")
    except Exception as e:
        print("Hata:", e)
    finally:
        conn.close()
        print(f"[-] Kilit ayrıldı: {addr}")

def run_tcp_server():
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.bind(("0.0.0.0", TCP_PORT))
    sock.listen()
    print(f"TCP Sunucu dinleniyor: 0.0.0.0:{TCP_PORT}")
    while True:
        conn, addr = sock.accept()
        threading.Thread(target=handle_client, args=(conn, addr), daemon=True).start()

app = Flask(__name__)

@app.route("/")
def index():
    return f"TCP sunucu aktif: {TCP_PORT}", 200

if __name__ == "__main__":
    threading.Thread(target=run_tcp_server, daemon=True).start()
    app.run(host="0.0.0.0", port=PORT)
