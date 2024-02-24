from dotenv import load_dotenv
import os
from flask import Flask, redirect, session, request, render_template
import spotipy
from spotipy.oauth2 import SpotifyOAuth

load_dotenv()

# this code is retarded because it's caching everyones user auth in the .cache file
client_id = os.getenv("CLIENT_ID")
client_secret = os.getenv("CLIENT_SECRET")

# This is what connects the front end to the backend
app = Flask(__name__)
app.secret_key = client_secret

# Initialize SpotifyOAuth object within the route
sp_oauth = SpotifyOAuth(
        client_id = os.getenv("CLIENT_ID"),
        client_secret = os.getenv("CLIENT_SECRET"),
        redirect_uri = 'http://localhost:5000/callback',
        scope = 'user-read-private user-top-read user-library-read',
        cache_path=None
    )

def htmlForLoginButton():
    auth_url = getSPOauthURI()
    htmlLoginButton = "<a href='" + auth_url + "'>Login to Spotify</a>"
    return htmlLoginButton

def getSPOauthURI():
    auth_url = sp_oauth.get_authorize_url()
    return auth_url

# --- routes ---
@app.route('/')
def index():
  
    # Get user's profile information
    token_info = session.get('spotify_token_info')

    if not token_info or sp_oauth.is_token_expired(token_info):
        # return redirect('/callback')
        return htmlForLoginButton()
    
    sp = spotipy.Spotify(auth=session['spotify_token_info']['access_token'])
    user_profile = sp.current_user()

    # user variables
    username = user_profile['display_name']
    pfp = user_profile['images'][0]['url'] if user_profile['images'] else ''
    id = user_profile['id']  
    topSongs = sp.current_user_top_tracks(limit=6)

    pics = []
    for song in topSongs['items']:
        album_id = song['album']['id']
        album_info = sp.album(album_id)
        cover_art_url = album_info['images'][0]['url'] if len(album_info['images']) > 0 else None
        pics.append(cover_art_url)
        print(cover_art_url)
    
    return render_template('index.html', username=username, pfp=pfp, id=id, pics=pics)

@app.route('/callback')
def callback():
    # Parse authorization response
    code = request.args.get('code')
    print(str(code))
    token_info = sp_oauth.get_access_token(code)
    print(token_info)
    session['spotify_token_info'] = token_info
    return redirect('/')

# TODO needs to be implemented
@app.route('/logout')
def logout():
    session['spotify_token_info'] = None
    return redirect('/')

if __name__ == '__main__':
    app.run(port=5000, debug=True)

