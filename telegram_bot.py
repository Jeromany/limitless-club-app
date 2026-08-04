import os
import requests
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler

# --- THE BRAIN (Single Source of Truth) ---
GITHUB_JSON_URL = "https://raw.githubusercontent.com/jeromany/limitless-club-app/main/daily-briefing.json"

# --- PAYMENT GATEWAY ---
NOWPAYMENTS_API_KEY = "P3N58GH-RD448ET-PVEVA05-3TGZF8Q" # PASTE YOUR KEY HERE

def create_crypto_invoice():
    """Creates a $97 invoice on NOWPayments and returns the payment link"""
    url = "https://api.nowpayments.io/v1/invoice"
    headers = {
        "x-api-key": NOWPAYMENTS_API_KEY,
        "Content-Type": "application/json"
    }
    payload = {
        "price_amount": 97,
        "price_currency": "usd",
        "order_description": "Limitless Journeys Club - Lifetime Access ($97)",
        "success_url": "https://jeromany.github.io/limitless-club-app/",
        "cancel_url": "https://jeromany.github.io/limitless-club-app/"
    }
    
    try:
        response = requests.post(url, json=payload, headers=headers)
        if response.status_code == 200:
            return response.json()['invoice_url']
        else:
            print(f"Payment API Error: {response.text}")
            return None
    except Exception as e:
        print(f"Payment Error: {e}")
        return None

# --- BOT COMMANDS ---

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Welcome to Limitless Journeys! 🌍\n\n"
        "I am Jasai, your AI trading assistant.\n\n"
        "Use these commands:\n"
        "/briefing - Get the daily Gold market briefing\n"
        "/price - Get the current Gold price\n"
        "/buy - Purchase Lifetime Access ($97)\n"
        "/help - Show available commands"
    )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Use /briefing for analysis, /price for Gold, or /buy to join the Inner Circle.")

async def get_briefing(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("📡 Fetching the latest intelligence from the Master Briefing...")
    data = requests.get(GITHUB_JSON_URL, timeout=5).json()
    
    if data and 'gold' in data:
        g = data['gold']
        sign = '+' if g['priceChangePercent'] > 0 else ''
        msg = (
            f"📊 *Daily Gold Briefing*\n\n"
            f"💰 *Price:* ${g['currentPrice']} ({sign}{g['priceChangePercent']}%)\n"
            f"📉 *Bias:* {g['bias'].capitalize()}\n"
            f"🎯 *Macro Target:* $3,200 (Moody's Gap)\n\n"
            f"📝 *Analysis:*\n{g['analysis']}\n\n"
            f"🛡️ *Key Levels:*\n"
            f"- Support: ${g['support']}\n"
            f"- Resistance: ${g['resistance']}\n"
            f"- 61.8% Fib: ${g['fib618']}"
        )
        await update.message.reply_text(msg, parse_mode='Markdown')
    else:
        await update.message.reply_text("⚠️ Master Briefing is currently updating.")

async def get_price(update: Update, context: ContextTypes.DEFAULT_TYPE):
    data = requests.get(GITHUB_JSON_URL, timeout=5).json()
    if data and 'gold' in data:
        await update.message.reply_text(f"💰 Current Gold Price: ${data['gold']['currentPrice']}")
    else:
        await update.message.reply_text("⚠️ Price data unavailable right now.")

async def buy_access(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🔐 Processing your request for Lifetime Access...")
    link = create_crypto_invoice()
    
    if link:
        msg = (
            "🚀 *Limitless Journeys Inner Circle*\n\n"
            "You are about to secure 1 of 7 Lifetime Spots.\n"
            "Price: $97 (Crypto)\n\n"
            "Click the secure link below to complete your payment via Bitcoin, USDT, or Ethereum:\n\n"
            f"👉 {link}\n\n"
            "Once paid, you will receive instant access to the private Telegram group!"
        )
        await update.message.reply_text(msg, parse_mode='Markdown', disable_web_page_preview=True)
    else:
        await update.message.reply_text("❌ Payment gateway is currently unavailable. Please try again later.")

# --- START THE ENGINE ---
def run_telegram_bot():
    TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
    if not TOKEN:
        # Fallback for local testing if env var isn't set
        TOKEN = "YOUR_TELEGRAM_BOT_TOKEN_HERE" 
        
    application = ApplicationBuilder().token(TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("briefing", get_briefing))
    application.add_handler(CommandHandler("price", get_price))
    application.add_handler(CommandHandler("buy", buy_access))
    
    print("🤖 Jasai Telegram Bot is listening...")
    application.run_polling()

if __name__ == '__main__':
    run_telegram_bot()
