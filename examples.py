#!/usr/bin/env python3
"""
Example usage scenarios for Mojila Signal RSI Stock Market Signal Generator

This file demonstrates various ways to use the signal generator with different
configurations and stock selections.
"""

from main import RSISignalGenerator
import config
import json


def example_single_stock_analysis():
    """
    Example: Analyze a single stock with default settings.
    """
    print("=" * 60)
    print("EXAMPLE 1: Single Stock Analysis (AAPL)")
    print("=" * 60)
    
    signal_generator = RSISignalGenerator()
    result = signal_generator.generate_signals('AAPL', period='6mo')
    
    if 'error' not in result:
        print(f"Stock: {result['symbol']}")
        print(f"Current Price: ${result['currentPrice']}")
        print(f"Current RSI: {result['currentRSI']}")
        print(f"Signal: {result['currentSignal']} ({result['signalStrength']})")
        print(f"Recent Buy Signals (30d): {result['recentBuySignals']}")
        print(f"Recent Sell Signals (30d): {result['recentSellSignals']}")
        print(f"Last Updated: {result['lastUpdated']}")
    else:
        print(f"Error: {result['error']}")
    
    print("\n")


def example_custom_rsi_settings():
    """
    Example: Use custom RSI settings for more sensitive signals.
    """
    print("=" * 60)
    print("EXAMPLE 2: Custom RSI Settings (More Sensitive)")
    print("=" * 60)
    
    # More sensitive settings: RSI 25/75 with 10-period calculation
    signal_generator = RSISignalGenerator(
        rsi_period=10,
        oversold_threshold=25,
        overbought_threshold=75
    )
    
    stocks = ['TSLA', 'NVDA', 'AMD']
    results = signal_generator.analyze_multiple_stocks(stocks, period='3mo')
    
    print(f"RSI Period: {signal_generator.rsi_period}")
    print(f"Oversold Threshold: {signal_generator.oversold_threshold}")
    print(f"Overbought Threshold: {signal_generator.overbought_threshold}")
    print("-" * 60)
    
    for result in results:
        if 'error' not in result:
            print(f"{result['symbol']}: ${result['currentPrice']} | RSI: {result['currentRSI']} | Signal: {result['currentSignal']}")
            if result.get('calendarReasons'):
                print(f"Calendar Events: {', '.join(result['calendarReasons'])}")
            else:
                print("Calendar Events: None")
        else:
            print(f"{result.get('symbol', 'Unknown')}: Error fetching data")
    
    print("\n")


def example_sector_analysis():
    """
    Example: Analyze specific sectors using predefined stock lists.
    """
    print("=" * 60)
    print("EXAMPLE 3: Technology Sector Analysis")
    print("=" * 60)
    
    signal_generator = RSISignalGenerator()
    
    # Analyze tech stocks
    tech_results = signal_generator.analyze_multiple_stocks(config.TECH_STOCKS[:6])
    
    print(f"{'Symbol':<8} {'Price':<10} {'RSI':<8} {'Signal':<8}")
    print("-" * 40)
    
    for result in tech_results:
        if 'error' not in result:
            print(f"{result['symbol']:<8} ${result['currentPrice']:<9} {result['currentRSI']:<7.1f} {result['currentSignal']:<8}")
    
    print("\n")


def example_json_output():
    """
    Example: Generate JSON output for API integration.
    """
    print("=" * 60)
    print("EXAMPLE 4: JSON Output for API Integration")
    print("=" * 60)
    
    signal_generator = RSISignalGenerator()
    
    # Analyze a few stocks and format as JSON
    stocks = ['AAPL', 'MSFT', 'GOOGL']
    results = signal_generator.analyze_multiple_stocks(stocks)
    
    # Create a clean JSON structure
    json_output = {
        "timestamp": results[0]['lastUpdated'] if results else None,
        "rsiSettings": {
            "period": signal_generator.rsi_period,
            "oversoldThreshold": signal_generator.oversold_threshold,
            "overboughtThreshold": signal_generator.overbought_threshold
        },
        "signals": []
    }
    
    for result in results:
        if 'error' not in result:
            json_output["signals"].append({
                "symbol": result['symbol'],
                "price": result['currentPrice'],
                "rsi": result['currentRSI'],
                "signal": result['currentSignal'],
                "strength": result['signalStrength']
            })
    
    print(json.dumps(json_output, indent=2))
    print("\n")


