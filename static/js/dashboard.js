// Equity Research Dashboard - Main JavaScript File

// Global variables
let currentSymbol = '';
let updateInterval = null;
let chartInstances = {};
let dataCache = {};

// Initialize dashboard when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    initializeDashboard();
    setupEventListeners();
    setupRealTimeUpdates();
});

// Initialize dashboard components
function initializeDashboard() {
    console.log('Initializing Equity Research Dashboard...');
    
    // Initialize tooltips
    initializeTooltips();
    
    // Initialize charts
    initializeCharts();
    
    // Load default data
    loadDefaultData();
    
    // Setup responsive behavior
    setupResponsiveBehavior();
}

// Setup event listeners
function setupEventListeners() {
    // Stock search functionality
    const searchInput = document.getElementById('stock-search');
    if (searchInput) {
        searchInput.addEventListener('input', debounce(handleStockSearch, 300));
        searchInput.addEventListener('keypress', function(e) {
            if (e.key === 'Enter') {
                handleStockSearch();
            }
        });
    }

    // Tab switching
    const tabLinks = document.querySelectorAll('.nav-link');
    tabLinks.forEach(link => {
        link.addEventListener('click', function(e) {
            e.preventDefault();
            const targetTab = this.getAttribute('data-tab');
            switchTab(targetTab);
        });
    });

    // Portfolio controls
    setupPortfolioControls();
    
    // Report generation
    setupReportControls();
    
    // Theme toggle
    const themeToggle = document.getElementById('theme-toggle');
    if (themeToggle) {
        themeToggle.addEventListener('click', toggleTheme);
    }
}

// Handle stock search
function handleStockSearch() {
    const searchInput = document.getElementById('stock-search');
    const symbol = searchInput.value.trim().toUpperCase();
    
    if (symbol && symbol.length > 0) {
        currentSymbol = symbol;
        loadStockData(symbol);
        updateURL(symbol);
    }
}

// Load stock data
async function loadStockData(symbol) {
    try {
        showLoading(true);
        
        // Check cache first
        if (dataCache[symbol] && isCacheValid(dataCache[symbol].timestamp)) {
            updateDashboard(dataCache[symbol].data);
            return;
        }

        // Fetch new data
        const response = await fetch(`/api/stock/${symbol}`);
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const data = await response.json();
        
        // Cache the data
        dataCache[symbol] = {
            data: data,
            timestamp: Date.now()
        };
        
        updateDashboard(data);
        
    } catch (error) {
        console.error('Error loading stock data:', error);
        showError(`Failed to load data for ${symbol}: ${error.message}`);
    } finally {
        showLoading(false);
    }
}

// Update dashboard with new data
function updateDashboard(data) {
    updatePriceDisplay(data.price);
    updateCharts(data);
    updateMetrics(data.metrics);
    updateNews(data.news);
    updateAnalystData(data.analyst);
}

// Update price display
function updatePriceDisplay(priceData) {
    const priceElement = document.getElementById('current-price');
    const changeElement = document.getElementById('price-change');
    const changePercentElement = document.getElementById('price-change-percent');
    
    if (priceElement && priceData) {
        priceElement.textContent = formatCurrency(priceData.current);
        
        if (changeElement && changePercentElement) {
            const change = priceData.change;
            const changePercent = priceData.changePercent;
            
            changeElement.textContent = formatCurrency(change);
            changePercentElement.textContent = `(${formatPercent(changePercent)})`;
            
            // Set color based on change
            const color = change >= 0 ? 'text-success' : 'text-danger';
            changeElement.className = color;
            changePercentElement.className = color;
        }
    }
}

// Update charts
function updateCharts(data) {
    if (data.charts) {
        Object.keys(data.charts).forEach(chartType => {
            const chartId = `${chartType}-chart`;
            const chartElement = document.getElementById(chartId);
            
            if (chartElement && data.charts[chartType]) {
                Plotly.newPlot(chartId, data.charts[chartType].data, data.charts[chartType].layout, {
                    responsive: true,
                    displayModeBar: false
                });
            }
        });
    }
}

// Update metrics
function updateMetrics(metrics) {
    if (!metrics) return;
    
    Object.keys(metrics).forEach(metric => {
        const element = document.getElementById(`${metric}-metric`);
        if (element) {
            element.textContent = formatMetric(metrics[metric], metric);
        }
    });
}

