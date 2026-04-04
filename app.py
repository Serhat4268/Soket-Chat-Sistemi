from flask import Flask, render_template
from flask_socketio import SocketIO, emit

app = Flask(__name__)
app.config['SECRET_KEY'] = 'pasam_ozel_anahtar'
socketio = SocketIO(app, cors_allowed_origins="*", max_decode_size=20 * 1024 * 1024) # 20MB limit

@socketio.on('message')
def handle_message(data):
    # Mesaj veya Dosya verisini herkese yayınla
    emit('response', data, broadcast=True)

@app.route('/')
def index():
    return render_template('index.html')

if __name__ == '__main__':
    socketio.run(app, debug=True, port=5555)