import socket
import threading
import time

clients = {}
lock_status = {}

def handle_client(conn, addr):
    print(f"Yeni bağlantı: {addr}")
    clients[addr] = conn
    lock_status[addr] = {"connected": True, "last_seen": time.time(), "location": None, "voltage": None}
    try:
        while True:
            data = conn.recv(1024)
            if not data:
                break
            message = data.decode()
            print(f"{addr} mesajı: {message}")
            # Gelen mesajı işleme (örnek Q0 voltaj vs)
            if message.startswith("Q0"):
                voltage = message.split()[1] if len(message.split()) > 1 else None
                lock_status[addr]["voltage"] = voltage
            lock_status[addr]["last_seen"] = time.time()
            # Lokasyon vb varsa buraya eklenebilir
    except Exception as e:
        print(f"Hata {addr}: {e}")
    finally:
        print(f"Bağlantı kapandı: {addr}")
        lock_status[addr]["connected"] = False
        conn.close()
        del clients[addr]

def start_server():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(('0.0.0.0', 5000))
    server.listen(5)
    print("Sunucu başlatıldı, dinleniyor: 0.0.0.0:5000")
    while True:
        conn, addr = server.accept()
        thread = threading.Thread(target=handle_client, args=(conn, addr))
        thread.start()

if __name__ == "__main__":
    start_server()
