#!/usr/bin/env python3
"""
Mojila Signal - Stock Market RSI Signal Generator

This module provides buy/sell signals for US stocks based on RSI (Relative Strength Index)
indicators using 30 and 70 thresholds.
"""

import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime, timedelta, date
from typing import Dict, List, Tuple, Optional
import config
import time
import os
import json
import asyncio
from telegram import Bot
from telegram.error import TelegramError


class RSISignalGenerator:
    """
    A class to generate buy/sell signals based on RSI indicators.
    
    RSI below 30 indicates oversold condition (potential buy signal)
    RSI above 70 indicates overbought condition (potential sell signal)
    """
    
    def __init__(self, rsi_period: int = None, oversold_threshold: float = None, overbought_threshold: float = None, check_calendar_events: bool = True):
        """
        Initialize the RSI Signal Generator.
        
        Args:
            rsi_period (int): Period for RSI calculation (default: from config)
            oversold_threshold (float): RSI threshold for oversold condition (default: from config)
            overbought_threshold (float): RSI threshold for overbought condition (default: from config)
            check_calendar_events (bool): Whether to check for ex-dividend and earnings dates (default: True)
        """
        self.rsi_period = rsi_period or config.RSI_PERIOD
        self.oversold_threshold = oversold_threshold or config.OVERSOLD_THRESHOLD
        self.overbought_threshold = overbought_threshold or config.OVERBOUGHT_THRESHOLD
        self.check_calendar_events = check_calendar_events
    
    def calculate_rsi(self, prices: pd.Series) -> pd.Series:
        """
        Calculate the Relative Strength Index (RSI) for given price series.
        
        Args:
            prices (pd.Series): Series of closing prices
            
        Returns:
            pd.Series: RSI values
        """
        delta = prices.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=self.rsi_period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=self.rsi_period).mean()
        
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        
        return rsi
    
    def get_stock_data(self, symbol: str, period: str = "1y") -> pd.DataFrame:
        """
        Fetch stock data from Yahoo Finance.
        
        Args:
            symbol (str): Stock symbol (e.g., 'AAPL', 'MSFT')
            period (str): Time period for data (default: '1y')
            
        Returns:
            pd.DataFrame: Stock data with OHLCV information
        """
        for attempt in range(config.RETRY_ATTEMPTS):
            try:
                stock = yf.Ticker(symbol)
                data = stock.history(period=period, timeout=config.REQUEST_TIMEOUT)
                if not data.empty:
                    return data
                else:
                    print(f"No data returned for {symbol}")
                    return pd.DataFrame()
            except Exception as e:
                if attempt < config.RETRY_ATTEMPTS - 1:
                    print(f"Attempt {attempt + 1} failed for {symbol}: {e}. Retrying...")
                    time.sleep(1)  # Wait 1 second before retry
                else:
                    print(f"Error fetching data for {symbol} after {config.RETRY_ATTEMPTS} attempts: {e}")
                    return pd.DataFrame()
    
    def get_calendar_events(self, symbol: str) -> Dict[str, bool]:
        """
        Check if the stock has ex-dividend date or earnings date tomorrow.
        
        Args:
            symbol (str): Stock symbol
            
        Returns:
            Dict[str, bool]: Dictionary with ex_date_tomorrow and earnings_tomorrow flags
        """
        tomorrow = date.today() + timedelta(days=1)
        ex_date_tomorrow = False
        earnings_tomorrow = False
        
        try:
            stock = yf.Ticker(symbol)
            
            # Check ex-dividend date
            try:
                info = stock.info
                if 'exDividendDate' in info and info['exDividendDate']:
                    # Convert timestamp to date
                    if isinstance(info['exDividendDate'], (int, float)):
                        ex_date = pd.to_datetime(info['exDividendDate'], unit='s').date()
                    else:
                        ex_date = pd.to_datetime(info['exDividendDate']).date()
                    
                    if ex_date == tomorrow:
                        ex_date_tomorrow = True
            except Exception as e:
                print(f"Warning: Could not fetch ex-dividend date for {symbol}: {e}")
            
            # Check earnings date
            try:
                earnings_dates = stock.get_earnings_dates(limit=4)
                if earnings_dates is not None and not earnings_dates.empty:
                    # Get the next earnings date (first row should be the upcoming one)
                    next_earnings = earnings_dates.index[0].date()
                    if next_earnings == tomorrow:
                        earnings_tomorrow = True
            except Exception as e:
                print(f"Warning: Could not fetch earnings dates for {symbol}: {e}")
                
        except Exception as e:
            print(f"Warning: Could not fetch calendar data for {symbol}: {e}")
        
        return {
             'ex_date_tomorrow': ex_date_tomorrow,
             'earnings_tomorrow': earnings_tomorrow
         }
    
    def get_stock_data(self, symbol: str, period: str = "1y") -> pd.DataFrame:
        """
        Fetch stock data from Yahoo Finance.
        
        Args:
            symbol (str): Stock symbol (e.g., 'AAPL', 'MSFT')
            period (str): Time period for data (default: '1y')
            
        Returns:
            pd.DataFrame: Stock data with OHLCV information
        """
        for attempt in range(config.RETRY_ATTEMPTS):
            try:
                stock = yf.Ticker(symbol)
                data = stock.history(period=period, timeout=config.REQUEST_TIMEOUT)
                if not data.empty:
                    return data
                else:
                    print(f"No data returned for {symbol}")
                    return pd.DataFrame()
            except Exception as e:
                if attempt < config.RETRY_ATTEMPTS - 1:
                    print(f"Attempt {attempt + 1} failed for {symbol}: {e}. Retrying...")
                    time.sleep(1)  # Wait 1 second before retry
                else:
                    print(f"Error fetching data for {symbol} after {config.RETRY_ATTEMPTS} attempts: {e}")
                    return pd.DataFrame()
    
    def generate_signals(self, symbol: str, period: str = "1y") -> Dict:
        """
        Generate buy/sell signals for a given stock symbol.
        
        Args:
            symbol (str): Stock symbol
            period (str): Time period for analysis
            
        Returns:
            Dict: Dictionary containing signal information
        """
        # Fetch stock data
        data = self.get_stock_data(symbol, period)
        
        if data.empty:
            return {"error": f"No data available for {symbol}"}
        
        # Calculate RSI
        data['RSI'] = self.calculate_rsi(data['Close'])
        
        # Generate signals
        data['Signal'] = 'HOLD'
        data.loc[data['RSI'] <= self.oversold_threshold, 'Signal'] = 'BUY'
        data.loc[data['RSI'] >= self.overbought_threshold, 'Signal'] = 'SELL'
        
        # Check calendar events for additional SELL signal
        calendar_events = {'ex_date_tomorrow': False, 'earnings_tomorrow': False}
        if self.check_calendar_events:
            calendar_events = self.get_calendar_events(symbol)
            
            # Override signal to SELL if ex-date or earnings date is tomorrow
            if calendar_events['ex_date_tomorrow'] or calendar_events['earnings_tomorrow']:
                # Set the last signal to SELL due to calendar event
                data.iloc[-1, data.columns.get_loc('Signal')] = 'SELL'
        
        # Get current signal
        current_rsi = data['RSI'].iloc[-1]
        current_signal = data['Signal'].iloc[-1]
        current_price = data['Close'].iloc[-1]
        
        # Count recent signals
        recent_data = data.tail(config.MAX_RECENT_DAYS)
        buy_signals = len(recent_data[recent_data['Signal'] == 'BUY'])
        sell_signals = len(recent_data[recent_data['Signal'] == 'SELL'])
        
        # Determine signal strength
        signal_strength = "NORMAL"
        if current_rsi <= config.STRONG_BUY_THRESHOLD:
            signal_strength = "STRONG"
        elif current_rsi >= config.STRONG_SELL_THRESHOLD:
            signal_strength = "STRONG"
        
        # Get updated current signal after calendar check
        current_signal = data['Signal'].iloc[-1]
        
        # Prepare calendar event reasons
        calendar_reasons = []
        if calendar_events['ex_date_tomorrow']:
            calendar_reasons.append('Ex-dividend date tomorrow')
        if calendar_events['earnings_tomorrow']:
            calendar_reasons.append('Earnings report tomorrow')
        
        return {
            "symbol": symbol,
            "currentPrice": round(current_price, config.PRICE_DECIMAL_PLACES),
            "currentRSI": round(current_rsi, config.RSI_DECIMAL_PLACES),
            "currentSignal": current_signal,
            "signalStrength": signal_strength,
            "recentBuySignals": buy_signals,
            "recentSellSignals": sell_signals,
            "calendarEvents": calendar_events,
            "calendarReasons": calendar_reasons,
            "lastUpdated": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "data": data.tail(config.MAX_DISPLAY_ROWS).to_dict('records')
        }
    
    def analyze_multiple_stocks(self, symbols: List[str], period: str = "1y") -> List[Dict]:
        """
        Analyze multiple stocks and return signals for each.
        
        Args:
            symbols (List[str]): List of stock symbols
            period (str): Time period for analysis
            
        Returns:
            List[Dict]: List of signal dictionaries for each stock
        """
        results = []
        
        for symbol in symbols:
            print(f"Analyzing {symbol}...")
            signal_data = self.generate_signals(symbol, period)
            results.append(signal_data)
        
        return results


