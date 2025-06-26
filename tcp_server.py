import socket

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind(('0.0.0.0', 5000))  # 5000 portunda dinle
server.listen()

print("TCP Sunucu dinleniyor: 0.0.0.0:5000")

while True:
    client_socket, addr = server.accept()
    print(f"Bağlandı: {addr}")
    # Buraya kilitten gelen veriyi işleyecek kodu yazabilirsin
    client_socket.close()
