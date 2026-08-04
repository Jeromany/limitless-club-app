import os
import requests
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler

# --- THE BRAIN (Single Source of Truth) ---
GITHUB_JSON_URL = "https://raw.githubusercontent.com/jeromany/limitless-club-app/main/daily-briefing.json"

def fetch_briefing():
    """Fetches the live data from GitHub"""
    try:
        response = requests.get(GITHUB_JSON_URL, timeout=5)
        if response.status_code == 200:
            return response.json()
        return None
    except Exception as e:
        print(f"Error fetching data: {e}")
        return None

# --- BOT COMMANDS ---

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Welcome to Limitless Journeys! 🌍\n\n"
        "I am Jasai, your AI trading assistant.\n\n"
        "Use these commands:\n"
        "/briefing - Get the daily Gold market briefing\n"
        "/price - Get the current Gold price\n"
        "/help - Show available commands"
    )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Use /briefing for the daily analysis or /price for the live Gold price.")

async def get_briefing(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("📡 Fetching the latest intelligence from the Master Briefing...")
    data = fetch_briefing()
    
    if data and 'gold' in data:
        g = data['gold']
        sign = '+' if g['priceChangePercent'] > 0 else ''
        msg = (
            f"📊 *Daily Gold Briefing*\n\n"
            f"💰 *Price:* ${g['currentPrice']} ({sign}{g['priceChangePercent']}%)\n"
            f" *Bias:* {g['bias'].capitalize()}\n"
            f"🎯 *Macro Target:* $3,200 (Moody's Gap)\n\n"
            f"📝 *Analysis:*\n{g['analysis']}\n\n"
            f"🛡️ *Key Levels:*\n"
            f"- Support: ${g['support']}\n"
            f"- Resistance: ${g['resistance']}\n"
            f"- 61.8% Fib: ${g['fib618']}"
        )
        await update.message.reply_text(msg, parse_mode='Markdown')
    else:
        await update.message.reply_text("⚠️ Master Briefing is currently updating. Please check back in a few minutes.")

async def get_price(update: Update, context: ContextTypes.DEFAULT_TYPE):
    data = fetch_briefing()
    if data and 'gold' in data:
        price = data['gold']['currentPrice']
        await update.message.reply_text(f"💰 Current Gold Price: ${price}")
    else:
        await update.message.reply_text("⚠️ Price data unavailable right now.")

# --- START THE ENGINE ---
if __name__ == '__main__':
    # Fetches the token securely from the cloud server's environment variables
    TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
    
    if not TOKEN:
        print("❌ ERROR: TELEGRAM_BOT_TOKEN is not set in environment variables!")
        exit(1)
        
    application = ApplicationBuilder().token(TOKEN).build()
    
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("briefing", get_briefing))
    application.add_handler(CommandHandler("price", get_price))

    print("🤖 Jasai Telegram Bot is listening...")
    application.run_polling()
