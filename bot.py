import requests
import time
import datetime

TOKEN = "8809756992:AAEq_CYIMiYcN4VOXFmYvUEjN3YT1TzH9VU"

def get_chat_id():
    url = f"https://api.telegram.org/bot{TOKEN}/getUpdates"
    r = requests.get(url).json()
    try:
        return r['result'][-1]['message']['chat']['id']
    except:
        return None

def send_message(chat_id, text):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    requests.post(url, data={'chat_id': chat_id, 'text': text, 'parse_mode': 'HTML'})

def get_btc_data():
    url = "https://api.binance.com/api/v3/klines?symbol=BTCUSDT&interval=5m&limit=60"
    r = requests.get(url).json()
    closes = [float(c[4]) for c in r]
    return closes

def calc_ema(prices, period):
    k = 2 / (period + 1)
    ema = prices[0]
    for price in prices[1:]:
        ema = price * k + ema * (1 - k)
    return ema

def calc_rsi(prices, period=14):
    gains, losses = [], []
    for i in range(1, len(prices)):
        diff = prices[i] - prices[i-1]
        gains.append(max(diff, 0))
        losses.append(max(-diff, 0))
    avg_gain = sum(gains[-period:]) / period
    avg_loss = sum(losses[-period:]) / period
    if avg_loss == 0:
        return 100
    rs = avg_gain / avg_loss
    return 100 - (100 / (1 + rs))

def analyze():
    closes = get_btc_data()
    ema20 = calc_ema(closes[-20:], 20)
    ema50 = calc_ema(closes[-50:], 50)
    rsi = calc_rsi(closes[-15:])
    price = closes[-1]

    signal = None
    reasons = []

    if ema20 > ema50 and price > ema20 and 45 < rsi < 65:
        signal = "⬆️ ВВЕРХ (BUY)"
        reasons = [
            "✅ EMA20 выше EMA50 — бычий тренд",
            f"✅ RSI = {rsi:.1f} — хорошая зона входа",
            "✅ Цена выше EMA20"
        ]
    elif ema20 < ema50 and price < ema20 and 35 < rsi < 55:
        signal = "⬇️ ВНИЗ (SELL)"
        reasons = [
            "✅ EMA20 ниже EMA50 — медвежий тренд",
            f"✅ RSI = {rsi:.1f} — хорошая зона входа",
            "✅ Цена ниже EMA20"
        ]
    elif rsi >= 70:
        signal = "⬇️ ВНИЗ (SELL)"
        reasons = [
            f"⚠️ RSI = {rsi:.1f} — перекуплен",
            "✅ Ожидается откат вниз"
        ]
    elif rsi <= 30:
        signal = "⬆️ ВВЕРХ (BUY)"
        reasons = [
            f"⚠️ RSI = {rsi:.1f} — перепродан",
            "✅ Ожидается отскок вверх"
        ]

    return signal, reasons, price, ema20, ema50, rsi

def main():
    print("🤖 Бот запущен...")
    chat_id = None

    # Получаем chat_id
    for _ in range(10):
        chat_id = get_chat_id()
        if chat_id:
            break
        time.sleep(3)

    if not chat_id:
        print("❌ Не удалось получить chat_id")
        return

    print(f"✅ Подключён к chat_id: {chat_id}")
    send_message(chat_id, 
        "🤖 <b>Бот сигналов запущен!</b>\n\n"
        "📊 Актив: <b>Bitcoin OTC</b>\n"
        "⏱ Интервал анализа: каждые 5 минут\n"
        "☁️ Работает 24/7 на сервере\n\n"
        "Жди сигналов... 🚀"
    )

    last_signal = None

    while True:
        try:
            signal, reasons, price, ema20, ema50, rsi = analyze()
            now = datetime.datetime.utcnow().strftime("%H:%M UTC")

            if signal and signal != last_signal:
                msg = f"🔔 <b>СИГНАЛ!</b> [{now}]\n\n"
                msg += f"💰 Цена BTC: <b>${price:,.0f}</b>\n"
                msg += f"📊 Актив: <b>Bitcoin OTC</b>\n\n"
                msg += f"🎯 <b>{signal}</b>\n\n"
                msg += "📋 Причины:\n"
                for r in reasons:
                    msg += f"{r}\n"
                msg += f"\n📈 EMA20: ${ema20:,.0f}\n"
                msg += f"📈 EMA50: ${ema50:,.0f}\n"
                msg += f"📉 RSI: {rsi:.1f}\n\n"
                msg += "⏱ Время сделки: <b>5 минут</b>\n"
                msg += "⚠️ <i>Решение всегда за тобой!</i>"

                send_message(chat_id, msg)
                last_signal = signal
                print(f"✅ Сигнал отправлен: {signal}")
            else:
                print(f"[{now}] Нет сигнала | BTC: ${price:,.0f} | RSI: {rsi:.1f}")

            time.sleep(300)

        except Exception as e:
            print(f"❌ Ошибка: {e}")
            time.sleep(60)

if __name__ == "__main__":
    main()