// Update news
function updateNews(newsData) {
    const newsContainer = document.getElementById('news-container');
    if (!newsContainer || !newsData) return;
    
    newsContainer.innerHTML = '';
    
    newsData.forEach(news => {
        const newsCard = createNewsCard(news);
        newsContainer.appendChild(newsCard);
    });
}

// Create news card
function createNewsCard(news) {
    const card = document.createElement('div');
    card.className = 'news-card';
    card.innerHTML = `
        <div class="news-header">
            <h6 class="news-title">${news.title}</h6>
            <small class="news-source">${news.source}</small>
        </div>
        <p class="news-summary">${news.summary}</p>
        <div class="news-footer">
            <small class="news-time">${formatTime(news.publishedAt)}</small>
            <a href="${news.url}" target="_blank" class="btn btn-sm btn-outline-primary">Read More</a>
        </div>
    `;
    return card;
}

// Update analyst data
function updateAnalystData(analystData) {
    if (!analystData) return;
    
    const recommendationsContainer = document.getElementById('recommendations-container');
    if (recommendationsContainer) {
        recommendationsContainer.innerHTML = '';
        
        analystData.recommendations.forEach(rec => {
            const recElement = document.createElement('div');
            recElement.className = 'recommendation-item';
            recElement.innerHTML = `
                <div class="recommendation-firm">${rec.firm}</div>
                <div class="recommendation-rating">${rec.rating}</div>
                <div class="recommendation-target">${formatCurrency(rec.targetPrice)}</div>
                <div class="recommendation-date">${formatDate(rec.date)}</div>
            `;
            recommendationsContainer.appendChild(recElement);
        });
    }
}

// Setup portfolio controls
function setupPortfolioControls() {
    const addStockBtn = document.getElementById('add-stock-btn');
    const optimizeBtn = document.getElementById('optimize-portfolio-btn');
    const rebalanceBtn = document.getElementById('rebalance-portfolio-btn');
    
    if (addStockBtn) {
        addStockBtn.addEventListener('click', addStockToPortfolio);
    }
    
    if (optimizeBtn) {
        optimizeBtn.addEventListener('click', optimizePortfolio);
    }
    
    if (rebalanceBtn) {
        rebalanceBtn.addEventListener('click', rebalancePortfolio);
    }
}

// Add stock to portfolio
async function addStockToPortfolio() {
    const symbol = currentSymbol || document.getElementById('stock-search').value.trim();
    const shares = document.getElementById('shares-input').value;
    const price = document.getElementById('price-input').value;
    
    if (!symbol || !shares || !price) {
        showError('Please fill in all fields');
        return;
    }
    
    try {
        const response = await fetch('/api/portfolio/add', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                symbol: symbol.toUpperCase(),
                shares: parseFloat(shares),
                price: parseFloat(price)
            })
        });
        
        if (response.ok) {
            showSuccess('Stock added to portfolio');
            loadPortfolioData();
        } else {
            throw new Error('Failed to add stock');
        }
    } catch (error) {
        showError('Error adding stock to portfolio: ' + error.message);
    }
}

// Optimize portfolio
async function optimizePortfolio() {
    try {
        showLoading(true);
        
        const response = await fetch('/api/portfolio/optimize', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                method: document.getElementById('optimization-method').value
            })
        });
        
        if (response.ok) {
            const result = await response.json();
            displayOptimizationResults(result);
        } else {
            throw new Error('Failed to optimize portfolio');
        }
    } catch (error) {
        showError('Error optimizing portfolio: ' + error.message);
    } finally {
        showLoading(false);
    }
}

// Display optimization results
function displayOptimizationResults(results) {
    const resultsContainer = document.getElementById('optimization-results');
    if (!resultsContainer) return;
    
    resultsContainer.innerHTML = `
        <div class="optimization-summary">
            <h5>Optimization Results</h5>
            <div class="row">
                <div class="col-md-6">
                    <p><strong>Expected Return:</strong> ${formatPercent(results.expectedReturn)}</p>
                    <p><strong>Volatility:</strong> ${formatPercent(results.volatility)}</p>
                    <p><strong>Sharpe Ratio:</strong> ${results.sharpeRatio.toFixed(3)}</p>
                </div>
                <div class="col-md-6">
                    <p><strong>Max Drawdown:</strong> ${formatPercent(results.maxDrawdown)}</p>
                    <p><strong>VaR (95%):</strong> ${formatPercent(results.var)}</p>
                </div>
            </div>
        </div>
        <div class="optimization-weights">
            <h6>Optimal Weights</h6>
            <div class="weights-list">
                ${Object.entries(results.weights).map(([symbol, weight]) => 
                    `<div class="weight-item">
                        <span class="symbol">${symbol}</span>
                        <span class="weight">${formatPercent(weight)}</span>
                    </div>`
                ).join('')}
            </div>
        </div>
    `;
}

