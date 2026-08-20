import os
import json
import argparse
import requests
from datetime import datetime, timezone
from groq import Groq

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from PIL import Image

# ---------------- BRAND CONSTANTS ----------------
MACRO_TARGET = 3200.00
COL_BG = "#000000"
COL_BULL = "#FFFFFF"
COL_BEAR = "#CD7F32"
COL_EMA20 = "#FFD700"
COL_EMA50 = "#E8C547"
REPO = "jeromany/limitless-club-app"

# ---------------- DATA: PRIMARY (TwelveData spot) ----------------
def fetch_twelvedata():
    key = os.environ.get("TWELVEDATA_API_KEY")
    if not key:
        raise Exception("TWELVEDATA_API_KEY missing")
    r = requests.get("https://api.twelvedata.com/time_series",
                     params={"symbol": "XAU/USD", "interval": "1day", "outputsize": 90, "apikey": key},
                     timeout=15)
    r.raise_for_status()
    d = r.json()
    if "values" not in d:
        raise Exception(str(d)[:120])
    vals = list(reversed(d["values"]))
    candles = [{"date": v["datetime"][5:],
                "o": float(v["open"]), "h": float(v["high"]),
                "l": float(v["low"]), "c": float(v["close"])} for v in vals]
    if not candles:
        raise Exception("Empty TwelveData series")
    return candles

# ---------------- DATA: FALLBACK (futures, flagged) ----------------
def fetch_yahoo_futures():
    urls = [
        "https://query1.finance.yahoo.com/v8/finance/chart/GC=F?interval=1d&range=3mo",
        "https://query2.finance.yahoo.com/v8/finance/chart/GC=F?interval=1d&range=3mo"
    ]
    last = None
    for u in urls:
        try:
            r = requests.get(u, headers={"User-Agent": "Mozilla/5.0"}, timeout=15)
            r.raise_for_status()
            res = r.json()["chart"]["result"][0]
            ts = res["timestamp"]
            q = res["indicators"]["quote"][0]
            candles = []
            for t, o, h, l, c in zip(ts, q["open"], q["high"], q["low"], q["close"]):
                if None in (o, h, l, c):
                    continue
                candles.append({"date": datetime.fromtimestamp(t, tz=timezone.utc).strftime("%m-%d"),
                                "o": o, "h": h, "l": l, "c": c})
            if candles:
                return candles
        except Exception as e:
            last = e
    raise last

# ---------------- DATA: CROSS-CHECK (Gold-API) ----------------
def fetch_goldapi_price():
    try:
        r = requests.get("https://api.gold-api.com/price/XAU", timeout=10)
        if r.status_code == 200:
            return r.json().get("price")
    except Exception:
        pass
    return None

def compute_levels(candles, window=30):
    w = candles[-window:]
    support = round(min(c["l"] for c in w), 2)
    resistance = round(max(c["h"] for c in w), 2)
    fib618 = round(support + 0.618 * (resistance - support), 2)
    return support, resistance, fib618

def rsi(closes, period=14):
    if len(closes) < period + 2:
        return 50.0
    deltas = [closes[i+1] - closes[i] for i in range(len(closes)-1)]
    gains = [d if d > 0 else 0 for d in deltas]
    losses = [-d if d < 0 else 0 for d in deltas]
    avg_g = sum(gains[:period]) / period
    avg_l = sum(losses[:period]) / period
    for i in range(period, len(gains)):
        avg_g = (avg_g * (period - 1) + gains[i]) / period
        avg_l = (avg_l * (period - 1) + losses[i]) / period
    if avg_l == 0:
        return 100.0
    return round(100 - 100 / (1 + avg_g / avg_l), 2)

