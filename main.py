import time
import requests
import yfinance as yf
from datetime import datetime

# ==========================================
# 【設定】DiscordウェブフックURL
# ==========================================
DISCORD_WEBHOOK_URL = "https://discord.com/api/webhooks/1536912331097907313/ERdrTQA5Eqn9OovCMs2qQavrNghEXUGWv9r13WL2tJd6wJLDAkpZW47FglwgcQSKrwY1"

TARGET_ASSETS = {
    # --- 【日本株 (50銘柄)】 ---
    "7203.T": "[日本株] トヨタ自動車", "6758.T": "[日本株] ソニーグループ", "8306.T": "[日本株] 三菱UFJフィナンシャルG", "8411.T": "[日本株] みずほフィナンシャルG", "8316.T": "[日本株] 三井住友フィナンシャルG", "6920.T": "[日本株] レーザーテック", "8035.T": "[日本株] 東京エレクトロン", "6857.T": "[日本株] アドバンテスト", "6146.T": "[日本株] ディスコ", "9984.T": "[日本株] ソフトバンクグループ", "7974.T": "[日本株] 任天堂", "8058.T": "[日本株] 三菱商事", "8031.T": "[日本株] 三井物産", "9983.T": "[日本株] ファーストリテイリング", "7011.T": "[日本株] 三菱重工業", "9432.T": "[日本株] NTT", "9433.T": "[日本株] KDDI", "9434.T": "[日本株] ソフトバンク", "4519.T": "[日本株] 中外製薬", "6501.T": "[日本株] 日立製作所", "7267.T": "[日本株] ホンダ", "6367.T": "[日本株] ダイキン工業", "4063.T": "[日本株] 信越化学工業", "6981.T": "[日本株] 村田製作所", "7751.T": "[日本株] キヤノン", "2914.T": "[日本株] JT (日本タバコ)", "8001.T": "[日本株] 伊藤忠商事", "8002.T": "[日本株] 丸紅", "8053.T": "[日本株] 住友商事", "8591.T": "[日本株] オリックス", "8766.T": "[日本株] 東京海上HD", "8308.T": "[日本株] りそなHD", "9101.T": "[日本株] 日本郵船", "9104.T": "[日本株] 商船三井", "9107.T": "[日本株] 川崎汽船", "4502.T": "[日本株] 武田薬品", "4503.T": "[日本株] アステラス製薬", "4568.T": "[日本株] 第一三共", "6503.T": "[日本株] 三菱電機", "6702.T": "[日本株] 富士通", "6723.T": "[日本株] ルネサス", "6902.T": "[日本株] デンソー", "7733.T": "[日本株] オリンパス", "4901.T": "[日本株] 富士フイルムHD", "5108.T": "[日本株] ブリヂストン", "6273.T": "[日本株] SMC", "6301.T": "[日本株] 小松製作所", "4661.T": "[日本株] オリエンタルランド", "9201.T": "[日本株] 日本航空 (JAL)", "9202.T": "[日本株] ANAホールディングス",

    # --- 【米国株 (30銘柄)】 ---
    "NVDA":  "[米国株] エヌビディア", "TSLA":  "[米国株] テスラ", "AAPL":  "[米国株] アップル", "MSFT":  "[米国株] マイクロソフト", "AMZN":  "[米国株] アマゾン", "GOOGL": "[米国株] アルファベット", "META":  "[米国株] メタ", "AMD":   "[米国株] AMD", "AVGO":  "[米国株] ブロードコム", "NFLX":  "[米国株] ネットフリックス", "PLTR":  "[米国株] パランティア", "ARM":   "[米国株] アーム", "INTC":  "[米国株] インテル", "QCOM":  "[米国株] クアルコム", "MU":    "[米国株] マイクロン", "SMCI":  "[米国株] スーパー・マイクロ", "BAC":   "[米国株] バンク・オブ・アメリカ", "JPM":   "[米国株] JPモルガン", "GS":    "[米国株] ゴールドマン・サックス", "V":     "[米国株] ビザ", "MA":    "[米国株] マスターカード", "DIS":   "[米国株] ディズニー", "NKE":   "[米国株] ナイキ", "KO":    "[米国株] コカ・コーラ", "PEP":   "[米国株] ペプシコ", "PFE":   "[米国株] ファイザー", "LLY":   "[米国株] イーライリリー", "UNH":   "[米国株] ユナイテッドヘルス", "COIN":  "[米国株] コインベース", "MSTR":  "[米国株] マイクロストラテジー",

    # --- 【指数・商品・FX・暗号資産 (20銘柄)】 ---
    "^N225":    "[指数] 日経平均株価", "^IXIC":    "[指数] NASDAQ100", "^GSPC":    "[指数] S&P500", "^DJI":     "[指数] NYダウ", "^RUT":     "[指数] ラッセル2000", "^FTSE":    "[指数] イギリスFTSE100", "^GDAXI":   "[指数] ドイツDAX", "GC=F":     "[商品] 金スポット (ゴールド)", "SI=F":     "[商品] 銀スポット (シルバー)", "CL=F":     "[商品] WTI原油", "NG=F":     "[商品] 天然ガス", "HG=F":     "[商品] 銅", "C=F":      "[商品] トウモロコシ", "S=F":      "[商品] 大豆", "JPY=X":    "[FX] 米ドル/円", "EURJPY=X": "[FX] ユーロ/円", "GBPJPY=X": "[FX] ポンド/円", "AUDJPY=X": "[FX] 豪ドル/円", "BTC-JPY":  "[暗号資産] ビットコイン (BTC/円)", "ETH-JPY":  "[暗号資産] イーサリアム (ETH/円)"
}