def example_signal_filtering():
    """
    Example: Filter stocks by signal type.
    """
    print("=" * 60)
    print("EXAMPLE 5: Filter Stocks by Signal Type")
    print("=" * 60)
    
    signal_generator = RSISignalGenerator()
    
    # Analyze a larger set of stocks
    all_stocks = config.DEFAULT_STOCKS + config.TECH_STOCKS[:5]
    results = signal_generator.analyze_multiple_stocks(list(set(all_stocks)))  # Remove duplicates
    
    # Filter by signal types
    buy_signals = [r for r in results if 'error' not in r and r['currentSignal'] == 'BUY']
    sell_signals = [r for r in results if 'error' not in r and r['currentSignal'] == 'SELL']
    strong_signals = [r for r in results if 'error' not in r and r['signalStrength'] == 'STRONG']
    
    print(f"BUY SIGNALS ({len(buy_signals)} found):")
    for result in buy_signals:
        print(f"  {result['symbol']}: RSI {result['currentRSI']} - ${result['currentPrice']}")
    
    print(f"\nSELL SIGNALS ({len(sell_signals)} found):")
    for result in sell_signals:
        print(f"  {result['symbol']}: RSI {result['currentRSI']} - ${result['currentPrice']}")
    
    print(f"\nSTRONG SIGNALS ({len(strong_signals)} found):")
    for result in strong_signals:
        print(f"  {result['symbol']}: {result['currentSignal']} - RSI {result['currentRSI']} - ${result['currentPrice']}")
    
    print("\n")


def example_historical_data_analysis():
    """
    Example: Analyze historical data and recent signal patterns.
    """
    print("=" * 60)
    print("EXAMPLE 6: Historical Data Analysis")
    print("=" * 60)
    
    signal_generator = RSISignalGenerator()
    
    # Get detailed data for a specific stock
    result = signal_generator.generate_signals('AAPL', period='1y')
    
    if 'error' not in result:
        print(f"Stock: {result['symbol']}")
        print(f"Current Status: {result['currentSignal']} (RSI: {result['currentRSI']})")
        print(f"Signal Activity (last 30 days): {result['recentBuySignals']} buys, {result['recentSellSignals']} sells")
        
        print("\nRecent Historical Data (last 5 days):")
        print(f"{'Close':<10} {'RSI':<8} {'Signal':<8}")
        print("-" * 30)
        
        # Display last 5 days from historical data
        for day in result['data'][-5:]:
            print(f"${day['Close']:<9.2f} {day['RSI']:<7.1f} {day['Signal']:<8}")
    
    print("\n")


def example_calendar_events():
    """
    Example demonstrating calendar event detection functionality.
    """
    print("\n" + "=" * 80)
    print("EXAMPLE: Calendar Events Detection")
    print("=" * 80)
    
    # Create signal generator with calendar events enabled
    signal_generator = RSISignalGenerator(check_calendar_events=True)
    
    # Analyze a few stocks that might have upcoming events
    test_stocks = ['JNJ', 'KO', 'PG']  # Dividend-paying stocks
    
    print(f"\nAnalyzing {len(test_stocks)} dividend-paying stocks for calendar events...")
    
    results = signal_generator.analyze_multiple_stocks(test_stocks)
    
    print("\nResults with Calendar Event Detection:")
    print("-" * 70)
    print(f"{'Symbol':<8} {'Signal':<8} {'RSI':<8} {'Calendar Events':<20}")
    print("-" * 70)
    
    for result in results:
        if 'error' not in result:
            calendar_info = ", ".join(result.get('calendarReasons', [])) or "None"
            print(f"{result['symbol']:<8} {result['currentSignal']:<8} {result['currentRSI']:<7.1f} {calendar_info:<20}")
        else:
            print(f"{result.get('symbol', 'Unknown'):<8} ERROR")
    
    print("-" * 70)
    print("\nNote: Calendar events (ex-dividend, earnings) can trigger SELL signals")
    print("even when RSI is not in overbought territory.")


def example_telegram_notifications():
    """
    Example of how Telegram notifications work.
    
    This function demonstrates the Telegram notification feature by:
    1. Checking if telegram_config.json exists
    2. Loading sample stock data
    3. Showing what the notification message would look like
    """
    print("\n" + "=" * 50)
    print("EXAMPLE: Telegram Notifications")
    print("=" * 50)
    
    # Import required functions from main module
    from main import load_telegram_config, format_telegram_message, format_scan_telegram_message
    
    # Check if Telegram is configured
    telegram_config = load_telegram_config()
    
    if telegram_config:
        print("✅ Telegram configuration found!")
        print(f"📱 Bot configured for {len(telegram_config['user_ids'])} user(s)")
        
        # Create sample results to show message format
        sample_results = [
            {
                'symbol': 'AAPL',
                'currentSignal': 'BUY',
                'currentRSI': 28.5,
                'currentPrice': 175.43,
                'calendarReasons': []
            },
            {
                'symbol': 'MSFT',
                'currentSignal': 'SELL',
                'currentRSI': 78.9,
                'currentPrice': 325.31,
                'calendarReasons': []
            },
            {
                'symbol': 'TSLA',
                'currentSignal': 'HOLD',
                'currentRSI': 45.7,
                'currentPrice': 325.31,
                'calendarReasons': []
            }
        ]
        
        print("\n📱 Sample portfolio notification message:")
        print("-" * 50)
        message = format_telegram_message(sample_results)
        print(message)
        print("-" * 50)
        
        # Show scan notification example
        scan_sample_results = [
            {
                'symbol': 'NVDA',
                'currentSignal': 'BUY',
                'currentRSI': 25.2,
                'currentPrice': 425.67,
                'calendarReasons': []
            },
            {
                'symbol': 'GOOGL',
                'currentSignal': 'SELL',
                'currentRSI': 72.8,
                'currentPrice': 142.15,
                'calendarReasons': ['Ex-Dividend']
            }
        ]
        
        print("\n🔍 Sample market scan notification message:")
        print("-" * 50)
        scan_message = format_scan_telegram_message(scan_sample_results)
        if scan_message:
            print(scan_message)
        else:
            print("No buy/sell signals found")
        print("-" * 50)
        
    else:
        print("❌ Telegram not configured")
        print("\n📋 To set up Telegram notifications:")
        print("1. Create a Telegram bot via @BotFather")
        print("2. Get your user ID from @userinfobot")
        print("3. Copy telegram_config.json.template to telegram_config.json")
        print("4. Fill in your bot token and user ID")
        
    print("\nNote: Telegram notifications are sent automatically when you run main.py")


