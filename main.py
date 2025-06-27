import os
import socket
import threading
import time
from datetime import datetime, timezone

OM_MANUFACTURER_CODE = os.getenv("OM_MANUFACTURER_CODE", "OM")
OM_LOCK_IMEI = os.getenv("OM_LOCK_IMEI", "862205059210023")
HOST = "0.0.0.0"
PORT = int(os.getenv("PORT", "5000"))

def calc_timestamp():
    return datetime.now(timezone.utc).strftime("%y%m%d%H%M%S")

def build_tcp_command(cmd_type: str, *params) -> bytes:
    ts = calc_timestamp()
    parts = ["*CMDS", OM_MANUFACTURER_CODE, OM_LOCK_IMEI, ts, cmd_type] + list(params)
    cmd_str = ",".join(parts) + "#\n"
    return b"\xFF\xFF" + cmd_str.encode()

def handle_client(conn, addr):
    print(f"[+] Kilit bağlandı: {addr}")
    try:
        conn.sendall(build_tcp_command("Q0", "0", "80"))
        conn.sendall(build_tcp_command("H0", "0", "412", "28", "80"))

        user_id = "1234"
        op_ts = str(int(datetime.now(timezone.utc).timestamp()))

        # 1. Kilidi aç (L0)
        print(">> Kilit açılıyor (L0)...")
        conn.sendall(build_tcp_command("L0", "0", user_id, op_ts))

        # 2. 3 saniye sonra kilidi kapat (L1)
        time.sleep(3)
        print(">> Kilit kapatılıyor (L1)...")
        conn.sendall(build_tcp_command("L1", "0", user_id, op_ts))

        while True:
            data = conn.recv(1024)
            if not data:
                break
            print(f"[{addr}] <<< {data.decode(errors='ignore').strip()}")

    except Exception as e:
        print(f"[!] Hata: {e}")
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
