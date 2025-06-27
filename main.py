# main.py
import os
import socket
import threading
from datetime import datetime

# Environment değişkenleri Railway’den çekiliyor
OM_MANUFACTURER_CODE = os.getenv("OM_MANUFACTURER_CODE", "OM")
OM_LOCK_IMEI = os.getenv("OM_LOCK_IMEI", "862205059210023")
HOST = "0.0.0.0"
PORT = int(os.getenv("PORT", "5000"))

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
        # 1. Giriş (Q0)
        conn.sendall(build_tcp_command("Q0", "0", "80"))
        # 2. Heartbeat (H0)
        conn.sendall(build_tcp_command("H0", "0", "412", "28", "80"))
        # 3. Uzaktan Kilit Aç (L0)
        user_id = "1234"
        op_ts = str(int(datetime.utcnow().timestamp()))
        conn.sendall(build_tcp_command("L0", "0", user_id, op_ts))

        # Gelen cevapları logla
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

def main():
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.bind((HOST, PORT))
    sock.listen()
    print(f"Sunucu dinleniyor: {HOST}:{PORT}")
    while True:
        conn, addr = sock.accept()
        threading.Thread(target=handle_client, args=(conn, addr), daemon=True).start()

if __name__ == "__main__":
    main()
