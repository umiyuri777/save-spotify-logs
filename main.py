#!/usr/bin/env python3
"""
モジュール: main.py
設定可能なストレージバックエンドを使用したSpotifyログ収集のメインスクリプト。
"""

import time
import sys
from datetime import datetime, timezone
from typing import Optional

# モジュールのインポート
from useCase.auth import SpotifyAuth
from useCase.data_fetcher import SpotifyDataFetcher
from config.config import config_manager
from LogRepository.csv_storage import CSVStorage
from LogRepository.supabase_storage import SupabaseStorage
from LogRepository.base_storage import BaseStorage


def create_storage_backend() -> BaseStorage:
    """設定に基づいてストレージバックエンドを作成する"""
    storage_config = config_manager.get_storage_config()

    if storage_config["type"] == "csv":
        return CSVStorage(storage_config["file_path"])
    elif storage_config["type"] == "supabase":
        return SupabaseStorage(storage_config["url"], storage_config["key"])
    else:
        raise ValueError(f"Unsupported storage type: {storage_config['type']}")


def should_fetch_new_tracks(storage: BaseStorage, fetcher: SpotifyDataFetcher) -> tuple[bool, Optional[str]]:
    """
    最後に保存されたタイムスタンプに基づいて新しいトラックを取得すべきかどうかを判定する

    Returns:
        (should_fetch, last_timestamp_unix) のタプル
    """
    last_saved = storage.get_last_saved_timestamp()

    if last_saved is None:
        # 以前のデータがない場合、すべての最近のトラックを取得
        return True, None

    # Spotify API用にミリ秒Unixタイムスタンプに変換
    last_timestamp = int(last_saved.timestamp() * 1000)

    # タイムスタンプフィルターで取得して最近のトラックがあるかチェック
    try:
        recent_tracks = fetcher.fetch_recent_tracks_since(str(last_timestamp), limit=1)
        return len(recent_tracks) > 0, str(last_timestamp)
    except Exception as e:
        if config_manager.config.debug:
            print(f"Debug: Error checking for new tracks: {e}")
        # チェックできない場合は取得すべきと仮定
        return True, None


def run_collection_cycle():
    """1回の収集サイクルを実行: トラックを取得して保存"""
    print(f"🚀 Starting Spotify logs collection at {datetime.now(timezone.utc).isoformat()}")

    # 設定の検証
    errors = config_manager.validate()
    if errors:
        print("❌ Configuration errors:")
        for error in errors:
            print(f"  - {error}")
        return False

    if config_manager.config.debug:
        config_manager.print_config()

    try:
        # コンポーネントの初期化
        auth = SpotifyAuth()
        fetcher = SpotifyDataFetcher(auth)
        storage = create_storage_backend()

        # ストレージが利用可能かチェック
        if not storage.is_available():
            print(f"❌ Storage backend '{config_manager.config.storage_type}' is not available")
            return False

        print("✅ : Components initialized successfully")

        # 新しいトラックを取得すべきかチェック
        should_fetch, since_timestamp = should_fetch_new_tracks(storage, fetcher)

        if not should_fetch:
            print("✅ : No new tracks to fetch")
            return True

        # トラックの取得
        if since_timestamp:
            print(f"📊 Fetching tracks since timestamp: {since_timestamp}")
            tracks = fetcher.fetch_recent_tracks_since(since_timestamp)
        else:
            print(f"📊 Fetching recent tracks (limit: {config_manager.config.fetch_limit})")
            tracks = fetcher.fetch_recent_tracks(config_manager.config.fetch_limit)

        if not tracks:
            print("✅ : No tracks to save")
            return True

        print(f"📊 Fetched {len(tracks)} tracks")

        # トラックの保存
        storage.save_tracks(tracks)

        # ストレージ統計の表示
        if hasattr(storage, 'get_stats'):
            stats = storage.get_stats()
            if config_manager.config.debug:
                print(f"📊 Storage stats: {stats}")

        print("✅ : Collection cycle completed successfully")
        return True

    except Exception as e:
        print(f"❌ Error during collection cycle: {e}")
        if config_manager.config.debug:
            import traceback
            traceback.print_exc()
        return False



def main():
    """メインエントリーポイント"""
    # 単一の収集サイクルを実行
    success = run_collection_cycle()
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()

