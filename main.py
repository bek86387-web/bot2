import telebot
import yfinance as yf
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import mplfinance as mpf
import io

# BOT TOKEN
TOKEN = '8568851239:AAHMy_VrKrlM6r9v4-rPKB9mgPEa7nnpsPc'
bot = telebot.TeleBot(TOKEN)

def get_gann_fan(df, start_idx, start_price, direction='up'):
    """Gann burchaklarini hisoblash funksiyasi"""
    x = range(start_idx, len(df) + 30) # Grafikdan oldinga ham chizish
    # Scale aktivning volatilligiga qarab (ATR kabi mantiq)
    scale = (df['High'].max() - df['Low'].min()) / 100 
    
    lines = []
    # 1x1, 2x1, 1x2 nisbatlari
    ratios = [1, 2, 0.5]
    for r in ratios:
        slope = scale * r if direction == 'up' else -scale * r
        line = [start_price + (i - start_idx) * slope for i in x]
        lines.append((x, line))
    return lines

@bot.message_handler(func=lambda message: True)
def handle_analysis(message):
    ticker = message.text.upper().strip()
    if ticker == "OLTIN": ticker = "GC=F"
    if len(ticker) < 6 and "-" not in ticker and "=" not in ticker and "^" not in ticker:
        ticker += "-USD"

    try:
        sent_msg = bot.send_message(message.chat.id, f"🔍 {ticker} bo'yicha professional grafik tayyorlanmoqda...")
        
        # Ma'lumotni yuklash
        df = yf.download(ticker, period="1mo", interval="1d", auto_adjust=True)
        if df.empty:
            bot.reply_to(message, "❌ Aktiv topilmadi.")
            return

        # MultiIndex muammosini tuzatish
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.get_level_values(0)

        # Pivot nuqtalarni topish (Max va Min)
        low_idx = df.index.get_loc(df['Low'].idxmin())
        low_price = float(df['Low'].min())
        
        high_idx = df.index.get_loc(df['High'].idxmax())
        high_price = float(df['High'].max())

        # Grafik chizish sozlamalari
        mc = mpf.make_marketcolors(up='green', down='red', edge='inherit', wick='inherit', volume='in')
        s = mpf.make_mpf_style(marketcolors=mc, gridstyle='--', gridcolor='gray', gridalpha=0.3)

        fig, ax = mpf.plot(df, type='candle', style=s, figsize=(12, 8), returnfig=True, tight_layout=True)

        # Gann burchaklarini qo'shish (Minimumdan yuqoriga)
        fans_up = get_gann_fan(df, low_idx, low_price, 'up')
        colors = ['green', 'red', 'blue']
        labels = ['1x1', '2x1', '1x2']
        
        for i, (x, y) in enumerate(fans_up):
            ax[0].plot(x, y, color=colors[i], linestyle='--', alpha=0.6, label=f"Gann {labels[i]}")

        # Gann burchaklarini qo'shish (Maksimumdan pastga)
        fans_down = get_gann_fan(df, high_idx, high_price, 'down')
        for i, (x, y) in enumerate(fans_down):
            ax[0].plot(x, y, color=colors[i], linestyle=':', alpha=0.5)

        ax[0].set_title(f"{ticker} Professional Gann Fan Tahlili", fontsize=15)
        ax[0].legend(loc='best')

        # Rasmni yuborish
        buf = io.BytesIO()
        plt.savefig(buf, format='png', dpi=150)
        buf.seek(0)
        plt.close()

        bot.delete_message(message.chat.id, sent_msg.message_id)
        bot.send_photo(message.chat.id, buf, caption=f"📊 **{ticker}** tahlili.\n\n"
                                                      f"✅ Yashil chiziqlar: Minimumdan o'sish\n"
                                                      f"✅ Nuqtali chiziqlar: Maksimumdan pasayish\n"
                                                      f"💰 Joriy narx: {round(float(df['Close'].iloc[-1]), 2)}$")

    except Exception as e:
        bot.send_message(message.chat.id, f"❌ Xato: {str(e)}")

if __name__ == "__main__":
    bot.infinity_polling()