def load_portfolio_stocks() -> List[str]:
    """
    Load stock symbols from my_portfolio.txt if it exists, otherwise use default stocks.
    
    Returns:
        List[str]: List of stock symbols to analyze
    """
    portfolio_file = "my_portfolio.txt"
    
    if os.path.exists(portfolio_file):
        try:
            with open(portfolio_file, 'r') as file:
                stocks = [line.strip().upper() for line in file if line.strip() and not line.strip().startswith('#')]
            print(f"📁 Loaded {len(stocks)} stocks from {portfolio_file}")
            return stocks
        except Exception as e:
            print(f"❌ Error reading {portfolio_file}: {e}")
            print(f"📁 Using default stocks instead")
            return config.DEFAULT_STOCKS
    else:
        print(f"📁 {portfolio_file} not found, using default stocks")
        return config.DEFAULT_STOCKS


def load_scan_list(exclude_stocks: List[str] = None) -> List[str]:
    """
    Load stock symbols from scan_list.txt for market scanning.
    
    Args:
        exclude_stocks (List[str], optional): List of stock symbols to exclude from scan
    
    Returns:
        List[str]: List of stock symbols to scan, empty list if file doesn't exist
    """
    scan_file = "scan_list.txt"
    exclude_stocks = exclude_stocks or []
    
    if os.path.exists(scan_file):
        try:
            with open(scan_file, 'r') as file:
                all_stocks = [line.strip().upper() for line in file if line.strip() and not line.strip().startswith('#')]
            
            # Filter out stocks that are already in portfolio
            filtered_stocks = [stock for stock in all_stocks if stock not in exclude_stocks]
            excluded_count = len(all_stocks) - len(filtered_stocks)
            
            print(f"🔍 Loaded {len(all_stocks)} stocks from {scan_file}")
            if excluded_count > 0:
                print(f"🔍 Excluded {excluded_count} stocks already in portfolio")
            print(f"🔍 Final scan list: {len(filtered_stocks)} stocks")
            
            return filtered_stocks
        except Exception as e:
            print(f"❌ Error reading {scan_file}: {e}")
            return []
    else:
        print(f"🔍 {scan_file} not found, skipping market scan")
        return []


