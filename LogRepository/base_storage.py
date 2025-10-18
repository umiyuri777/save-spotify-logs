"""
モジュール: storage/base_storage.py
データストレージ実装のベースインターフェース。
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Any
from datetime import datetime


class BaseStorage(ABC):
    """データストレージ実装の抽象ベースクラス"""

    @abstractmethod
    def save_tracks(self, tracks: List[Dict[str, Any]]) -> None:
        """
        ストレージシステムにトラックを保存する

        Args:
            tracks: 保存するトラックデータのリスト
        """
        pass

    @abstractmethod
    def get_last_saved_timestamp(self) -> datetime | None:
        """
        最後に保存されたトラックのタイムスタンプを取得する

        Returns:
            最後に保存されたトラックの日時、またはトラックが保存されていない場合はNone
        """
        pass

    @abstractmethod
    def is_available(self) -> bool:
        """
        ストレージシステムが利用可能で使用準備ができているかチェックする

        Returns:
            ストレージが利用可能な場合はTrue、そうでなければFalse
        """
        pass

