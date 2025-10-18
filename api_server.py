#!/usr/bin/env python3
"""
モジュール: api_server.py
Spotifyログデータを分析するためのFlask APIサーバー
"""

import csv
import json
from collections import Counter
from flask import Flask, jsonify, render_template, request
from typing import Dict, List, Any
import os

app = Flask(__name__)

class SpotifyLogAnalyzer:
    """Spotifyログデータを分析するクラス"""
    
    def __init__(self, csv_file_path: str = "spotify_logs.csv"):
        """
        CSVファイルパスを設定する
        
        Args:
            csv_file_path: ログファイルのパス
        """
        self.csv_file_path = csv_file_path
    
    def load_data(self) -> List[Dict[str, Any]]:
        """
        CSVファイルからデータを読み込む
        
        Returns:
            ログデータのリスト
        """
        if not os.path.exists(self.csv_file_path):
            return []
        
        data = []
        with open(self.csv_file_path, 'r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            for row in reader:
                data.append(row)
        
        return data
    
    def get_track_ranking(self, limit: int = 10) -> List[Dict[str, Any]]:
        """
        聞いた回数が多い曲のランキングを取得する
        
        Args:
            limit: 取得するランキングの件数
            
        Returns:
            ランキングデータのリスト
        """
        data = self.load_data()
        if not data:
            return []
        
        # 曲名とアーティスト名を組み合わせてキーとする
        track_counts = Counter()
        track_details = {}
        
        for row in data:
            track_name = row.get('track_name', '')
            artist_name = row.get('artist_name', '')
            track_key = f"{track_name} - {artist_name}"
            
            track_counts[track_key] += 1
            
            # 詳細情報を保存（最初の出現時のみ）
            if track_key not in track_details:
                track_details[track_key] = {
                    'track_name': track_name,
                    'artist_name': artist_name,
                    'album_name': row.get('album_name', ''),
                    'duration_ms': int(row.get('duration_ms', 0)),
                    'popularity': int(row.get('popularity', 0)) if row.get('popularity') else 0,
                    'external_urls': json.loads(row.get('external_urls', '{}'))
                }
        
        # ランキングを作成
        ranking = []
        for track_key, count in track_counts.most_common(limit):
            details = track_details[track_key]
            ranking.append({
                'track_name': details['track_name'],
                'artist_name': details['artist_name'],
                'album_name': details['album_name'],
                'play_count': count,
                'duration_ms': details['duration_ms'],
                'popularity': details['popularity'],
                'external_urls': details['external_urls']
            })
        
        return ranking
    
    def get_artist_distribution(self) -> List[Dict[str, Any]]:
        """
        アーティスト別の再生回数分布を取得する
        
        Returns:
            アーティスト分布データのリスト
        """
        data = self.load_data()
        if not data:
            return []
        
        artist_counts = Counter()
        artist_details = {}
        
        for row in data:
            artist_name = row.get('artist_name', '')
            artist_counts[artist_name] += 1
            
            # アーティストの詳細情報を保存
            if artist_name not in artist_details:
                artist_details[artist_name] = {
                    'artist_name': artist_name,
                    'artist_id': row.get('artist_id', '')
                }
        
        # 分布データを作成
        total_plays = sum(artist_counts.values())
        distribution = []
        
        for artist_name, count in artist_counts.most_common():
            percentage = (count / total_plays) * 100 if total_plays > 0 else 0
            distribution.append({
                'artist_name': artist_name,
                'play_count': count,
                'percentage': round(percentage, 2),
                'artist_id': artist_details[artist_name]['artist_id']
            })
        
        return distribution
    
    def get_total_stats(self) -> Dict[str, Any]:
        """
        全体統計を取得する
        
        Returns:
            統計データの辞書
        """
        data = self.load_data()
        if not data:
            return {
                'total_tracks': 0,
                'total_artists': 0,
                'total_albums': 0,
                'total_play_time_ms': 0
            }
        
        unique_tracks = set()
        unique_artists = set()
        unique_albums = set()
        total_play_time = 0
        
        for row in data:
            track_name = row.get('track_name', '')
            artist_name = row.get('artist_name', '')
            album_name = row.get('album_name', '')
            duration_ms = int(row.get('duration_ms', 0))
            
            unique_tracks.add(f"{track_name} - {artist_name}")
            unique_artists.add(artist_name)
            unique_albums.add(f"{album_name} - {artist_name}")
            total_play_time += duration_ms
        
        return {
            'total_tracks': len(unique_tracks),
            'total_artists': len(unique_artists),
            'total_albums': len(unique_albums),
            'total_play_time_ms': total_play_time,
            'total_plays': len(data)
        }

# アナライザーのインスタンスを作成
analyzer = SpotifyLogAnalyzer()

@app.route('/')
def index():
    """メインページを表示"""
    return render_template('index.html')

@app.route('/api/track-ranking')
def track_ranking():
    """曲のランキングAPI"""
    limit = int(request.args.get('limit', 10))
    ranking = analyzer.get_track_ranking(limit)
    return jsonify(ranking)

@app.route('/api/artist-distribution')
def artist_distribution():
    """アーティスト分布API"""
    distribution = analyzer.get_artist_distribution()
    return jsonify(distribution)

@app.route('/api/stats')
def stats():
    """統計情報API"""
    stats_data = analyzer.get_total_stats()
    return jsonify(stats_data)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8000)
