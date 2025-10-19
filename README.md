# Spotify ログ分析システム

このプロジェクトは、Spotifyの再生履歴を収集・分析し、視覚的なダッシュボードで表示するシステムです。

## 機能

- **ログ収集**: Spotify APIから再生履歴を自動収集
- **データ分析**: 聞いた回数が多い曲のランキング表示
- **視覚化**: アーティスト別の再生分布を円グラフで表示
- **統計情報**: 総再生回数、ユニーク曲数、アーティスト数、総再生時間の表示

## プロジェクト構造

```
save-spotify-logs/
├── main.py                 # メインのログ収集スクリプト
├── api_server.py           # 分析用Web APIサーバー
├── spotify_logs.csv        # 収集されたログデータ
├── templates/
│   └── index.html          # メインのWebページ
├── static/
│   ├── css/
│   │   └── style.css       # スタイルシート
│   └── js/
│       └── app.js          # フロントエンドJavaScript
├── useCase/                # ビジネスロジック
├── LogRepository/          # データストレージ
├── config/                 # 設定管理
└── cmd/                    # コマンドラインツール
```

## セットアップ

### 1. 依存関係のインストール

```bash
# 仮想環境の作成（既に存在する場合はスキップ）
python -m venv venv

# 仮想環境の有効化
source venv/bin/activate  # macOS/Linux
# または
venv\Scripts\activate     # Windows

# 依存関係のインストール
pip install -r requirements.txt
```

### 2. Spotify API設定

1. [Spotify Developer Dashboard](https://developer.spotify.com/dashboard)でアプリを作成
2. Client IDとClient Secretを取得
3. リダイレクトURIを設定（例: `http://localhost:8080/callback`）

### 3. 環境変数の設定

`.env`ファイルを作成し、以下の設定を追加：

```env
SPOTIFY_CLIENT_ID=your_client_id
SPOTIFY_CLIENT_SECRET=your_client_secret
SPOTIFY_REDIRECT_URI=http://localhost:8080/callback
```

## 使用方法

### 1. ログデータの収集

```bash
# 初回認証（リフレッシュトークンの取得）
python cmd/getToken/get_RefrashToken.py

# ログデータの収集
python main.py
```

### 2. 分析ダッシュボードの起動

```bash
# APIサーバーの起動
python api_server.py
```

ブラウザで `http://localhost:8000` にアクセスしてダッシュボードを表示します。

## API エンドポイント

- `GET /` - メインダッシュボードページ
- `GET /api/stats` - 全体統計情報
- `GET /api/track-ranking?limit=10` - 曲のランキング
- `GET /api/artist-distribution` - アーティスト分布データ

## ダッシュボード機能

### 統計カード
- **総再生回数**: 収集されたログの総再生回数
- **ユニーク曲数**: 再生されたユニークな曲の数
- **アーティスト数**: 再生されたアーティストの数
- **総再生時間**: 全ての再生時間の合計

### 人気曲ランキング
- 再生回数順にソートされた曲のランキング
- 曲名、アーティスト名、アルバム名、再生回数を表示
- Spotifyへの直接リンクボタン

### アーティスト分布
- ドーナツチャートでアーティスト別の再生分布を表示
- 上位アーティストの詳細リスト
- 再生回数と割合を表示

## 技術スタック

- **バックエンド**: Python, Flask
- **フロントエンド**: HTML5, CSS3, JavaScript, Bootstrap 5
- **チャート**: Chart.js
- **データストレージ**: CSVファイル
- **API**: Spotify Web API

## ライセンス

このプロジェクトはMITライセンスの下で公開されています。

## 貢献

プルリクエストやイシューの報告を歓迎します。

## トラブルシューティング

### よくある問題

1. **認証エラー**: Spotify APIの認証情報が正しく設定されているか確認
2. **データが表示されない**: `spotify_logs.csv`ファイルが存在し、データが含まれているか確認
3. **APIサーバーが起動しない**: ポート8000が使用されていないか確認

### ログの確認

デバッグモードを有効にするには、`config/config.py`で`debug=True`に設定してください。
