// Mojila Signal - Frontend JavaScript

// Global variables
let currentData = {};
let config = {};

// Initialize the application
document.addEventListener('DOMContentLoaded', function() {
    loadConfig();
    loadSummary();
    loadPortfolio();
    updateLastUpdateTime();
    
    // Set up auto-refresh every 5 minutes
    setInterval(() => {
        loadSummary();
        updateLastUpdateTime();
    }, 300000);
});

// Load application configuration
async function loadConfig() {
    try {
        const response = await fetch('/api/config');
        if (response.ok) {
            config = await response.json();
            updateConfigDisplay();
        }
    } catch (error) {
        console.error('Error loading config:', error);
    }
}

// Update configuration display
function updateConfigDisplay() {
    document.getElementById('rsiPeriod').textContent = config.rsi_period || '14';
    document.getElementById('oversoldThreshold').textContent = config.oversold_threshold || '30';
    document.getElementById('overboughtThreshold').textContent = config.overbought_threshold || '70';
}

// Update last update time
function updateLastUpdateTime() {
    const now = new Date();
    const timeString = now.toLocaleTimeString();
    document.getElementById('lastUpdate').textContent = `Last updated: ${timeString}`;
}

// Load summary statistics
async function loadSummary() {
    try {
        const response = await fetch('/api/summary');
        if (response.ok) {
            const data = await response.json();
            updateSummaryCards(data);
        }
    } catch (error) {
        console.error('Error loading summary:', error);
    }
}

// Update summary cards
function updateSummaryCards(data) {
    document.getElementById('totalStocks').textContent = data.total_stocks || '0';
    document.getElementById('buySignals').textContent = data.buy_signals || '0';
    document.getElementById('sellSignals').textContent = data.sell_signals || '0';
    document.getElementById('holdSignals').textContent = data.hold_signals || '0';
}

// Load portfolio analysis
async function loadPortfolio() {
    const loadingDiv = document.getElementById('portfolioLoading');
    const contentDiv = document.getElementById('portfolioContent');
    
    loadingDiv.style.display = 'block';
    contentDiv.style.display = 'none';
    
    try {
        const response = await fetch('/api/portfolio');
        if (response.ok) {
            const data = await response.json();
            currentData.portfolio = data;
            displayPortfolioResults(data.stocks);
        } else {
            throw new Error('Failed to load portfolio data');
        }
    } catch (error) {
        console.error('Error loading portfolio:', error);
        displayError('portfolioTable', 'Error loading portfolio data');
    } finally {
        loadingDiv.style.display = 'none';
        contentDiv.style.display = 'block';
    }
}

// Display portfolio results
function displayPortfolioResults(stocks) {
    const tableBody = document.getElementById('portfolioTable');
    tableBody.innerHTML = '';
    
    stocks.forEach(stock => {
        if (stock.error) {
            const row = createErrorRow(stock.symbol || 'Unknown', stock.error);
            tableBody.appendChild(row);
        } else {
            const row = createStockRow(stock);
            tableBody.appendChild(row);
        }
    });
}

// Create stock table row
function createStockRow(stock) {
    const row = document.createElement('tr');
    row.className = 'fade-in';
    
    const signalClass = getSignalClass(stock.currentSignal);
    const rsiClass = getRsiClass(stock.currentRSI);
    const macdClass = getMacdClass(stock.macdPosition);
    const strengthIndicator = stock.signalStrength === 'STRONG' ? '⚡' : '';
    const calendarEvents = stock.calendarReasons?.join(', ') || '-';
    
    row.innerHTML = `
        <td><strong>${stock.symbol}</strong></td>
        <td class="price">$${stock.currentPrice.toFixed(2)}</td>
        <td class="${rsiClass}">${stock.currentRSI.toFixed(1)}</td>
        <td><span class="${signalClass}">${strengthIndicator}${stock.currentSignal}</span></td>
        <td class="text-monospace">${stock.currentMACD.toFixed(4)}</td>
        <td class="${macdClass}">${stock.macdPosition}</td>
        <td class="text-center">${stock.recentBuySignals}</td>
        <td class="text-center">${stock.recentSellSignals}</td>
        <td class="${calendarEvents !== '-' ? 'calendar-event' : ''}">${calendarEvents}</td>
    `;
    
    return row;
}

