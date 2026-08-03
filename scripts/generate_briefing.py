import os
import json
import requests
from datetime import datetime

def get_gold_data():
    try:
        url = "https://query1.finance.yahoo.com/v8/finance/chart/XAUUSD=X?interval=1d&range=1d"
        headers = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)"}
        response = requests.get(url, headers=headers, timeout=10)
        data = response.json()
        meta = data['chart']['result'][0]['meta']
        price = meta['regularMarketPrice']
        prev = meta['previousClose']
        change = ((price - prev) / prev) * 100
        return round(price, 2), round(change, 2)
    except Exception as e:
        print(f"Warning: Live data fetch failed. Using fallback. Error: {e}")
        return 4032.48, 0.05 # Fallback data to ensure file is always created

def get_ai_analysis(price, change):
    try:
        api_key = os.environ.get('GROQ_API_KEY')
        if not api_key:
            return "API Key missing in GitHub Secrets."
        
        change_sign = '+' if change > 0 else ''
        prompt = f"""You are Jeremy Romany, a professional institutional gold trader. 
        Current Data: Gold is at ${price} ({change_sign}{change}%). Key Support: $3964.20. Key Resistance: $4199.70. 61.8% Golden Zone: $4109.74.
        
        Task: Write exactly 2 to 3 sentences of market analysis.
        STRICT RULES:
        1. Tone: Professional, institutional, concise. No retail fluff.
        2. Focus: Mention the EMA stack, Asian session range, or the need for a liquidity sweep before entry.
        3. Bias: Maintain a macro bearish bias targeting the 4000 line in the sand.
        4. Formatting: PLAIN TEXT ONLY. No asterisks or markdown."""

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
        return f"AI Analysis failed: {e}"

# --- MAIN EXECUTION ---
try:
    price, change = get_gold_data()
    analysis = get_ai_analysis(price, change)
    
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
    print("✅ Briefing generated successfully.")

except Exception as e:
    print(f"❌ Error: {e}")

with open('daily-briefing.json', 'w') as f:
    json.dump(briefing, f, indent=2)
print("✅ Briefing generated and saved successfully.")
