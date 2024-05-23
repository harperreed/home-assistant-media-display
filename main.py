import eventlet
eventlet.monkey_patch()
import pprint
from flask import Flask, render_template
from flask_socketio import SocketIO
import requests
from dotenv import load_dotenv
import os
import time
import datetime

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

cached_fip_metadata = {}

# Define a dictionary to map station names to their corresponding codes
station_map = {
    "FIP autour du reggae": "fip_reggae",
    "FIP Reggae": "fip_reggae",
    "FIP POP": "fip_pop",
    "FIP Metal": "fip_metal",
    "FIP Hip Hop": "fip_hiphop",
    "Fip Hip Hop": "fip_hiphop",
    "FIP autour du rock": "fip_rock",
    "FIP autour du jazz": "fip_jazz",
    "FIP autour du monde": "fip_world",
    "FIP autour du groove": "fip_groove",
    "Tout nouveau, tout FIP": "fip_nouveautes",
    "FIP autour de l’électro": "fip_electro",
    "FIP (hls)": "fip",
    "FIP (hifi)": "fip"
}



import logging

def get_fip_metadata(station_name):
    """
    Fetches metadata for a given FIP station.

    Args:
        station_name (str): The name of the FIP station.

    Returns:
        dict: A dictionary containing metadata about the current playing media.
    """
    logging.info(f"Fetching FIP metadata for station: {station_name}")
    station = station_map.get(station_name, 'unknown')
    logging.debug(f"Station code resolved to: {station}")
    url = f"https://fip-metadata.fly.dev/api/metadata/{station}"
    try:
        response = requests.get(url)
        if response.status_code == 200:
            logging.info("Successfully fetched FIP metadata")
            fip_metadata = response.json()
            logging.debug(f"FIP metadata: {fip_metadata}")
            return {
                'media_title': fip_metadata['now']['firstLine']['title'],
                'media_artist': fip_metadata['now']['secondLine']['title'],
                'media_starttime': fip_metadata['now']['startTime'],
                'media_endtime': fip_metadata['now']['endTime'],
                'media_position': 0,
                'media_duration': 0,
                'media_volume': 0,
                'cover_art_url': fip_metadata['now']['visuals']['card']['src'].replace('200x200','400x400'),
                'full_metadata': fip_metadata,
            }
        else:
            logging.warning("Failed to fetch FIP metadata: Status code {response.status_code}")
            return {
                'media_title': 'Unavailable',
                'media_artist': '',
                'media_position': 0,
                'media_endtime': 0,
                'media_starttime': 0,
                'media_duration': 0,
                'media_volume': 0,
                'cover_art_url': None
            }
    except requests.RequestException as e:
        logging.error(f"Error fetching FIP metadata: {e}")
        return {
            'media_title': 'Unavailable',
            'media_artist': '',
            'media_position': 0,
            'media_duration': 0,
            'media_endtime': 0,
            'media_starttime': 0,
            'media_volume': 0,
            'cover_art_url': None
        }

def get_media_state():
    with app.app_context():

        url = f"{base_url}/api/states/{entity_id}"

        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            data = response.json()
            media_volume = data['attributes'].get('volume_level', 0) * 100  # Convert to percentage
            media_title = data['attributes'].get('media_title', 'Unknown')
            if "FIP" in media_title:
                fip_data = get_fip_metadata(media_title)
                media_title = fip_data['media_title']
                media_artist = fip_data['media_artist']
                cover_art_url = fip_data['cover_art_url']
                media_position = fip_data['media_position']
                media_duration = fip_data['media_duration']
                media_endtime = fip_data['media_endtime']
                media_starttime = fip_data['media_starttime']
            else:
                # {'attributes': {'device_class': 'speaker',
                #                 'entity_picture': '/api/media_player_proxy/media_player.office?token=778befffca6e0328cb17ed4c38294fdb19a39608a1574c6cc22cf4383af17ad1&cache=e98a27680054cfda',
                #                 'friendly_name': 'Office',
                #                 'group_members': ['media_player.office',
                #                                   'media_player.turntable'],
                #                 'is_volume_muted': False,
                #                 'media_album_name': 'I FIGHT BITCHES',
                #                 'media_artist': 'THOT SQUAD',
                #                 'media_content_id': 'x-sonos-spotify:spotify%3atrack%3a6rWoDGYgLVGkU8ZBvW7eXX?sid=12&flags=8232&sn=3',
                #                 'media_content_type': 'music',
                #                 'media_duration': 111,
                #                 'media_playlist': 'Top Tracks',
                #                 'media_position': 1,
                #                 'media_position_updated_at': '2024-05-23T15:44:29.151914+00:00',
                #                 'media_title': 'I FIGHT BITCHES',
                #                 'queue_position': 6,
                #                 'queue_size': 10,
                #                 'repeat': 'off',
                #                 'shuffle': False,
                #                 'source_list': ['Line-in'],
                #                 'supported_features': 4127295,
                #                 'volume_level': 0.31},
                #  'context': {'id': '01HYK202Z006HMTTH4E1W1JE24',
                #              'parent_id': None,
                #              'user_id': None},
                #  'entity_id': 'media_player.office',
                #  'last_changed': '2024-05-23T15:41:14.139850+00:00',
                #  'last_reported': '2024-05-23T15:44:29.152136+00:00',
                #  'last_updated': '2024-05-23T15:44:29.152136+00:00',
                #  'state': 'playing'}
                media_artist = data['attributes'].get('media_artist', 'Unknown')
                entity_picture = data['attributes'].get('entity_picture', None)

                media_duration = data['attributes'].get('media_duration', 0)

                song_start = data['attributes'].get('last_changed', time.time())
                # media_position = time.time() - song_start

                media_position = (datetime.datetime.fromtimestamp(song_start)- datetime.datetime.fromtimestamp(time.time())).total_seconds()
                #media duration is in seconds. add it to the song start to get the song end
                song_end = song_start + media_duration
                song_start = datetime.datetime.fromtimestamp(song_start).isoformat()
                song_end = datetime.datetime.fromtimestamp(song_end).isoformat()


                print(song_start)
                print(song_end)
                media_endtime = song_end
                media_starttime = song_start

                # calculate the position of the song using the last reported time, which is the last time the song was updated. not using the position attribute


                cover_art_url = f"{base_url}{entity_picture}" if entity_picture else None
                # updated_position = time.time() - data['attributes'].get('media_position_updated_at', time.time())
                # print(f"Updated position: {updated_position}")

                #calculate when the media will end



            return {
                'media_title': media_title,
                'media_artist': media_artist,
                'media_position': media_position,
                'media_duration': media_duration,
                'media_volume': media_volume,
                'media_endtime': media_endtime,
                'media_starttime': media_starttime,
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
    """
    Runs in the background to periodically check for changes in media state and emit updates to connected clients.
    """
    logging.info("Background thread started")
    previous_media_title = None
    previous_media_volume = None
    while True:
        socketio.sleep(2)  # Update every 2 seconds
        media_state = get_media_state()
        if media_state['media_title'] != previous_media_title or media_state['media_volume'] != previous_media_volume:
            logging.info(f"Emitting new media state: {media_state['media_title']}, volume: {media_state['media_volume']}")
            socketio.emit('media_state', media_state)
            previous_media_title = media_state['media_title']
            previous_media_volume = media_state['media_volume']


if __name__ == '__main__':
    eventlet.spawn(background_thread)
    socketio.run(app, debug=True, host='0.0.0.0', port=5000)
