import os
import json
import requests
from datetime import datetime, timezone

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

# ---------------- DATA (futures-first, multi-source) ----------------
def fetch_chart_payload():
    urls = [
        "https://query1.finance.yahoo.com/v8/finance/chart/GC=F?interval=1d&range=3mo",
        "https://query2.finance.yahoo.com/v8/finance/chart/GC=F?interval=1d&range=3mo",
        "https://query1.finance.yahoo.com/v8/finance/chart/XAUUSD=X?interval=1d&range=3mo",
        "https://query2.finance.yahoo.com/v8/finance/chart/XAUUSD=X?interval=1d&range=3mo"
    ]
    last_err = None
    for u in urls:
        try:
            r = requests.get(u, headers={"User-Agent": "Mozilla/5.0"}, timeout=15)
            r.raise_for_status()
            print("✅ Data source:", u)
            return r.json()["chart"]["result"][0]
        except Exception as e:
            last_err = e
            print("⚠️ Source failed:", u, "-", e)
    raise last_err


def get_gold_series():
    res = fetch_chart_payload()
    meta = res["meta"]
    ts = res["timestamp"]
    q = res["indicators"]["quote"][0]
    candles = []
    for t, o, h, l, c in zip(ts, q["open"], q["high"], q["low"], q["close"]):
        if None in (o, h, l, c):
            continue
        candles.append({"date": datetime.fromtimestamp(t, tz=timezone.utc).strftime("%m-%d"),
                        "o": o, "h": h, "l": l, "c": c})
    if not candles:
        raise Exception("Empty candle series")
    price = round(meta.get("regularMarketPrice") or candles[-1]["c"], 2)
    prev = (meta.get("previousClose") or meta.get("chartPreviousClose")
            or (candles[-2]["c"] if len(candles) >= 2 else price))
    change = round(((price - prev) / prev) * 100, 2)
    return candles, price, change


def compute_levels(candles, window=30):
    w = candles[-window:]
    support = round(min(c["l"] for c in w), 2)
    resistance = round(max(c["h"] for c in w), 2)
    fib618 = round(support + 0.618 * (resistance - support), 2)
    return support, resistance, fib618


def get_ai_analysis(price, change, support, resistance, fib618):
    try:
        sign = "+" if change > 0 else ""
        prompt = f"""You are Jeremy Romany, a professional institutional gold trader and founder of Limitless Journeys Club.
        Current Data: Gold is at ${price} ({sign}{change}%). Key Support: ${support}. Key Resistance: ${resistance}. 61.8% Golden Zone: ${fib618}.

        Task: Write exactly 3 to 4 sentences of market analysis.

        STRICT RULES:
        1. Tone: Professional, institutional, concise. No retail fluff.
        2. Focus: Mention the EMA stack, Asian session range, or the need for a liquidity sweep before entry.
        3. Bias: Maintain a macro bearish bias targeting the 3200 line (Moody's Gap).
        4. Formatting: PLAIN TEXT ONLY. No asterisks, markdown, or hashtags.
        5. Do NOT repeat the exact price or signal from the context."""
        r = requests.post(
            "https://api.groq.com/openai/v1/chat/completions",
            headers={"Authorization": f"Bearer {os.environ['GROQ_API_KEY']}", "Content-Type": "application/json"},
            json={"model": "llama-3.1-8b-instant",
                  "messages": [{"role": "user", "content": prompt}],
                  "temperature": 0.3},
            timeout=20)
        return r.json()["choices"][0]["message"]["content"].strip()
    except Exception as e:
        return f"AI analysis unavailable: {e}"


# ---------------- CHART ENGINE v3 ----------------
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

    # Brand watermark BEHIND everything - never blocks a candle
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


# ---------------- DELIVERY ----------------
def post_telegram(text, img):
    tok = os.environ.get("TELEGRAM_BOT_TOKEN")
    chat = os.environ.get("TELEGRAM_CHAT_ID")
    if not tok or not chat:
        print("⚠️ Telegram secrets missing - skipping")
        return
    with open(img, "rb") as f:
        r = requests.post(f"https://api.telegram.org/bot{tok}/sendPhoto",
                          data={"chat_id": chat, "caption": text[:1024]},
                          files={"photo": f}, timeout=30)
    print("Telegram post:", r.status_code)


def post_discord(text, img):
    url = os.environ.get("DISCORD_WEBHOOK_URL")
    if not url:
        print("⚠️ Discord webhook missing - skipping")
        return
    with open(img, "rb") as f:
        r = requests.post(url,
                          data={"content": text[:2000], "username": "Limitless Journeys Bot"},
                          files={"file": (img, f, "image/png")}, timeout=30)
    print("Discord post:", r.status_code)


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
    try:
        candles, price, change = get_gold_series()
    except Exception as e:
        print("❌ All data sources failed:", e)
        candles, price, change = [], 4266.0, 0.05

    if candles:
        support, resistance, fib618 = compute_levels(candles)
    else:
        support, resistance, fib618 = 3964.20, 4199.70, 4109.74
    print(f"✅ Dynamic levels - S:{support} R:{resistance} F:{fib618}")

    analysis = get_ai_analysis(price, change, support, resistance, fib618)

    briefing = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "gold": {
            "currentPrice": price,
            "priceChangePercent": change,
            "support": support,
            "resistance": resistance,
            "fib618": fib618,
            "bias": "bearish",
            "macroTarget": MACRO_TARGET,
            "analysis": analysis
        }
    }
    with open("daily-briefing.json", "w") as f:
        json.dump(briefing, f, indent=2)
    print("✅ daily-briefing.json written")

    sign = "+" if change > 0 else ""
    caption = (
        "📊 DAILY GOLD BRIEFING\n\n"
        f"💰 Price: ${price} ({sign}{change}%)\n"
        "📉 Bias: Bearish\n"
        "🎯 Macro Target: $3,200 (Moody's Gap)\n\n"
        f"📝 Analysis:\n{analysis}\n\n"
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
