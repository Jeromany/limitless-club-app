import os
import requests

print("\n=== 🛰️ LIMITLESS JOURNEYS DATA RECON v2 ===")

def show(name, ok, detail):
    print(f"{'✅' if ok else '❌'} {name}: {detail}")

# 1 Yahoo RAW spot (keyless)
try:
    r = requests.get("https://query1.finance.yahoo.com/v8/finance/chart/XAUUSD=X?interval=1d&range=5d",
                     headers={"User-Agent": "Mozilla/5.0"}, timeout=10)
    if r.status_code == 200:
        show("Yahoo RAW Spot", True, f"${r.json()['chart']['result'][0]['meta']['regularMarketPrice']}")
    else:
        show("Yahoo RAW Spot", False, f"HTTP {r.status_code}")
except Exception as e:
    show("Yahoo RAW Spot", False, str(e)[:80])

# 2 TwelveData (keyed) - spot OHLC + price
key = os.environ.get("fe0e1b8963cb434497bc6fe92dc7e65a")
if key:
    try:
        r = requests.get("https://api.twelvedata.com/time_series",
                         params={"symbol": "XAU/USD", "interval": "1day", "outputsize": 5, "apikey": key}, timeout=10)
        d = r.json()
        if r.status_code == 200 and "values" in d:
            show("TwelveData Spot", True, f"latest close ${d['values'][0]['close']}")
        else:
            show("TwelveData Spot", False, str(d)[:120])
    except Exception as e:
        show("TwelveData Spot", False, str(e)[:80])
else:
    show("TwelveData Spot", False, "no key in secrets")

# 3 MetalpriceAPI (keyed) - spot now
key = os.environ.get("f5914bcc214eab01d2928c669352e519")
if key:
    try:
        r = requests.get("https://api.metalpriceapi.com/v1/latest",
                         params={"api_key": key, "base": "USD", "quotes": "XAU"}, timeout=10)
        d = r.json()
        if r.status_code == 200 and d.get("success") and d.get("rates", {}).get("XAU"):
            show("MetalpriceAPI Spot", True, f"${round(1 / d['rates']['XAU'], 2)}")
        else:
            show("MetalpriceAPI Spot", False, str(d)[:120])
    except Exception as e:
        show("MetalpriceAPI Spot", False, str(e)[:80])
else:
    show("MetalpriceAPI Spot", False, "no key in secrets")

# 4 Alpha Vantage (keyed) - spot now
key = os.environ.get("VEWK52O07C1UW6FX")
if key:
    try:
        r = requests.get("https://www.alphavantage.co/query",
                         params={"function": "CURRENCY_EXCHANGE_RATE", "from_currency": "XAU",
                                 "to_currency": "USD", "apikey": key}, timeout=10)
        rate = r.json().get("Realtime Currency Exchange Rate", {}).get("5. Exchange Rate")
        show("AlphaVantage Spot", bool(rate), f"${rate}" if rate else str(r.json())[:120])
    except Exception as e:
        show("AlphaVantage Spot", False, str(e)[:80])
else:
    show("AlphaVantage Spot", False, "no key in secrets")

# 5 Finnhub (keyed) - spot now
key = os.environ.get("d8t18p9r01qh5rf0tkp0d8t18p9r01qh5rf0tkpg")
if key:
    try:
        r = requests.get("https://finnhub.io/api/v1/quote",
                         params={"symbol": "OANDA:XAU_USD", "token": key}, timeout=10)
        d = r.json()
        show("Finnhub Spot", bool(d.get("c")), f"${d['c']}" if d.get("c") else str(d)[:120])
    except Exception as e:
        show("Finnhub Spot", False, str(e)[:80])
else:
    show("Finnhub Spot", False, "no key in secrets")

# 6 Gold-API (keyless) - spot now
try:
    r = requests.get("https://api.gold-api.com/price/XAU", timeout=10)
    if r.status_code == 200:
        show("Gold-API Spot", True, f"${r.json().get('price')}")
    else:
        show("Gold-API Spot", False, f"HTTP {r.status_code}")
except Exception as e:
    show("Gold-API Spot", False, str(e)[:80])

print("\n=== 🛰️ END RECON v2 ===\n")
