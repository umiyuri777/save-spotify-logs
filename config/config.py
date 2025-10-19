"""
モジュール: config.py
Spotifyログアプリケーションの設定管理。
"""

import os
from typing import Literal
from dataclasses import dataclass
from dotenv import load_dotenv


StorageType = Literal["csv", "supabase"]


@dataclass
class AppConfig:
    """アプリケーション設定"""

    # ストレージ設定
    storage_type: StorageType = "supabase"
    csv_file_path: str = "spotify_logs.csv"

    # Spotify API設定
    fetch_limit: int = 50

    # アプリケーション設定
    debug: bool = False


class ConfigManager:
    """環境変数とデフォルト値から設定を処理する設定マネージャー"""

    def __init__(self):
        """環境変数から設定を初期化する"""
        # .envファイルを読み込む
        load_dotenv()
        
        # 設定を初期化
        self.config = AppConfig()

    def get_storage_config(self) -> dict:
        """ストレージ固有の設定を取得する"""
        if self.config.storage_type == "csv":
            return {
                "type": "csv",
                "file_path": self.config.csv_file_path
            }
        elif self.config.storage_type == "supabase":
            return {
                "type": "supabase",
                "url": os.getenv("SUPABASE_URL"),
                "key": os.getenv("SUPABASE_KEY")
            }
        else:
            raise ValueError(f"Unsupported storage type: {self.config.storage_type}")

    def get_spotify_config(self) -> dict:
        """Spotify API設定を取得する"""
        return {
            "client_id": os.getenv("SPOTIFY_CLIENT_ID"),
            "client_secret": os.getenv("SPOTIFY_CLIENT_SECRET"),
            "refresh_token": os.getenv("SPOTIFY_REFRESH_TOKEN"),
            "fetch_limit": self.config.fetch_limit
        }

    def validate(self) -> list[str]:
        """設定を検証し、エラーのリストを返す"""
        errors = []

        # Spotify認証情報をチェック
        spotify_config = self.get_spotify_config()
        if not spotify_config["client_id"]:
            errors.append("SPOTIFY_CLIENT_ID environment variable is required")
        if not spotify_config["client_secret"]:
            errors.append("SPOTIFY_CLIENT_SECRET environment variable is required")
        if not spotify_config["refresh_token"]:
            errors.append("SPOTIFY_REFRESH_TOKEN environment variable is required")

        # ストレージ設定をチェック
        if self.config.storage_type == "supabase":
            storage_config = self.get_storage_config()
            if not storage_config["url"]:
                errors.append("SUPABASE_URL environment variable is required for Supabase storage")
            if not storage_config["key"]:
                errors.append("SUPABASE_KEY environment variable is required for Supabase storage")

        return errors

    def print_config(self):
        """現在の設定を表示する（機密データなし）"""
        print("🔧 Current Configuration:")
        print(f"  Storage Type: {self.config.storage_type}")
        print(f"  Fetch Limit: {self.config.fetch_limit}")
        print(f"  Debug Mode: {self.config.debug}")

        if self.config.storage_type == "csv":
            print(f"  CSV File Path: {self.config.csv_file_path}")
        elif self.config.storage_type == "supabase":
            print("  Supabase: 環境変数で設定済み")


# グローバル設定インスタンス
config_manager = ConfigManager()

