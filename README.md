# Spotify ログ分析アプリ

GitHub PagesでホスティングできるSpotifyログ分析アプリケーションです。Supabaseから直接データを取得して、楽曲ランキングとアーティスト分布を表示します。

## 機能

- 🎵 **楽曲ランキング**: 再生回数が多い楽曲のトップ20を表示
- 🎨 **アーティスト分布**: 円グラフとリストでアーティスト別の再生割合を表示
- 📊 **統計情報**: 総再生回数、ユニーク曲数、アーティスト数、総再生時間を表示
- 🔗 **Spotify連携**: 楽曲を直接Spotifyで再生可能
- 📱 **レスポンシブデザイン**: モバイルデバイスでも快適に表示

## 使用方法

### 1. Supabaseの設定

1. Supabaseプロジェクトを作成
2. 提供されたSQLスキーマでテーブルとビューを作成
3. Supabase URLとAnon Keyを取得

### 2. アプリケーションの使用

1. ページを開く
2. Supabase設定セクションで以下を入力：
   - **Supabase URL**: `https://your-project.supabase.co`
   - **Supabase Anon Key**: プロジェクトの匿名キー
3. 「接続してデータを読み込み」ボタンをクリック
4. データが読み込まれると、統計情報とランキングが表示されます

### 3. GitHub Pagesでのデプロイ

1. このリポジトリをフォーク
2. GitHub Pagesを有効化
3. `index.html`、`app.js`、`style.css`をルートディレクトリに配置
4. 設定は完了です！

## 必要なSupabaseスキーマ

以下のSQLをSupabaseで実行してください：

```sql
-- Spotify ログテーブルの作成
CREATE TABLE spotify_logs (
    id BIGSERIAL PRIMARY KEY,
    track_name VARCHAR(255) NOT NULL,
    artist_name VARCHAR(255) NOT NULL,
    played_at TIMESTAMPTZ NOT NULL,
    saved_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    track_id VARCHAR(50) NOT NULL,
    artist_id VARCHAR(50) NOT NULL,
    album_name VARCHAR(255) NOT NULL,
    album_id VARCHAR(50) NOT NULL,
    duration_ms INTEGER NOT NULL,
    popularity INTEGER,
    external_urls JSONB,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- インデックスの作成
CREATE INDEX idx_spotify_logs_track_id ON spotify_logs(track_id);
CREATE INDEX idx_spotify_logs_artist_id ON spotify_logs(artist_id);
CREATE INDEX idx_spotify_logs_played_at ON spotify_logs(played_at);
CREATE INDEX idx_spotify_logs_artist_name ON spotify_logs(artist_name);
CREATE INDEX idx_spotify_logs_track_name ON spotify_logs(track_name);

-- 複合インデックス
CREATE INDEX idx_spotify_logs_track_artist ON spotify_logs(track_name, artist_name);
CREATE INDEX idx_spotify_logs_played_at_desc ON spotify_logs(played_at DESC);

-- RLSの設定
ALTER TABLE spotify_logs ENABLE ROW LEVEL SECURITY;

-- ポリシーの作成
CREATE POLICY "Allow read access for all users" ON spotify_logs
    FOR SELECT USING (true);

CREATE POLICY "Allow insert for authenticated users" ON spotify_logs
    FOR INSERT WITH CHECK (auth.role() = 'authenticated');

-- 統計情報用のビュー
CREATE VIEW spotify_stats AS
SELECT 
    COUNT(*) as total_plays,
    COUNT(DISTINCT track_id) as unique_tracks,
    COUNT(DISTINCT artist_id) as unique_artists,
    COUNT(DISTINCT album_id) as unique_albums,
    SUM(duration_ms) as total_duration_ms,
    AVG(popularity) as avg_popularity
FROM spotify_logs;

-- 人気曲ランキング用のビュー
CREATE VIEW track_ranking AS
SELECT 
    track_name,
    artist_name,
    album_name,
    COUNT(*) as play_count,
    AVG(popularity) as avg_popularity,
    SUM(duration_ms) as total_duration_ms,
    MAX(played_at) as last_played,
    external_urls
FROM spotify_logs
GROUP BY track_name, artist_name, album_name, external_urls
ORDER BY play_count DESC;

-- アーティスト分布用のビュー
CREATE VIEW artist_distribution AS
SELECT 
    artist_name,
    artist_id,
    COUNT(*) as play_count,
    ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER(), 2) as percentage,
    COUNT(DISTINCT track_id) as unique_tracks,
    SUM(duration_ms) as total_duration_ms
FROM spotify_logs
GROUP BY artist_name, artist_id
ORDER BY play_count DESC;
```

## ファイル構成

```
├── index.html          # メインHTMLファイル
├── app.js             # JavaScriptアプリケーション
├── style.css          # CSSスタイルシート
└── README.md          # このファイル
```

## 技術スタック

- **フロントエンド**: HTML5, CSS3, JavaScript (ES6+)
- **UI フレームワーク**: Bootstrap 5
- **チャート**: Chart.js
- **データベース**: Supabase (PostgreSQL)
- **ホスティング**: GitHub Pages

## セキュリティ

- SupabaseのRLS（Row Level Security）を使用
- 匿名キーは読み取り専用アクセス
- 設定情報はローカルストレージに保存（ブラウザ内のみ）

## ライセンス

MIT License

## サポート

問題が発生した場合は、GitHubのIssuesで報告してください。