#!/usr/bin/env python3
"""
Test script to verify yfinance fixes work properly
"""
import sys
import time
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
import yfinance as yf

def configure_yfinance_session():
    """Configure yfinance with proper headers and retry logic"""
    session = requests.Session()
    retry_strategy = Retry(
        total=3,
        backoff_factor=1,
        status_forcelist=[429, 500, 502, 503, 504],
    )
    adapter = HTTPAdapter(max_retries=retry_strategy)
    session.mount("http://", adapter)
    session.mount("https://", adapter)
    
    # Set proper headers to mimic a real browser
    session.headers.update({
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
        'Accept-Encoding': 'gzip, deflate',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
    })
    
    return session

def test_symbol(symbol, name):
    """Test fetching data for a specific symbol"""
    print(f"\nTesting {name} ({symbol})...")
    
    try:
        # Configure session
        session = configure_yfinance_session()
        
        # Create ticker with custom session
        ticker = yf.Ticker(symbol)
        ticker._session = session
        
        # Try to get data
        hist = ticker.history(period='2d', interval='1d', progress=False)
        
        if not hist.empty and len(hist) >= 2:
            current = hist['Close'].iloc[-1]
            previous = hist['Close'].iloc[-2]
            change = current - previous
            change_pct = (change / previous) * 100
            
            print(f"✅ SUCCESS: {name}")
            print(f"   Current: {current:.2f}")
            print(f"   Change: {change:+.2f} ({change_pct:+.2f}%)")
            return True
        else:
            print(f"❌ FAILED: {name} - No data available")
            return False
            
    except Exception as e:
        print(f"❌ FAILED: {name} - Error: {e}")
        return False

def main():
    """Main test function"""
    print("Testing yfinance fixes...")
    print("=" * 50)
    
    # Test symbols
    test_symbols = [
        ('^GSPC', 'S&P 500'),
        ('SPY', 'SPY ETF'),
        ('^IXIC', 'NASDAQ'),
        ('QQQ', 'QQQ ETF'),
        ('^VIX', 'VIX'),
        ('VXX', 'VXX ETF'),
        ('^TNX', '10Y Treasury'),
        ('AAPL', 'Apple'),
        ('GOOGL', 'Google'),
        ('MSFT', 'Microsoft')
    ]
    
    success_count = 0
    total_count = len(test_symbols)
    
    for symbol, name in test_symbols:
        if test_symbol(symbol, name):
            success_count += 1
        time.sleep(1)  # Delay between requests
    
    print("\n" + "=" * 50)
    print(f"Test Results: {success_count}/{total_count} symbols successful")
    
    if success_count >= total_count * 0.7:  # 70% success rate
        print("✅ yfinance fixes appear to be working!")
        return True
    else:
        print("❌ yfinance still has issues")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
