#!/usr/bin/env python3

import sqlite3
from datetime import datetime

def check_database():
    """Check the contents of the signals database."""
    try:
        conn = sqlite3.connect('signals.db')
        cursor = conn.cursor()
        
        # Check if table exists
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='signals';")
        table_exists = cursor.fetchone()
        
        if table_exists:
            print("✅ Signals table exists")
            
            # Get all signals
            cursor.execute("SELECT symbol, date, signal_data FROM signals ORDER BY date DESC, symbol;")
            signals = cursor.fetchall()
            
            if signals:
                print(f"\n📊 Found {len(signals)} signals in database:")
                print("Symbol\t\tDate\t\tSignal Type")
                print("-" * 40)
                for signal in signals:
                    symbol, date, signal_data_json = signal
                    try:
                        import json
                        signal_data = json.loads(signal_data_json)
                        signal_type = signal_data.get('currentSignal', 'UNKNOWN')
                        print(f"{symbol}\t\t{date}\t{signal_type}")
                    except:
                        print(f"{symbol}\t\t{date}\tERROR_PARSING")
            else:
                print("\n⚠️  No signals found in database")
                
            # Get today's signals
            today = datetime.now().strftime('%Y-%m-%d')
            cursor.execute("SELECT symbol, date, signal_data FROM signals WHERE date = ? ORDER BY symbol;", (today,))
            today_signals = cursor.fetchall()
            
            if today_signals:
                print(f"\n📅 Today's signals ({today}):")
                for signal in today_signals:
                    symbol, date, signal_data_json = signal
                    try:
                        import json
                        signal_data = json.loads(signal_data_json)
                        signal_type = signal_data.get('currentSignal', 'UNKNOWN')
                        print(f"  {signal_type}: {symbol}")
                    except:
                        print(f"  ERROR_PARSING: {symbol}")
            else:
                print(f"\n📅 No signals found for today ({today})")
                
        else:
            print("❌ Signals table does not exist")
            
        conn.close()
        
    except Exception as e:
        print(f"❌ Error checking database: {e}")

if __name__ == "__main__":
    check_database()