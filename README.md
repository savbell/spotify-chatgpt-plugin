# 🎵🗨 Spotify ChatGPT Plugin

This project is a Flask-based application that acts as a wrapper for the Spotify API. When installed as a ChatGPT plugin, it allows ChatGPT to authenticate with Spotify and make requests to the Spotify Web API. It is meant only to be run locally using your own Spotify developer app credentials. This project is not affiliated with Spotify.

Note that to use this app, you must be a Plus user and have beta access to [ChatGPT plugins](https://openai.com/blog/chatgpt-plugins). If you do not have access, you can join the waitlist [here](https://openai.com/waitlist/plugins).

## Setup

1. Clone this repository:
```
git clone https://github.com/savbell/spotify-chatgpt-plugin.git
cd spotify-chatgpt-plugin
```

2. Install the required Python packages:
```
pip install -r requirements.txt
```

3. Create a Spotify developer app [here](https://developer.spotify.com/dashboard) by following [these instructions](https://developer.spotify.com/documentation/web-api/concepts/apps). Add `http://localhost:3333/callback` as a redirect URI in the app settings.

5. Copy the ".env.example" file to a new file named ".env":
```
cp .env.example .env # For Linux and macOS
copy .env.example .env # For Windows
```

6. Open the ".env" file and add in the necessary values for your newly-created Spotify app:
```
SPOTIFY_CLIENT_ID=<your_spotify_client_id_here>
SPOTIFY_CLIENT_SECRET=<your_spotify_client_secret_here>
SPOTIFY_REDIRECT_URI=http://localhost:3333/callback
```

## Usage

1. Run the script with `python main.py`.
2. A web browser should automatically open to `localhost:3333/login`. Log in with your Spotify credentials and give permissions to your Spotify development app.
3. Go to [ChatGPT](https://chat.openai.com/?model=gpt-4-plugins). Choose "GPT-4", click "Plugins (Beta)", open the plugin drop-down menu and go to the Plugin Store. Click "Develop your own plugin" in the bottom-right corner and enter `localhost:3333`. Ignore the manifest warnings and install the plugin.
4. You should now be able to use the Spotify API plugin in ChatGPT!

## Endpoints

This wrapper supports all endpoints provided by the Spotify API. For more information about the available endpoints and their usage, please refer to the [Spotify API documentation](https://developer.spotify.com/documentation/web-api/reference/).

## Known Issues

ChatGPT likes to make up IDs, especially for lesser-known artists and songs. It doesn't seem to be a problem with the wrapper, but rather with ChatGPT itself. If you run into this issue, try using the Spotify API or UI directly to get the ID of the artist, track, or playlist you're looking for, then use that ID in ChatGPT.

I have not done too much investigation yet, but I believe ChatGPT is not able to modify the endpoint URL to include the ID of the artist, track, or playlist. For example, it will attempt to get an artist's albums using the endpoint `https://api.spotify.com/v1/artists/` instead of `https://api.spotify.com/v1/artists/{id}/albums`. This is likely due to the fact that the Spotify API uses path parameters instead of query parameters for these endpoints. Because this project was made as a proof-of-concept rather than a production-ready application, I have not yet implemented a workaround for this issue and currently have no plans to do so. Therefore, the functionality of this wrapper is limited to the endpoints that use query parameters for now.

## Acknowledgements

The OpenAPI specification for the Spotify Web API used in this applicataion was created by [sonallux](https://github.com/sonallux) and can be found [here](https://github.com/sonallux/spotify-web-api/blob/b911852839d7a71b5b9216bb018cb31a4fe6887e/fixed-spotify-open-api.yml). Thank you for saving me a lot of work!
