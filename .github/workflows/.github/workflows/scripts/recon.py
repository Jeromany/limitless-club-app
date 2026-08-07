import requests
import yfinance as yf

print("\n=== 🛰️ LIMITLESS JOURNEYS DATA RECON ===")

# 1. Yahoo Raw API (Spot)
try:
    r = requests.get("https://query1.finance.yahoo.com/v8/finance/chart/XAUUSD=X?interval=1d&range=5d", headers={"User-Agent": "Mozilla/5.0"}, timeout=10)
    print(f"1. Yahoo RAW Spot (XAUUSD=X): HTTP {r.status_code} -> {r.text[:80]}")
except Exception as e:
    print(f"1. Yahoo RAW Spot failed: {e}")

# 2. Yahoo Raw API (Futures - for comparison)
try:
    r = requests.get("https://query1.finance.yahoo.com/v8/finance/chart/GC=F?interval=1d&range=5d", headers={"User-Agent": "Mozilla/5.0"}, timeout=10)
    if r.status_code == 200:
        price = r.json()['chart']['result'][0]['meta']['regularMarketPrice']
        print(f"2. Yahoo RAW Futures (GC=F): HTTP 200 -> ${price}")
    else:
        print(f"2. Yahoo RAW Futures: HTTP {r.status_code}")
except Exception as e:
    print(f"2. Yahoo RAW Futures failed: {e}")

# 3. yfinance library (Spot) - bypasses some API blocks
try:
    ticker = yf.Ticker("XAUUSD=X")
    hist = ticker.history(period="5d")
    if not hist.empty:
        print(f"3. yfinance Spot (XAUUSD=X): SUCCESS. Last close: ${hist['Close'].iloc[-1]:.2f}")
    else:
        print("3. yfinance Spot (XAUUSD=X): Empty data")
except Exception as e:
    print(f"3. yfinance Spot failed: {e}")

# 4. Gold-API (Spot)
try:
    r = requests.get("https://api.gold-api.com/price/XAU", timeout=10)
    if r.status_code == 200:
        print(f"4. Gold-API Spot: HTTP 200 -> ${r.json().get('price')}")
    else:
        print(f"4. Gold-API Spot: HTTP {r.status_code}")
except Exception as e:
    print(f"4. Gold-API Spot failed: {e}")

print("\n=== 🛰️ END RECON ===\n")
