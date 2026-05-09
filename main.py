import telebot
import ccxt
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import io

# BOT TOKEN
TOKEN = '8568851239:AAHMy_VrKrlM6r9v4-rPKB9mgPEa7nnpsPc' 
bot = telebot.TeleBot(TOKEN)
exchange = ccxt.binance()

@bot.message_handler(commands=['start'])
def start(message):
    bot.reply_to(message, "Zzzzzzzzzzss_bot ishga tushdi! Tahlil uchun /check yuboring. ⚔️")

@bot.message_handler(commands=['check'])
def send_gann_chart(message):
    try:
        sent_msg = bot.send_message(message.chat.id, "🔍 Tahlil qilinmoqda...")
        
        bars = exchange.fetch_ohlcv('BTC/USDT', timeframe='1h', limit=100)
        df = pd.DataFrame(bars, columns=['time', 'open', 'high', 'low', 'close', 'vol'])
        
        current_price = df['close'].iloc[-1]
        low_pivot = df['low'].min()
        low_index = df['low'].idxmin()
        
        scale = 10 
        x_range = range(low_index, len(df) + 20)
        
        gann_1x1 = [low_pivot + (i - low_index) * scale for i in x_range]
        gann_2x1 = [low_pivot + (i - low_index) * scale * 2 for i in x_range]
        gann_1x2 = [low_pivot + (i - low_index) * scale * 0.5 for i in x_range]

        plt.figure(figsize=(10, 6))
        plt.plot(df.index, df['close'], label='BTC/USDT', color='black')
        plt.plot(x_range, gann_1x1, '--', label='1x1', color='green')
        plt.plot(x_range, gann_2x1, '--', label='2x1', color='red')
        plt.plot(x_range, gann_1x2, '--', label='1x2', color='blue')
        
        plt.title(f"Gann Fan: {current_price}$")
        plt.legend()
        plt.grid(True)

        buf = io.BytesIO()
        plt.savefig(buf, format='png')
        buf.seek(0)
        plt.close()

        bot.delete_message(message.chat.id, sent_msg.message_id)
        bot.send_photo(message.chat.id, buf, caption=f"📊 BTC joriy narxi: {current_price}$")
        
    except Exception as e:
        bot.reply_to(message, f"Xato: {e}")

if __name__ == "__main__":
    bot.infinity_polling()

        # 4. GRAFIK CHIZISH (Optimallashgan variant)
        plt.figure(figsize=(10, 6))
        plt.plot(df.index, df['close'], label='BTC/USDT', color='black', linewidth=1.5)
        
        # Gann chiziqlari
        plt.plot(x_range, gann_1x1, '--', label='1x1 (45°)', color='green', alpha=0.8)
        plt.plot(x_range, gann_2x1, '--', label='2x1 (63.75°)', color='red', alpha=0.8)
        plt.plot(x_range, gann_1x2, '--', label='1x2 (26.25°)', color='blue', alpha=0.8)
        
        plt.title(f"Gann Fan Tahlili: {current_price}$")
        plt.legend()
        plt.grid(True, linestyle=':', alpha=0.7)

        # 5. RASMNI YUBORISH (Sifatni sozlash)
        buf = io.BytesIO()
        plt.savefig(buf, format='png', dpi=100) # dpi=100 rasmni yengilroq qiladi
        buf.seek(0)
        plt.close()
