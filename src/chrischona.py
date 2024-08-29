import os
from churchtools import ChurchTools
import spotipy
from spotipy.oauth2 import SpotifyOAuth


class Church(ChurchTools):
    def __init__(self, base_url, churchtools_email, churchtools_password, spotify_client_id, spotify_client_secret, spotify_redirect_uri):
        super().__init__(base_url)
        self.login(churchtools_email, churchtools_password)
        self.spotify_client_id = spotify_client_id
        self.spotify_client_secret = spotify_client_secret
        self.spotify_redirect_uri = spotify_redirect_uri

    def find_or_create_playlist(self, sp, user_id, playlist_name):
        playlists = sp.current_user_playlists()
        for playlist in playlists['items']:
            if playlist['name'] == playlist_name and playlist['owner']['id'] == user_id:
                return playlist['id']
        # If playlist does not exist, create it
        return sp.user_playlist_create(user_id, playlist_name)['id']

    def create_spotify_playlist(self, songs, playlist_name):
        sp_oauth = SpotifyOAuth(client_id=self.spotify_client_id,
                                client_secret=self.spotify_client_secret,
                                redirect_uri=self.spotify_redirect_uri,
                                scope="playlist-modify-public user-library-read",
                                cache_path=".spotify_cache")

        token_info = sp_oauth.get_cached_token()

        if not token_info:
            auth_url = sp_oauth.get_authorize_url()
            print(f"Please navigate to this URL to authorize: {auth_url}")
            
            # You'll need to capture the redirected URL from the browser after authorizing
            response = input("Paste the URL you were redirected to: ")
            
            # Ensure that the correct code is being extracted from the URL
            code = sp_oauth.parse_response_code(response.strip())
            if not code:
                print("Error: Unable to extract authorization code from the provided URL.")
                return
            
            try:
                token_info = sp_oauth.get_access_token(code)
            except SpotifyOauthError as e:
                print(f"Error obtaining access token: {e}")
                return

        if not token_info:
            print("Failed to get the token info. Exiting.")
            return

        sp = spotipy.Spotify(auth=token_info['access_token'])

        # Get user's ID
        try:
            user_id = sp.current_user()["id"]
        except spotipy.exceptions.SpotifyException as e:
            print(f"Error while fetching current user: {str(e)}")
            return

        # Find existing playlist or create a new one
        playlist_id = self.find_or_create_playlist(sp, user_id, playlist_name)

        # Clear existing tracks in the playlist
        sp.playlist_replace_items(playlist_id, [])

        track_ids = []

        for song in songs:
            # Check for a Spotify link in the song's arrangements
            spotify_link = None
            for arrangement in song.arrangements:
                for link in arrangement.links:
                    if "open.spotify.com" in link.fileUrl:
                        spotify_link = link.fileUrl
                        break
                if spotify_link:
                    break

            if spotify_link:
                # Extract the Spotify track ID from the link
                track_id = spotify_link.split('/')[-1].split('?')[0]
                track_ids.append(track_id)
            else:
                print(f"Warning: No Spotify link found for the song '{song.name}'.")

        if not track_ids:
            print("Error: No valid Spotify links were found in the provided song list. No songs were added to the playlist.")
            return

        # Add tracks to the playlist in batches of 100
        batch_size = 100
        for i in range(0, len(track_ids), batch_size):
            batch = track_ids[i:i + batch_size]
            try:
                sp.playlist_add_items(playlist_id, batch)
            except spotipy.exceptions.SpotifyException as e:
                print(f"Error while adding batch to the playlist: {str(e)}")

        print(f"Playlist '{playlist_name}' updated successfully with {len(track_ids)} tracks.")

    def get_all_songs(self, limit=200, category_filter=None):
        all_songs = []
        current_page = 1
        
        while True:
            result = self.songs.list(limit=limit, page=current_page)
            songs = result[0]
            pagination = result[1].pagination
            
            if category_filter:
                # Filter songs by category name
                filtered_songs = [song for song in songs if song.category.name == category_filter]
                all_songs.extend(filtered_songs)
            else:
                all_songs.extend(songs)
            
            if pagination.current >= pagination.lastPage:
                break
            
            current_page += 1
        
        return all_songs