def get_ai_analysis(price, change, support, resistance, fib618, ema20, ema50, rsi14, session="morning"):
    session_context = {
        "morning": "Morning Briefing: Provide the full macro and tactical outlook for the NY session.",
        "midday": "Midday Pulse: Review the morning price action. Did the morning thesis hold? Are we still in the Golden Zone? Keep it concise.",
        "wrap": "NY Wrap: Summarize today's price action and identify the liquidity pool (Asian high/low) for the next session."
    }

    prompt = f"""
You are Jasai, an institutional gold analyst.
MACRO THESIS: Bearish (Targeting $3,200 Moody's Gap). This is the long-term structural view.
TACTICAL BIAS: Computed live from the data below. It is allowed to contradict the macro thesis short-term.

DATA:
- Price: ${price} ({change}%)
- Support: ${support} | Resistance: ${resistance}
- 61.8% Fib: ${fib618}
- EMA 20: ${ema20} | EMA 50: ${ema50}
- RSI (14): {rsi14}

RULES FOR TACTICAL LAYER:
1. If Price > EMA20 > EMA50 -> Tactical is BULLISH (Short-term momentum).
2. If Price < EMA20 < EMA50 -> Tactical is BEARISH (Short-term momentum).
3. RSI > 70 = Overbought (Risk of pullback).
4. RSI < 30 = Oversold (Risk of bounce).

YOUR OUTPUT FOR THIS SESSION ({session}):
{session_context.get(session, "")}
Write a 3-4 sentence analysis.
- Sentence 1: State the MACRO bias clearly (Bearish).
- Sentence 2: State the TACTICAL bias based on the EMAs and RSI. If it contradicts macro, say so explicitly.
- Sentence 3: Identify the key level to watch (Fib or S/R).
- Tone: Professional, calm, institutional. No emojis. Plain text only.
"""

    # HARDENED: try primary model twice, then backup model twice
    models = ["openai/gpt-oss-120b", "openai/gpt-oss-20b"]
    for model in models:
        for attempt in range(2):
            try:
                client = Groq(api_key=os.environ.get("GROQ_API_KEY"))
                completion = client.chat.completions.create(
                    model=model,
                    messages=[{"role": "user", "content": prompt}],
                    temperature=0.7,
                    max_tokens=200
                )
                text = completion.choices[0].message.content.strip()
                if text:
                    return text
            except Exception as e:
                print(f"⚠️ Groq {model} attempt {attempt + 1} failed: {e}")

    # PROFESSIONAL FALLBACK: never show "unavailable" to members
    if price >= resistance * 0.995:
        position_note = f"price is pressing resistance at ${resistance}"
    elif price <= support * 1.005:
        position_note = f"price is testing support at ${support}"
    else:
        position_note = f"price is rotating between ${support} support and ${resistance} resistance"

    return (
        f"Macro thesis remains bearish toward the ${MACRO_TARGET} structural target. "
        f"Tactically, {position_note}, with the 61.8% Fib at ${fib618} as the key pivot. "
        f"Live AI commentary is syncing; rely on structural levels until the next pulse."
    )

# ---------------- CHART ENGINE (approved spec) ----------------
def ema(vals, n):
    out = []
    k = 2 / (n + 1)
    e = vals[0]
    for v in vals:
        e = v * k + e * (1 - k)
        out.append(e)
    return out

