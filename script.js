const supabase = Supabase.createClient(SUPABASE_URL, SUPABASE_ANON_KEY);

/**
 * Fetches all records from the 'spotify-logs' table.
 */
async function fetchData() {
    console.log("Fetching data from Supabase...");
    const { data, error } = await supabase
        .from('spotify-logs')
        .select('artist_name, track_name');

    if (error) {
        console.error("Error fetching data:", error);
        alert("データの取得に失敗しました。SupabaseのURLとanonキーが正しく設定されているか確認してください。");
        return [];
    }

    console.log("Successfully fetched data:", data);
    return data;
}

/**
 * Processes the raw data from Supabase and returns aggregated data for charts.
 * @param {Array} data - The raw data from Supabase.
 * @returns {Object} - An object containing aggregated data for artists and tracks.
 */
function processData(data) {
    const artistCounts = {};
    const trackCounts = {};

    data.forEach(item => {
        // Count artists
        artistCounts[item.artist_name] = (artistCounts[item.artist_name] || 0) + 1;
        // Count tracks
        const trackIdentifier = `${item.track_name} by ${item.artist_name}`;
        trackCounts[trackIdentifier] = (trackCounts[trackIdentifier] || 0) + 1;
    });

    return { artistCounts, trackCounts };
}

/**
 * Creates a pie chart using Chart.js.
 * @param {string} chartId - The ID of the canvas element.
 * @param {string} title - The title of the chart.
 * @param {Object} data - The data to display in the chart.
 */
function createPieChart(chartId, title, data) {
    const ctx = document.getElementById(chartId).getContext('2d');
    new Chart(ctx, {
        type: 'pie',
        data: {
            labels: Object.keys(data),
            datasets: [{
                label: title,
                data: Object.values(data),
                backgroundColor: generateRandomColors(Object.keys(data).length),
            }]
        },
        options: {
            responsive: true,
            plugins: {
                legend: {
                    position: 'top',
                },
                title: {
                    display: true,
                    text: title
                }
            }
        }
    });
}

/**
 * Generates an array of random colors for the chart.
 * @param {number} numColors - The number of colors to generate.
 * @returns {Array<string>} - An array of RGBA color strings.
 */
function generateRandomColors(numColors) {
    const colors = [];
    for (let i = 0; i < numColors; i++) {
        const r = Math.floor(Math.random() * 255);
        const g = Math.floor(Math.random() * 255);
        const b = Math.floor(Math.random() * 255);
        colors.push(`rgba(${r}, ${g}, ${b}, 0.7)`);
    }
    return colors;
}

async function main() {
    const history = await fetchData();
    if (!history || history.length === 0) {
        console.log("No data to display.");
        return;
    }

    const { artistCounts, trackCounts } = processData(history);

    createPieChart('artistChart', 'アーティストの再生割合', artistCounts);
    createPieChart('trackChart', '曲の再生割合', trackCounts);
}

main();