import streamlit as st
import yfinance as yf
import pandas as pd
import ta
import requests
import time

# ==================================
# DISCORD
# ==================================

DISCORD_WEBHOOK = "https://discord.com/api/webhooks/1499397129217769734/mvCVc6ArmwgHySBie_0seTHHFfQaW_I7v-R4HZG_vzlZRcgFu3dIGNKKVMos0Br5yinP"

# ==================================
# TOP US STOCKS
# ==================================

SYMBOLS = [
    "NVDA","MSFT","AAPL","AMZN","GOOGL","META","PLTR",
    "TSLA","AMD","SMCI","COIN","SNOW","CRWD",
    "AVGO","MU","QCOM","INTC","MRVL","AMAT",
    "ASML","ARM","ADBE","CRM","ORCL","NOW",
    "DDOG","NET","PANW","SHOP","UBER","ABNB",

    "JPM","BAC","GS","MS","WFC","C",
    "BLK","SCHW","AXP","COF","SPGI","MCO",

    "XOM","CVX","OXY","SLB","COP",
    "EOG","MPC","PSX","VLO","DVN",

    "BA","LMT","RTX","CAT","GE",
    "DE","ETN","PH","HON","NOC","GD",

    "NKE","SBUX","MCD","WMT","COST","TGT",
    "HD","LOW","TJX","CMG",

    "JNJ","PFE","LLY","ABBV","MRK",
    "UNH","ISRG","ABT","TMO","DHR","SYK",

    "TMUS","VZ","T","CHTR",

    "LIN","FCX","NEM","APD","ECL",

    "NFLX","DIS","CMCSA",

    "O","PLD","AMT",

    "SPY","QQQ","IWM","ARKK",
    "DIA","SMH","SOXX","XLF","XLE","XLV"
]

# ==================================
# DISCORD
# ==================================

def send_discord(message):

    if not DISCORD_WEBHOOK:
        return

    try:

        requests.post(
            DISCORD_WEBHOOK,
            json={"content": message},
            timeout=10
        )

    except Exception as e:
        print(e)

# ==================================
# SCANNER (ORIGINAL LOGIC)
# ==================================

def scan_stock(symbol):

    try:

        df = yf.download(
            symbol,
            interval="1h",
            period="60d",
            auto_adjust=True,
            progress=False
        )

        if df.empty:
            return None

        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.get_level_values(0)

        df.dropna(inplace=True)

        df["ema_200"] = ta.trend.ema_indicator(
            df["Close"],
            window=200
        )

        df["bb_upper"] = ta.volatility.bollinger_hband(
            df["Close"]
        )

        df["bb_lower"] = ta.volatility.bollinger_lband(
            df["Close"]
        )

        df["vol_sma"] = (
            df["Volume"]
            .rolling(20)
            .mean()
        )

        df.dropna(inplace=True)

        if len(df) < 250:
            return None

        last = df.iloc[-2]

        high_volume = (
            last["Volume"]
            > last["vol_sma"] * 1.2
        )

        volume_ratio = round(
            last["Volume"] /
            last["vol_sma"],
            2
        )

        # LONG

        if (
            last["Close"] > last["ema_200"]
            and
            last["Close"] > last["bb_upper"]
            and
            high_volume
        ):

            return {
                "Symbol": symbol,
                "Signal": "LONG",
                "Price": round(
                    last["Close"],2
                ),
                "Volume Ratio": volume_ratio
            }

        # SHORT

        elif (
            last["Close"] < last["ema_200"]
            and
            last["Close"] < last["bb_lower"]
            and
            high_volume
        ):

            return {
                "Symbol": symbol,
                "Signal": "SHORT",
                "Price": round(
                    last["Close"],2
                ),
                "Volume Ratio": volume_ratio
            }

        return None

    except:
        return None

# ==================================
# STREAMLIT
# ==================================

def run_scanner():

    st.header("🚀 US Stock Scanner")

    col1, col2 = st.columns(2)

    with col1:

        run = st.button(
            "🚀 Run Scan",
            key="scan_button"
        )

    with col2:

        auto_refresh = st.checkbox(
            "🔄 Auto Refresh 5 Min"
        )

    # ==================================
    # AUTO REFRESH
    # ==================================

    if auto_refresh:

        if "refresh_time" not in st.session_state:

            st.session_state.refresh_time = time.time()

        now = time.time()

        if (
            now -
            st.session_state.refresh_time
        ) > 300:

            st.session_state.refresh_time = now
            st.rerun()

    # ==================================
    # RUN SCAN
    # ==================================

    if run:

        results = []

        progress = st.progress(0)

        for i, symbol in enumerate(SYMBOLS):

            result = scan_stock(symbol)

            if result:
                results.append(result)

            progress.progress(
                (i + 1) / len(SYMBOLS)
            )

        df_result = pd.DataFrame(results)

        if len(df_result):

            df_result = df_result.sort_values(
                "Volume Ratio",
                ascending=False
            )

        st.session_state["scanner_results"] = df_result

        # DISCORD

        if len(df_result):

            msg = "🔥 TOP SETUPS\n\n"

            for _, row in (
                df_result
                .head(5)
                .iterrows()
            ):

                msg += (
                    f"{row['Symbol']} | "
                    f"{row['Signal']} | "
                    f"Vol {row['Volume Ratio']}x\n"
                )

            send_discord(msg)

    # ==================================
    # DISPLAY
    # ==================================

    if "scanner_results" in st.session_state:

        df_result = st.session_state[
            "scanner_results"
        ]

        if len(df_result):

            st.success(
                f"Found {len(df_result)} setups"
            )

            long_df = (
                df_result[
                    df_result["Signal"]
                    == "LONG"
                ]
                .sort_values(
                    "Volume Ratio",
                    ascending=False
                )
            )

            short_df = (
                df_result[
                    df_result["Signal"]
                    == "SHORT"
                ]
                .sort_values(
                    "Volume Ratio",
                    ascending=False
                )
            )

            st.subheader(
                "🚀 TOP 10 LONG"
            )

            st.dataframe(
                long_df.head(10),
                use_container_width=True
            )

            st.subheader(
                "🔻 TOP 10 SHORT"
            )

            st.dataframe(
                short_df.head(10),
                use_container_width=True
            )

            st.subheader(
                "📊 ALL RESULTS"
            )

            st.dataframe(
                df_result,
                use_container_width=True
            )

            csv = (
                df_result
                .to_csv(index=False)
                .encode()
            )

            st.download_button(
                "📥 Export CSV",
                csv,
                "scanner_results.csv",
                "text/csv"
            )

        else:

            st.warning(
                "No setup found ❌"
            )
