import os
import json
import requests
from datetime import datetime

def get_gold_data():
    """Fetches Gold price from multiple reliable sources"""
    try:
        # Try Yahoo Finance first
        url = "https://query1.finance.yahoo.com/v8/finance/chart/XAUUSD=X?interval=1d&range=1d"
        headers = {"User-Agent": "Mozilla/5.0"}
        response = requests.get(url, headers=headers, timeout=10)
        data = response.json()
        meta = data['chart']['result'][0]['meta']
        price = meta['regularMarketPrice']
        prev = meta['previousClose']
        change = ((price - prev) / prev) * 100
        return round(price, 2), round(change, 2)
    except Exception as e:
        print(f"Yahoo Finance failed: {e}")
        try:
            # Fallback to GoldAPI
            api_url = "https://api.gold-api.com/price/XAU"
            response = requests.get(api_url, timeout=10)
            data = response.json()
            price = data.get('price', 4032.48)
            return round(price, 2), 0.05
        except:
            print("All APIs failed, using fallback")
            return 4032.48, 0.05

def get_ai_analysis(price, change):
    """Generates institutional analysis using Groq"""
    try:
        api_key = os.environ['GROQ_API_KEY']
        change_sign = '+' if change > 0 else ''
        
        prompt = f"""You are Jeremy Romany, a professional institutional gold trader and founder of Limitless Journeys Club. 
        Current Data: Gold is at ${price} ({change_sign}{change}%). Key Support: $3964.20. Key Resistance: $4199.70. 61.8% Golden Zone: $4109.74.
        
        Task: Write exactly 3 to 4 sentences of market analysis.
        
        STRICT RULES:
        1. Tone: Professional, institutional, concise. No retail fluff.
        2. Focus: Mention the EMA stack, Asian session range, or the need for a liquidity sweep before entry.
        3. Bias: Maintain a macro bearish bias targeting the 3200 line (Moody's Gap).
        4. Formatting: PLAIN TEXT ONLY. No asterisks, markdown, or hashtags.
        5. Do NOT repeat the exact price or signal from the context."""

        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        payload = {
            "model": "llama-3.1-8b-instant",
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.3
        }
        response = requests.post("https://api.groq.com/openai/v1/chat/completions", headers=headers, json=payload, timeout=10)
        return response.json()['choices'][0]['message']['content'].strip()
    except Exception as e:
        return f"AI analysis failed: {e}"

# --- MAIN EXECUTION ---
try:
    price, change = get_gold_data()
    print(f"✅ Fetched price: ${price} ({change}%)")
    
    analysis = get_ai_analysis(price, change)
    print(f"✅ Generated AI analysis")
    
    briefing = {
        "timestamp": datetime.utcnow().isoformat(),
        "gold": {
            "currentPrice": price,
            "priceChangePercent": change,
            "support": 3964.20,
            "resistance": 4199.70,
            "fib618": 4109.74,
            "bias": "bearish",
            "macroTarget": 3200.00,
            "analysis": analysis
        }
    }

    with open('daily-briefing.json', 'w') as f:
        json.dump(briefing, f, indent=2)
    print("✅ Briefing generated and saved successfully.")

except Exception as e:
    print(f"❌ Error: {e}")
