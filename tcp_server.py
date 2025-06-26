import socket
import threading

def handle_client(client_socket, addr):
    print(f"{addr} bağlandı.")
    while True:
        try:
            data = client_socket.recv(1024)
            if not data:
                break
            print(f"Gelen veri: {data.decode()}")
            # Burada kilit komutlarını işleyebilirsin
            client_socket.send(b"ACK")  # Basit cevap
        except:
            break
    client_socket.close()
    print(f"{addr} bağlantısı kapandı.")

def start_tcp_server():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(('0.0.0.0', 5000))
    server.listen(5)
    print("TCP Sunucu dinleniyor: 0.0.0.0:5000")
    while True:
        client_socket, addr = server.accept()
        client_thread = threading.Thread(target=handle_client, args=(client_socket, addr))
        client_thread.start()

if __name__ == '__main__':
    start_tcp_server()
