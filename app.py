import streamlit as st
import yfinance as yf
import pandas as pd

# 1. Branding & Style
st.set_page_config(page_title="Kunal Wealth-Tech", page_icon="🦁", layout="wide")

# CSS to hide Streamlit header/footer
hide_style = """
    <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    </style>
"""
st.markdown(hide_style, unsafe_allow_html=True)

# 2. Sidebar Branding
st.sidebar.markdown("<h1 style='text-align: center; color: #FFD700;'>🦁 KUNAL</h1>", unsafe_allow_html=True)
st.sidebar.markdown("<p style='text-align: center;'>Wealth-Tech Analyst v1.1</p>", unsafe_allow_html=True)
st.sidebar.divider()

# Input with .NS reminder
ticker_input = st.sidebar.text_input("Stock Symbol (e.g., SBIN.NS):", "TCS.NS").upper()
btn = st.sidebar.button("Analyze Now")

if btn:
    try:
        with st.spinner('Fetching Real-Time Fundamentals...'):
            stock = yf.Ticker(ticker_input)
            
            # Forced Data Fetching
            info = stock.info
            
            # Agar info khali hai ya fundamentals nahi mil rahe
            if not info or 'currentPrice' not in info:
                st.error("Data nahi mil raha! Kya aapne '.NS' lagaya hai? (Example: RELIANCE.NS)")
                st.stop()

            # --- DISPLAY SECTION ---
            st.title(f"📈 {info.get('longName', ticker_input)}")
            
            # Metrics Row
            m1, m2, m3, m4 = st.columns(4)
            curr_price = info.get('currentPrice', 0)
            mcap = info.get('marketCap', 0) / 10**7 # In Crores
            m1.metric("Live Price", f"₹{curr_price:,.2f}")
            m2.metric("Market Cap", f"{mcap:,.0f} Cr")
            m3.metric("52W High", f"₹{info.get('fiftyTwoWeekHigh', 0):,.2f}")
            m4.metric("52W Low", f"₹{info.get('fiftyTwoWeekLow', 0):,.2f}")

            st.divider()

            # Fundamental Section
            st.subheader("👨‍🏫 Fundamental Health Scorecard")
            f1, f2, f3 = st.columns(3)
            
            # Handling Missing Fundamental Data
            debt_equity = info.get('debtToEquity', 0)
            roe = info.get('returnOnEquity', 0) * 100
            cash = info.get('freeCashflow', 0)

            with f1:
                st.write("**Debt-to-Equity**")
                st.title(f"{debt_equity:.2f}")
                if debt_equity < 100: st.success("Low Debt ✅")
                else: st.warning("High Debt ⚠️")

            with f2:
                st.write("**Return on Equity (ROE)**")
                st.title(f"{roe:.1f}%")
                if roe > 15: st.success("High Growth ✅")
                else: st.error("Low Growth ❌")

            with f3:
                st.write("**Cash Flow Status**")
                if cash > 0: st.success("Positive Cash Flow 💰")
                else: st.info("Data Unclear/Negative 💸")

            # Chart Section
            st.divider()
            st.subheader("Price Movement (Last 1 Year)")
            hist = stock.history(period="1y")
            if not hist.empty:
                st.line_chart(hist['Close'])
            else:
                st.write("Chart data available nahi hai.")

    except Exception as e:
        st.error(f"Technical Error: {e}")

# Footer
st.markdown("<br><hr><center>Developed & Owned by Kunal © 2026</center>", unsafe_allow_html=True)