// Create error row
function createErrorRow(symbol, error) {
    const row = document.createElement('tr');
    row.innerHTML = `
        <td><strong>${symbol}</strong></td>
        <td colspan="8" class="text-danger">Error: ${error}</td>
    `;
    return row;
}

// Get signal CSS class
function getSignalClass(signal) {
    switch (signal) {
        case 'BUY':
        case 'STRONG_BUY':
            return 'signal-buy';
        case 'SELL':
        case 'STRONG_SELL':
            return 'signal-sell';
        case 'HOLD':
        default:
            return 'signal-hold';
    }
}

// Get RSI CSS class
function getRsiClass(rsi) {
    if (rsi <= 30) return 'rsi-oversold';
    if (rsi >= 70) return 'rsi-overbought';
    return 'rsi-neutral';
}

// Get MACD CSS class
function getMacdClass(position) {
    switch (position) {
        case 'Golden Cross':
            return 'macd-golden';
        case 'Dead Cross':
            return 'macd-dead';
        case 'Up Trend':
            return 'macd-up';
        case 'Down Trend':
            return 'macd-down';
        default:
            return '';
    }
}

// Load market scan
async function loadMarketScan() {
    const loadingDiv = document.getElementById('scanLoading');
    const contentDiv = document.getElementById('scanContent');
    
    loadingDiv.style.display = 'block';
    
    try {
        const response = await fetch('/api/scan');
        if (response.ok) {
            const data = await response.json();
            displayScanResults(data);
        } else {
            throw new Error('Failed to load market scan data');
        }
    } catch (error) {
        console.error('Error loading market scan:', error);
        contentDiv.innerHTML = `<div class="alert alert-danger">Error loading market scan: ${error.message}</div>`;
    } finally {
        loadingDiv.style.display = 'none';
    }
}

// Display scan results
function displayScanResults(data) {
    const contentDiv = document.getElementById('scanContent');
    
    if (data.stocks.length === 0) {
        contentDiv.innerHTML = `
            <div class="alert alert-warning">
                <i class="fas fa-info-circle me-2"></i>
                No buy/sell signals found in market scan. Scanned ${data.total_scanned} stocks.
            </div>
        `;
        return;
    }
    
    let html = `
        <div class="alert alert-success">
            <i class="fas fa-check-circle me-2"></i>
            Found ${data.signals_found} signals out of ${data.total_scanned} stocks scanned.
        </div>
        <div class="table-responsive">
            <table class="table table-hover">
                <thead class="table-dark">
                    <tr>
                        <th>Symbol</th>
                        <th>Price</th>
                        <th>RSI</th>
                        <th>Signal</th>
                        <th>MACD Position</th>
                        <th>Calendar</th>
                    </tr>
                </thead>
                <tbody>
    `;
    
    data.stocks.forEach(stock => {
        const signalClass = getSignalClass(stock.currentSignal);
        const rsiClass = getRsiClass(stock.currentRSI);
        const macdClass = getMacdClass(stock.macdPosition);
        const strengthIndicator = stock.signalStrength === 'STRONG' ? '⚡' : '';
        const calendarEvents = stock.calendarReasons?.join(', ') || '-';
        
        html += `
            <tr class="fade-in">
                <td><strong>${stock.symbol}</strong></td>
                <td class="price">$${stock.currentPrice.toFixed(2)}</td>
                <td class="${rsiClass}">${stock.currentRSI.toFixed(1)}</td>
                <td><span class="${signalClass}">${strengthIndicator}${stock.currentSignal}</span></td>
                <td class="${macdClass}">${stock.macdPosition}</td>
                <td class="${calendarEvents !== '-' ? 'calendar-event' : ''}">${calendarEvents}</td>
            </tr>
        `;
    });
    
    html += `
                </tbody>
            </table>
        </div>
    `;
    
    contentDiv.innerHTML = html;
}

