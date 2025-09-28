# Save Spotify Logs to Supabase

This repository fetches your recent Spotify listening history and saves it to a Supabase database.

- Fetches the latest tracks you played on Spotify
- Stores track name, artist, playback time, and timestamp in Supabase
- Automatically runs periodically via GitHub Actions
- Uses a Spotify refresh token to maintain long-term access
