import os
import socket
import threading
import time
from datetime import datetime, timezone
from flask import Flask, render_template, request, redirect, url_for, session, flash

# --- Configuration from ENV ---
OM_MANUFACTURER_CODE = os.getenv("OM_MANUFACTURER_CODE", "OM")
OM_LOCK_IMEI = os.getenv("OM_LOCK_IMEI", "862205059210023")
HOST = "0.0.0.0"
PORT = int(os.getenv("PORT", "5000"))
ADMIN_USER = os.getenv("ADMIN_USER", "admin")
ADMIN_PASS = os.getenv("ADMIN_PASS", "password")
SECRET_KEY = os.getenv("SECRET_KEY", "supersecretkey")

# --- Global state ---
state = {
    'conn': None,
    'addr': None,
    'last_q0': None,
    'last_d0': None,
    'last_timestamp': None
}

app = Flask(__name__)
app.secret_key = SECRET_KEY

# --- Helper functions ---
def calc_timestamp():
    return datetime.now(timezone.utc).strftime("%y%m%d%H%M%S")

def build_tcp_command(cmd_type: str, *params) -> bytes:
    ts = calc_timestamp()
    parts = ["*CMDS", OM_MANUFACTURER_CODE, OM_LOCK_IMEI, ts, cmd_type] + list(params)
    cmd_str = ",".join(parts) + "#\n"
    return b"\xFF\xFF" + cmd_str.encode()

def send_command(cmd_type, *params):
    conn = state.get('conn')
    if conn:
        cmd = build_tcp_command(cmd_type, *params)
        conn.sendall(cmd)
        state['last_timestamp'] = datetime.now(timezone.utc).isoformat()
        return True
    return False

# --- TCP server thread ---

def handle_client(conn, addr):
    state['conn'] = conn
    state['addr'] = addr
    print(f"[+] Kilit bağlandı: {addr}")
    try:
        conn.sendall(build_tcp_command("Q0", "0", "80"))
        conn.sendall(build_tcp_command("H0", "0", "412", "28", "80"))
        while True:
            data = conn.recv(1024)
            if not data:
                break
            text = data.decode(errors='ignore').strip()
            print(f"[{addr}] <<< {text}")
            # Parse Q0 and D0 responses
            parts = text.split(',')
            if len(parts) > 4 and parts[4] == 'Q0':
                state['last_q0'] = text
n            if len(parts) > 4 and parts[4] == 'D0':
                state['last_d0'] = text
    except Exception as e:
        print(f"[!] Hata: {e}")
    finally:
        conn.close()
        state['conn'] = None
        print(f"[-] Kilit ayrıldı: {addr}")


def start_tcp_server():
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.bind((HOST, PORT))
    sock.listen()
    print(f"Sunucu dinleniyor: {HOST}:{PORT}")
    while True:
        conn, addr = sock.accept()
        threading.Thread(target=handle_client, args=(conn, addr), daemon=True).start()

# --- Flask routes ---

@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        if request.form['username'] == ADMIN_USER and request.form['password'] == ADMIN_PASS:
            session['logged_in'] = True
            return redirect(url_for('dashboard'))
        flash('Invalid credentials', 'danger')
    return render_template('login.html')

@app.route('/dashboard')
def dashboard():
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    return render_template('dashboard.html', state=state)

@app.route('/unlock')
def unlock():
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    success = send_command('L0', '0', '1234', str(int(datetime.now(timezone.utc).timestamp())))
    flash('Unlock command sent' if success else 'No device connected', 'info')
    return redirect(url_for('dashboard'))

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

# --- Main entry ---

if __name__ == '__main__':
    import multiprocessing

    # Start TCP server in background
    p = multiprocessing.Process(target=start_tcp_server, daemon=True)
    p.start()

    # Start Flask app
    app.run(host='0.0.0.0', port=8000)