def load_telegram_config() -> Optional[Dict]:
    """
    Load Telegram configuration from telegram_config.json if it exists.
    
    Returns:
        Optional[Dict]: Telegram configuration with api_key and user_ids, or None if not found
    """
    config_file = "telegram_config.json"
    
    if os.path.exists(config_file):
        try:
            with open(config_file, 'r') as file:
                telegram_config = json.load(file)
                
                # Validate required fields
                if 'api_key' in telegram_config and 'user_ids' in telegram_config:
                    if telegram_config['api_key'] and telegram_config['user_ids']:
                        print(f"📱 Telegram notifications enabled for {len(telegram_config['user_ids'])} users")
                        return telegram_config
                    else:
                        print("⚠️  Telegram config found but api_key or user_ids are empty")
                        return None
                else:
                    print("⚠️  Telegram config missing required fields (api_key, user_ids)")
                    return None
        except json.JSONDecodeError as e:
            print(f"⚠️  Error parsing {config_file}: {e}")
            return None
        except Exception as e:
            print(f"⚠️  Error reading {config_file}: {e}")
            return None
    else:
        print(f"📋 {config_file} not found, Telegram notifications disabled")
        return None


async def send_telegram_message(bot_token: str, user_ids: List[str], message: str) -> None:
    """
    Send a message to multiple Telegram users.
    
    Args:
        bot_token (str): Telegram bot API token
        user_ids (List[str]): List of Telegram user IDs to send message to
        message (str): Message content to send
    """
    bot = Bot(token=bot_token)
    
    for user_id in user_ids:
        try:
            await bot.send_message(chat_id=user_id, text=message, parse_mode='Markdown')
            print(f"✅ Message sent to Telegram user {user_id}")
        except TelegramError as e:
            print(f"❌ Failed to send message to user {user_id}: {e}")
        except Exception as e:
            print(f"❌ Unexpected error sending to user {user_id}: {e}")


