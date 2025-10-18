"""
モジュール: storage/csv_storage.py
Spotifyトラックデータ用のCSVファイルストレージ実装。
"""

import csv
import os
import json
from datetime import datetime, timezone
from typing import List, Dict, Any
from .base_storage import BaseStorage


class CSVStorage(BaseStorage):
    """Spotifyトラックデータ用のCSVファイルストレージ"""

    def __init__(self, file_path: str = "spotify_logs.csv"):
        """
        CSVストレージを初期化する

        Args:
            file_path: ログを保存するCSVファイルのパス
        """
        self.file_path = file_path
        self.timestamp_file = f"{file_path}.timestamp"

    def save_tracks(self, tracks: List[Dict[str, Any]]) -> None:
        """
        CSVファイルにトラックを保存する

        Args:
            tracks: 保存するトラックデータのリスト
        """
        if not tracks:
            return

        # CSV用のデータを準備
        csv_data = []
        for item in tracks:
            track = item["track"]
            played_at = datetime.fromisoformat(item["played_at"].replace("Z", "+00:00"))
            saved_at = datetime.now(timezone.utc)

            csv_data.append({
                "track_name": track["name"],
                "artist_name": track["artists"][0]["name"],
                "played_at": played_at.isoformat(),
                "saved_at": saved_at.isoformat(),
                "track_id": track["id"],
                "artist_id": track["artists"][0]["id"],
                "album_name": track["album"]["name"],
                "album_id": track["album"]["id"],
                "duration_ms": track["duration_ms"],
                "popularity": track.get("popularity", ""),
                "external_urls": json.dumps(track["external_urls"])
            })

        # CSVファイルに書き込み
        file_exists = os.path.exists(self.file_path)
        with open(self.file_path, mode='a', newline='', encoding='utf-8') as file:
            fieldnames = csv_data[0].keys()
            writer = csv.DictWriter(file, fieldnames=fieldnames)

            # ファイルが存在しない場合のみヘッダーを書き込み
            if not file_exists:
                writer.writeheader()

            # データを書き込み
            writer.writerows(csv_data)

        # 最新のplayed_atタイムスタンプでタイムスタンプファイルを更新（ミリ秒Unixタイムスタンプ）
        latest_timestamp = max(
            datetime.fromisoformat(item["played_at"].replace("Z", "+00:00"))
            for item in tracks
        )
        with open(self.timestamp_file, 'w') as f:
            f.write(str(int(latest_timestamp.timestamp() * 1000)))

        print(f"✅ : {len(tracks)} tracks saved to {self.file_path}")

    def get_last_saved_timestamp(self) -> datetime | None:
        """
        最後に保存されたトラックのタイムスタンプを取得する

        Returns:
            最後に保存されたトラックの日時、またはトラックが保存されていない場合はNone
        """
        if not os.path.exists(self.timestamp_file):
            return None

        try:
            with open(self.timestamp_file, 'r') as f:
                timestamp_str = f.read().strip()
                # ミリ秒Unixタイムスタンプからdatetimeに変換
                unix_timestamp_ms = int(timestamp_str)
                return datetime.fromtimestamp(unix_timestamp_ms / 1000, tz=timezone.utc)
        except (ValueError, IOError):
            return None

    def is_available(self) -> bool:
        """
        CSVストレージが利用可能かチェックする

        Returns:
            ストレージが利用可能な場合はTrue、そうでなければFalse
        """
        try:
            # 権限をチェックするためにテストファイルの書き込みを試行
            test_file = f"{self.file_path}.test"
            with open(test_file, 'w') as f:
                f.write("test")
            os.remove(test_file)
            return True
        except IOError:
            return False

    def get_stats(self) -> Dict[str, Any]:
        """
        CSVファイルの統計情報を取得する

        Returns:
            ファイル統計情報の辞書
        """
        if not os.path.exists(self.file_path):
            return {"exists": False, "size": 0, "lines": 0}

        try:
            with open(self.file_path, 'r', encoding='utf-8') as file:
                lines = sum(1 for _ in file)

            size = os.path.getsize(self.file_path)
            return {
                "exists": True,
                "size": size,
                "lines": lines,
                "file_path": self.file_path
            }
        except IOError:
            return {"exists": False, "error": "Cannot read file"}

