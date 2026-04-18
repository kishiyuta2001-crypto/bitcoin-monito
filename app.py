import streamlit as st
import requests
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from datetime import datetime
import time

st.set_page_config(
    page_title="Bitcoin Monitor | 40年エンジニア作",
    page_icon="₿",
    layout="wide"
)

st.title("₿ Bitcoin Monitor")
st.caption("Powered by Python | 40年エンジニア作 | Data: CoinGecko API")

@st.cache_data(ttl=300)  # 5分キャッシュ
def get_btc_current_price():
    url = "https://api.coingecko.com/api/v3/simple/price"
    params = {
        "ids": "bitcoin",
        "vs_currencies": "jpy,usd",
        "include_24hr_change": "true",
        "include_market_cap": "true"
    }
    try:
        response = requests.get(url, params=params, timeout=10)
        if response.status_code == 200:
            return response.json()
    except:
        pass
    return None

@st.cache_data(ttl=300)
def get_btc_history(days=30):
    url = "https://api.coingecko.com/api/v3/coins/bitcoin/market_chart"
    params = {
        "vs_currency": "jpy",
        "days": days,
        "interval": "daily"
    }
    try:
        response = requests.get(url, params=params, timeout=10)
        if response.status_code == 200:
            data = response.json()
            prices = data["prices"]
            df = pd.DataFrame(prices, columns=["timestamp", "price"])
            df["date"] = pd.to_datetime(df["timestamp"], unit="ms")
            return df
    except:
        pass
    return None

# データ取得
with st.spinner("データ取得中..."):
    current = get_btc_current_price()
    history = get_btc_history(30)

if current and history is not None:
    btc_jpy = current["bitcoin"]["jpy"]
    btc_usd = current["bitcoin"]["usd"]
    change_24h = current["bitcoin"]["jpy_24h_change"]
    market_cap = current["bitcoin"]["jpy_market_cap"]

    # 現在価格表示
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric(
            label="現在価格（円）",
            value=f"¥{btc_jpy:,.0f}",
            delta=f"{change_24h:.2f}%"
        )

    with col2:
        st.metric(
            label="現在価格（USD）",
            value=f"${btc_usd:,.0f}"
        )

    with col3:
        max_price = history["price"].max()
        st.metric(
            label="30日高値",
            value=f"¥{max_price:,.0f}"
        )

    with col4:
        min_price = history["price"].min()
        st.metric(
            label="30日安値",
            value=f"¥{min_price:,.0f}"
        )

    st.divider()

    # グラフ
    st.subheader("30日間価格推移")

    fig, ax = plt.subplots(figsize=(12, 5))
    ax.plot(history["date"], history["price"],
            color='#F7931A', linewidth=2, label='BTC/JPY')
    ax.fill_between(history["date"], history["price"],
                    alpha=0.2, color='#F7931A')

    max_date = history.loc[history["price"].idxmax(), "date"]
    min_date = history.loc[history["price"].idxmin(), "date"]

    ax.annotate(f'High: ¥{max_price:,.0f}',
                xy=(max_date, max_price),
                xytext=(10, -30), textcoords='offset points',
                fontsize=9, color='red',
                arrowprops=dict(arrowstyle='->', color='red'))

    ax.annotate(f'Low: ¥{min_price:,.0f}',
                xy=(min_date, min_price),
                xytext=(10, 20), textcoords='offset points',
                fontsize=9, color='blue',
                arrowprops=dict(arrowstyle='->', color='blue'))

    ax.xaxis.set_major_formatter(mdates.DateFormatter('%m/%d'))
    ax.xaxis.set_major_locator(mdates.WeekdayLocator())
    ax.grid(True, alpha=0.3)
    ax.legend()
    ax.set_ylabel('Price (JPY)')

    st.pyplot(fig)

    st.divider()

    # 時価総額
    st.metric(
        label="時価総額（円）",
        value=f"¥{market_cap:,.0f}"
    )

    st.caption(f"最終更新: {datetime.now().strftime('%Y/%m/%d %H:%M:%S')} | "
               f"Data: CoinGecko API（無料・合法）| "
               f"このアプリはPythonで作られています")

    # 更新ボタン
    if st.button("🔄 データを更新する"):
        st.cache_data.clear()
        st.rerun()

else:
    st.error("データの取得に失敗しました。しばらく待ってから更新してください。")

st.divider()
st.markdown("""
**このアプリについて**

40年エンジニアがPythonで作ったビットコイン価格監視ツールです。
CoinGecko APIを使用しています（無料・合法）。

詳しい作り方はnoteで公開中 → [Python副業完全記録](https://note.com/cinephileangel/m/m3da5ac0c94bb)
""")
