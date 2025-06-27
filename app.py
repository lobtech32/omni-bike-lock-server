from flask import Flask, render_template, request, redirect, url_for, session, flash
import socket
import threading
import time

app = Flask(__name__)
app.secret_key = "süpergizlisifre123"  # Bunu kendin değiştir

# Sabit kullanıcı adı ve şifre (basit örnek)
USERNAME = "admin"
PASSWORD = "123456"

# TCP client dictionary (ip:port → socket)
clients = {}
lock_status = {}

# Bu kısmı main.py ile senkron tutmak için basit mekanizma kurabiliriz,
# ama şu aşamada aynı sunucuya bağlanıyorsan ayrı thread veya API çağrısı gerek.

# TCP sunucu ile haberleşme için (örn. localhost:5000)
TCP_HOST = "127.0.0.1"
TCP_PORT = 5000

# Basit TCP client ile L0 komutu gönderme fonksiyonu
def send_l0_command(addr):
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect(addr)
        sock.sendall(b"L0\n")
        sock.close()
        return True
    except Exception as e:
        print(f"L0 komutu gönderilemedi: {e}")
        return False

@app.route("/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        if username == USERNAME and password == PASSWORD:
            session["logged_in"] = True
            return redirect(url_for("panel"))
        else:
            flash("Hatalı kullanıcı adı veya şifre")
    return render_template("login.html")

@app.route("/panel")
def panel():
    if not session.get("logged_in"):
        return redirect(url_for("login"))
    
    # Örnek veri (gerçek durum main.py'den alınmalı)
    # Şimdilik sabit örnek
    locks = [
        {"id": 1, "address": ("127.0.0.1", 6000), "connected": True, "last_seen": "2025-06-27 15:00:00", "location": "Belirtilmedi", "voltage": "12.5V"},
        # Bunu gerçek veriye göre güncelle
    ]

    return render_template("index.html", locks=locks)

@app.route("/unlock/<int:lock_id>", methods=["POST"])
def unlock(lock_id):
    if not session.get("logged_in"):
        return redirect(url_for("login"))
    
    # Örnek: lock_id ile adres bul, L0 komutu gönder
    # Burada hardcoded, kendi TCP client yapına göre değiştir
    addr = ("127.0.0.1", 6000)
    success = send_l0_command(addr)
    if success:
        flash(f"Kilit {lock_id} başarıyla açıldı.")
    else:
        flash(f"Kilit {lock_id} açılamadı.")
    return redirect(url_for("panel"))

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, debug=True)
