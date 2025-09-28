"""
Script: save_spotify_logs.py
Fetches Spotify listening history and saves it to Supabase.
"""

import os
from datetime import datetime, timedelta, timezone
import requests
from supabase import create_client, Client
from auth import SpotifyAuth

# Supabase configuration
SUPABASE_URL = os.environ["SUPABASE_URL"]
SUPABASE_KEY = os.environ["SUPABASE_KEY"]
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)


def fetch_recent_tracks(spotify_auth: SpotifyAuth):
    """Fetch recently played tracks from Spotify API"""

    url = "https://api.spotify.com/v1/me/player/recently-played?limit=50"
    headers = {"Authorization": f"Bearer {spotify_auth.token}"}
    res = requests.get(url, headers=headers, timeout=10)

    res.raise_for_status()
    return res.json()["items"]


def save_to_supabase(track_logs, target_database):
    """Save Spotify listening history to Supabase (filtered to the last hour)"""

    now = datetime.now(timezone.utc)
    one_hour_ago = now - timedelta(hours=1)

    for item in track_logs:
        track = item["track"]
        played_at = datetime.fromisoformat(item["played_at"].replace("Z", "+00:00"))

        # Only save tracks played within the last hour
        if played_at >= one_hour_ago:
            target_database.table("spotify-logs").insert(
                {
                    "track_name": track["name"],
                    "artist_name": track["artists"][0]["name"],
                    "played_at": played_at.isoformat(),
                    "saved_at": now.isoformat(),
                }
            ).execute()


if __name__ == "__main__":
    auth = SpotifyAuth()
    print("✅ : Loaded Spotify authentication module")

    tracks = fetch_recent_tracks(auth)
    print("✅ : Successfully fetched recent tracks")

    save_to_supabase(tracks, supabase)
    print("✅ : Successfully saved tracks to Supabase")
