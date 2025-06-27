import socket
import threading
import os
from dotenv import load_dotenv

load_dotenv()

TCP_PORT = int(os.getenv("TCP_PORT", 39051))

connections = {}

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

if __name__ == "__main__":
    tcp_server()
