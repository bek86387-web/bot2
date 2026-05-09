import telebot
import yfinance as yf
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import io

# BOT TOKEN
TOKEN = '8568851239:AAHMy_VrKrlM6r9v4-rPKB9mgPEa7nnpsPc' 
bot = telebot.TeleBot(TOKEN)

@bot.message_handler(commands=['start'])
def start(message):
    bot.reply_to(message, "Zzzzzzzzzzss_bot ishga tushdi! Tahlil uchun /check yuboring. ⚔️")

@bot.message_handler(commands=['check'])
def send_gann_chart(message):
    try:
        sent_msg = bot.send_message(message.chat.id, "🔍 Yahoo Finance orqali tahlil qilinmoqda...")
        
        # Ma'lumotlarni olish (BTC-USD Yahoo Finance orqali)
        data = yf.download("BTC-USD", period="5d", interval="1h")
        if data.empty:
            bot.reply_to(message, "Xato: Ma'lumot olib bo'lmadi.")
            return

        df = data.tail(100).copy()
        current_price = round(df['Close'].iloc[-1], 2)
        low_pivot = df['Low'].min()
        # Pivot indeksini raqam ko'rinishida olish
        low_id = df['Low'].idxmin()
        low_index = df.index.get_loc(low_id)
        
        scale = 10 
        x_range = range(low_index, len(df) + 20)
        
        # Grafik chizish
        plt.figure(figsize=(10, 6), dpi=100)
        plt.plot(range(len(df)), df['Close'], label='BTC/USD', color='black', linewidth=1.5)
        
        # Gann chiziqlari
        plt.plot(x_range, [low_pivot + (i - low_index) * scale for i in x_range], '--', label='1x1', color='green')
        plt.plot(x_range, [low_pivot + (i - low_index) * scale * 2 for i in x_range], '--', label='2x1', color='red')
        
        plt.title(f"Gann Fan (Yahoo Finance): {current_price}$")
        plt.legend()
        plt.grid(True, alpha=0.3)

        buf = io.BytesIO()
        plt.savefig(buf, format='png', bbox_inches='tight')
        buf.seek(0)
        plt.close()

        bot.delete_message(message.chat.id, sent_msg.message_id)
        bot.send_photo(message.chat.id, buf, caption=f"📊 BTC: {current_price}$ (Yahoo Finance orqali)")
        
    except Exception as e:
        bot.reply_to(message, f"Xato: {str(e)}")

if __name__ == "__main__":
    bot.infinity_polling()

