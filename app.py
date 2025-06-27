from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
import requests

app = Flask(__name__)
app.secret_key = "süpergizlisifre123"  # Değiştir!

# API ayarları — main.py Flask API adresi
API_URL = "http://localhost:8000"  # Railway'de gerçek URL olmalı

USERNAME = "admin"
PASSWORD = "123456"

@app.route("/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        u = request.form.get("username")
        p = request.form.get("password")
        if u == USERNAME and p == PASSWORD:
            session["logged_in"] = True
            return redirect(url_for("panel"))
        else:
            flash("Kullanıcı adı veya şifre yanlış!")
    return render_template("login.html")

@app.route("/panel")
def panel():
    if not session.get("logged_in"):
        return redirect(url_for("login"))

    try:
        r = requests.get(f"{API_URL}/locks")
        locks = r.json()
    except Exception as e:
        locks = []
        flash(f"Kilitleme servisine bağlanılamadı: {e}")

    return render_template("index.html", locks=locks)

@app.route("/unlock", methods=["POST"])
def unlock():
    if not session.get("logged_in"):
        return redirect(url_for("login"))
    address = request.form.get("address")
    if not address:
        flash("Adres bilgisi eksik")
        return redirect(url_for("panel"))
    try:
        r = requests.post(f"{API_URL}/send_l0", json={"address": address})
        resp = r.json()
        if r.status_code == 200 and resp.get("status") == "ok":
            flash(f"{address} kilidi açıldı.")
        else:
            flash(f"Kilit açılamadı: {resp.get('message')}")
    except Exception as e:
        flash(f"İstek gönderilirken hata: {e}")

    return redirect(url_for("panel"))

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080, debug=True)
