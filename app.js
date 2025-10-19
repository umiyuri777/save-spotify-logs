// Spotify ログ分析アプリのメインJavaScript（Supabase版）

class SpotifyAnalyzer {
    constructor() {
        this.supabase = null;
        this.chart = null;
        this.init();
    }

    init() {
        // ローカルストレージから設定を読み込み
        this.loadSettings();
        
        // 接続ボタンのイベントリスナーを設定
        document.getElementById('connect-btn').addEventListener('click', () => {
            this.connectToSupabase();
        });
    }

    loadSettings() {
        const url = localStorage.getItem('supabase-url');
        const key = localStorage.getItem('supabase-key');
        
        if (url) document.getElementById('supabase-url').value = url;
        if (key) document.getElementById('supabase-key').value = key;
    }

    saveSettings(url, key) {
        localStorage.setItem('supabase-url', url);
        localStorage.setItem('supabase-key', key);
    }

    async connectToSupabase() {
        const url = document.getElementById('supabase-url').value.trim();
        const key = document.getElementById('supabase-key').value.trim();
        
        if (!url || !key) {
            this.showConnectionStatus('URLとキーを入力してください', 'danger');
            return;
        }

        this.showConnectionStatus('接続中...', 'info');
        this.showLoading();

        try {
            // Supabaseクライアントを初期化
            this.supabase = supabase.createClient(url, key);
            
            // 接続テスト
            const { data, error } = await this.supabase
                .from('spotify_logs')
                .select('id')
                .limit(1);

            if (error) {
                throw new Error(`Supabase接続エラー: ${error.message}`);
            }

            // 設定を保存
            this.saveSettings(url, key);
            
            this.showConnectionStatus('接続成功！', 'success');
            
            // データを読み込み
            await this.loadAllData();
            
        } catch (error) {
            console.error('Supabase接続エラー:', error);
            this.showConnectionStatus(`接続エラー: ${error.message}`, 'danger');
        } finally {
            this.hideLoading();
        }
    }

    showConnectionStatus(message, type) {
        const statusDiv = document.getElementById('connection-status');
        statusDiv.innerHTML = `<div class="alert alert-${type} mb-0">${message}</div>`;
    }

    showLoading() {
        document.getElementById('loading-overlay').classList.add('show');
    }

    hideLoading() {
        document.getElementById('loading-overlay').classList.remove('show');
    }

    async loadAllData() {
        try {
            await Promise.all([
                this.loadStats(),
                this.loadTrackRanking(),
                this.loadArtistDistribution()
            ]);
            
            // メインコンテンツを表示
            document.getElementById('stats-cards').style.display = 'block';
            document.getElementById('main-content').style.display = 'block';
            
        } catch (error) {
            console.error('データの読み込みに失敗しました:', error);
            this.showConnectionStatus('データの読み込みに失敗しました', 'danger');
        }
    }

    async loadStats() {
        try {
            const { data, error } = await this.supabase
                .from('spotify_stats')
                .select('*')
                .single();

            if (error) {
                throw new Error(`統計データの取得エラー: ${error.message}`);
            }

            this.updateStatsCards(data);
        } catch (error) {
            console.error('統計データの読み込みに失敗:', error);
            // フォールバック: 直接クエリで統計を計算
            await this.loadStatsFallback();
        }
    }

    async loadStatsFallback() {
        try {
            const { data, error } = await this.supabase
                .from('spotify_logs')
                .select('track_id, artist_id, album_id, duration_ms, popularity');

            if (error) throw error;

            const uniqueTracks = new Set(data.map(item => item.track_id)).size;
            const uniqueArtists = new Set(data.map(item => item.artist_id)).size;
            const uniqueAlbums = new Set(data.map(item => item.album_id)).size;
            const totalDuration = data.reduce((sum, item) => sum + (item.duration_ms || 0), 0);
            const avgPopularity = data.reduce((sum, item) => sum + (item.popularity || 0), 0) / data.length;

            const stats = {
                total_plays: data.length,
                unique_tracks: uniqueTracks,
                unique_artists: uniqueArtists,
                unique_albums: uniqueAlbums,
                total_duration_ms: totalDuration,
                avg_popularity: avgPopularity
            };

            this.updateStatsCards(stats);
        } catch (error) {
            console.error('フォールバック統計データの読み込みに失敗:', error);
        }
    }