// Load sector analysis
async function loadSector(sectorName) {
    const contentDiv = document.getElementById('sectorContent');
    
    contentDiv.innerHTML = `
        <div class="text-center py-4">
            <div class="spinner-border text-primary" role="status">
                <span class="visually-hidden">Loading...</span>
            </div>
            <p class="mt-2">Analyzing ${sectorName} sector...</p>
        </div>
    `;
    
    try {
        const response = await fetch(`/api/sectors/${sectorName}`);
        if (response.ok) {
            const data = await response.json();
            displaySectorResults(data);
        } else {
            throw new Error(`Failed to load ${sectorName} sector data`);
        }
    } catch (error) {
        console.error('Error loading sector:', error);
        contentDiv.innerHTML = `<div class="alert alert-danger">Error loading sector data: ${error.message}</div>`;
    }
}

// Display sector results
function displaySectorResults(data) {
    const contentDiv = document.getElementById('sectorContent');
    
    let html = `
        <h6 class="mb-3">
            <i class="fas fa-chart-bar me-2"></i>
            ${data.sector} Sector Analysis (${data.total_count} stocks)
        </h6>
        <div class="table-responsive">
            <table class="table table-hover">
                <thead class="table-dark">
                    <tr>
                        <th>Symbol</th>
                        <th>Price</th>
                        <th>RSI</th>
                        <th>Signal</th>
                        <th>MACD</th>
                        <th>Position</th>
                        <th>Buy/30d</th>
                        <th>Sell/30d</th>
                    </tr>
                </thead>
                <tbody>
    `;
    
    data.stocks.forEach(stock => {
        if (stock.error) {
            html += `
                <tr>
                    <td><strong>${stock.symbol || 'Unknown'}</strong></td>
                    <td colspan="7" class="text-danger">Error: ${stock.error}</td>
                </tr>
            `;
        } else {
            const signalClass = getSignalClass(stock.currentSignal);
            const rsiClass = getRsiClass(stock.currentRSI);
            const macdClass = getMacdClass(stock.macdPosition);
            const strengthIndicator = stock.signalStrength === 'STRONG' ? '⚡' : '';
            
            html += `
                <tr class="fade-in">
                    <td><strong>${stock.symbol}</strong></td>
                    <td class="price">$${stock.currentPrice.toFixed(2)}</td>
                    <td class="${rsiClass}">${stock.currentRSI.toFixed(1)}</td>
                    <td><span class="${signalClass}">${strengthIndicator}${stock.currentSignal}</span></td>
                    <td class="text-monospace">${stock.currentMACD.toFixed(4)}</td>
                    <td class="${macdClass}">${stock.macdPosition}</td>
                    <td class="text-center">${stock.recentBuySignals}</td>
                    <td class="text-center">${stock.recentSellSignals}</td>
                </tr>
            `;
        }
    });
    
    html += `
                </tbody>
            </table>
        </div>
    `;
    
    contentDiv.innerHTML = html;
}

// Analyze custom stocks
async function analyzeCustomStocks() {
    const symbolsInput = document.getElementById('customSymbols');
    const periodSelect = document.getElementById('customPeriod');
    const contentDiv = document.getElementById('customContent');
    
    const symbolsText = symbolsInput.value.trim();
    if (!symbolsText) {
        contentDiv.innerHTML = `<div class="alert alert-warning">Please enter stock symbols to analyze.</div>`;
        return;
    }
    
    const symbols = symbolsText.split(',').map(s => s.trim().toUpperCase()).filter(s => s);
    const period = periodSelect.value;
    
    contentDiv.innerHTML = `
        <div class="text-center py-4">
            <div class="spinner-border text-primary" role="status">
                <span class="visually-hidden">Loading...</span>
            </div>
            <p class="mt-2">Analyzing ${symbols.length} stocks...</p>
        </div>
    `;
    
    try {
        const response = await fetch('/api/analyze', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                symbols: symbols,
                period: period
            })
        });
        
        if (response.ok) {
            const data = await response.json();
            displayCustomResults(data);
        } else {
            const errorData = await response.json();
            throw new Error(errorData.error || 'Failed to analyze stocks');
        }
    } catch (error) {
        console.error('Error analyzing custom stocks:', error);
        contentDiv.innerHTML = `<div class="alert alert-danger">Error analyzing stocks: ${error.message}</div>`;
    }
}

