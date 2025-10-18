"""auth-server.py"""
from base64 import b64encode
import os
import requests
from flask import Flask, redirect, request
from dotenv import load_dotenv

# 環境変数から読み込み
load_dotenv()
CLIENT_ID = os.getenv("SPOTIFY_CLIENT_ID")
CLIENT_SECRET = os.getenv("SPOTIFY_CLIENT_SECRET")
REDIRECT_URI = "http://[::1]:5000/callback"

app = Flask(__name__)

@app.route("/login")
def login():
    """ログイン用のルート"""
    scope = "user-read-recently-played"
    url = (
        "https://accounts.spotify.com/authorize"
        f"?client_id={CLIENT_ID}"
        f"&response_type=code"
        f"&redirect_uri={REDIRECT_URI}"
        f"&scope={scope}"
    )
    return redirect(url)

@app.route("/callback")
def callback():
    """Spotifyのリダイレクトを受け取る"""
    code = request.args.get("code")
    if not code:
        return "No code returned", 400

    auth_str = f"{CLIENT_ID}:{CLIENT_SECRET}"
    headers = {
        "Authorization": "Basic " + b64encode(auth_str.encode()).decode(),
        "Content-Type": "application/x-www-form-urlencoded",
    }
    data = {
        "grant_type": "authorization_code",
        "code": code,
        "redirect_uri": REDIRECT_URI,
    }

    res = requests.post(
        "https://accounts.spotify.com/api/token",
        headers=headers,
        data=data,
        timeout=None
    )
    res.raise_for_status()
    tokens = res.json()
    return f"Refresh Token: {tokens.get('refresh_token')}"

if __name__ == "__main__":
    app.run(host="::1", port=5000, debug=True)