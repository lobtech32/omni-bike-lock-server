### 📄 app.py (Web Panel)
```python
from flask import Flask, render_template, request, redirect, session
import os, requests
from dotenv import load_dotenv

load_dotenv()
app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "devkey")

ADMIN_USER = os.getenv("ADMIN_USER", "admin")
ADMIN_PASS = os.getenv("ADMIN_PASS", "admin")
MAIN_URL = os.getenv("MAIN_URL", "http://localhost:5000")

lock_ids = ["862205059210023"]
lock_status = {id: "Kapalı" for id in lock_ids}

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        if (request.form["username"] == ADMIN_USER and
            request.form["password"] == ADMIN_PASS):
            session["logged_in"] = True
            return redirect("/admin")
        return render_template("login.html", error="Hatalı giriş")
    return render_template("login.html", error=None)

@app.route("/logout")
def logout():
    session.clear()
    return redirect("/login")

@app.route("/admin")
def admin():
    if not session.get("logged_in"):
        return redirect("/login")
    return render_template("admin.html",
                           devices=lock_ids,
                           statuses=lock_status)

@app.route("/open/<device_id>", methods=["POST"])
def open_admin(device_id):
    try:
        res = requests.post(f"{MAIN_URL}/open/{device_id}")
        if res.status_code == 200:
            lock_status[device_id] = "Açık"
    except:
        pass
    return redirect(request.referrer or "/admin")

@app.route("/customer/<device_id>", methods=["GET", "POST"])
def customer(device_id):
    status = lock_status.get(device_id, "Bilinmiyor")
    if request.method == "POST" and status == "Kapalı":
        try:
            res = requests.post(f"{MAIN_URL}/open/{device_id}")
            if res.status_code == 200:
                status = "Açık"
        except:
            pass
    return render_template("customer.html",
                           device_id=device_id,
                           status=status)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.getenv("WEB_PORT", 8000)))
```