def format_telegram_message(results: List[Dict]) -> str:
    """
    Format the stock analysis results into a Telegram message.
    
    Args:
        results (List[Dict]): List of stock analysis results
        
    Returns:
        str: Formatted message for Telegram
    """
    message = "🔔 *Portfolio Signal Alert*\n\n"
    message += "📊 *Current Signals:*\n"
    message += "```\n"
    message += f"{'Symbol':<6} {'Signal':<6} {'RSI':<6} {'Price':<10}\n"
    message += "-" * 35 + "\n"
    
    buy_signals = []
    sell_signals = []
    
    for result in results:
        if 'error' not in result:
            symbol = result['symbol']
            signal = result['currentSignal']
            rsi = result['currentRSI']
            price = result['currentPrice']
            calendar_reasons = result.get('calendarReasons', [])
            
            # Add emoji indicators
            if signal == 'BUY':
                signal_emoji = "🟢"
                buy_signals.append(f"{symbol} (RSI: {rsi:.1f})")
            elif signal == 'SELL':
                signal_emoji = "🔴"
                reason = " (Calendar)" if calendar_reasons else ""
                sell_signals.append(f"{symbol} (RSI: {rsi:.1f}){reason}")
            else:
                signal_emoji = "🟡"
            
            message += f"{symbol:<6} {signal_emoji}{signal:<5} {rsi:<6.1f} ${price:<9.2f}\n"
    
    message += "```\n\n"
    
    # Add summary
    if buy_signals:
        message += "🟢 *Buy Signals:* " + ", ".join(buy_signals) + "\n\n"
    
    if sell_signals:
        message += "🔴 *Sell Signals:* " + ", ".join(sell_signals) + "\n\n"
    
    if not buy_signals and not sell_signals:
        message += "🟡 *No active buy/sell signals*\n\n"
    
    message += f"📅 *Generated:* {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
    message += "⚠️ *Disclaimer:* Educational purposes only. Not financial advice."
    
    return message