// Setup report controls
function setupReportControls() {
    const generateReportBtn = document.getElementById('generate-report-btn');
    const reportTypeSelect = document.getElementById('report-type');
    
    if (generateReportBtn) {
        generateReportBtn.addEventListener('click', generateReport);
    }
    
    if (reportTypeSelect) {
        reportTypeSelect.addEventListener('change', function() {
            updateReportOptions(this.value);
        });
    }
}

// Generate report
async function generateReport() {
    const symbol = currentSymbol || document.getElementById('stock-search').value.trim();
    const reportType = document.getElementById('report-type').value;
    
    if (!symbol) {
        showError('Please select a stock first');
        return;
    }
    
    try {
        showLoading(true);
        
        const response = await fetch('/api/reports/generate', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                symbol: symbol,
                type: reportType
            })
        });
        
        if (response.ok) {
            const report = await response.json();
            displayReport(report);
        } else {
            throw new Error('Failed to generate report');
        }
    } catch (error) {
        showError('Error generating report: ' + error.message);
    } finally {
        showLoading(false);
    }
}

// Display report
function displayReport(report) {
    const reportContainer = document.getElementById('report-container');
    if (!reportContainer) return;
    
    reportContainer.innerHTML = `
        <div class="report-header">
            <h4>${report.title}</h4>
            <div class="report-meta">
                <span>Generated: ${formatDateTime(report.generatedAt)}</span>
                <button class="btn btn-sm btn-outline-primary" onclick="downloadReport('${report.id}')">Download PDF</button>
            </div>
        </div>
        <div class="report-content">
            ${report.content}
        </div>
    `;
}

// Setup real-time updates
function setupRealTimeUpdates() {
    // Update every 30 seconds
    updateInterval = setInterval(() => {
        if (currentSymbol) {
            updateRealTimeData(currentSymbol);
        }
    }, 30000);
}

// Update real-time data
async function updateRealTimeData(symbol) {
    try {
        const response = await fetch(`/api/stock/${symbol}/realtime`);
        if (response.ok) {
            const data = await response.json();
            updatePriceDisplay(data.price);
        }
    } catch (error) {
        console.error('Error updating real-time data:', error);
    }
}

// Switch tabs
function switchTab(tabName) {
    // Remove active class from all tabs
    document.querySelectorAll('.nav-link').forEach(link => {
        link.classList.remove('active');
    });
    
    // Add active class to clicked tab
    document.querySelector(`[data-tab="${tabName}"]`).classList.add('active');
    
    // Hide all tab content
    document.querySelectorAll('.tab-content').forEach(content => {
        content.style.display = 'none';
    });
    
    // Show selected tab content
    document.getElementById(`${tabName}-tab`).style.display = 'block';
    
    // Load tab-specific data
    loadTabData(tabName);
}

// Load tab-specific data
function loadTabData(tabName) {
    switch (tabName) {
        case 'dashboard':
            loadDashboardData();
            break;
        case 'analysis':
            loadAnalysisData();
            break;
        case 'portfolio':
            loadPortfolioData();
            break;
        case 'reports':
            loadReportsData();
            break;
    }
}

// Initialize tooltips
function initializeTooltips() {
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
}

// Initialize charts
function initializeCharts() {
    // Initialize any charts that need special setup
    console.log('Charts initialized');
}

// Setup responsive behavior
function setupResponsiveBehavior() {
    // Handle window resize
    window.addEventListener('resize', debounce(() => {
        Object.keys(chartInstances).forEach(chartId => {
            if (chartInstances[chartId]) {
                Plotly.Plots.resize(chartId);
            }
        });
    }, 250));
}