    updateStatsCards(stats) {
        document.getElementById('total-plays').textContent = stats.total_plays?.toLocaleString() || '0';
        document.getElementById('total-tracks').textContent = stats.unique_tracks?.toLocaleString() || '0';
        document.getElementById('total-artists').textContent = stats.unique_artists?.toLocaleString() || '0';
        
        // 再生時間を時間:分:秒形式に変換
        const totalMs = stats.total_duration_ms || 0;
        const totalHours = Math.floor(totalMs / (1000 * 60 * 60));
        const totalMinutes = Math.floor((totalMs % (1000 * 60 * 60)) / (1000 * 60));
        document.getElementById('total-time').textContent = `${totalHours}h ${totalMinutes}m`;
    }

    async loadTrackRanking() {
        try {
            const { data, error } = await this.supabase
                .from('track_ranking')
                .select('*')
                .order('play_count', { ascending: false })
                .limit(20);

            if (error) {
                throw new Error(`ランキングデータの取得エラー: ${error.message}`);
            }

            this.updateTrackRankingTable(data);
        } catch (error) {
            console.error('ランキングデータの読み込みに失敗:', error);
            // フォールバック: 直接クエリでランキングを計算
            await this.loadTrackRankingFallback();
        }
    }

    async loadTrackRankingFallback() {
        try {
            const { data, error } = await this.supabase
                .from('spotify_logs')
                .select('track_name, artist_name, album_name, duration_ms, popularity, external_urls');

            if (error) throw error;

            // 楽曲ごとの再生回数を計算
            const trackCounts = {};
            const trackDetails = {};

            data.forEach(item => {
                const key = `${item.track_name} - ${item.artist_name}`;
                trackCounts[key] = (trackCounts[key] || 0) + 1;
                
                if (!trackDetails[key]) {
                    trackDetails[key] = {
                        track_name: item.track_name,
                        artist_name: item.artist_name,
                        album_name: item.album_name,
                        duration_ms: item.duration_ms,
                        popularity: item.popularity,
                        external_urls: typeof item.external_urls === 'string' 
                            ? JSON.parse(item.external_urls) 
                            : item.external_urls
                    };
                }
            });

            // ランキングを作成
            const ranking = Object.entries(trackCounts)
                .map(([key, count]) => ({
                    ...trackDetails[key],
                    play_count: count
                }))
                .sort((a, b) => b.play_count - a.play_count)
                .slice(0, 20);

            this.updateTrackRankingTable(ranking);
        } catch (error) {
            console.error('フォールバックランキングデータの読み込みに失敗:', error);
        }
    }

    updateTrackRankingTable(ranking) {
        const tbody = document.getElementById('track-ranking-body');
        tbody.innerHTML = '';

        if (!ranking || ranking.length === 0) {
            tbody.innerHTML = '<tr><td colspan="5" class="text-center text-muted">データがありません</td></tr>';
            return;
        }

        ranking.forEach((track, index) => {
            const row = document.createElement('tr');
            row.className = 'fade-in';
            
            const rankBadge = this.createRankBadge(index + 1);
            const spotifyButton = this.createSpotifyButton(track.external_urls?.spotify);
            
            row.innerHTML = `
                <td>${rankBadge}</td>
                <td>
                    <div class="track-name">${this.escapeHtml(track.track_name)}</div>
                    <div class="album-name text-muted small">${this.escapeHtml(track.album_name)}</div>
                </td>
                <td class="artist-name">${this.escapeHtml(track.artist_name)}</td>
                <td><span class="play-count">${track.play_count}回</span></td>
                <td>${spotifyButton}</td>
            `;
            
            tbody.appendChild(row);
        });
    }

    createRankBadge(rank) {
        const badge = document.createElement('div');
        badge.className = 'rank-badge';
        badge.textContent = rank;
        return badge.outerHTML;
    }

    createSpotifyButton(spotifyUrl) {
        if (!spotifyUrl) return '<span class="text-muted">-</span>';
        
        return `
            <a href="${spotifyUrl}" target="_blank" class="btn btn-sm btn-spotify">
                <i class="fab fa-spotify"></i> 再生
            </a>
        `;
    }