def format_scan_telegram_message(results: List[Dict]) -> str:
    """
    Format the scan results into a Telegram message showing only buy/sell signals.
    
    Args:
        results (List[Dict]): List of stock analysis results from scan
        
    Returns:
        str: Formatted message for Telegram with only buy/sell signals
    """
    buy_signals = []
    sell_signals = []
    
    for result in results:
        if 'error' not in result:
            symbol = result['symbol']
            signal = result['currentSignal']
            rsi = result['currentRSI']
            calendar_reasons = result.get('calendarReasons', [])
            
            if signal == 'BUY':
                buy_signals.append(f"{symbol} (RSI: {rsi:.1f})")
            elif signal == 'SELL':
                reason = " (Calendar)" if calendar_reasons else ""
                sell_signals.append(f"{symbol} (RSI: {rsi:.1f}){reason}")
    
    # Only send message if there are buy or sell signals
    if not buy_signals and not sell_signals:
        return None
    
    message = "🔍 *Market Scan Alert*\n\n"
    
    if buy_signals:
        message += "🟢 *Buy Signals Found:*\n"
        for signal in buy_signals:
            message += f"• {signal}\n"
        message += "\n"
    
    if sell_signals:
        message += "🔴 *Sell Signals Found:*\n"
        for signal in sell_signals:
            message += f"• {signal}\n"
        message += "\n"
    
    message += f"📅 *Scanned:* {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
    message += "⚠️ *Disclaimer:* Educational purposes only. Not financial advice."
    
    return message


def send_telegram_notifications(results: List[Dict]) -> None:
    """
    Send stock analysis results to Telegram if configuration exists.
    
    Args:
        results (List[Dict]): List of stock analysis results
    """
    telegram_config = load_telegram_config()
    
    if telegram_config:
        try:
            message = format_telegram_message(results)
            
            # Run the async function
            asyncio.run(send_telegram_message(
                telegram_config['api_key'],
                telegram_config['user_ids'],
                message
            ))
        except Exception as e:
            print(f"❌ Error sending Telegram notifications: {e}")


def send_scan_telegram_notifications(scan_results: List[Dict]) -> None:
    """
    Send market scan results to Telegram if configuration exists and signals are found.
    
    Args:
        scan_results (List[Dict]): List of stock analysis results from market scan
    """
    telegram_config = load_telegram_config()
    
    if telegram_config:
        try:
            message = format_scan_telegram_message(scan_results)
            
            # Only send if there are actual buy/sell signals
            if message:
                # Run the async function
                asyncio.run(send_telegram_message(
                    telegram_config['api_key'],
                    telegram_config['user_ids'],
                    message
                ))
                print("📱 Market scan signals sent to Telegram")
            else:
                print("🔍 No buy/sell signals found in market scan")
        except Exception as e:
            print(f"❌ Error sending scan Telegram notifications: {e}")


def analyze_sector(sector_name: str, stocks: List[str], signal_generator: RSISignalGenerator) -> None:
    """
    Analyze stocks in a specific sector and display results.
    
    Args:
        sector_name (str): Name of the sector
        stocks (List[str]): List of stock symbols in the sector
        signal_generator (RSISignalGenerator): Signal generator instance
    """
    print(f"\n{sector_name.upper()} SECTOR ANALYSIS:")
    print("-" * 90)
    print(f"{'Symbol':<8} {'Price':<10} {'RSI':<8} {'Signal':<8} {'Strength':<10} {'Buy/30d':<8} {'Sell/30d':<8} {'Calendar':<15}")
    print("-" * 90)
    
    results = signal_generator.analyze_multiple_stocks(stocks[:8])  # Limit to 8 stocks per sector
    
    for result in results:
        if 'error' not in result:
            strength_indicator = "⚡" if result['signalStrength'] == "STRONG" else "  "
            calendar_indicator = ", ".join(result.get('calendarReasons', [])) or "-"
            print(f"{result['symbol']:<8} ${result['currentPrice']:<9} {result['currentRSI']:<7.1f} {result['currentSignal']:<8} {strength_indicator}{result['signalStrength']:<8} {result['recentBuySignals']:<8} {result['recentSellSignals']:<8} {calendar_indicator:<15}")
        else:
            print(f"{result.get('symbol', 'Unknown'):<8} Error fetching data")


