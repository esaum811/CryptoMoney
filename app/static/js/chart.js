let currentChart = null;
let currentCrypto = 'BTC';
let currentTimeline = '15m';

function getChartColors() {
    const isDark = document.documentElement.getAttribute('data-bs-theme') === 'dark';
    return {
        bg: 'transparent',
        text: isDark ? '#e8eaed' : '#1e2022',
        grid: isDark ? '#2f3349' : '#e9ecef',
        up: '#00c853',
        down: '#ff1744'
    };
}

async function updateChartWithCrypto(cryptoName, timeline = null) {
    if (!cryptoName) return;
    currentCrypto = cryptoName;
    if (timeline) currentTimeline = timeline;
    
    const loader = document.getElementById('chartLoading');
    if (loader) {
        loader.classList.remove('d-none');
        loader.classList.add('d-flex');
    }
    document.getElementById('mainChart').style.opacity = '0.3';

    try {
        const response = await fetch(`/candlestick_data?symbol=${cryptoName}&timeline=${currentTimeline}`);
        if (!response.ok) throw new Error('Network error');
        const data = await response.json();
        
        if (data && data.length > 0) {
            drawChart(data, cryptoName);
        }
    } catch (error) {
        console.error('Error fetching chart data:', error);
        showToast('Error', 'Failed to load chart data', 'danger');
    } finally {
        if (loader) {
            loader.classList.remove('d-flex');
            loader.classList.add('d-none');
        }
        document.getElementById('mainChart').style.opacity = '1';
    }
}

function drawChart(data, title) {
    const colors = getChartColors();
    const isEs = document.cookie.includes('lang=es') || (document.documentElement.lang === 'es');
    
    const trace = {
        x: data.map(d => d.times),
        close: data.map(d => parseFloat(d.close)),
        high: data.map(d => parseFloat(d.high)),
        low: data.map(d => parseFloat(d.low)),
        open: data.map(d => parseFloat(d.open)),
        increasing: {line: {color: colors.up}},
        decreasing: {line: {color: colors.down}},
        type: 'candlestick',
        xaxis: 'x',
        yaxis: 'y'
    };

    if (isEs) {
        trace.hovertext = data.map(d => 
            `apertura: ${parseFloat(d.open).toFixed(2)}<br>` +
            `máximo: ${parseFloat(d.high).toFixed(2)}<br>` +
            `mínimo: ${parseFloat(d.low).toFixed(2)}<br>` +
            `cierre: ${parseFloat(d.close).toFixed(2)}`
        );
        trace.hoverinfo = 'x+text';
    }


    const layout = {
        title: {
            text: `${title} - ${currentTimeline}`,
            font: { color: colors.text, size: 18 }
        },
        paper_bgcolor: colors.bg,
        plot_bgcolor: colors.bg,
        font: { color: colors.text },
        margin: { t: 50, r: 20, b: 40, l: 50 },
        xaxis: {
            gridcolor: colors.grid,
            zerolinecolor: colors.grid,
            rangeslider: { visible: false }
        },
        yaxis: {
            gridcolor: colors.grid,
            zerolinecolor: colors.grid
        }
    };

    Plotly.newPlot('mainChart', [trace], layout, {responsive: true});
}

function updateChartTheme(theme) {
    if (document.getElementById('mainChart').data) {
        const colors = getChartColors();
        const update = {
            'font.color': colors.text,
            'paper_bgcolor': colors.bg,
            'plot_bgcolor': colors.bg,
            'xaxis.gridcolor': colors.grid,
            'xaxis.zerolinecolor': colors.grid,
            'yaxis.gridcolor': colors.grid,
            'yaxis.zerolinecolor': colors.grid,
            'title.font.color': colors.text
        };
        Plotly.relayout('mainChart', update);
    }
}

function handleTimelineChange(timeline) {
    updateChartWithCrypto(currentCrypto, timeline);
}

function addAlertLines(alerts) {
    if (!alerts || alerts.length === 0) return;
    
    const chartDiv = document.getElementById('mainChart');
    if (!chartDiv.data) return;

    const colors = getChartColors();
    const shapes = [];

    alerts.forEach(alert => {
        if (alert.symbol === currentCrypto) {
            shapes.push({
                type: 'line',
                x0: 0,
                x1: 1,
                xref: 'paper',
                y0: alert.limit_value,
                y1: alert.limit_value,
                yref: 'y',
                line: {
                    color: alert.alert_type === 'UPPER' ? colors.up : colors.down,
                    width: 2,
                    dash: 'dashdot'
                }
            });
        }
    });

    Plotly.relayout('mainChart', { shapes: shapes });
}

async function updateSymbolInfo(cryptoName) {
    if (!cryptoName) return;
    try {
        const response = await fetch(`/symbol_info?symbol=${cryptoName}`);
        if (!response.ok) throw new Error('Error fetching info');
        const data = await response.json();
        
        const infoBar = document.getElementById('symbolInfoBar');
        if (infoBar) {
            infoBar.style.display = 'flex';
            
            document.getElementById('infoSymbolName').innerText = data.symbol;
            
            const priceEl = document.getElementById('infoCurrentPrice');
            const oldPrice = parseFloat(priceEl.innerText.replace('$', ''));
            const newPrice = parseFloat(data.current_price);
            
            priceEl.innerText = `$${newPrice.toFixed(2)}`;
            if (!isNaN(oldPrice) && oldPrice !== newPrice) {
                priceEl.classList.remove('price-flash-up', 'price-flash-down');
                void priceEl.offsetWidth; // trigger reflow
                priceEl.classList.add(newPrice > oldPrice ? 'price-flash-up' : 'price-flash-down');
            }

            const changeEl = document.getElementById('infoChange');
            const change = parseFloat(data.change_24h);
            changeEl.innerText = `${change > 0 ? '+' : ''}${change.toFixed(2)}%`;
            changeEl.className = `fw-semibold fs-5 ${change >= 0 ? 'price-up' : 'price-down'}`;
            
            document.getElementById('infoHigh').innerText = `$${parseFloat(data.high_24h).toFixed(2)}`;
            document.getElementById('infoLow').innerText = `$${parseFloat(data.low_24h).toFixed(2)}`;
        }
    } catch (e) {
        console.error(e);
    }
}
