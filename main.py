import telebot
import yfinance as yf
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import io

TOKEN = '8568851239:AAHMy_VrKrlM6r9v4-rPKB9mgPEa7nnpsPc' 
bot = telebot.TeleBot(TOKEN)

@bot.message_handler(commands=['start', 'help'])
def start(message):
    help_text = (
        "📊 **Zzzzzzzzzzss_bot yordam bo'limi**\n\n"
        "Quyidagi buyruqlardan foydalaning:\n"
        "/check - BTC/USD Gann tahlili (Grafik)\n"
        "/market - Joriy narxlarni ko'rish\n"
        "/help - Ushbu yordam oynasi"
    )
    bot.reply_to(message, help_text, parse_mode='Markdown')

@bot.message_handler(commands=['market'])
def market_status(message):
    try:
        btc = yf.Ticker("BTC-USD").history(period="1d")['Close'].iloc[-1]
        eth = yf.Ticker("ETH-USD").history(period="1d")['Close'].iloc[-1]
        bot.reply_to(message, f"💰 **Bozor narxlari:**\n\nBTC: {round(btc, 2)}$\nETH: {round(eth, 2)}$", parse_mode='Markdown')
    except:
        bot.reply_to(message, "Narxlarni olib bo'lmadi.")

@bot.message_handler(commands=['check'])
def send_gann_chart(message):
    try:
        sent_msg = bot.send_message(message.chat.id, "🔍 Tahlil qilinmoqda...")
        data = yf.download("BTC-USD", period="5d", interval="1h", auto_adjust=True)
        
        if isinstance(data.columns, pd.MultiIndex):
            data.columns = data.columns.get_level_values(0)
            
        df = data.copy()
        current_price = round(float(df['Close'].iloc[-1]), 2)
        low_pivot = float(df['Low'].min())
        low_idx_val = df['Low'].idxmin()
        low_index = df.index.get_loc(low_idx_val)
        
        scale = 15 
        x_range = range(low_index, len(df) + 24)
        
        plt.figure(figsize=(10, 6), dpi=100)
        plt.plot(range(len(df)), df['Close'].values, label='BTC/USD', color='black')
        
        plt.plot(x_range, [low_pivot + (i - low_index) * scale for i in x_range], '--', label='1x1', color='green')
        plt.plot(x_range, [low_pivot + (i - low_index) * scale * 2 for i in x_range], '--', label='2x1', color='red')
        
        plt.title(f"Gann Fan: {current_price}$")
        plt.legend()
        plt.grid(True, alpha=0.2)

        buf = io.BytesIO()
        plt.savefig(buf, format='png', bbox_inches='tight')
        buf.seek(0)
        plt.close()

        bot.delete_message(message.chat.id, sent_msg.message_id)
        bot.send_photo(message.chat.id, buf, caption=f"📊 BTC: {current_price}$")
    except Exception as e:
        bot.reply_to(message, f"Xato: {str(e)}")

if __name__ == "__main__":
    bot.infinity_polling()
