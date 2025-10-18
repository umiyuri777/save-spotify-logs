"""
モジュール: auth.py
リフレッシュトークンを使用したSpotify認証を処理する。
アクセストークンの期限切れ時に自動的にリフレッシュする。
"""

from base64 import b64encode
import requests
from config.config import config_manager


class SpotifyAuth:
    """Spotify認証を処理するクラス"""

    def __init__(self):
        """設定から認証情報を読み込み、初期化する"""
        spotify_config = config_manager.get_spotify_config()
        self.client_id = spotify_config["client_id"]
        self.client_secret = spotify_config["client_secret"]
        self.refresh_token = spotify_config["refresh_token"]
        self._access_token = None

    def refresh_access_token(self) -> str:
        """リフレッシュトークンを使用してアクセストークンを要求・リフレッシュする"""
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
        res.raise_for_status()

        self._access_token = res.json()["access_token"]
        print("✅ : Access token refreshed")
        return self._access_token

    @property
    def token(self) -> str:
        """現在のアクセストークンを返す（利用できない場合はリフレッシュ）"""
        if not self._access_token:
            return self.refresh_access_token()
        return self._access_token


if __name__ == "__main__":
    auth = SpotifyAuth()
    print("✅ : Auth object created")

    token = auth.token
    print("✅ : Access token retrieved successfully")
