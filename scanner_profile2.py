import streamlit as st
import yfinance as yf
import pandas as pd
import ta

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

def run_ichimoku():

    st.header("☁️ Ichimoku Scanner 4H PRO")

    run = st.button(
        "☁️ Run Ichimoku",
        key="ichi_btn"
    )

    if run:

        results=[]

        progress=st.progress(0)

        for i,sym in enumerate(SYMBOLS):

            try:

                df = yf.download(
                    sym,
                    period="1y",
                    interval="4h",
                    progress=False,
                    auto_adjust=True
                )

                if len(df)<200:
                    continue

                if isinstance(
                    df.columns,
                    pd.MultiIndex
                ):
                    df.columns=df.columns.get_level_values(0)

                close=df["Close"]
                high=df["High"]
                low=df["Low"]

                df["EMA200"] = ta.trend.ema_indicator(
                    close,
                    200
                )

                df["ADX"] = ta.trend.adx(
                    high,
                    low,
                    close
                )

                df["ATR"] = (
                    ta.volatility
                    .average_true_range(
                        high,
                        low,
                        close
                    )
                )

                ichi = ta.trend.IchimokuIndicator(
                    high,
                    low
                )

                df["TENKAN"] = (
                    ichi
                    .ichimoku_conversion_line()
                )

                df["KIJUN"] = (
                    ichi
                    .ichimoku_base_line()
                )

                last=df.iloc[-1]

                score=0

                if last["Close"] > last["EMA200"]:
                    score += 30

                if last["TENKAN"] > last["KIJUN"]:
                    score += 30

                if last["ADX"] > 25:
                    score += 40

                entry=last["Close"]
                atr=last["ATR"]

                results.append({

                    "Symbol":sym,

                    "Score":score,

                    "ADX":round(
                        last["ADX"],
                        2
                    ),

                    "Entry":round(
                        entry,
                        2
                    ),

                    "SL":round(
                        entry-atr,
                        2
                    ),

                    "TP":round(
                        entry+atr*3,
                        2
                    )
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

        st.session_state.ichi = df_result

    if "ichi" in st.session_state:

        st.dataframe(
            st.session_state.ichi,
            use_container_width=True
        )

        csv = (
            st.session_state.ichi
            .to_csv(index=False)
            .encode()
        )

        st.download_button(
            "📥 Export CSV",
            csv,
            "ichimoku.csv",
            "text/csv"
        )