// Load default data
function loadDefaultData() {
    // Load market overview
    loadMarketOverview();
    
    // Load default stock if specified
    const urlParams = new URLSearchParams(window.location.search);
    const symbol = urlParams.get('symbol');
    if (symbol) {
        currentSymbol = symbol;
        document.getElementById('stock-search').value = symbol;
        loadStockData(symbol);
    }
}

// Load market overview
async function loadMarketOverview() {
    try {
        const response = await fetch('/api/market/overview');
        if (response.ok) {
            const data = await response.json();
            updateMarketOverview(data);
        }
    } catch (error) {
        console.error('Error loading market overview:', error);
    }
}

// Update market overview
function updateMarketOverview(data) {
    // Update market indices
    if (data.indices) {
        Object.keys(data.indices).forEach(index => {
            const element = document.getElementById(`${index}-index`);
            if (element) {
                const indexData = data.indices[index];
                element.innerHTML = `
                    <div class="index-name">${indexData.name}</div>
                    <div class="index-value">${formatNumber(indexData.value)}</div>
                    <div class="index-change ${indexData.change >= 0 ? 'positive' : 'negative'}">
                        ${formatPercent(indexData.changePercent)}
                    </div>
                `;
            }
        });
    }
    
    // Update sector performance
    if (data.sectors) {
        const sectorContainer = document.getElementById('sector-performance');
        if (sectorContainer) {
            sectorContainer.innerHTML = data.sectors.map(sector => `
                <div class="sector-item">
                    <span class="sector-name">${sector.name}</span>
                    <span class="sector-change ${sector.change >= 0 ? 'positive' : 'negative'}">
                        ${formatPercent(sector.change)}
                    </span>
                </div>
            `).join('');
        }
    }
}

// Utility functions
function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

function showLoading(show) {
    const loadingElement = document.getElementById('loading-overlay');
    if (loadingElement) {
        loadingElement.style.display = show ? 'flex' : 'none';
    }
}

function showError(message) {
    showNotification(message, 'error');
}

function showSuccess(message) {
    showNotification(message, 'success');
}

function showNotification(message, type) {
    const notification = document.createElement('div');
    notification.className = `alert alert-${type === 'error' ? 'danger' : 'success'} notification`;
    notification.textContent = message;
    
    document.body.appendChild(notification);
    
    setTimeout(() => {
        notification.remove();
    }, 5000);
}

function formatCurrency(value) {
    return new Intl.NumberFormat('en-US', {
        style: 'currency',
        currency: 'USD'
    }).format(value);
}

function formatPercent(value) {
    return `${(value * 100).toFixed(2)}%`;
}

function formatNumber(value) {
    return new Intl.NumberFormat('en-US').format(value);
}

function formatDate(dateString) {
    return new Date(dateString).toLocaleDateString();
}

function formatTime(dateString) {
    return new Date(dateString).toLocaleTimeString();
}

function formatDateTime(dateString) {
    return new Date(dateString).toLocaleString();
}

function formatMetric(value, metric) {
    switch (metric) {
        case 'pe':
        case 'pb':
        case 'ps':
            return value.toFixed(2);
        case 'marketCap':
        case 'enterpriseValue':
            return formatLargeNumber(value);
        case 'dividendYield':
        case 'returnOnEquity':
        case 'returnOnAssets':
            return formatPercent(value);
        default:
            return value;
    }
}

function formatLargeNumber(value) {
    if (value >= 1e12) {
        return (value / 1e12).toFixed(2) + 'T';
    } else if (value >= 1e9) {
        return (value / 1e9).toFixed(2) + 'B';
    } else if (value >= 1e6) {
        return (value / 1e6).toFixed(2) + 'M';
    } else if (value >= 1e3) {
        return (value / 1e3).toFixed(2) + 'K';
    }
    return value.toFixed(2);
}

function isCacheValid(timestamp) {
    const cacheAge = Date.now() - timestamp;
    return cacheAge < 5 * 60 * 1000; // 5 minutes
}

function updateURL(symbol) {
    const url = new URL(window.location);
    url.searchParams.set('symbol', symbol);
    window.history.pushState({}, '', url);
}

function toggleTheme() {
    document.body.classList.toggle('dark-theme');
    localStorage.setItem('theme', document.body.classList.contains('dark-theme') ? 'dark' : 'light');
}

// Export functions for external use
window.Dashboard = {
    loadStockData,
    switchTab,
    addStockToPortfolio,
    optimizePortfolio,
    generateReport,
    toggleTheme
};
