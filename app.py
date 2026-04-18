import streamlit as st
import requests
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from datetime import datetime
import time

st.set_page_config(
    page_title="もやし何袋買えるか監視ツール",
    page_icon="🌱",
    layout="wide"
)

MOYASHI_PRICE = 30  # もやし1袋30円

st.title("🌱 ビットコイン＝もやし何袋？監視ツール")
st.caption("40年エンジニアがPythonで作った｜もやしで生きている男の本気｜Data: CoinGecko API（無料・合法）")

@st.cache_data(ttl=600)
def get_btc_current_price():
    headers = {"accept": "application/json"}
    url = "https://api.coingecko.com/api/v3/simple/price"
    params = {
        "ids": "bitcoin",
        "vs_currencies": "jpy,usd",
        "include_24hr_change": "true",
        "include_market_cap": "true"
    }
    try:
        time.sleep(1)
        response = requests.get(url, params=params, headers=headers, timeout=15)
        if response.status_code == 200:
            return response.json()
        elif response.status_code == 429:
            st.warning("少し待ってから更新してください。")
    except Exception as e:
        st.error(f"接続エラー: {e}")
    return None

@st.cache_data(ttl=600)
def get_btc_history(days=30):
    headers = {"accept": "application/json"}
    url = "https://api.coingecko.com/api/v3/coins/bitcoin/market_chart"
    params = {
        "vs_currency": "jpy",
        "days": days,
        "interval": "daily"
    }
    try:
        time.sleep(1)
        response = requests.get(url, params=params, headers=headers, timeout=15)
        if response.status_code == 200:
            data = response.json()
            prices = data["prices"]
            df = pd.DataFrame(prices, columns=["timestamp", "price"])
            df["date"] = pd.to_datetime(df["timestamp"], unit="ms")
            return df
    except Exception as e:
        st.error(f"接続エラー: {e}")
    return None

with st.spinner("もやしを数えています..."):
    current = get_btc_current_price()
    time.sleep(2)
    history = get_btc_history(30)

if current and history is not None:
    btc_jpy = current["bitcoin"]["jpy"]
    btc_usd = current["bitcoin"]["usd"]
    change_24h = current["bitcoin"]["jpy_24h_change"]
    market_cap = current["bitcoin"]["jpy_market_cap"]

    moyashi_count = int(btc_jpy / MOYASHI_PRICE)
    market_cap_moyashi = int(market_cap / MOYASHI_PRICE)

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric(
            label="🌱 もやし何袋買える？",
            value=f"{moyashi_count:,}袋",
            delta=f"{change_24h:.2f}%（昨日より）"
        )
    with col2:
        st.metric(
            label="💴 今日のビットコイン（円）",
            value=f"¥{btc_jpy:,.0f}",
        )
    with col3:
        st.metric(
            label="🇺🇸 アメリカのおじさん換算",
            value=f"${btc_usd:,.0f}"
        )
    with col4:
        max_price = history["price"].max()
        min_price = history["price"].min()
        st.metric(
            label="📈 30日高値",
            value=f"¥{max_price:,.0f}",
        )

    st.divider()

    if change_24h >= 0:
        st.success(f"📈 昨日より {change_24h:.2f}% 上がった。もやしが {int(btc_jpy * change_24h / 100 / MOYASHI_PRICE):,}袋 多く買える。")
    else:
        st.error(f"📉 昨日より {abs(change_24h):.2f}% 下がった。もやしが {int(btc_jpy * abs(change_24h) / 100 / MOYASHI_PRICE):,}袋 消えた。")

    st.divider()

    st.subheader("🌱 30日間のもやし換算推移（1袋30円）")

    history["moyashi"] = history["price"] / MOYASHI_PRICE

    fig, ax = plt.subplots(figsize=(12, 5))
    ax.plot(history["date"], history["moyashi"],
            color='#4CAF50', linewidth=2, label='もやし換算（袋）')
    ax.fill_between(history["date"], history["moyashi"],
                    alpha=0.2, color='#4CAF50')

    max_moyashi = history["moyashi"].max()
    min_moyashi = history["moyashi"].min()
    max_date = history.loc[history["moyashi"].idxmax(), "date"]
    min_date = history.loc[history["moyashi"].idxmin(), "date"]

    ax.annotate(f'最多: {max_moyashi:,.0f}袋',
                xy=(max_date, max_moyashi),
                xytext=(10, -30), textcoords='offset points',
                fontsize=9, color='red',
                arrowprops=dict(arrowstyle='->', color='red'))
    ax.annotate(f'最少: {min_moyashi:,.0f}袋',
                xy=(min_date, min_moyashi),
                xytext=(10, 20), textcoords='offset points',
                fontsize=9, color='blue',
                arrowprops=dict(arrowstyle='->', color='blue'))

    ax.xaxis.set_major_formatter(mdates.DateFormatter('%m/%d'))
    ax.xaxis.set_major_locator(mdates.WeekdayLocator())
    ax.grid(True, alpha=0.3)
    ax.legend()
    ax.set_ylabel('もやし（袋）')
    st.pyplot(fig)

    st.divider()

    st.metric(
        label="🌍 地球全体の総もやし換算（時価総額）",
        value=f"{market_cap_moyashi:,}袋"
    )
    st.caption("※ もやし1袋30円で計算。地球上の全ビットコインでもやしを買い占めた場合の枚数です。")

    st.caption(f"最終更新: {datetime.now().strftime('%Y/%m/%d %H:%M:%S')} | "
               f"Data: CoinGecko API（無料・合法）| "
               f"このアプリはPythonで作られています")

    if st.button("🔄 もやしを数え直す"):
        st.cache_data.clear()
        st.rerun()

else:
    st.warning("もやしを数えています。1〜2分後に更新してください。")
    st.info("CoinGecko APIの無料プランはアクセス頻度に制限があります。")
    if st.button("🔄 もう一度もやしを数える"):
        st.cache_data.clear()
        st.rerun()

st.divider()
st.markdown("""
**このアプリについて**

40年エンジニアがPythonで作ったビットコイン監視ツールです。
もやしで生きている男が、もやし換算でビットコインを監視しています。

**なぜもやし換算なのか？**
有料記事が1冊も売れていないからです😭

作り方はnoteで有料公開中 → [Python副業完全記録](https://note.com/cinephileangel/m/m3da5ac0c94bb)

チップ（もやし1袋分=30円）はこちら → [ダンちゃんのnote](https://note.com/cinephileangel)
""")
