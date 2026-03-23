import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
from difflib import get_close_matches # No extra library needed

# --- 1. CONFIG & THEME ---
st.set_page_config(page_title="Kunal Wealth-Tech Elite", layout="wide")

st.markdown("""
    <style>
    .stApp { background: #050a14; color: #ffffff; }
    .main-title { color: #ffd700; text-align: center; font-size: 40px; font-weight: 800; margin-bottom: 10px; }
    .kiyosaki-card { background: rgba(255, 215, 0, 0.05); border: 1px solid #ffd700; padding: 20px; border-radius: 15px; text-align: center; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. SMART SEARCH LOGIC (No .NS needed) ---
STOCKS_DB = {
    "RELIANCE": "RELIANCE.NS", "TATAMOTORS": "TATAMOTORS.NS", "ZOMATO": "ZOMATO.NS",
    "SBIN": "SBIN.NS", "TCS": "TCS.NS", "INFY": "INFY.NS", "ITC": "ITC.NS",
    "HDFCBANK": "HDFCBANK.NS", "ADANIENT": "ADANIENT.NS", "PAYTM": "PAYTM.NS",
    "TATASTEEL": "TATASTEEL.NS", "WIPRO": "WIPRO.NS", "BHARTIARTL": "BHARTIARTL.NS"
}

def get_ticker(user_input):
    clean_input = user_input.upper().replace(" ", "")
    # Agar user ne pehle se .NS dala hai
    if clean_input.endswith(".NS"): return clean_input
    
    # Try matching with DB
    matches = get_close_matches(clean_input, STOCKS_DB.keys(), n=1, cutoff=0.6)
    if matches:
        return STOCKS_DB[matches[0]]
    
    # Otherwise just append .NS
    return f"{clean_input}.NS"

# --- 3. DATA ENGINE ---
@st.cache_data(ttl=600)
def fetch_all_data(ticker):
    try:
        stock = yf.Ticker(ticker)
        hist = stock.history(period="1y")
        if hist.empty: return None, None, None, None
        
        # Manual RSI Calculation
        delta = hist['Close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        hist['RSI'] = 100 - (100 / (1 + (gain / loss)))
        
        return stock.info, hist, stock.balance_sheet, stock.cashflow
    except:
        return None, None, None, None

# --- 4. DASHBOARD UI ---
st.markdown("<div class='main-title'>🏦 KUNAL WEALTH-TECH : PRO TERMINAL</div>", unsafe_allow_html=True)

# Search Bar
query = st.text_input("🔍 Company ka naam likho (e.g. 'tata', 'zomato', 'reliance'):", value="RELIANCE")
ticker = get_ticker(query)

if st.button("🚀 START DEEP ANALYSIS"):
    with st.spinner(f"Analyzing {ticker}..."):
        info, hist, bs, cf = fetch_all_data(ticker)
        
    if info and hist is not None:
        st.success(f"Found: {info.get('longName', ticker)}")
        
        # Row 1: Kiyosaki Highlights
        st.subheader("💰 Rich Dad Fundamentals")
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Live Price", f"₹{info.get('currentPrice', 0):,.2f}")
        c2.metric("Debt/Equity", f"{info.get('debtToEquity', 0):.2f}")
        c3.metric("Div. Yield", f"{info.get('dividendYield', 0)*100:.2f}%")
        c4.metric("Free Cash Flow", f"₹{info.get('freeCashflow', 0)/1e7:,.1f} Cr")

        # Row 2: Tabs
        tab_chart, tab_bs, tab_cf = st.tabs(["📊 ANALYSIS CHART", "📋 BALANCE SHEET", "💸 CASH FLOW"])
        
        with tab_chart:
            fig = go.Figure(data=[go.Candlestick(x=hist.index, open=hist['Open'], high=hist['High'], low=hist['Low'], close=hist['Close'])])
            fig.update_layout(template="plotly_dark", height=500, xaxis_rangeslider_visible=False)
            st.plotly_chart(fig, use_container_width=True)
            
        with tab_bs:
            st.write("### Official Balance Sheet (Assets & Liabilities)")
            st.dataframe(bs, use_container_width=True)
            
        with tab_cf:
            st.write("### Official Cash Flow (Actual Money)")
            st.dataframe(cf, use_container_width=True)
    else:
        st.error(f"Data nahi mila! Check karo '{ticker}' sahi hai ya nahi.")

st.markdown("<br><hr><center>Kunal Wealth-Tech Elite © 2026 | No-Friction Analysis</center>", unsafe_allow_html=True)
