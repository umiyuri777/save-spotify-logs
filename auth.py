import os
import requests
from base64 import b64encode

CLIENT_ID = os.environ["SPOTIFY_CLIENT_ID"]
CLIENT_SECRET = os.environ["SPOTIFY_CLIENT_SECRET"]
REFRESH_TOKEN = os.environ["SPOTIFY_REFRESH_TOKEN"]


class SpotifyAuth:
    def __init__(self):
        self.client_id = CLIENT_ID
        self.client_secret = CLIENT_SECRET
        self.refresh_token = REFRESH_TOKEN
        self._access_token = None

    def refresh_access_token(self) -> str:
        """Refresh access token using refresh_token"""
        url = "https://accounts.spotify.com/api/token"
        auth_str = f"{self.client_id}:{self.client_secret}"
        headers = {
            "Authorization": "Basic " + b64encode(auth_str.encode()).decode(),
            "Content-Type": "application/x-www-form-urlencoded",
        }
        data = {
            "grant_type": "refresh_token",
            "refresh_token": self.refresh_token,
        }
        res = requests.post(url, headers=headers, data=data, timeout=10)

        res = requests.post(url, headers=headers, data=data, timeout=10)

        res.raise_for_status()

        res.raise_for_status()
        self._access_token = res.json()["access_token"]
        return self._access_token

    @property
    def token(self) -> str:
        if not self._access_token:
            return self.refresh_access_token()
        return self._access_token
