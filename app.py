import streamlit as st
import yfinance as yf
import pandas as pd

# 1. Branding
st.set_page_config(page_title="Kunal Wealth-Tech", page_icon="🦁", layout="wide")

# Hide Streamlit elements
st.markdown("<style>#MainMenu {visibility: hidden;} footer {visibility: hidden;} header {visibility: hidden;}</style>", unsafe_allow_html=True)

# 2. Sidebar
st.sidebar.markdown("<h1 style='text-align: center; color: #FFD700;'>🦁 KUNAL</h1>", unsafe_allow_html=True)
ticker = st.sidebar.text_input("Stock Symbol (e.g., RELIANCE.NS):", "TCS.NS").upper()
btn = st.sidebar.button("Analyze Now")

# 3. Logic
if btn:
    try:
        stock = yf.Ticker(ticker)
        info = stock.info
        hist = stock.history(period="1y")

        st.title(f"📈 {info.get('longName', ticker)}")
        
        c1, c2, c3 = st.columns(3)
        c1.metric("Current Price", f"₹{info.get('currentPrice', 0):,.2f}")
        c2.metric("ROE", f"{info.get('returnOnEquity', 0)*100:.1f}%")
        c3.metric("Debt-to-Equity", f"{info.get('debtToEquity', 0):.2f}")

        st.line_chart(hist['Close'])

        st.subheader("👨‍🏫 Analyst Verdict")
        if info.get('debtToEquity', 100) < 100 and info.get('returnOnEquity', 0)*100 > 15:
            st.success("Kiyosaki says: This is an ASSET! 💎")
        else:
            st.warning("Kiyosaki says: Be Careful! Could be a LIABILITY. ⚠️")
    except:
        st.error("Sahi symbol dalein!")

st.markdown("<br><hr><center>Developed & Owned by Kunal © 2026</center>", unsafe_allow_html=True)
