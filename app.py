import streamlit as st

from scanner_profile1 import run_scanner
from scanner_profile2 import run_ichimoku

st.set_page_config(
    page_title="US Stock Platform",
    layout="wide"
)

st.title("📈 US Stock Trading Platform")

profile = st.sidebar.selectbox(
    "Select Profile",
    [
        "US Stock Scanner + Discord",
        "Ichimoku Trend Scanner 4H"
    ]
)

if profile == "US Stock Scanner + Discord":
    run_scanner()

if profile == "Ichimoku Trend Scanner 4H":
    run_ichimoku()