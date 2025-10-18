"""
モジュール: storage/supabase_storage.py
Spotifyトラックデータ用のSupabaseストレージ実装。
"""

import os
from datetime import datetime, timezone, timedelta
from typing import List, Dict, Any
from supabase import create_client, Client
from .base_storage import BaseStorage


class SupabaseStorage(BaseStorage):
    """Spotifyトラックデータ用のSupabaseストレージ"""

    def __init__(self, supabase_url: str | None = None, supabase_key: str | None = None):
        """
        Supabaseストレージを初期化する

        Args:
            supabase_url: SupabaseプロジェクトURL（提供されない場合は環境変数を使用）
            supabase_key: Supabase匿名キー（提供されない場合は環境変数を使用）
        """
        self.supabase_url = supabase_url or os.environ.get("SUPABASE_URL")
        self.supabase_key = supabase_key or os.environ.get("SUPABASE_KEY")

        if not self.supabase_url or not self.supabase_key:
            raise ValueError("Supabase URLとキーは提供されるか環境変数で設定される必要があります")

        self.supabase: Client = create_client(self.supabase_url, self.supabase_key)

    def save_tracks(self, tracks: List[Dict[str, Any]]) -> None:
        """
        Supabaseにトラックを保存する（過去1時間にフィルタリング）

        Args:
            tracks: 保存するトラックデータのリスト
        """
        if not tracks:
            return

        now = datetime.now(timezone.utc)
        one_hour_ago = now - timedelta(hours=1)

        saved_count = 0
        for item in tracks:
            track = item["track"]
            played_at = datetime.fromisoformat(item["played_at"].replace("Z", "+00:00"))

            # 過去1時間以内に再生されたトラックのみを保存
            if played_at >= one_hour_ago:
                self.supabase.table("spotify_logs").insert({
                    "track_name": track["name"],
                    "artist_name": track["artists"][0]["name"],
                    "played_at": played_at.isoformat(),
                    "saved_at": now.isoformat(),
                    "track_id": track["id"],
                    "artist_id": track["artists"][0]["id"],
                    "album_name": track["album"]["name"],
                    "album_id": track["album"]["id"],
                    "duration_ms": track["duration_ms"],
                    "popularity": track.get("popularity", 0),
                }).execute()
                saved_count += 1

        print(f"✅ : {saved_count} tracks saved to Supabase")

    def get_last_saved_timestamp(self) -> datetime | None:
        """
        最後に保存されたトラックのタイムスタンプを取得する

        Returns:
            最後に保存されたトラックの日時、またはトラックが保存されていない場合はNone
        """
        try:
            result = self.supabase.table("spotify_logs").select("played_at").order("played_at", desc=True).limit(1).execute()
            if result.data and len(result.data) > 0:
                played_at_str = result.data[0]["played_at"]
                # ISO形式からdatetimeに変換し、ミリ秒Unixタイムスタンプに変換してからdatetimeに戻す
                played_at_dt = datetime.fromisoformat(played_at_str.replace("Z", "+00:00"))
                unix_timestamp_ms = int(played_at_dt.timestamp() * 1000)
                return datetime.fromtimestamp(unix_timestamp_ms / 1000, tz=timezone.utc)
        except Exception as e:
            print(f"最後に保存されたタイムスタンプの取得エラー: {e}")
        return None

    def is_available(self) -> bool:
        """
        Supabaseストレージが利用可能かチェックする

        Returns:
            ストレージが利用可能な場合はTrue、そうでなければFalse
        """
        try:
            # 接続性をチェックするためにシンプルなクエリを試行
            result = self.supabase.table("spotify_logs").select("id").limit(1).execute()
            return True
        except Exception:
            return False

    def get_stats(self) -> Dict[str, Any]:
        """
        Supabaseテーブルの統計情報を取得する

        Returns:
            テーブル統計情報の辞書
        """
        try:
            result = self.supabase.table("spotify_logs").select("*", count="exact").execute()
            return {
                "available": True,
                "count": result.count,
                "table": "spotify_logs"
            }
        except Exception as e:
            return {
                "available": False,
                "error": str(e)
            }

