import os
import json
import asyncio
from yahooquery import Ticker
import pandas as pd
from telegram import Bot

# Parametri Phil Town
TARGET_PAYBACK_TIME = 8
MOS_PERCENT = 0.5

async def send_telegram(msg):
    token = os.getenv('TELEGRAM_TOKEN')
    chat_id = os.getenv('TELEGRAM_CHAT_ID')
    if token and chat_id:
        bot = Bot(token=token)
        await bot.send_message(chat_id=chat_id, text=msg, parse_mode='Markdown')

def calculate_payback(price, eps, growth):
    if eps <= 0 or growth <= 0: return 20
    total = 0
    for year in range(1, 21):
        eps *= (1 + growth)
        total += eps
        if total >= price: return year
    return 20

def analyze_stock(symbol):
    try:
        t = Ticker(symbol)
        d = t.all_modules[symbol]
        
        price = d['financialData']['currentPrice']
        eps = d['defaultKeyStatistics']['trailingEps']
        # Crestere estimata (default 15% daca nu gaseste)
        growth = d.get('earningsTrend', {}).get('trend', [{},{},{},{},{'growth': 0.15}])[4].get('growth', 0.15)
        
        # Sticker Price & MoS
        future_pe = growth * 2 * 100
        sticker = (eps * ((1 + growth) ** 10) * future_pe) / (1.15 ** 10)
        payback = calculate_payback(price, eps, growth)
        
        return {
            "symbol": symbol,
            "price": price,
            "sticker": round(sticker, 2),
            "mos": round(sticker * MOS_PERCENT, 2),
            "payback": payback,
            "growth": round(growth * 100, 2),
            "debt_y": round(d['financialData'].get('totalDebt', 0) / d['financialData'].get('freeCashflow', 1), 1)
        }
    except: return None

async def main():
    watchlist = ["AAPL", "MSFT", "GOOGL", "NVDA", "TSLA", "META", "AMZN", "COST", "V", "MA"]
    results = []
    
    for s in watchlist:
        print(f"Analizez {s}...")
        res = analyze_stock(s)
        if res: results.append(res)
    
    # Salvare JSON pentru interfata web locala
    with open('data.json', 'w') as f:
        json.dump(results, f)
        
    await send_telegram(f"✅ Scanare finalizată pe serverul local pentru {len(results)} acțiuni.")

if __name__ == "__main__":
    asyncio.run(main())
