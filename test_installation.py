#!/usr/bin/env python3
"""
Installation and functionality test script for Mojila Signal

This script verifies that all dependencies are installed correctly
and that the basic functionality works as expected.
"""

import sys
import traceback
from datetime import datetime


def test_imports():
    """
    Test that all required modules can be imported.
    """
    print("Testing imports...")
    
    try:
        import yfinance as yf
        print("✓ yfinance imported successfully")
    except ImportError as e:
        print(f"✗ Failed to import yfinance: {e}")
        return False
    
    try:
        import pandas as pd
        print("✓ pandas imported successfully")
    except ImportError as e:
        print(f"✗ Failed to import pandas: {e}")
        return False
    
    try:
        import numpy as np
        print("✓ numpy imported successfully")
    except ImportError as e:
        print(f"✗ Failed to import numpy: {e}")
        return False
    
    try:
        import config
        print("✓ config module imported successfully")
    except ImportError as e:
        print(f"✗ Failed to import config: {e}")
        return False
    
    try:
        from main import RSISignalGenerator
        print("✓ RSISignalGenerator imported successfully")
    except ImportError as e:
        print(f"✗ Failed to import RSISignalGenerator: {e}")
        return False
    
    return True


def test_basic_functionality():
    """
    Test basic functionality with a simple stock analysis.
    """
    print("\nTesting basic functionality...")
    
    try:
        from main import RSISignalGenerator
        
        # Initialize signal generator
        signal_generator = RSISignalGenerator()
        print("✓ RSISignalGenerator initialized successfully")
        
        # Test with a reliable stock (Apple)
        print("Testing stock data retrieval for AAPL...")
        result = signal_generator.generate_signals('AAPL', period='1mo')
        
        if 'error' in result:
            print(f"✗ Error generating signals: {result['error']}")
            return False
        
        # Verify result structure
        required_fields = ['symbol', 'currentPrice', 'currentRSI', 'currentSignal', 
                          'signalStrength', 'recentBuySignals', 'recentSellSignals', 
                          'lastUpdated', 'data']
        
        for field in required_fields:
            if field not in result:
                print(f"✗ Missing required field: {field}")
                return False
        
        print("✓ Signal generation completed successfully")
        print(f"  Symbol: {result['symbol']}")
        print(f"  Current Price: ${result['currentPrice']}")
        print(f"  Current RSI: {result['currentRSI']}")
        print(f"  Current Signal: {result['currentSignal']}")
        print(f"  Signal Strength: {result['signalStrength']}")
        
        return True
        
    except Exception as e:
        print(f"✗ Error in basic functionality test: {e}")
        traceback.print_exc()
        return False


def test_configuration():
    """
    Test that configuration values are loaded correctly.
    """
    print("\nTesting configuration...")
    
    try:
        import config
        
        # Check that key configuration values exist
        required_configs = [
            'RSI_PERIOD', 'OVERSOLD_THRESHOLD', 'OVERBOUGHT_THRESHOLD',
            'DEFAULT_PERIOD', 'DEFAULT_STOCKS', 'MAX_RECENT_DAYS'
        ]
        
        for config_name in required_configs:
            if not hasattr(config, config_name):
                print(f"✗ Missing configuration: {config_name}")
                return False
        
        print("✓ All required configurations found")
        print(f"  RSI Period: {config.RSI_PERIOD}")
        print(f"  Oversold Threshold: {config.OVERSOLD_THRESHOLD}")
        print(f"  Overbought Threshold: {config.OVERBOUGHT_THRESHOLD}")
        print(f"  Default Stocks: {len(config.DEFAULT_STOCKS)} stocks")
        
        return True
        
    except Exception as e:
        print(f"✗ Error in configuration test: {e}")
        return False


def test_multiple_stocks():
    """
    Test analysis of multiple stocks.
    """
    print("\nTesting multiple stock analysis...")
    
    try:
        from main import RSISignalGenerator
        
        signal_generator = RSISignalGenerator()
        
        # Test with a small set of stocks
        test_stocks = ['AAPL', 'MSFT']
        results = signal_generator.analyze_multiple_stocks(test_stocks, period='1mo')
        
        if len(results) != len(test_stocks):
            print(f"✗ Expected {len(test_stocks)} results, got {len(results)}")
            return False
        
        successful_analyses = 0
        for result in results:
            if 'error' not in result:
                successful_analyses += 1
        
        print(f"✓ Multiple stock analysis completed")
        print(f"  Analyzed: {len(test_stocks)} stocks")
        print(f"  Successful: {successful_analyses} analyses")
        
        return successful_analyses > 0
        
    except Exception as e:
        print(f"✗ Error in multiple stock test: {e}")
        return False


def run_all_tests():
    """
    Run all tests and provide a summary.
    """
    print("=" * 60)
    print("MOJILA SIGNAL - INSTALLATION TEST")
    print("=" * 60)
    print(f"Test started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Python version: {sys.version}")
    print("=" * 60)
    
    tests = [
        ("Import Test", test_imports),
        ("Configuration Test", test_configuration),
        ("Basic Functionality Test", test_basic_functionality),
        ("Multiple Stocks Test", test_multiple_stocks)
    ]
    
    passed_tests = 0
    total_tests = len(tests)
    
    for test_name, test_function in tests:
        print(f"\n{'='*20} {test_name} {'='*20}")
        try:
            if test_function():
                passed_tests += 1
                print(f"✓ {test_name} PASSED")
            else:
                print(f"✗ {test_name} FAILED")
        except Exception as e:
            print(f"✗ {test_name} FAILED with exception: {e}")
    
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    print(f"Tests passed: {passed_tests}/{total_tests}")
    
    if passed_tests == total_tests:
        print("🎉 All tests passed! Mojila Signal is ready to use.")
        print("\nTo run the main application:")
        print("  python main.py")
        print("\nTo see usage examples:")
        print("  python examples.py")
    else:
        print("❌ Some tests failed. Please check the error messages above.")
        print("\nCommon solutions:")
        print("1. Install dependencies: pip install -r requirements.txt")
        print("2. Check internet connection for stock data retrieval")
        print("3. Ensure all project files are in the same directory")
    
    print("=" * 60)
    
    return passed_tests == total_tests


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)