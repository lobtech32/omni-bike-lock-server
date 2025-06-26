import threading
import socket
from flask import Flask

app = Flask(__name__)

@app.route('/')
def home():
    return "Flask server çalışıyor!"

def tcp_server():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(('0.0.0.0', 5000))
    server.listen(5)
    print("TCP Sunucu dinleniyor: 0.0.0.0:5000")
    while True:
        client_socket, addr = server.accept()
        print(f"Bağlantı geldi: {addr}")
        client_socket.send(b"Merhaba TCP Client!\n")
        client_socket.close()

if __name__ == '__main__':
    t = threading.Thread(target=tcp_server)
    t.daemon = True
    t.start()
    app.run(host='0.0.0.0', port=8080)
