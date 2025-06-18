#!/usr/bin/env python3
"""
Mojila Signal - Automated Scheduler

This script runs the signal generation process on a scheduled basis.
It can be run as a standalone service or integrated with system cron jobs.
"""

import schedule
import time
import logging
import sys
import os
from datetime import datetime
from typing import List, Tuple

# Import our signal generator
from main import RSISignalGenerator, load_scan_list
from database import SignalDatabase
import config

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('scheduler.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

class SignalScheduler:
    """
    Automated signal generation scheduler that runs market scans at regular intervals.
    """
    
    def __init__(self):
        """Initialize the scheduler with signal generator and database."""
        self.signal_generator = RSISignalGenerator()
        self.db = SignalDatabase()
        logger.info("Signal Scheduler initialized")
    
    def run_signal_scan(self) -> None:
        """
        Execute a complete market scan and save signals to database.
        This is the main scheduled task that runs hourly.
        """
        try:
            start_time = datetime.now()
            logger.info(f"Starting scheduled signal scan at {start_time}")
            
            # Load scan list
            scan_symbols = load_scan_list()
            if not scan_symbols:
                logger.warning("No symbols found in scan list")
                return
            
            logger.info(f"Scanning {len(scan_symbols)} symbols: {', '.join(scan_symbols)}")
            
            # Run market scan
            buy_signals, sell_signals = self.signal_generator.scan_market(scan_symbols)
            
            # Log results
            total_signals = len(buy_signals) + len(sell_signals)
            logger.info(f"Scan completed - Buy signals: {len(buy_signals)}, Sell signals: {len(sell_signals)}")
            
            if buy_signals:
                logger.info(f"Buy signals: {', '.join(buy_signals)}")
            
            if sell_signals:
                logger.info(f"Sell signals: {', '.join(sell_signals)}")
            
            # Get database statistics
            stats = self.db.get_database_stats()
            logger.info(f"Database stats - Total signals: {stats['total_signals']}, Today: {stats['signals_today']}")
            
            end_time = datetime.now()
            duration = (end_time - start_time).total_seconds()
            logger.info(f"Signal scan completed in {duration:.2f} seconds")
            
        except Exception as e:
            logger.error(f"Error during scheduled signal scan: {str(e)}")
            raise
    
    def cleanup_old_signals(self) -> None:
        """
        Clean up old signals from the database to prevent it from growing too large.
        This runs daily to maintain database performance.
        """
        try:
            logger.info("Starting database cleanup")
            
            # Delete signals older than 30 days
            deleted_count = self.db.delete_old_signals(days=30)
            logger.info(f"Cleaned up {deleted_count} old signals from database")
            
            # Get updated statistics
            stats = self.db.get_database_stats()
            logger.info(f"Database size after cleanup: {stats['database_size_mb']:.2f} MB")
            
        except Exception as e:
            logger.error(f"Error during database cleanup: {str(e)}")
    
    def health_check(self) -> bool:
        """
        Perform a health check to ensure all components are working.
        
        Returns:
            bool: True if all systems are healthy, False otherwise
        """
        try:
            # Check database connection
            stats = self.db.get_database_stats()
            logger.info(f"Health check - Database accessible, {stats['total_signals']} total signals")
            
            # Check if we can load scan list
            scan_symbols = load_scan_list()
            logger.info(f"Health check - Scan list loaded, {len(scan_symbols)} symbols")
            
            return True
            
        except Exception as e:
            logger.error(f"Health check failed: {str(e)}")
            return False
    
    def start_scheduler(self) -> None:
        """
        Start the scheduled tasks and run the scheduler loop.
        """
        logger.info("Starting Signal Scheduler...")
        
        # Schedule hourly signal scans
        schedule.every().hour.at(":00").do(self.run_signal_scan)
        
        # Schedule daily cleanup at 2 AM
        schedule.every().day.at("02:00").do(self.cleanup_old_signals)
        
        # Schedule health checks every 6 hours
        schedule.every(6).hours.do(self.health_check)
        
        # Run initial health check
        if not self.health_check():
            logger.error("Initial health check failed. Exiting.")
            sys.exit(1)
        
        logger.info("Scheduler started successfully")
        logger.info("Scheduled tasks:")
        logger.info("  - Signal scan: Every hour at :00")
        logger.info("  - Database cleanup: Daily at 02:00")
        logger.info("  - Health check: Every 6 hours")
        
        # Run the scheduler loop
        try:
            while True:
                schedule.run_pending()
                time.sleep(60)  # Check every minute
                
        except KeyboardInterrupt:
            logger.info("Scheduler stopped by user")
        except Exception as e:
            logger.error(f"Scheduler error: {str(e)}")
            raise

def run_once() -> None:
    """
    Run a single signal scan immediately (useful for testing or manual execution).
    """
    scheduler = SignalScheduler()
    logger.info("Running single signal scan...")
    scheduler.run_signal_scan()
    logger.info("Single scan completed")

def main():
    """
    Main entry point for the scheduler.
    """
    if len(sys.argv) > 1 and sys.argv[1] == "--once":
        run_once()
    else:
        scheduler = SignalScheduler()
        scheduler.start_scheduler()

if __name__ == "__main__":
    main()