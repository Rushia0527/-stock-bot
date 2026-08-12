import datetime
import time
import requests
import yfinance as yf

# ==========================================
# 【設定】DiscordウェブフックURL
# ==========================================
DISCORD_WEBHOOK_URL = "https://discord.com/api/webhooks/1536912331097907313/ERdrTQA5Eqn9OovCMs2qQavrNghEXUGWv9r13WL2tJd6wJLDAkpZW47FglwgcQSKrwY1"

# Gemini厳選！GMO対応のおすすめ主要25銘柄
TARGET_ASSETS = {
    # --- 【商品（コモディティ）：一番トレードしやすい】 ---
    "GC=F": "[GMO商品] 金スポット (ゴールド) ★一押し",
    "CL=F": "[GMO商品] WTI原油 ★おすすめ",
    "SI=F": "[GMO商品] 銀スポット (シルバー)",

    # --- 【株価指数：スプレッド最狭＆高ボラ】 ---
    "^N225": "[GMO指数] 日本225 (日経平均) ★定番",
    "^IXIC": "[GMO指数] 米国NQ100 (NASDAQ) ★高ボラ",
    "^GSPC": "[GMO指数] 米国S&P500",
    "^DJI":  "[GMO指数] 米国30 (NYダウ)",

    # --- 【米国株：トレンドが強烈な人気銘柄】 ---
    "NVDA":  "[GMO米国株] エヌビディア ★人気",
    "TSLA":  "[GMO米国株] テスラ ★高ボラ",
    "AAPL":  "[GMO米国株] アップル",
    "MSFT":  "[GMO米国株] マイクロソフト",
    "AMZN":  "[GMO米国株] アマゾン",
    "GOOGL": "[GMO米国株] グーグル",
    "META":  "[GMO米国株] メタ",

    # --- 【日本株：GMOで買える主力個別株】 ---
    "7203.T": "[GMO日本株] トヨタ自動車",
    "6758.T": "[GMO日本株] ソニーグループ",
    "8306.T": "[GMO日本株] 三菱UFJフィナンシャルG",
    "9984.T": "[GMO日本株] ソフトバンクグループ",
    "6857.T": "[GMO日本株] アドバンテスト",
    "7011.T": "[GMO日本株] 三菱重工業",

    # --- 【為替（FX）：低コストの主要通貨】 ---
    "JPY=X":    "[GMO FX] 米ドル/円 ★王道",
    "EURJPY=X": "[GMO FX] ユーロ/円",
    "GBPJPY=X": "[GMO FX] ポンド/円",

    # --- 【暗号資産：他社アプリ用注目株】 ---
    "BTC-JPY": "[暗号資産] ビットコイン (BTC/円)",
    "ETH-JPY": "[暗号資産] イーサリアム (ETH/円)"
}

last_signals = {}


def send_discord_message(text):
    data = {"content": text}
    try:
        requests.post(DISCORD_WEBHOOK_URL, json=data, timeout=10)
    except Exception as e:
        print(f"Discord送信エラー: {e}")


def check_markets():
    now_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"\n[{now_str}] 1時間足スキャン実行中（厳選{len(TARGET_ASSETS)}銘柄）...")

    buy_signals = []
    sell_signals = []

    for symbol, name in TARGET_ASSETS.items():
        try:
            df = yf.download(symbol, period="1mo", interval="1h", progress=False)
            if df.empty or len(df) < 20:
                continue

            df['SMA_short'] = df['Close'].rolling(window=5).mean()
            df['SMA_long'] = df['Close'].rolling(window=20).mean()

            latest_price = df['Close'].iloc[-1].item()
            sma_s_today = df['SMA_short'].iloc[-1].item()
            sma_l_today = df['SMA_long'].iloc[-1].item()
            sma_s_prev = df['SMA_short'].iloc[-2].item()
            sma_l_prev = df['SMA_long'].iloc[-2].item()

            unit = "ドル" if ("GMO米国株" in name or "GMO指数" in name or "GMO商品" in name) and not name.endswith("円") else "円"
            if "日本225" in name:
                unit = "円"

            current_signal = None
            if sma_s_prev <= sma_l_prev and sma_s_today > sma_l_today:
                current_signal = "BUY"
            elif sma_s_prev >= sma_l_prev and sma_s_today < sma_l_today:
                current_signal = "SELL"

            if current_signal and last_signals.get(symbol) != current_signal:
                last_signals[symbol] = current_signal
                text = f"・{name}: **{latest_price:,.1f}{unit}**"
                if current_signal == "BUY":
                    buy_signals.append(text)
                    print(f"  [発見] 買いサイン: {name}")
                else:
                    sell_signals.append(text)
                    print(f"  [発見] 売りサイン: {name}")

            time.sleep(0.02)
        except Exception:
            continue

    if buy_signals or sell_signals:
        if buy_signals:
            msg_buy = f"⚡ **【1時間足 買いアラート】** (`{now_str}`)\n🚀 **【買いサイン発生】**\n" + "\n".join(buy_signals)
            send_discord_message(msg_buy)
        if sell_signals:
            msg_sell = f"⚡ **【1時間足 売りアラート】** (`{now_str}`)\n🔻 **【売りサイン発生】**\n" + "\n".join(sell_signals)
            send_discord_message(msg_sell)


# --- メインループ ---
send_discord_message("🟢 **【売買アラート Bot】** GMO厳選おすすめ銘柄モードで起動しました！（1時間ごとに自動判定）")
print("1時間足の常時監視を開始しました。この画面は開いたままにしてください。")

while True:
    try:
        check_markets()
    except Exception as e:
        print(f"エラー発生: {e}")
    time.sleep(3600)