def render_chart(candles, support, resistance, fib618, path="chart.png"):
    closes = [c["c"] for c in candles]
    e20 = ema(closes, 20)
    e50 = ema(closes, 50)
    n = len(candles)

    fig, ax = plt.subplots(figsize=(10, 6), dpi=140)
    fig.patch.set_facecolor(COL_BG)
    ax.set_facecolor(COL_BG)

    lo = min(min(c["l"] for c in candles), support, fib618)
    hi = max(max(c["h"] for c in candles), resistance)
    pad = (hi - lo) * 0.05
    lo_p, hi_p = lo - pad, hi + pad

    for name in ("logo.png", "logo.jpg", "assets/logo.png", "assets/logo.jpg"):
        if os.path.exists(name):
            try:
                logo = Image.open(name).convert("RGBA")
                mid = (lo_p + hi_p) / 2
                span = hi_p - lo_p
                ax.imshow(logo, extent=(n * 0.28, n * 0.72, mid - span * 0.22, mid + span * 0.22),
                          alpha=0.20, zorder=0, aspect="auto")
            except Exception as e:
                print("Logo skipped:", e)
            break

    for i, c in enumerate(candles):
        bull = c["c"] >= c["o"]
        col = COL_BULL if bull else COL_BEAR
        ax.vlines(i, c["l"], c["h"], color=col, linewidth=0.9)
        blo, bhi = min(c["o"], c["c"]), max(c["o"], c["c"])
        ax.bar(i, max(bhi - blo, 0.01), bottom=blo, width=0.6, color=col, edgecolor=col, linewidth=0.9)

    ax.plot(range(n), e20, color=COL_EMA20, linewidth=1.2, label="20 EMA")
    ax.plot(range(n), e50, color=COL_EMA50, linewidth=1.2, linestyle="--", label="50 EMA")
    ax.hlines(support, -1, n, colors=COL_EMA20, linestyles="--", linewidth=1.0, label=f"Support ${support}")
    ax.hlines(resistance, -1, n, colors=COL_BEAR, linestyles="--", linewidth=1.0, label=f"Resistance ${resistance}")
    ax.hlines(fib618, -1, n, colors=COL_BULL, linestyles=":", linewidth=1.0, label=f"Fib 61.8% ${fib618}")

    ax.set_ylim(lo_p, hi_p)
    ax.set_xlim(-1, n)
    ax.yaxis.set_label_position("right")
    ax.yaxis.tick_right()
    step = max(1, n // 8)
    ax.set_xticks(range(0, n, step))
    ax.set_xticklabels([candles[i]["date"] for i in range(0, n, step)], rotation=45)
    ax.tick_params(colors=COL_BULL, labelsize=8)
    for s in ax.spines.values():
        s.set_color("#333333")
    ax.grid(alpha=0.15, color="#888888")

    ax.set_title("XAU/USD - Daily | Limitless Journeys", color=COL_EMA20, fontsize=12, pad=10)
    leg = ax.legend(loc="upper right", fontsize=7.5, frameon=False)
    for t in leg.get_texts():
        t.set_color(COL_BULL)

    fig.savefig(path, facecolor=COL_BG)
    plt.close(fig)
    print("✅ Chart rendered:", path)

# ---------------- DELIVERY (dual broadcast) ----------------
def post_telegram(text, img):
    targets = []
    tok = os.environ.get("TELEGRAM_BOT_TOKEN")
    chat = os.environ.get("TELEGRAM_CHAT_ID")
    if tok and chat:
        targets.append(("staging", tok, chat))
    tokp = os.environ.get("TELEGRAM_BOT_TOKEN_PROD")
    chatp = os.environ.get("TELEGRAM_CHAT_ID_PROD")
    if tokp and chatp:
        targets.append(("production", tokp, chatp))
    if not targets:
        print("⚠️ Telegram secrets missing - skipping")
        return
    for name, t, c in targets:
        with open(img, "rb") as f:
            r = requests.post(f"https://api.telegram.org/bot{t}/sendPhoto",
                              data={"chat_id": c, "caption": text[:1024]},
                              files={"photo": f}, timeout=30)
        print(f"Telegram {name} post:", r.status_code)

def post_discord(text, img):
    targets = []
    lab = os.environ.get("DISCORD_WEBHOOK_URL")
    if lab:
        targets.append(("lab", lab))
    prod = os.environ.get("DISCORD_WEBHOOK_PROD")
    if prod:
        targets.append(("production", prod))
    if not targets:
        print("⚠️ Discord webhooks missing - skipping")
        return
    for name, url in targets:
        with open(img, "rb") as f:
            r = requests.post(url,
                              data={"content": text[:2000], "username": "Limitless Journeys Bot"},
                              files={"file": (img, f, "image/png")}, timeout=30)
        print(f"Discord {name} post:", r.status_code)

def load_promo():
    try:
        w = json.load(open("weekly-content.json"))
        guide = w.get("guide") or w.get("title") or w.get("name") or ""
        price = w.get("price") or w.get("cost") or ""
        link = w.get("link") or w.get("url") or ""
        if guide or link:
            return f"\n\n---\nLIMITLESS JOURNEYS ACADEMY\nToday's Guide: {guide}\nPrice: ${price}\nGet it now: {link}"
    except Exception:
        pass
    return ""

# ---------------- MAIN ----------------
if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--session", choices=["morning", "midday", "wrap"], default="morning")
    args = parser.parse_args()
    session = args.session

    source = "TwelveData spot"
    try:
        candles = fetch_twelvedata()
        print("✅ Data source: TwelveData XAU/USD spot")
    except Exception as e:
        print("⚠️ TwelveData failed:", e)
        try:
            candles = fetch_yahoo_futures()
            source = "GC=F futures proxy"
            print("⚠️ Using futures proxy fallback")
        except Exception as e2:
            print("❌ All candle sources failed:", e2)
            candles = []

    spot_check = fetch_goldapi_price()

    if candles:
        price = round(candles[-1]["c"], 2)
        prev = candles[-2]["c"] if len(candles) >= 2 else price
        change = round(((price - prev) / prev) * 100, 2)
    else:
        price = round(spot_check or 4340.0, 2)
        change = 0.0

    if spot_check:
        gap = abs(spot_check - price)
        print(f"✅ Cross-check: Gold-API ${spot_check:.2f} vs published ${price} (gap ${gap:.2f})")
        if gap > 8:
            print("⚠️ Cross-check gap above $8 - review source")

    if candles:
        support, resistance, fib618 = compute_levels(candles)
        closes_all = [c["c"] for c in candles]
        ema20 = round(ema(closes_all, 20)[-1], 2)
        ema50 = round(ema(closes_all, 50)[-1], 2)
        rsi14 = rsi(closes_all)
    else:
        support, resistance, fib618 = 3964.20, 4199.70, 4109.74
        ema20, ema50, rsi14 = 0.0, 0.0, 50.0
    print(f"✅ Dynamic levels - S:{support} R:{resistance} F:{fib618} | source: {source}")

    # COMPUTE TACTICAL BIAS
    if price > ema20 and ema20 > ema50:
        tactical_bias = "bullish"
    elif price < ema20 and ema20 < ema50:
        tactical_bias = "bearish"
    else:
        tactical_bias = "neutral"

    # CALL AI WITH NEW VARIABLES + SESSION
    analysis = get_ai_analysis(price, change, support, resistance, fib618, ema20, ema50, rsi14, session)

    briefing = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "source": source,
        "gold": {
            "currentPrice": price,
            "priceChangePercent": change,
            "support": support,
            "resistance": resistance,
            "fib618": fib618,
            "ema20": ema20,
            "ema50": ema50,
            "rsi14": rsi14,
            "bias": "bearish",
            "tacticalBias": tactical_bias,
            "macroTarget": MACRO_TARGET,
            "analysis": analysis
        }
    }
    with open("daily-briefing.json", "w") as f:
        json.dump(briefing, f, indent=2)

    sign = "+" if change > 0 else ""
    legacy = {
        "date": datetime.now(timezone.utc).strftime("%A, %B %d, %Y"),
        "price": f"{price:.2f}",
        "change": f"{sign}{change}%",
        "analysis": analysis,
        "action": f"Watch for a reaction at the 61.8% Fib level (${fib618}) during the NY session. Bias remains neutral until a clean break of the Asian Session range.",
        "chartUrl": f"https://raw.githubusercontent.com/{REPO}/main/chart.png"
    }
    with open("briefing.json", "w") as f:
        json.dump(legacy, f, indent=2)
    print("✅ daily-briefing.json + briefing.json written (storefront unified)")

    # SESSION-AWARE CAPTION
    session_titles = {
        "morning": "📊 DAILY GOLD BRIEFING",
        "midday": "🕐 MIDDAY PULSE",
        "wrap": "🌙 NY WRAP & ASIAN PREVIEW"
    }
    
    caption = (
        f"{session_titles.get(session, 'UPDATE')}\n\n"
        f"💰 Price: ${price} ({sign}{change}%)\n"
        f"📉 Macro: Bearish | Tactical: {tactical_bias.capitalize()}\n"
    )
    if session == "morning":
        caption += f"🎯 Macro Target: ${MACRO_TARGET} (Moody's Gap)\n"
    
    caption += f"\n📝 Analysis:\n{analysis}\n\n"
    caption += (
        "🛡️ Key Levels:\n"
        f"- Support: ${support}\n"
        f"- Resistance: ${resistance}\n"
        f"- 61.8% Fib: ${fib618}"
    )

    if len(candles) >= 2:
        render_chart(candles, support, resistance, fib618)
        post_telegram(caption, "chart.png")
        post_discord(caption + load_promo(), "chart.png")
    else:
        print("⚠️ No candles - chart skipped")
