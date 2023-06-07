import base64
import threading
import requests
import os
import webbrowser
import yaml
from dotenv import load_dotenv
from flask import Flask, jsonify, Response, request, send_from_directory, redirect, request
from flask_cors import CORS
from urllib.parse import urlencode

app = Flask(__name__)
PORT = 3333

# Note: Setting CORS to allow chat.openapi.com is required for ChatGPT to access the plugin
CORS(app, origins=[f'http://localhost:{PORT}', 'https://chat.openai.com'])

load_dotenv()
CLIENT_ID = os.getenv('SPOTIFY_CLIENT_ID')
CLIENT_SECRET = os.getenv('SPOTIFY_CLIENT_SECRET')
REDIRECT_URI = os.getenv('SPOTIFY_REDIRECT_URI')
api_url = 'https://api.spotify.com/v1'
access_token = None
refresh_token = None

# Modify based off of the scopes you need for the API endpoints you wish to use
# Add "playlist-modify-private,playlist-modify-public" if you want to be able to create playlists
# https://developer.spotify.com/documentation/web-api/concepts/scopes
scope = 'playlist-read-private,playlist-read-collaborative,user-read-private,user-library-read,user-top-read'


@app.route('/.well-known/ai-plugin.json')
def serve_manifest():
    return send_from_directory(os.path.dirname(__file__) + '/.well-known', 'ai-plugin.json')


@app.route('/openapi.yaml')
def serve_openapi_yaml():
    with open(os.path.join(os.path.dirname(__file__), 'openapi.yaml'), 'r', encoding='utf-8') as f:
        yaml_data = f.read()
    yaml_data = yaml.load(yaml_data, Loader=yaml.FullLoader)
    return jsonify(yaml_data)


@app.route('/logo.png')
def serve_logo():
    return send_from_directory(os.path.dirname(__file__), 'logo.png')


@app.route('/login')
def login():
    auth_url = 'https://accounts.spotify.com/authorize?' + urlencode({
        'response_type': 'code',
        'client_id': CLIENT_ID,
        'scope': scope,
        'redirect_uri': REDIRECT_URI,
    })
    return redirect(auth_url)


@app.route('/callback')
def callback():
    global access_token, refresh_token
    code = request.args.get('code')
    auth_str = base64.b64encode(f'{CLIENT_ID}:{CLIENT_SECRET}'.encode('utf-8')).decode('utf-8')
    headers = {'Authorization': f'Basic {auth_str}', 'Content-Type': 'application/x-www-form-urlencoded'}
    data = {'grant_type': 'authorization_code', 'code': code, 'redirect_uri': REDIRECT_URI}
    r = requests.post('https://accounts.spotify.com/api/token', headers=headers, data=data)
    r.raise_for_status()
    access_token = r.json()['access_token']
    refresh_token = r.json()['refresh_token']
    return 'Logged in successfully!'


@app.route('/<path:path>', methods=['GET', 'POST'])
def wrapper(path):
    global access_token, refresh_token
    
    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/json',
    }

    url = f'{api_url}/{path}'
    print(f'Forwarding call: {request.method} {path} -> {url}')

    if request.method == 'GET':
        response = requests.get(url, headers=headers, params=request.args)
    elif request.method == 'POST':
        print(request.headers)
        response = requests.post(url, headers=headers, params=request.args, json=request.json)
    else:
        raise NotImplementedError(f'Method {request.method} not implemented in wrapper for {path=}')
    
    if response.status_code == 401:  # Access token expired
        auth_str = base64.b64encode(f'{CLIENT_ID}:{CLIENT_SECRET}'.encode('utf-8')).decode('utf-8')
        headers = {'Authorization': f'Basic {auth_str}'}
        data = {'grant_type': 'refresh_token', 'refresh_token': refresh_token}
        r = requests.post('https://accounts.spotify.com/api/token', headers=headers, data=data)
        r.raise_for_status()
        access_token = r.json()['access_token']
        refresh_token = r.json()['refresh_token'] if r.json()['refresh_token'] else None  # refresh token may be null
        headers['Authorization'] = f'Bearer {access_token}'
        # Retry request
        if request.method == 'GET':
            response = requests.get(url, headers=headers, params=request.args)
        elif request.method == 'POST':
            response = requests.post(url, headers=headers, params=request.args, json=request.json)
        response.raise_for_status()
    return response.content


if __name__ == '__main__':
    def open_browser():
        webbrowser.open_new(f'http://localhost:{PORT}/login')

    threading.Timer(1, open_browser).start()

    app.run(port=PORT, threaded=True)