last_signals = {}

def send_discord_message(text):
    try:
        requests.post(DISCORD_WEBHOOK_URL, json={"content": text}, timeout=10)
    except Exception as e:
        print(f"送信エラー: {e}")

def check_markets():
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    time_short = datetime.now().strftime("%H:%M")
    
    buy_signals = []
    sell_signals = []

    try:
        # 全100銘柄を一括ダウンロード（高速化＆タイムアウト防止）
        tickers_list = list(TARGET_ASSETS.keys())
        data = yf.download(tickers_list, period="7d", interval="1h", group_by='ticker', progress=False)

        for symbol, name in TARGET_ASSETS.items():
            try:
                if len(tickers_list) > 1:
                    if symbol not in data or data[symbol].empty:
                        continue
                    df = data[symbol].dropna(how='all')
                else:
                    df = data.dropna(how='all')

                if len(df) < 20:
                    continue

                df['SMA_short'] = df['Close'].rolling(window=5).mean()
                df['SMA_long'] = df['Close'].rolling(window=20).mean()

                latest_price = float(df['Close'].iloc[-1])
                sma_s_today = float(df['SMA_short'].iloc[-1])
                sma_l_today = float(df['SMA_long'].iloc[-1])
                sma_s_prev = float(df['SMA_short'].iloc[-2])
                sma_l_prev = float(df['SMA_long'].iloc[-2])

                unit = "ドル" if ("[米国株]" in name or "[商品]" in name or "[指数]" in name) and not name.endswith("円") and "日経" not in name else "円"

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
                    else:
                        sell_signals.append(text)

            except Exception as e:
                continue

    except Exception as e:
        print(f"一括取得エラー: {e}")

    # 通知処理
    if buy_signals or sell_signals:
        if buy_signals:
            send_discord_message(f"⚡ **【1時間足 買いアラート】** (`{now_str}`)\n🚀 **【買いサイン発生】**\n" + "\n".join(buy_signals))
        if sell_signals:
            send_discord_message(f"⚡ **【1時間足 売りアラート】** (`{now_str}`)\n🔻 **【売りサイン発生】**\n" + "\n".join(sell_signals))
    else:
        send_discord_message(f"🟢 【生存確認】全100銘柄のスキャンが完了しました（{time_short}）。現在、新規の売買サインはありません。")

# --- 起動通知 ---
send_discord_message("🟢 **【売買アラート Bot】** 高速・安定版（一括スキャン）で起動しました！")

while True:
    try:
        check_markets()
    except Exception as e:
        print(f"ループ内エラー: {e}")
    time.sleep(3600)
