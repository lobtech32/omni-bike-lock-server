import os

port = int(os.environ.get('PORT', 8000))  # Railway otomatik PORT verir, yoksa 8000

app.run(host='0.0.0.0', port=port)
