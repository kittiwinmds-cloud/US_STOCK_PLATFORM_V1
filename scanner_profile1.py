import streamlit as st
import yfinance as yf
import pandas as pd
import ta
import requests
import io

DISCORD_WEBHOOK = "https://discord.com/api/webhooks/1499397129217769734/mvCVc6ArmwgHySBie_0seTHHFfQaW_I7v-R4HZG_vzlZRcgFu3dIGNKKVMos0Br5yinP"

SYMBOLS = [
    "NVDA","MSFT","AAPL","AMZN","GOOGL","META","PLTR",
    "TSLA","AMD","SMCI","COIN","SNOW","CRWD",
    "AVGO","MU","QCOM","INTC","MRVL","AMAT",
    "JPM","BAC","GS","MS","WFC","C",
    "XOM","CVX","OXY","SLB","COP",
    "BA","LMT","RTX","CAT","GE",
    "NKE","SBUX","MCD","WMT","COST","TGT",
    "JNJ","PFE","LLY","ABBV","MRK",
    "NFLX","DIS","CMCSA",
    "O","PLD","AMT",
    "SPY","QQQ","IWM","ARKK",
    "ASML","ARM","ADBE","CRM","ORCL","NOW",
    "DDOG","NET","PANW","SHOP","UBER","ABNB",
    "BLK","SCHW","AXP","COF","SPGI","MCO",
    "EOG","MPC","PSX","VLO","DVN",
    "DE","ETN","PH","HON","NOC","GD",
    "UNH","ISRG","ABT","TMO","DHR","SYK",
    "HD","LOW","TJX","CMG",
    "TMUS","VZ","T","CHTR",
    "LIN","FCX","NEM","APD","ECL",
    "DIA","SMH","SOXX","XLF","XLE","XLV"
]

def send_discord(msg):

    if not DISCORD_WEBHOOK:
        return

    try:
        requests.post(
            DISCORD_WEBHOOK,
            json={"content": msg},
            timeout=10
        )

    except Exception as e:
        print(e)


def run_scanner():

    st.header("🚀 US Stock Scanner PRO")

    auto = st.checkbox("Auto Refresh")

    run = st.button(
        "🚀 Run Scan",
        key="scanner_run"
    )

    if run:

        results = []

        progress = st.progress(0)

        for i,sym in enumerate(SYMBOLS):

            try:

                df = yf.download(
                    sym,
                    period="60d",
                    interval="1h",
                    progress=False,
                    auto_adjust=True
                )

                if len(df) < 200:
                    continue

                if isinstance(df.columns,pd.MultiIndex):
                    df.columns=df.columns.get_level_values(0)

                df["EMA200"] = ta.trend.ema_indicator(
                    df["Close"],
                    window=200
                )

                df["VOL20"] = (
                    df["Volume"]
                    .rolling(20)
                    .mean()
                )

                last=df.iloc[-2]

                score=0

                if last["Close"] > last["EMA200"]:
                    score += 50

                if last["Volume"] > last["VOL20"]:
                    score += 50

                signal="LONG"

                if last["Close"] < last["EMA200"]:
                    signal="SHORT"

                results.append({
                    "Symbol":sym,
                    "Signal":signal,
                    "Score":score
                })

            except:
                pass

            progress.progress(
                (i+1)/len(SYMBOLS)
            )

        df_result = pd.DataFrame(results)

        df_result = df_result.sort_values(
            "Score",
            ascending=False
        )

        st.session_state.scanner = df_result

        msg = "🔥 TOP SETUPS\n\n"

        for _,row in df_result.head(5).iterrows():

            msg += (
                f"{row['Symbol']} "
                f"{row['Signal']} "
                f"Score:{row['Score']}\n"
            )

        send_discord(msg)

    if "scanner" in st.session_state:

        df_result = st.session_state.scanner

        st.metric(
            "Signals",
            len(df_result)
        )

        st.dataframe(
            df_result,
            use_container_width=True
        )

        csv = df_result.to_csv(
            index=False
        ).encode()

        st.download_button(
            "📥 Export CSV",
            csv,
            "scanner.csv",
            "text/csv"
        )

        st.subheader("🏆 Top 10")

        st.dataframe(
            df_result.head(10),
            use_container_width=True
        )

    if auto:
        st.rerun()