#!/usr/bin/env python3
"""
Database module for Mojila Signal - SQLite operations for storing daily signals
"""

import sqlite3
import json
from datetime import datetime, date
from typing import Dict, List, Optional, Any
import os

class SignalDatabase:
    """
    SQLite database handler for storing and retrieving stock signals.
    """
    
    def __init__(self, db_path: str = "signals.db"):
        """
        Initialize the database connection and create tables if they don't exist.
        
        Args:
            db_path (str): Path to the SQLite database file
        """
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """
        Create the signals table if it doesn't exist.
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS signals (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    symbol TEXT NOT NULL,
                    date TEXT NOT NULL,
                    signal_data TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(symbol, date)
                )
            """)
            
            # Create index for faster lookups
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_symbol_date 
                ON signals(symbol, date)
            """)
            
            conn.commit()
    
    def save_signal(self, symbol: str, signal_data: Dict[str, Any], signal_date: Optional[str] = None) -> bool:
        """
        Save a signal to the database.
        
        Args:
            symbol (str): Stock symbol
            signal_data (Dict): Signal data dictionary
            signal_date (str, optional): Date in YYYY-MM-DD format. Defaults to today.
            
        Returns:
            bool: True if saved successfully, False otherwise
        """
        if signal_date is None:
            signal_date = date.today().strftime('%Y-%m-%d')
        
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT OR REPLACE INTO signals (symbol, date, signal_data)
                    VALUES (?, ?, ?)
                """, (symbol, signal_date, json.dumps(signal_data)))
                conn.commit()
                return True
        except Exception as e:
            print(f"Error saving signal for {symbol}: {e}")
            return False
    
    def get_signal(self, symbol: str, signal_date: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """
        Retrieve a signal from the database.
        
        Args:
            symbol (str): Stock symbol
            signal_date (str, optional): Date in YYYY-MM-DD format. Defaults to today.
            
        Returns:
            Dict or None: Signal data if found, None otherwise
        """
        if signal_date is None:
            signal_date = date.today().strftime('%Y-%m-%d')
        
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT signal_data FROM signals 
                    WHERE symbol = ? AND date = ?
                """, (symbol, signal_date))
                
                result = cursor.fetchone()
                if result:
                    return json.loads(result[0])
                return None
        except Exception as e:
            print(f"Error retrieving signal for {symbol}: {e}")
            return None
    
    def get_signals_by_date(self, signal_date: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Retrieve all signals for a specific date.
        
        Args:
            signal_date (str, optional): Date in YYYY-MM-DD format. Defaults to today.
            
        Returns:
            List[Dict]: List of signal data dictionaries
        """
        if signal_date is None:
            signal_date = date.today().strftime('%Y-%m-%d')
        
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT symbol, signal_data FROM signals 
                    WHERE date = ?
                    ORDER BY symbol
                """, (signal_date,))
                
                results = cursor.fetchall()
                signals = []
                for symbol, signal_data in results:
                    data = json.loads(signal_data)
                    data['symbol'] = symbol
                    signals.append(data)
                return signals
        except Exception as e:
            print(f"Error retrieving signals for date {signal_date}: {e}")
            return []
    
    def signal_exists(self, symbol: str, signal_date: Optional[str] = None) -> bool:
        """
        Check if a signal exists for a given symbol and date.
        
        Args:
            symbol (str): Stock symbol
            signal_date (str, optional): Date in YYYY-MM-DD format. Defaults to today.
            
        Returns:
            bool: True if signal exists, False otherwise
        """
        if signal_date is None:
            signal_date = date.today().strftime('%Y-%m-%d')
        
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT COUNT(*) FROM signals 
                    WHERE symbol = ? AND date = ?
                """, (symbol, signal_date))
                
                count = cursor.fetchone()[0]
                return count > 0
        except Exception as e:
            print(f"Error checking signal existence for {symbol}: {e}")
            return False
    
    def get_portfolio_signals(self, symbols: List[str], signal_date: Optional[str] = None) -> Dict[str, Any]:
        """
        Get signals for a list of symbols (portfolio).
        
        Args:
            symbols (List[str]): List of stock symbols
            signal_date (str, optional): Date in YYYY-MM-DD format. Defaults to today.
            
        Returns:
            Dict: Dictionary with 'cached' and 'missing' symbols
        """
        if signal_date is None:
            signal_date = date.today().strftime('%Y-%m-%d')
        
        cached_signals = []
        missing_symbols = []
        
        for symbol in symbols:
            signal_data = self.get_signal(symbol, signal_date)
            if signal_data:
                signal_data['symbol'] = symbol
                cached_signals.append(signal_data)
            else:
                missing_symbols.append(symbol)
        
        return {
            'cached': cached_signals,
            'missing': missing_symbols,
            'date': signal_date
        }
    
    def delete_old_signals(self, days_to_keep: int = 30) -> int:
        """
        Delete signals older than specified days.
        
        Args:
            days_to_keep (int): Number of days to keep signals for
            
        Returns:
            int: Number of deleted records
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    DELETE FROM signals 
                    WHERE date < date('now', '-{} days')
                """.format(days_to_keep))
                
                deleted_count = cursor.rowcount
                conn.commit()
                return deleted_count
        except Exception as e:
            print(f"Error deleting old signals: {e}")
            return 0
    
    def get_database_stats(self) -> Dict[str, Any]:
        """
        Get database statistics.
        
        Returns:
            Dict: Database statistics
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Total signals
                cursor.execute("SELECT COUNT(*) FROM signals")
                total_signals = cursor.fetchone()[0]
                
                # Unique symbols
                cursor.execute("SELECT COUNT(DISTINCT symbol) FROM signals")
                unique_symbols = cursor.fetchone()[0]
                
                # Signals today
                today = date.today().strftime('%Y-%m-%d')
                cursor.execute("SELECT COUNT(*) FROM signals WHERE date = ?", (today,))
                signals_today = cursor.fetchone()[0]
                
                # Database file size
                file_size = os.path.getsize(self.db_path) if os.path.exists(self.db_path) else 0
                
                return {
                    'total_signals': total_signals,
                    'unique_symbols': unique_symbols,
                    'signals_today': signals_today,
                    'database_size_bytes': file_size,
                    'database_size_mb': round(file_size / (1024 * 1024), 2)
                }
        except Exception as e:
            print(f"Error getting database stats: {e}")
            return {
                'total_signals': 0,
                'unique_symbols': 0,
                'signals_today': 0,
                'database_size_bytes': 0,
                'database_size_mb': 0
            }