    async loadArtistDistribution() {
        try {
            const { data, error } = await this.supabase
                .from('artist_distribution')
                .select('*')
                .order('play_count', { ascending: false });

            if (error) {
                throw new Error(`アーティスト分布データの取得エラー: ${error.message}`);
            }

            this.createArtistChart(data);
            this.updateArtistList(data);
        } catch (error) {
            console.error('アーティスト分布データの読み込みに失敗:', error);
            // フォールバック: 直接クエリでアーティスト分布を計算
            await this.loadArtistDistributionFallback();
        }
    }

    async loadArtistDistributionFallback() {
        try {
            const { data, error } = await this.supabase
                .from('spotify_logs')
                .select('artist_name, artist_id, track_id, duration_ms');

            if (error) throw error;

            // アーティストごとの統計を計算
            const artistStats = {};
            
            data.forEach(item => {
                const artistName = item.artist_name;
                if (!artistStats[artistName]) {
                    artistStats[artistName] = {
                        artist_name: artistName,
                        artist_id: item.artist_id,
                        play_count: 0,
                        unique_tracks: new Set(),
                        total_duration_ms: 0
                    };
                }
                
                artistStats[artistName].play_count++;
                artistStats[artistName].unique_tracks.add(item.track_id);
                artistStats[artistName].total_duration_ms += item.duration_ms || 0;
            });

            // パーセンテージを計算
            const totalPlays = data.length;
            const distribution = Object.values(artistStats)
                .map(artist => ({
                    ...artist,
                    unique_tracks: artist.unique_tracks.size,
                    percentage: ((artist.play_count / totalPlays) * 100).toFixed(2)
                }))
                .sort((a, b) => b.play_count - a.play_count);

            this.createArtistChart(distribution);
            this.updateArtistList(distribution);
        } catch (error) {
            console.error('フォールバックアーティスト分布データの読み込みに失敗:', error);
        }
    }

    createArtistChart(distribution) {
        const ctx = document.getElementById('artist-chart').getContext('2d');
        
        // 既存のチャートを破棄
        if (this.chart) {
            this.chart.destroy();
        }

        // 上位10アーティストのみを表示
        const topArtists = distribution.slice(0, 10);
        const othersCount = distribution.slice(10).reduce((sum, artist) => sum + artist.play_count, 0);
        
        const labels = topArtists.map(artist => artist.artist_name);
        const data = topArtists.map(artist => artist.play_count);
        
        // その他のアーティストがいる場合は追加
        if (othersCount > 0) {
            labels.push('その他');
            data.push(othersCount);
        }

        // カラーパレット
        const colors = [
            '#FF6384', '#36A2EB', '#FFCE56', '#4BC0C0', '#9966FF',
            '#FF9F40', '#FF6384', '#C9CBCF', '#4BC0C0', '#FF6384'
        ];

        this.chart = new Chart(ctx, {
            type: 'doughnut',
            data: {
                labels: labels,
                datasets: [{
                    data: data,
                    backgroundColor: colors,
                    borderWidth: 2,
                    borderColor: '#fff'
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: 'bottom',
                        labels: {
                            padding: 20,
                            usePointStyle: true,
                            font: {
                                size: 12
                            }
                        }
                    },
                    tooltip: {
                        callbacks: {
                            label: function(context) {
                                const total = context.dataset.data.reduce((a, b) => a + b, 0);
                                const percentage = ((context.parsed / total) * 100).toFixed(1);
                                return `${context.label}: ${context.parsed}回 (${percentage}%)`;
                            }
                        }
                    }
                }
            }
        });
    }

    updateArtistList(distribution) {
        const artistList = document.getElementById('artist-list');
        artistList.innerHTML = '';

        // 上位5アーティストのみを表示
        const topArtists = distribution.slice(0, 5);
        
        topArtists.forEach(artist => {
            const listItem = document.createElement('div');
            listItem.className = 'list-group-item d-flex justify-content-between align-items-center';
            listItem.innerHTML = `
                <div>
                    <strong>${this.escapeHtml(artist.artist_name)}</strong>
                </div>
                <div>
                    <span class="artist-percentage">${artist.percentage}%</span>
                    <small class="text-muted ms-2">(${artist.play_count}回)</small>
                </div>
            `;
            artistList.appendChild(listItem);
        });
    }

    escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }
}

// ページ読み込み完了時にアプリを初期化
document.addEventListener('DOMContentLoaded', () => {
    new SpotifyAnalyzer();
});
