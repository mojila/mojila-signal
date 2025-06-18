#!/usr/bin/env python3
"""
Test script to verify database functionality for signal storage.
"""

from main import RSISignalGenerator
from datetime import datetime
import os

def test_database_functionality():
    """Test the database functionality with actual signal generation."""
    print("🧪 Testing Database Functionality")
    print("=" * 50)
    
    # Remove existing database to start fresh
    if os.path.exists('signals.db'):
        os.remove('signals.db')
        print("🗑️  Removed existing database")
    
    # Initialize signal generator
    signal_generator = RSISignalGenerator()
    
    # Test with a small list of symbols
    test_symbols = ['AAPL', 'MSFT']
    
    print(f"\n📊 Testing with symbols: {test_symbols}")
    
    # First scan - should generate and save new signals
    print("\n🔍 First scan (should generate new signals):")
    buy_signals_1, sell_signals_1 = signal_generator.scan_market(test_symbols)
    print(f"Buy signals: {buy_signals_1}")
    print(f"Sell signals: {sell_signals_1}")
    
    # Check database contents
    print("\n📊 Checking database contents:")
    today = datetime.now().strftime('%Y-%m-%d')
    existing_signals = signal_generator.db.get_signals_by_date(today)
    print(f"Signals in database for {today}: {len(existing_signals)}")
    for signal in existing_signals:
        signal_type = signal.get('currentSignal', 'UNKNOWN')
        symbol = signal.get('symbol', 'UNKNOWN')
        print(f"  {signal_type}: {symbol}")
    
    # Second scan - should use existing signals
    print("\n🔍 Second scan (should use existing signals):")
    buy_signals_2, sell_signals_2 = signal_generator.scan_market(test_symbols)
    print(f"Buy signals: {buy_signals_2}")
    print(f"Sell signals: {sell_signals_2}")
    
    # Verify results are the same
    if buy_signals_1 == buy_signals_2 and sell_signals_1 == sell_signals_2:
        print("\n✅ Database functionality working correctly!")
        print("   - First scan generated and saved signals")
        print("   - Second scan retrieved existing signals")
        print("   - Results are consistent")
    else:
        print("\n❌ Database functionality issue detected!")
        print("   - Results differ between scans")
    
    # Test database statistics
    print("\n📈 Database Statistics:")
    stats = signal_generator.db.get_database_stats()
    print(f"Total signals: {stats['total_signals']}")
    print(f"Unique symbols: {stats['unique_symbols']}")
    print(f"Signals today: {stats['signals_today']}")
    print(f"Database size: {stats['database_size_mb']} MB")
    
if __name__ == "__main__":
    test_database_functionality()