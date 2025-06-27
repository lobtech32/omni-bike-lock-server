import socket
import threading
from flask import Flask, request, jsonify, render_template, redirect, url_for, session
import os
from datetime import datetime

app = Flask(__name__)
app.secret_key = "super-secret-key"  # güvenlik için değiştir

# Basit kullanıcı giriş bilgisi
USERNAME = "admin"
PASSWORD = "1234"

# Cihaz durumu (güncellenecek)
device_data = {
    "online": False,
    "last_message": "",
    "last_seen": "",
    "voltage": None,
}

clients = []

# TCP komut gönderici
def send_command(command):
    for c in clients:
        try:
            c.sendall(command.encode())
        except:
            pass

# Giriş ekranı
@app.route("/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        if request.form["username"] == USERNAME and request.form["password"] == PASSWORD:
            session["logged_in"] = True
            return redirect(url_for("panel"))
        return "Hatalı giriş", 403
    return render_template("login.html")

# Admin paneli
@app.route("/panel")
def panel():
    if not session.get("logged_in"):
        return redirect(url_for("login"))
    return render_template("index.html", device=device_data)

# Kilidi aç
@app.route("/unlock", methods=["POST"])
def unlock():
    if not session.get("logged_in"):
        return redirect(url_for("login"))
    send_command("*CMDR,OM,862205059210023,000000000000,L0,0,1234,1751022197#")
    return jsonify({"status": "sent"})

# TCP sunucu
def start_tcp_server():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(('0.0.0.0', 39051))  # CİHAZLAR BURAYA GELİYOR
    server.listen()

    print("TCP Sunucu dinleniyor: 0.0.0.0:39051")
    while True:
        client, addr = server.accept()
        print(f"Yeni bağlantı: {addr}")
        clients.append(client)

        def handle_client(c):
            while True:
                try:
                    data = c.recv(1024)
                    if not data:
                        break
                    msg = data.decode(errors="ignore").strip()
                    print(f"{addr} mesajı: {msg}")
                    device_data["online"] = True
                    device_data["last_message"] = msg
                    device_data["last_seen"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

                    # Q0 mesajından voltaj ayıkla
                    if ",Q0," in msg:
                        try:
                            volt = msg.split(",Q0,")[1].replace("#", "")
                            device_data["voltage"] = volt
                        except:
                            pass

                except:
                    break

        threading.Thread(target=handle_client, args=(client,), daemon=True).start()

# TCP server ayrı thread'de başlat
threading.Thread(target=start_tcp_server, daemon=True).start()

# Flask başlat
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    print(f"Flask API başlatıldı: 0.0.0.0:{port}")
    app.run(host="0.0.0.0", port=port)
