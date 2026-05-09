import telebot
import yfinance as yf
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import io

TOKEN = '8568851239:AAHMy_VrKrlM6r9v4-rPKB9mgPEa7nnpsPc'
bot = telebot.TeleBot(TOKEN)

# Lug'at - foydalanuvchi yozgan so'zni Yahoo Tickeriga aylantiradi
ALIASES = {
    "oltin": "GC=F", "gold": "GC=F",
    "kumush": "SI=F", "silver": "SI=F",
    "neft": "CL=F", "oil": "CL=F",
    "spx500": "^GSPC", "sp500": "^GSPC",
    "nasdaq": "^IXIC",
    "apple": "AAPL", "tesla": "TSLA",
    "btc": "BTC-USD", "eth": "ETH-USD"
}

@bot.message_handler(commands=['start'])
def start(message):
    bot.reply_to(message, "Salom! Men tayyorman. Menga aktiv nomini yozing (masalan: Oltin yoki BTC) yoki /check yuboring. ⚔️")

# MATNLI QIDIRUV (Siz aytgandek ishlashi uchun)
@bot.message_handler(func=lambda message: True)
def handle_text(message):
    text = message.text.lower().strip()
    
    # Agar lug'atda bo'lsa tickerini oladi, bo'lmasa o'zini tekshiradi
    ticker = ALIASES.get(text, text.upper())
    
    if "usd" not in ticker and len(ticker) <= 5 and "^" not in ticker and "=" not in ticker:
        # Kripto bo'lsa avtomatik -USD qo'shish (masalan: btc -> btc-usd)
        ticker += "-USD"

    send_analysis(message, ticker)

def send_analysis(message, ticker):
    try:
        sent_msg = bot.send_message(message.chat.id, f"🔍 {ticker} bo'yicha mega tahlil tayyorlanmoqda...")
        
        data = yf.download(ticker, period="5d", interval="1h", auto_adjust=True)
        if data.empty:
            bot.reply_to(message, "❌ Bunday aktiv topilmadi. To'g'ri yozganingizga ishonch hosil qiling.")
            return

        if isinstance(data.columns, pd.MultiIndex):
            data.columns = data.columns.get_level_values(0)
            
        df = data.copy()
        price = round(float(df['Close'].iloc[-1]), 2)
        
        # Grafik chizish qismi (Gann bilan)
        plt.figure(figsize=(10, 6), dpi=100)
        plt.plot(range(len(df)), df['Close'].values, color='black', label=ticker)
        plt.title(f"{ticker} Tahlili: {price}$")
        plt.grid(True, alpha=0.2)
        
        buf = io.BytesIO()
        plt.savefig(buf, format='png')
        buf.seek(0)
        plt.close()

        bot.delete_message(message.chat.id, sent_msg.message_id)
        bot.send_photo(message.chat.id, buf, caption=f"✅ {ticker} tahlili tayyor!\n💰 Narx: {price}$")
        
    except Exception as e:
        bot.send_message(message.chat.id, f"Xato yuz berdi: {e}")

if __name__ == "__main__":
    bot.infinity_polling()
