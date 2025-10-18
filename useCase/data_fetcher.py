"""
モジュール: data_fetcher.py
Spotify APIからSpotifyリスニング履歴の取得を処理する。
"""

import requests
from typing import List, Dict, Any
from useCase.auth import SpotifyAuth


class SpotifyDataFetcher:
    """Spotifyリスニング履歴を取得するクラス"""

    def __init__(self, spotify_auth: SpotifyAuth):
        """Spotify認証で初期化する"""
        self.spotify_auth = spotify_auth

    def fetch_recent_tracks(self, limit: int = 50) -> List[Dict[str, Any]]:
        """
        Spotify APIから最近再生されたトラックを取得する

        Args:
            limit: 取得するトラック数（最大50）

        Returns:
            Spotify APIからのトラックアイテムのリスト
        """
        url = f"https://api.spotify.com/v1/me/player/recently-played?limit={limit}"
        headers = {"Authorization": f"Bearer {self.spotify_auth.token}"}
        res = requests.get(url, headers=headers, timeout=10)

        res.raise_for_status()
        return res.json()["items"]

    def fetch_recent_tracks_since(self, since_timestamp: str, limit: int = 50) -> List[Dict[str, Any]]:
        """
        特定のタイムスタンプ以降の最近再生されたトラックを取得する

        Args:
            since_timestamp: このタイムスタンプ以降のトラックを取得するUnixタイムスタンプ
            limit: 取得するトラック数（最大50）

        Returns:
            Spotify APIからのトラックアイテムのリスト
        """
        url = f"https://api.spotify.com/v1/me/player/recently-played?after={since_timestamp}&limit={limit}"
        headers = {"Authorization": f"Bearer {self.spotify_auth.token}"}
        res = requests.get(url, headers=headers, timeout=10)

        res.raise_for_status()
        return res.json()["items"]