def example_market_scan():
    """
    Example of how market scan functionality works.
    
    This function demonstrates the market scan feature by:
    1. Checking if scan_list.txt exists
    2. Loading scan stocks
    3. Showing how scan results are filtered for buy/sell signals only
    """
    print("\n" + "=" * 50)
    print("EXAMPLE: Market Scan")
    print("=" * 50)
    
    # Import required functions from main module
    from main import load_scan_list, format_scan_telegram_message, load_portfolio_stocks
    
    # Load portfolio stocks to demonstrate filtering
    portfolio_stocks = load_portfolio_stocks()
    print(f"📁 Portfolio contains {len(portfolio_stocks)} stocks: {', '.join(portfolio_stocks[:5])}{'...' if len(portfolio_stocks) > 5 else ''}")
    
    # Check if scan list exists and load with portfolio exclusion
    scan_stocks = load_scan_list(exclude_stocks=portfolio_stocks)
    
    if scan_stocks:
        print(f"✅ Scan list found with {len(scan_stocks)} stocks")
        print(f"📊 First 10 stocks: {', '.join(scan_stocks[:10])}")
        
        # Create sample scan results to show filtering
        sample_scan_results = [
            {
                'symbol': 'AAPL',
                'currentSignal': 'BUY',
                'currentRSI': 28.5,
                'currentPrice': 175.43,
                'calendarReasons': []
            },
            {
                'symbol': 'MSFT',
                'currentSignal': 'HOLD',
                'currentRSI': 45.2,
                'currentPrice': 325.31,
                'calendarReasons': []
            },
            {
                'symbol': 'GOOGL',
                'currentSignal': 'SELL',
                'currentRSI': 72.8,
                'currentPrice': 142.15,
                'calendarReasons': ['Ex-Dividend']
            },
            {
                'symbol': 'TSLA',
                'currentSignal': 'HOLD',
                'currentRSI': 55.7,
                'currentPrice': 245.67,
                'calendarReasons': []
            }
        ]
        
        print("\n🔍 Sample scan results (showing filtering):")
        print("All signals found: BUY (AAPL), HOLD (MSFT), SELL (GOOGL), HOLD (TSLA)")
        print("Filtered for Telegram: Only BUY and SELL signals")
        
        print("\n📱 Filtered scan notification message:")
        print("-" * 50)
        scan_message = format_scan_telegram_message(sample_scan_results)
        if scan_message:
            print(scan_message)
        else:
            print("No buy/sell signals found")
        print("-" * 50)
        
    else:
        print("❌ Scan list not found")
        print("\n📋 To enable market scanning:")
        print("1. Create scan_list.txt file")
        print("2. Add stock symbols (one per line)")
        print("3. Run main.py to scan for signals")
        
        print("\n📄 scan_list.txt should contain:")
        print("AAPL")
        print("MSFT")
        print("GOOGL")
        print("...")
    
    print("\nNote: Market scan runs automatically after portfolio analysis in main.py")


def main():
    """
    Run all example scenarios.
    """
    print("MOJILA SIGNAL - USAGE EXAMPLES")
    print("=" * 80)
    print("This script demonstrates various ways to use the RSI signal generator.")
    print("=" * 80)
    print()
    
    try:
        example_single_stock_analysis()
        example_custom_rsi_settings()
        example_sector_analysis()
        example_json_output()
        example_signal_filtering()
        example_historical_data_analysis()
        example_calendar_events()
        example_telegram_notifications()
        example_market_scan()
        
        print("=" * 80)
        print("All examples completed successfully!")
        print("=" * 80)
        
    except Exception as e:
        print(f"Error running examples: {e}")
        print("Make sure you have installed the required dependencies:")
        print("pip install -r requirements.txt")


if __name__ == "__main__":
    main()