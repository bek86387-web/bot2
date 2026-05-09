import telebot
import yfinance as yf
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import mplfinance as mpf
import io

# 1. YANGI API TOKEN
TOKEN = '8568851239:AAH08PrpahculGofM802IIRPgLmQ0IiqTb8'
bot = telebot.TeleBot(TOKEN)

def get_gann_fan(df, start_idx, start_price, direction='up'):
    """Gann burchaklarini professional hisoblash"""
    x = range(start_idx, len(df) + 40)
    # Masshtabni aktiv volatilligiga qarab aniqlash
    scale = (df['High'].max() - df['Low'].min()) / 120
    lines = []
    ratios = [1, 2, 4, 8, 0.5, 0.25]
    for r in ratios:
        slope = scale * r if direction == 'up' else -scale * r
        line = [start_price + (i - start_idx) * slope for i in x]
        lines.append((x, line))
    return lines

@bot.message_handler(func=lambda message: any(word in message.text.lower() for word in ['yaratuvchi', 'ega', 'kim yozgan', 'admin', 'u yaratuvching', 'egang']))
def owner_info(message):
    bot.reply_to(message, "⚔️ Ushbu haybatli botning mutloq yaratuvchisi va egasi: **OZODBEK YUSUPOV**", parse_mode='Markdown')

@bot.message_handler(commands=['start'])
def start(message):
    bot.reply_to(message, "⚔️ **Zzzzzzzzzzss_bot ishga tushdi!**\n\nMenga aktiv nomini yozing (masalan: BTC, Oltin, TSLA).", parse_mode='Markdown')

@bot.message_handler(func=lambda message: True)
def handle_analysis(message):
    text = message.text.upper().strip()
    ticker = text
    
    # Aktiv nomlarini Yahoo formatiga to'g'rilash
    if text == "OLTIN": ticker = "GC=F"
    elif text == "KUMUSH": ticker = "SI=F"
    elif text == "SPX500": ticker = "^GSPC"
    elif len(text) <= 5 and all(x not in text for x in ["-", "=", "^"]):
        ticker = f"{text}-USD"

    try:
        sent_msg = bot.send_message(message.chat.id, f"🔍 **{ticker}** tahlil qilinmoqda...", parse_mode='Markdown')
        
        # Ma'lumotni yuklash (MultiIndex xatosini oldini olish uchun auto_adjust=True)
        data = yf.download(ticker, period="1mo", interval="1d", auto_adjust=True)
        
        if data.empty:
            bot.reply_to(message, "❌ Aktiv topilmadi. Iltimos, nomini tekshiring.")
            return

        # Yahoo Finance MultiIndex muammosini hal qilish
        if isinstance(data.columns, pd.MultiIndex):
            data.columns = data.columns.get_level_values(0)

        df = data.copy()
        current_price = round(float(df['Close'].iloc[-1]), 2)
        
        # Pivot nuqtalarni aniqlash
        low_idx = df.index.get_loc(df['Low'].idxmin())
        low_price = float(df['Low'].min())
        high_idx = df.index.get_loc(df['High'].idxmax())
        high_price = float(df['High'].max())

        # TRADINGVIEW USLUBIDAGI GRAFIK (Qora fon)
        mc = mpf.make_marketcolors(up='#089981', down='#f23645', inherit=True)
        s = mpf.make_mpf_style(base_mpf_style='nightclouds', marketcolors=mc, gridstyle=':', facecolor='#131722')
        
        fig, ax = mpf.plot(df, type='candle', style=s, figsize=(14, 9), returnfig=True, datetime_format='%d-%m')

        # Gann burchaklarini chizish
        fans_up = get_gann_fan(df, low_idx, low_price, 'up')
        fans_down = get_gann_fan(df, high_idx, high_price, 'down')
        colors = ['#2962FF', '#FF6D00', '#787B86', '#E91E63', '#9C27B0', '#FFEB3B']
        
        for i, (x, y) in enumerate(fans_up):
            ax.plot(x, y, color=colors[i % len(colors)], linestyle='-', alpha=0.4, linewidth=0.8)
        for i, (x, y) in enumerate(fans_down):
            ax.plot(x, y, color=colors[i % len(colors)], linestyle=':', alpha=0.3, linewidth=0.8)

        ax.set_title(f"{ticker} Professional Analysis", color='white', fontsize=18, pad=30)
        
        # Rasmni saqlash
        buf = io.BytesIO()
        plt.savefig(buf, format='png', dpi=200, facecolor='#131722', bbox_inches='tight')
        buf.seek(0)
        plt.close(fig)

        bot.delete_message(message.chat.id, sent_msg.message_id)
        bot.send_photo(message.chat.id, buf, caption=f"✅ **{ticker} Tahlili Tayyor!**\n💰 **Narx:** `{current_price}$`", parse_mode='Markdown')
        
    except Exception as e:
        bot.send_message(message.chat.id, f"❌ Xatolik: `{str(e)}`", parse_mode='Markdown')

if __name__ == "__main__":
    # Conflict xatosini oldini olish uchun ishlatiladi
    bot.remove_webhook()
    bot.infinity_polling(timeout=10, long_polling_timeout=5)
