import eventlet
eventlet.monkey_patch()
import pprint
from flask import Flask, render_template
from flask_socketio import SocketIO
import requests
from dotenv import load_dotenv
import os

app = Flask(__name__)
socketio = SocketIO(app)

# Load environment variables from .env file
load_dotenv()

# Retrieve values from environment variables
base_url = os.getenv("BASE_URL")
api_token = os.getenv("API_TOKEN")
entity_id = os.getenv("ENTITY_ID")

headers = {
    "Authorization": f"Bearer {api_token}",
    "Content-Type": "application/json",
}

def get_media_state():
    with app.app_context():
        response = requests.get(f"{base_url}/api/states/{entity_id}", headers=headers)
        if response.status_code == 200:
            data = response.json()
            pprint.pprint(data)
            media_title = data['attributes'].get('media_title', 'Unknown')
            media_artist = data['attributes'].get('media_artist', 'Unknown')
            entity_picture = data['attributes'].get('entity_picture', None)
            media_position = data['attributes'].get('media_position', 0)
            media_duration = data['attributes'].get('media_duration', 0)
            media_volume = data['attributes'].get('volume_level', 0) * 100  # Convert to percentage
            cover_art_url = f"{base_url}{entity_picture}" if entity_picture else None
            return {
                'media_title': media_title,
                'media_artist': media_artist,
                'media_position': media_position,
                'media_duration': media_duration,
                'media_volume': media_volume,
                'cover_art_url': cover_art_url
            }
        else:
            return {
                'media_title': 'Unavailable',
                'media_artist': '',
                'media_position': 0,
                'media_duration': 0,
                'media_volume': 0,
                'cover_art_url': None
            }

@app.route('/')
def index():
    return render_template('index.html')

@socketio.on('connect')
def handle_connect():
    media_state = get_media_state()
    socketio.emit('media_state', media_state)

def background_thread():
    while True:
        socketio.sleep(2)  # Update every 2 seconds
        media_state = get_media_state()
        socketio.emit('media_state', media_state)

if __name__ == '__main__':
    eventlet.spawn(background_thread)
    socketio.run(app, debug=True)
