from flask import json, request, Flask
from waitress import serve
from threading import Thread
app = Flask(__name__)


@app.route('/health_check')
def health_check():
    return '200 OK'

@app.route('/')
def listen():
    return '<h1>SURE, ITS WORKING</h1>'

def run():
    serve(app, host="0.0.0.0", port=8080)

def keep_alive():
    t = Thread(target=run)
    t.start()
