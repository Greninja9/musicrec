import streamlit as st
import requests
import base64
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials

st.markdown(
    """
    <style>
    .reportview-container {
        background: url("https://www.pexels.com/photo/green-and-blue-peacock-feather-674010/")
    }
   .sidebar .sidebar-content {
        background: url("https://www.pexels.com/photo/green-and-blue-peacock-feather-674010/")
    }
    </style>
    """,
    unsafe_allow_html=True
)




client_credentials_manager = SpotifyClientCredentials(client_id='06efd7289817442293ffea29b7962ce5', client_secret='55119dd838f644ca98159fddaa886a6d')
sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)
def get_access_token(client_id, client_secret):
    auth_header = base64.b64encode(f"{client_id}:{client_secret}".encode()).decode()
    token_url = 'https://accounts.spotify.com/api/token'
    data = {
        'grant_type': 'client_credentials'
    }
    headers = {
        'Authorization': f'Basic {auth_header}'
    }
    response = requests.post(token_url, data=data, headers=headers)
    if response.status_code == 200:
        return response.json()['access_token']
    else:
        print("Failed to retrieve access token:", response.text)
        return None

def search_track_on_spotify(track_title, access_token):
    headers = {
        "Authorization": f"Bearer {access_token}"
    }
    url = "https://api.spotify.com/v1/search"
    params = {
        "q": track_title,
        "type": "track",
        "limit": 1
    }
    response = requests.get(url, headers=headers, params=params)
    if response.status_code == 200:
        try:
            data = response.json()
            if data['tracks']['items']:
                track = data['tracks']['items'][0]
                name = track['name']
                poster = track['album']['images'][0]['url']
                preview = track['preview_url']
                track_id = track['id']  # Extracting track ID
                return name, poster, preview, track_id
            else:
                print("No track found with the given name")
                return None, None, None, None
        except Exception as e:
            print("Error:", e)
            return None, None, None, None
    else:
        print("Request failed with status code:", response.status_code)
        return None, None, None, None

def recommend_similar_tracks(track_id, access_token):
    headers = {
        "Authorization": f"Bearer {access_token}"
    }
    url = "https://api.spotify.com/v1/recommendations"
    params = {
        "seed_tracks": track_id,
        "limit": 10
    }
    response = requests.get(url, headers=headers, params=params)
    if response.status_code == 200:
        try:
            data = response.json()
            if data['tracks']:
                recommended_tracks = []
                for track in data['tracks']:
                    recommended_tracks.append({
                        'name': track['name'],
                        'poster': track['album']['images'][0]['url'],
                        'preview': track['preview_url']
                    })
                return recommended_tracks
            else:
                print("No recommendations found")
                return None
        except Exception as e:
            print("Error:", e)
            return None
    else:
        print("Request failed with status code:", response.status_code)
        return None

st.title('BeatBot')

selected_music_name = st.text_input('Type the name of a music you like')

if st.button('Recommend'):
    client_id = '06efd7289817442293ffea29b7962ce5'
    client_secret = '55119dd838f644ca98159fddaa886a6d'
    access_token = get_access_token(client_id, client_secret)

    if access_token:
        searched_name, searched_poster, searched_preview, searched_track_id = search_track_on_spotify(selected_music_name, access_token)

        if searched_poster:
            st.subheader('Searched Song')
            st.text(searched_name)
            st.image(searched_poster)
            st.markdown(
                f'<audio src="{searched_preview}" controls style="width: 100%;"></audio>',
                unsafe_allow_html=True
            )

        similar_tracks = recommend_similar_tracks(searched_track_id, access_token)

        if similar_tracks:
            st.subheader('Recommended Songs')
            for track in similar_tracks:
                col1, col2 = st.columns([1, 3])  # Adjust the width ratio as needed
                with col1:
                    st.text(track['name'])
                    st.image(track['poster'])
                with col2:
                    st.markdown(
                        f'<audio src="{track["preview"]}" controls style="width: 100%;"></audio>',
                        unsafe_allow_html=True
                    )
