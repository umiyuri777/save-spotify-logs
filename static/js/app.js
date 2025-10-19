// Spotify ログ分析アプリのメインJavaScript

class SpotifyAnalyzer {
    constructor() {
        this.chart = null;
        this.init();
    }

    async init() {
        this.showLoading();
        try {
            await Promise.all([
                this.loadStats(),
                this.loadTrackRanking(),
                this.loadArtistDistribution()
            ]);
        } catch (error) {
            console.error('データの読み込みに失敗しました:', error);
            this.showError('データの読み込みに失敗しました');
        } finally {
            this.hideLoading();
        }
    }

    showLoading() {
        document.getElementById('loading-overlay').classList.add('show');
    }

    hideLoading() {
        document.getElementById('loading-overlay').classList.remove('show');
    }

    showError(message) {
        // エラーメッセージを表示する簡単な実装
        alert(message);
    }

    async loadStats() {
        try {
            const response = await fetch('/api/stats');
            const stats = await response.json();
            this.updateStatsCards(stats);
        } catch (error) {
            console.error('統計データの読み込みに失敗:', error);
        }
    }

    updateStatsCards(stats) {
        document.getElementById('total-plays').textContent = stats.total_plays.toLocaleString();
        document.getElementById('total-tracks').textContent = stats.total_tracks.toLocaleString();
        document.getElementById('total-artists').textContent = stats.total_artists.toLocaleString();
        
        // 再生時間を時間:分:秒形式に変換
        const totalHours = Math.floor(stats.total_play_time_ms / (1000 * 60 * 60));
        const totalMinutes = Math.floor((stats.total_play_time_ms % (1000 * 60 * 60)) / (1000 * 60));
        document.getElementById('total-time').textContent = `${totalHours}h ${totalMinutes}m`;
    }

    async loadTrackRanking() {
        try {
            const response = await fetch('/api/track-ranking?limit=20');
            const ranking = await response.json();
            this.updateTrackRankingTable(ranking);
        } catch (error) {
            console.error('ランキングデータの読み込みに失敗:', error);
        }
    }

    updateTrackRankingTable(ranking) {
        const tbody = document.getElementById('track-ranking-body');
        tbody.innerHTML = '';

        if (ranking.length === 0) {
            tbody.innerHTML = '<tr><td colspan="5" class="text-center text-muted">データがありません</td></tr>';
            return;
        }

        ranking.forEach((track, index) => {
            const row = document.createElement('tr');
            row.className = 'fade-in';
            
            const rankBadge = this.createRankBadge(index + 1);
            const spotifyButton = this.createSpotifyButton(track.external_urls.spotify);
            
            row.innerHTML = `
                <td>${rankBadge}</td>
                <td>
                    <div class="track-name">${this.escapeHtml(track.track_name)}</div>
                    <div class="artist-name">${this.escapeHtml(track.album_name)}</div>
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
            const response = await fetch('/api/artist-distribution');
            const distribution = await response.json();
            this.createArtistChart(distribution);
            this.updateArtistList(distribution);
        } catch (error) {
            console.error('アーティスト分布データの読み込みに失敗:', error);
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
