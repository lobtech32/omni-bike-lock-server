import socket
import threading
from flask import Flask

app = Flask(__name__)

# TCP sunucunun dinleyeceği port
TCP_PORT = 5000

def handle_client(client_socket, address):
    print(f"[+] Yeni bağlantı: {address}")
    try:
        while True:
            data = client_socket.recv(1024)
            if not data:
                break
            print(f"[{address}] Gelen veri: {data.decode()}")
            client_socket.send(b"OK")
    except Exception as e:
        print(f"[!] Hata: {e}")
    finally:
        client_socket.close()
        print(f"[-] Bağlantı kapatıldı: {address}")

def start_tcp_server():
    tcp_server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    tcp_server.bind(("0.0.0.0", TCP_PORT))
    tcp_server.listen(5)
    print(f"TCP Sunucu dinleniyor: 0.0.0.0:{TCP_PORT}")
    while True:
        client_sock, addr = tcp_server.accept()
        client_thread = threading.Thread(target=handle_client, args=(client_sock, addr))
        client_thread.start()

@app.route("/")
def index():
    return "TCP Sunucu çalışıyor!"

if __name__ == "__main__":
    # TCP sunucusunu ayrı bir thread'de başlat
    tcp_thread = threading.Thread(target=start_tcp_server, daemon=True)
    tcp_thread.start()

    # Flask uygulamasını başlat (aynı portta HTTP çalışsın istersen başka porta taşı)
    app.run(host="0.0.0.0", port=5000)
