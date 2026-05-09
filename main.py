import telebot
import yfinance as yf
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import mplfinance as mpf
import io

# 1. TOZA API TOKEN
TOKEN = '8568851239:AAH08PrpahculGofM802IIRPgLmQ0IiqTb8'
bot = telebot.TeleBot(TOKEN)

# Aktivlarni to'g'ri Yahoo tickerlariga aylantirish lug'ati
TICKERS = {
    "GOLD": "GC=F", "OLTIN": "GC=F",
    "SILVER": "SI=F", "KUMUSH": "SI=F",
    "SP500": "^GSPC", "SPX500": "^GSPC",
    "NASDAQ": "^IXIC", "DOW": "^DJI",
    "NEFT": "CL=F", "OIL": "CL=F"
}

def get_gann_fan(df, start_idx, start_price, direction='up'):
    x = range(start_idx, len(df) + 40)
    scale = (df['High'].max() - df['Low'].min()) / 120
    ratios = [1, 2, 4, 8, 0.5, 0.25]
    lines = []
    for r in ratios:
        slope = scale * r if direction == 'up' else -scale * r
        line = [start_price + (i - start_idx) * slope for i in x]
        lines.append((x, line))
    return lines

@bot.message_handler(commands=['start'])
def start(message):
    bot.reply_to(message, "⚔️ **Zzzzzzzzzzss_bot tayyor!**\n\nAktiv nomini yozing (masalan: BTC, Gold, Apple).", parse_mode='Markdown')

@bot.message_handler(func=lambda message: True)
def handle_analysis(message):
    text = message.text.upper().strip()
    
    # 1. Komandalarni (/) o'tkazib yuborish
    if text.startswith('/'): 
        if text == "/START": return
        bot.reply_to(message, "❌ Noto'g'ri buyruq. Aktiv nomini yozing (masalan: BTC).")
        return

    # 2. Tickerlarni aniqlash
    ticker = TICKERS.get(text, text)
    if ticker == text and len(text) <= 5 and not any(c in text for c in ["-", "=", "^"]):
        ticker = f"{text}-USD"

    try:
        sent_msg = bot.send_message(message.chat.id, f"🔍 **{ticker}** tahlil qilinmoqda...", parse_mode='Markdown')
        
        data = yf.download(ticker, period="1mo", interval="1d", auto_adjust=True)
        
        if data.empty:
            bot.edit_message_text(f"❌ Aktiv topilmadi: {ticker}", message.chat.id, sent_msg.message_id)
            return

        if isinstance(data.columns, pd.MultiIndex):
            data.columns = data.columns.get_level_values(0)

        df = data.copy()
        current_price = round(float(df['Close'].iloc[-1]), 2)
        low_idx = df.index.get_loc(df['Low'].idxmin())
        high_idx = df.index.get_loc(df['High'].idxmax())

        # Grafik stili (TradingView / Nightclouds)
        mc = mpf.make_marketcolors(up='#089981', down='#f23645', inherit=True)
        s = mpf.make_mpf_style(base_mpf_style='nightclouds', marketcolors=mc, gridstyle=':', facecolor='#131722')
        fig, ax = mpf.plot(df, type='candle', style=s, figsize=(12, 7), returnfig=True)

        # Gann burchaklari
        fans_up = get_gann_fan(df, low_idx, float(df['Low'].min()), 'up')
        fans_down = get_gann_fan(df, high_idx, float(df['High'].max()), 'down')
        colors = ['#2962FF', '#FF6D00', '#787B86', '#E91E63', '#9C27B0', '#FFEB3B']
        
        for i, (x, y) in enumerate(fans_up):
            ax.plot(x, y, color=colors[i % len(colors)], linestyle='-', alpha=0.4, linewidth=0.8)
        for i, (x, y) in enumerate(fans_down):
            ax.plot(x, y, color=colors[i % len(colors)], linestyle=':', alpha=0.3, linewidth=0.8)

        buf = io.BytesIO()
        plt.savefig(buf, format='png', dpi=150, facecolor='#131722', bbox_inches='tight')
        buf.seek(0)
        plt.close(fig)

        bot.delete_message(message.chat.id, sent_msg.message_id)
        bot.send_photo(message.chat.id, buf, caption=f"✅ **{ticker}**\n💰 Narx: `{current_price}$`", parse_mode='Markdown')
        
    except Exception as e:
        bot.send_message(message.chat.id, f"❌ Xato yuz berdi: {str(e)}")

if __name__ == "__main__":
    bot.remove_webhook()
    bot.infinity_polling()
