from flask import Flask
import threading
import socket

app = Flask(__name__)

tcp_started = False

def start_tcp_server():
    global tcp_started
    if tcp_started:
        print("TCP zaten başlatıldı.")
        return
    tcp_started = True
    try:
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.bind(('0.0.0.0', 5000))
        server.listen()
        print("TCP Sunucu dinleniyor: 0.0.0.0:5000")
        while True:
            conn, addr = server.accept()
            print(f"Bağlantı geldi: {addr}")
            conn.close()
    except OSError as e:
        print(f"TCP başlatılamadı: {e}")

@app.route("/")
def home():
    return "Flask ve TCP sunucu çalışıyor."

# Railway otomatik çalıştırıyorsa aşağıdaki kısmı EKLEME
if __name__ == "__main__":
    threading.Thread(target=start_tcp_server, daemon=True).start()
    app.run(host="0.0.0.0", port=5000)