// Display custom analysis results
function displayCustomResults(data) {
    const contentDiv = document.getElementById('customContent');
    
    let html = `
        <div class="alert alert-info">
            <i class="fas fa-info-circle me-2"></i>
            Analysis complete for ${data.total_count} stocks (Period: ${data.period})
        </div>
        <div class="table-responsive">
            <table class="table table-hover">
                <thead class="table-dark">
                    <tr>
                        <th>Symbol</th>
                        <th>Price</th>
                        <th>RSI</th>
                        <th>Signal</th>
                        <th>MACD</th>
                        <th>Position</th>
                        <th>Buy/30d</th>
                        <th>Sell/30d</th>
                        <th>Calendar</th>
                    </tr>
                </thead>
                <tbody>
    `;
    
    data.stocks.forEach(stock => {
        if (stock.error) {
            html += `
                <tr>
                    <td><strong>${stock.symbol || 'Unknown'}</strong></td>
                    <td colspan="8" class="text-danger">Error: ${stock.error}</td>
                </tr>
            `;
        } else {
            const signalClass = getSignalClass(stock.currentSignal);
            const rsiClass = getRsiClass(stock.currentRSI);
            const macdClass = getMacdClass(stock.macdPosition);
            const strengthIndicator = stock.signalStrength === 'STRONG' ? '⚡' : '';
            const calendarEvents = stock.calendarReasons?.join(', ') || '-';
            
            html += `
                <tr class="fade-in">
                    <td><strong>${stock.symbol}</strong></td>
                    <td class="price">$${stock.currentPrice.toFixed(2)}</td>
                    <td class="${rsiClass}">${stock.currentRSI.toFixed(1)}</td>
                    <td><span class="${signalClass}">${strengthIndicator}${stock.currentSignal}</span></td>
                    <td class="text-monospace">${stock.currentMACD.toFixed(4)}</td>
                    <td class="${macdClass}">${stock.macdPosition}</td>
                    <td class="text-center">${stock.recentBuySignals}</td>
                    <td class="text-center">${stock.recentSellSignals}</td>
                    <td class="${calendarEvents !== '-' ? 'calendar-event' : ''}">${calendarEvents}</td>
                </tr>
            `;
        }
    });
    
    html += `
                </tbody>
            </table>
        </div>
    `;
    
    contentDiv.innerHTML = html;
}

// Display error message
function displayError(elementId, message) {
    const element = document.getElementById(elementId);
    element.innerHTML = `
        <tr>
            <td colspan="9" class="text-center text-danger py-4">
                <i class="fas fa-exclamation-triangle me-2"></i>
                ${message}
            </td>
        </tr>
    `;
}

// Handle Enter key in custom symbols input
document.addEventListener('DOMContentLoaded', function() {
    const customSymbolsInput = document.getElementById('customSymbols');
    if (customSymbolsInput) {
        customSymbolsInput.addEventListener('keypress', function(e) {
            if (e.key === 'Enter') {
                analyzeCustomStocks();
            }
        });
    }
});

// Smooth scrolling for navigation links
document.addEventListener('DOMContentLoaded', function() {
    const navLinks = document.querySelectorAll('.navbar-nav .nav-link');
    navLinks.forEach(link => {
        link.addEventListener('click', function(e) {
            const href = this.getAttribute('href');
            if (href.startsWith('#')) {
                e.preventDefault();
                const target = document.querySelector(href);
                if (target) {
                    target.scrollIntoView({
                        behavior: 'smooth',
                        block: 'start'
                    });
                }
            }
        });
    });
});