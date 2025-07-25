#!/usr/bin/env python3
"""
Mojila Signal - Web Application Backend

Flask web application that provides REST API endpoints for stock signal analysis.
This serves as the backend for the web interface.
"""

from flask import Flask, jsonify, request, render_template, send_from_directory
from flask_cors import CORS
import os
import sys
from datetime import datetime
from typing import Dict, List, Optional

# Import our existing signal generator and database
from main import RSISignalGenerator, load_portfolio_stocks, load_scan_list
from database import SignalDatabase
import config

app = Flask(__name__, static_folder='static', template_folder='templates')
CORS(app)  # Enable CORS for all routes

# Initialize the signal generator and database
signal_generator = RSISignalGenerator()
db = SignalDatabase()

@app.route('/')
def index():
    """Serve the main web interface."""
    return render_template('index.html')

@app.route('/api/health')
def health_check():
    """Health check endpoint."""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'version': '1.0.0'
    })

@app.route('/api/config')
def get_config():
    """Get current configuration settings."""
    return jsonify({
        'rsi_period': signal_generator.rsi_period,
        'oversold_threshold': signal_generator.oversold_threshold,
        'overbought_threshold': signal_generator.overbought_threshold,
        'default_period': config.DEFAULT_PERIOD,
        'macd_fast_period': config.MACD_FAST_PERIOD,
        'macd_slow_period': config.MACD_SLOW_PERIOD,
        'macd_signal_period': config.MACD_SIGNAL_PERIOD
    })