def main():
    """
    Main function to demonstrate the RSI signal generator.
    """
    # Initialize the signal generator
    signal_generator = RSISignalGenerator()
    
    print("=" * 70)
    print("MOJILA SIGNAL - RSI Stock Market Signal Generator")
    print("=" * 70)
    print(f"RSI Period: {signal_generator.rsi_period}")
    print(f"RSI Oversold Threshold: {signal_generator.oversold_threshold}")
    print(f"RSI Overbought Threshold: {signal_generator.overbought_threshold}")
    print(f"Analysis Period: {config.DEFAULT_PERIOD}")
    print("=" * 70)
    
    # Load and analyze stocks from portfolio or default list
    stocks_to_analyze = load_portfolio_stocks()
    print(f"\nANALYZING {len(stocks_to_analyze)} STOCKS...")
    results = signal_generator.analyze_multiple_stocks(stocks_to_analyze)
    
    # Display main results
    print("\nCURRENT SIGNALS:")
    print("-" * 90)
    print(f"{'Symbol':<8} {'Price':<10} {'RSI':<8} {'Signal':<8} {'Strength':<10} {'Buy/30d':<8} {'Sell/30d':<8} {'Calendar':<15}")
    print("-" * 90)
    
    for result in results:
        if 'error' not in result:
            strength_indicator = "⚡" if result['signalStrength'] == "STRONG" else "  "
            calendar_indicator = ", ".join(result.get('calendarReasons', [])) or "-"
            print(f"{result['symbol']:<8} ${result['currentPrice']:<9} {result['currentRSI']:<7.1f} {result['currentSignal']:<8} {strength_indicator}{result['signalStrength']:<8} {result['recentBuySignals']:<8} {result['recentSellSignals']:<8} {calendar_indicator:<15}")
        else:
            print(f"{result.get('symbol', 'Unknown'):<8} Error fetching data")
    
    # Send Telegram notifications if configured
    print("\n📱 Checking for Telegram notifications...")
    send_telegram_notifications(results)
    
    # Market scan analysis
    scan_stocks = load_scan_list(exclude_stocks=stocks_to_analyze)
    if scan_stocks:
        print(f"\n🔍 MARKET SCAN - Analyzing {len(scan_stocks)} stocks...")
        scan_results = signal_generator.analyze_multiple_stocks(scan_stocks)
        
        # Count signals found
        buy_count = sum(1 for r in scan_results if 'error' not in r and r['currentSignal'] == 'BUY')
        sell_count = sum(1 for r in scan_results if 'error' not in r and r['currentSignal'] == 'SELL')
        
        print(f"🔍 Scan complete: {buy_count} BUY signals, {sell_count} SELL signals found")
        
        # Send scan notifications if signals found
        if buy_count > 0 or sell_count > 0:
            print("📱 Sending market scan notifications...")
            send_scan_telegram_notifications(scan_results)
        else:
            print("🔍 No actionable signals found in market scan")
    
    # Sector analysis (optional - uncomment to enable)
    # analyze_sector("Technology", config.TECH_STOCKS, signal_generator)
    # analyze_sector("Financial", config.FINANCIAL_STOCKS, signal_generator)
    
    print("-" * 90)
    print("\nLegend:")
    print("BUY  - RSI <= 30 (Oversold, potential buying opportunity)")
    print("SELL - RSI >= 70 (Overbought, potential selling opportunity)")
    print("     - Also triggered by ex-dividend or earnings date tomorrow")
    print("HOLD - RSI between 30-70 (Neutral zone)")
    print("⚡   - Strong signal (RSI <= 20 or RSI >= 80)")
    print(f"Buy/30d, Sell/30d - Number of signals in the last {config.MAX_RECENT_DAYS} days")
    print("Calendar - Shows upcoming ex-dividend or earnings events")
    print("\n⚠️  Disclaimer: This is for educational purposes only. Not financial advice.")


if __name__ == "__main__":
    main()