import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
import requests
from requests import Session

# --- 1. UI SETUP ---
st.set_page_config(page_title="Kunal Elite Terminal", layout="wide")

st.markdown("""
    <style>
    .stApp { background: #050a14; color: #ffffff; }
    .header-text { color: #ffd700; font-size: 35px; font-weight: bold; text-align: center; margin-bottom: 20px; }
    .kiyosaki-card { background: rgba(255, 215, 0, 0.05); border: 1px solid #ffd700; padding: 20px; border-radius: 15px; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. THE ULTIMATE ANTI-BLOCK ENGINE ---
def get_rsi(series, period=14):
    if len(series) < period: return pd.Series([0]*len(series))
    delta = series.diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
    rs = gain / loss
    return 100 - (100 / (1 + rs))

@st.cache_data(ttl=300)
def fetch_elite_data_v2(ticker):
    try:
        # Creating a session with real browser headers
        session = Session()
        session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36'
        })
        
        stock = yf.Ticker(ticker, session=session)
        
        # Download history with a direct call to bypass some blocks
        hist = stock.history(period="1y", interval="1d")
        
        if hist.empty:
            return None, None, None, None
            
        hist['RSI'] = get_rsi(hist['Close'])
        hist['EMA50'] = hist['Close'].ewm(span=50, adjust=False).mean()
        
        return stock.info, hist, stock.balance_sheet, stock.cashflow
    except Exception as e:
        return None, None, None, None

# --- 3. UI LAYOUT ---
st.markdown("<div class='header-text'>🏦 KUNAL ELITE: FINANCIAL TERMINAL</div>", unsafe_allow_html=True)

u_ticker = st.text_input("🔍 ENTER NSE SYMBOL (e.g. RELIANCE.NS):", value="TATAMOTORS.NS").upper().strip()

if st.button("🚀 DEEP SCAN"):
    with st.spinner(f"Accessing Legal Archives for {u_ticker}..."):
        info, hist_df, bs_df, cf_df = fetch_elite_data_v2(u_ticker)

    if info and hist_df is not None:
        # --- ROW 1: QUICK ASSET CHECK ---
        st.subheader("💰 Rich Dad Analysis")
        c1, c2, c3, c4 = st.columns(4)
        
        price = info.get('currentPrice') or hist_df['Close'].iloc[-1]
        debt = info.get('debtToEquity', 0)
        div = info.get('dividendYield', 0) * 100
        fcf = info.get('freeCashflow', 0)

        c1.metric("Live Price", f"₹{price:,.2f}")
        c2.metric("Debt/Equity", f"{debt:.2f}")
        c3.metric("Dividend Yield", f"{div:.2f}%")
        c4.metric("Free Cash Flow", f"₹{fcf/1e7:,.1f} Cr")

        # Tabs
        t_chart, t_bs, t_cf = st.tabs(["📊 CHART", "📋 BALANCE SHEET", "💸 CASH FLOW"])

        with t_chart:
            fig = go.Figure(data=[go.Candlestick(x=hist_df.index, open=hist_df['Open'], high=hist_df['High'], low=hist_df['Low'], close=hist_df['Close'])])
            fig.update_layout(template="plotly_dark", height=500, xaxis_rangeslider_visible=False)
            st.plotly_chart(fig, use_container_width=True)

        with t_bs:
            st.dataframe(bs_df, use_container_width=True)

        with t_cf:
            st.dataframe(cf_df, use_container_width=True)
            
    else:
        st.error("❌ Ticker Not Found or Yahoo Blocked. Please try: RELIANCE.NS or TCS.NS")

st.markdown("<br><hr><center>© 2026 Kunal Wealth-Tech | Rich Dad Edition</center>", unsafe_allow_html=True)
