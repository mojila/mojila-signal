#!/usr/bin/env python3
import requests
import json

def test_api_endpoint():
    """Test the API endpoint to verify database-first loading."""
    try:
        # Test single stock endpoint
        response = requests.get('http://127.0.0.1:5001/api/stocks/AAPL')
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"Symbol: {data.get('symbol', 'N/A')}")
            print(f"Signal: {data.get('currentSignal', 'N/A')}")
            print(f"Source: {data.get('source', 'N/A')}")
            print(f"RSI: {data.get('currentRSI', 'N/A')}")
            
            if data.get('source') == 'database':
                print("✅ Successfully loaded from database!")
            elif data.get('source') == 'generated':
                print("⚠️  Generated new signal (not from database)")
            else:
                print("❓ Unknown source")
        else:
            print(f"Error: {response.text}")
            
    except Exception as e:
        print(f"Error testing API: {e}")

if __name__ == '__main__':
    test_api_endpoint()