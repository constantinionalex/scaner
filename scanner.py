import os
import json
import asyncio
from yahooquery import Ticker
import pandas as pd
from telegram import Bot

# CREDENTIALE TELEGRAM (Hardcoded)
TELEGRAM_TOKEN = "8722371365:AAGiQ8g9M2LPNQIsYaM6V0KApwkKaJTi5vg"
TELEGRAM_CHAT_ID = "8708984447"

# PARAMETRI PHIL TOWN
TARGET_PAYBACK_TIME = 8
MOS_PERCENT = 0.5

async def send_telegram(msg):
    try:
        bot = Bot(token=TELEGRAM_TOKEN)
        await bot.send_message(chat_id=TELEGRAM_CHAT_ID, text=msg, parse_mode='Markdown')
    except Exception as e:
        print(f"Eroare Telegram: {e}")

def calculate_payback(price, eps, growth):
    if eps <= 0 or growth <= 0: return 20
    total = 0
    current_eps = eps
    for year in range(1, 21):
        current_eps *= (1 + growth)
        total += current_eps
        if total >= price: return year
    return 20

def analyze_stock(symbol):
    try:
        t = Ticker(symbol)
        d = t.all_modules[symbol]
        
        # Date fundamentale
        price = d['financialData']['currentPrice']
        eps = d['defaultKeyStatistics']['trailingEps']
        
        # Estimare crestere (Growth)
        growth = 0.15
        if 'earningsTrend' in d:
            trends = d['earningsTrend'].get('trend', [])
            for trend in trends:
                if trend.get('period') == '+5y':
                    growth = trend.get('growth', 0.15)
        
        # Sticker Price (Rule #1 Formula)
        future_pe = growth * 2 * 100
        sticker = (eps * ((1 + growth) ** 10) * future_pe) / (1.15 ** 10)
        payback = calculate_payback(price, eps, growth)
        
        # Management (Debt/FCF)
        debt = d['financialData'].get('totalDebt', 0)
        fcf = d['financialData'].get('freeCashflow', 1)
        debt_years = debt / fcf if fcf > 0 else 99

        return {
            "symbol": symbol,
            "price": price,
            "sticker": round(sticker, 2),
            "mos": round(sticker * MOS_PERCENT, 2),
            "payback": payback,
            "growth": round(growth * 100, 2),
            "debt_y": round(debt_years, 1)
        }
    except:
        return None

async def main():
    # Lista de actiuni de scanat
    watchlist = ["AAPL", "MSFT", "GOOGL", "NVDA", "TSLA", "META", "AMZN", "COST", "V", "MA", "ASML", "AVGO"]
    results = []
    
    print("Incepere scanare...")
    for s in watchlist:
        res = analyze_stock(s)
        if res:
            results.append(res)
    
    # Salvare JSON pentru interfata web (locala in container)
    with open('data.json', 'w') as f:
        json.dump(results, f)
        
    await send_telegram(f"✅ *Scanner Phil Town Local*\nAnaliza finalizata pentru {len(results)} companii.\nVerifica interfata web la portul 8080.")

if __name__ == "__main__":
    asyncio.run(main())