@app.route('/api/stocks/<symbol>')
def get_stock_signal(symbol: str):
    """Get signal analysis for a single stock."""
    try:
        symbol = symbol.upper()
        period = request.args.get('period', config.DEFAULT_PERIOD)
        
        # Try to load from database first
        cached_signal = db.get_signal(symbol)
        if cached_signal:
            cached_signal['source'] = 'database'
            return jsonify(cached_signal)
        
        # If not in database, generate new signal
        result = signal_generator.generate_signals(symbol, period)
        
        if 'error' in result:
            return jsonify({'error': result['error']}), 400
        
        result['source'] = 'generated'
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/portfolio')
def get_portfolio_signals():
    """Get signal analysis for the entire portfolio."""
    try:
        period = request.args.get('period', config.DEFAULT_PERIOD)
        stocks = load_portfolio_stocks()
        
        # Try to load from database first
        portfolio_data = db.get_portfolio_signals(stocks)
        results = portfolio_data['cached']
        missing_symbols = portfolio_data['missing']
        
        # Generate signals for missing symbols
        for symbol in missing_symbols:
            result = signal_generator.generate_signals(symbol, period)
            if 'error' not in result:
                result['source'] = 'generated'
                results.append(result)
        
        # Mark cached results
        for result in portfolio_data['cached']:
            result['source'] = 'database'
        
        return jsonify({
            'stocks': results,
            'total_count': len(results),
            'cached_count': len(portfolio_data['cached']),
            'generated_count': len(missing_symbols),
            'timestamp': datetime.now().isoformat(),
            'period': period
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/scan')
def scan_market():
    """Scan the market for signals."""
    try:
        period = request.args.get('period', config.DEFAULT_PERIOD)
        limit = int(request.args.get('limit', 50))
        
        scan_list = load_scan_list()[:limit]
        
        # Try to load from database first
        scan_data = db.get_portfolio_signals(scan_list)
        results = scan_data['cached']
        missing_symbols = scan_data['missing']
        
        # Generate signals for missing symbols
        for symbol in missing_symbols:
            result = signal_generator.generate_signals(symbol, period)
            if 'error' not in result:
                result['source'] = 'generated'
                results.append(result)
        
        # Mark cached results
        for result in scan_data['cached']:
            result['source'] = 'database'
        
        return jsonify({
            'stocks': results,
            'total_count': len(results),
            'cached_count': len(scan_data['cached']),
            'generated_count': len(missing_symbols),
            'scanned_symbols': len(scan_list),
            'timestamp': datetime.now().isoformat(),
            'period': period
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/analyze', methods=['POST'])
def analyze_custom_stocks():
    """Analyze custom list of stocks."""
    try:
        data = request.get_json()
        if not data or 'symbols' not in data:
            return jsonify({'error': 'Missing symbols in request body'}), 400
        
        symbols = data['symbols']
        period = data.get('period', config.DEFAULT_PERIOD)
        
        if not isinstance(symbols, list) or not symbols:
            return jsonify({'error': 'Symbols must be a non-empty list'}), 400
        
        # Clean and normalize symbols
        clean_symbols = []
        for symbol in symbols:
            if isinstance(symbol, str) and symbol.strip():
                clean_symbols.append(symbol.upper().strip())
        
        # Try to load from database first
        analyze_data = db.get_portfolio_signals(clean_symbols)
        results = analyze_data['cached']
        missing_symbols = analyze_data['missing']
        
        # Generate signals for missing symbols
        for symbol in missing_symbols:
            result = signal_generator.generate_signals(symbol, period)
            if 'error' not in result:
                result['source'] = 'generated'
                results.append(result)
        
        # Mark cached results
        for result in analyze_data['cached']:
            result['source'] = 'database'
        
        return jsonify({
            'stocks': results,
            'total_count': len(results),
            'cached_count': len(analyze_data['cached']),
            'generated_count': len(missing_symbols),
            'timestamp': datetime.now().isoformat(),
            'period': period
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/sectors/<sector_name>')
def get_sector_analysis(sector_name: str):
    """Get analysis for a specific sector."""
    try:
        period = request.args.get('period', config.DEFAULT_PERIOD)
        
        # Map sector names to stock lists
        sector_stocks = {
            'technology': config.TECH_STOCKS,
            'financial': config.FINANCIAL_STOCKS,
            'healthcare': config.HEALTHCARE_STOCKS,
            'energy': config.ENERGY_STOCKS
        }
        
        sector_key = sector_name.lower()
        if sector_key not in sector_stocks:
            return jsonify({'error': f'Unknown sector: {sector_name}'}), 400
        
        stocks = sector_stocks[sector_key][:10]  # Limit to 10 stocks per sector
        
        # Try to load from database first
        sector_data = db.get_portfolio_signals(stocks)
        results = sector_data['cached']
        missing_symbols = sector_data['missing']
        
        # Generate signals for missing symbols
        for symbol in missing_symbols:
            result = signal_generator.generate_signals(symbol, period)
            if 'error' not in result:
                result['source'] = 'generated'
                results.append(result)
        
        # Mark cached results
        for result in sector_data['cached']:
            result['source'] = 'database'
        
        return jsonify({
            'sector': sector_name.title(),
            'stocks': results,
            'total_count': len(results),
            'cached_count': len(sector_data['cached']),
            'generated_count': len(missing_symbols),
            'timestamp': datetime.now().isoformat(),
            'period': period
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/summary')
def get_summary():
    """Get summary statistics of current signals."""
    try:
        period = request.args.get('period', config.DEFAULT_PERIOD)
        stocks = load_portfolio_stocks()
        
        # Try to load from database first
        portfolio_data = db.get_portfolio_signals(stocks)
        results = portfolio_data['cached']
        missing_symbols = portfolio_data['missing']
        
        # Generate signals for missing symbols
        for symbol in missing_symbols:
            result = signal_generator.generate_signals(symbol, period)
            if 'error' not in result:
                results.append(result)
        
        # Calculate summary statistics
        total_stocks = len(results)
        buy_signals = len([r for r in results if r['currentSignal'] in ['BUY', 'STRONG_BUY']])
        sell_signals = len([r for r in results if r['currentSignal'] in ['SELL', 'STRONG_SELL']])
        hold_signals = len([r for r in results if r['currentSignal'] == 'HOLD'])
        
        avg_rsi = sum(r['currentRSI'] for r in results) / total_stocks if total_stocks > 0 else 0
        
        return jsonify({
            'total_stocks': total_stocks,
            'buy_signals': buy_signals,
            'sell_signals': sell_signals,
            'hold_signals': hold_signals,
            'average_rsi': round(avg_rsi, 2),
            'cached_count': len(portfolio_data['cached']),
            'generated_count': len(missing_symbols),
            'timestamp': datetime.now().isoformat(),
            'period': period
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors."""
    return jsonify({'error': 'Endpoint not found'}), 404

@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors."""
    return jsonify({'error': 'Internal server error'}), 500

if __name__ == '__main__':
    # Create templates and static directories if they don't exist
    os.makedirs('templates', exist_ok=True)
    os.makedirs('static', exist_ok=True)
    
    # Get configuration from environment variables
    port = int(os.environ.get('PORT', 5001))
    debug_mode = os.environ.get('FLASK_ENV', 'production') == 'development'
    
    print("🚀 Starting Mojila Signal Web Application...")
    print(f"📊 RSI Period: {signal_generator.rsi_period}")
    print(f"📈 Oversold Threshold: {signal_generator.oversold_threshold}")
    print(f"📉 Overbought Threshold: {signal_generator.overbought_threshold}")
    print(f"🌐 Server will be available at: http://localhost:{port}")
    print(f"🔧 Debug mode: {debug_mode}")
    print("")
    
    app.run(debug=debug_mode, host='0.0.0.0', port=port)