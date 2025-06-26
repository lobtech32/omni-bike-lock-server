from flask import Flask, request

app = Flask(__name__)

@app.route('/')
def home():
    return "Merhaba, Kilit Server Çalışıyor!"

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)  # Flask web arayüzü 8080 portunda
