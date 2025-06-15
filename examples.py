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
    Example demonstrating Telegram notification functionality.
    """
    print("\n" + "=" * 80)
    print("EXAMPLE: Telegram Notifications")
    print("=" * 80)
    
    # Import required functions from main module
    from main import load_telegram_config, format_telegram_message, send_telegram_notifications
    
    # Check if Telegram is configured
    telegram_config = load_telegram_config()
    
    if telegram_config:
        print("✅ Telegram configuration found!")
        print(f"📱 Bot configured for {len(telegram_config['user_ids'])} users")
        
        # Create signal generator and analyze a few stocks
        signal_generator = RSISignalGenerator()
        test_stocks = ['AAPL', 'MSFT', 'TSLA']
        
        print(f"\nAnalyzing {len(test_stocks)} stocks for Telegram notification demo...")
        results = signal_generator.analyze_multiple_stocks(test_stocks)
        
        # Show what the Telegram message would look like
        message = format_telegram_message(results)
        print("\nTelegram Message Preview:")
        print("-" * 50)
        # Convert markdown to plain text for console display
        preview = message.replace('*', '').replace('`', '').replace('\n', '\n')
        print(preview)
        print("-" * 50)
        
        # Optionally send the actual notification (commented out for demo)
        # print("\nSending Telegram notification...")
        # send_telegram_notifications(results)
        
    else:
        print("❌ Telegram not configured")
        print("\nTo enable Telegram notifications:")
        print("1. Create a telegram_config.json file")
        print("2. Add your bot token and user IDs")
        print("3. See README.md for detailed setup instructions")
        
        # Show template
        print("\nTemplate telegram_config.json:")
        print("{")
        print('    "api_key": "YOUR_BOT_TOKEN",')
        print('    "user_ids": ["YOUR_USER_ID"]')
        print("}")
    
    print("\nNote: Telegram notifications are sent automatically when you run main.py")


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
        
        print("=" * 80)
        print("All examples completed successfully!")
        print("=" * 80)
        
    except Exception as e:
        print(f"Error running examples: {e}")
        print("Make sure you have installed the required dependencies:")
        print("pip install -r requirements.txt")


if __name__ == "__main__":
    main()