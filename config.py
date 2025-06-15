#!/usr/bin/env python3
"""
Configuration file for Mojila Signal RSI Stock Market Signal Generator

This file contains all configurable parameters for the signal generator.
Modify these values to customize the behavior of the application.
"""

# RSI Configuration
RSI_PERIOD = 14  # Number of periods for RSI calculation (typically 14)
OVERSOLD_THRESHOLD = 30  # RSI value below which stock is considered oversold (buy signal)
OVERBOUGHT_THRESHOLD = 70  # RSI value above which stock is considered overbought (sell signal)

# Default time period for stock data analysis
DEFAULT_PERIOD = "1y"  # Options: 1d, 5d, 1mo, 3mo, 6mo, 1y, 2y, 5y, 10y, ytd, max

# Stock symbols to analyze (popular US stocks)
DEFAULT_STOCKS = [
    'AAPL',   # Apple Inc.
    'MSFT',   # Microsoft Corporation
    'GOOGL',  # Alphabet Inc. (Google)
    'AMZN',   # Amazon.com Inc.
    'TSLA',   # Tesla Inc.
    'NVDA',   # NVIDIA Corporation
    'META',   # Meta Platforms Inc. (Facebook)
    'NFLX',   # Netflix Inc.
    'JPM',    # JPMorgan Chase & Co.
    'V',      # Visa Inc.
]

# Additional stock lists for different sectors
TECH_STOCKS = [
    'AAPL', 'MSFT', 'GOOGL', 'AMZN', 'TSLA', 'NVDA', 'META', 'NFLX',
    'CRM', 'ORCL', 'ADBE', 'INTC', 'AMD', 'PYPL', 'UBER', 'ZOOM'
]

FINANCIAL_STOCKS = [
    'JPM', 'BAC', 'WFC', 'GS', 'MS', 'C', 'AXP', 'BLK', 'SCHW', 'USB'
]

HEALTHCARE_STOCKS = [
    'JNJ', 'PFE', 'UNH', 'ABBV', 'TMO', 'DHR', 'BMY', 'AMGN', 'GILD', 'CVS'
]

ENERGY_STOCKS = [
    'XOM', 'CVX', 'COP', 'EOG', 'SLB', 'PSX', 'VLO', 'MPC', 'OXY', 'BKR'
]

# Display configuration
MAX_RECENT_DAYS = 30  # Number of recent days to analyze for signal counting
MAX_DISPLAY_ROWS = 10  # Maximum number of historical data rows to display

# API configuration
REQUEST_TIMEOUT = 30  # Timeout for API requests in seconds
RETRY_ATTEMPTS = 3    # Number of retry attempts for failed API calls

# Output formatting
PRICE_DECIMAL_PLACES = 2
RSI_DECIMAL_PLACES = 1

# Alert thresholds (for future enhancement)
STRONG_BUY_THRESHOLD = 20   # RSI below this value indicates strong buy signal
STRONG_SELL_THRESHOLD = 80  # RSI above this value indicates strong sell signal