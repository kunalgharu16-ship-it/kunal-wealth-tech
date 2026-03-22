import streamlit as st
import yfinance as yf
import pandas as pd
import pandas_ta as ta
import plotly.graph_objects as go
import requests

# --- 1. THEME & UI ---
st.set_page_config(page_title="Kunal Wealth-Tech Elite", layout="wide")

st.markdown("""
    <style>
    .stApp { background: #0a0e17; color: #ffffff; }
    .kiyosaki-header { 
        background: linear-gradient(90deg, #ffd700, #b8860b);
        -webkit-background-clip: text; -webkit-text-fill-color: transparent;
        font-size: 35px; font-weight: bold; text-align: center;
    }
    .metric-box {
        background: rgba(255, 255, 255, 0.05); padding: 15px;
        border-radius: 10px; border-left: 5px solid #ffd700;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 2. DEEP DATA ENGINE ---
@st.cache_data(ttl=3600)
def get_comprehensive_data(ticker):
    try:
        stock = yf.Ticker(ticker)
        hist = stock.history(period="2y")
        # Technical Indicators
        if not hist.empty:
            hist.ta.rsi(append=True)
            hist.ta.ema(length=50, append=True)
            hist.ta.ema(length=200, append=True)
        return stock, hist
    except: return None, None

# --- 3. TOP SEARCH BAR ---
st.markdown("<div class='kiyosaki-header'>KUNAL ELITE: FINANCIAL INTELLIGENCE</div>", unsafe_allow_html=True)

col_a, col_b = st.columns([3, 1])
with col_a:
    u_ticker = st.text_input("🔍 SEARCH STOCK (NSE Only):", value="RELIANCE.NS").upper()
with col_b:
    st.write(" ") # Spacing
    analyze_btn = st.button("RUN DEEP ANALYSIS")

# --- 4. DASHBOARD EXECUTION ---
stock_obj, hist_df = get_comprehensive_data(u_ticker)

if stock_obj and not hist_df.empty:
    info = stock_obj.info
    
    # --- ROW 1: KIYOSAKI METRICS ---
    st.subheader("💰 Asset vs Liability (Rich Dad Test)")
    m1, m2, m3, m4 = st.columns(4)
    
    with m1:
        debt = info.get('debtToEquity', 0)
        st.markdown(f"<div class='metric-box'><b>Debt/Equity:</b><br>{debt:.2f}</div>", unsafe_allow_html=True)
        if debt > 100: st.error("High Debt (Liability)")
    with m2:
        div = info.get('dividendYield', 0) * 100
        st.markdown(f"<div class='metric-box'><b>Cash Flow (Div %):</b><br>{div:.2f}%</div>", unsafe_allow_html=True)
    with m3:
        fcf = info.get('freeCashflow', 0)
        st.markdown(f"<div class='metric-box'><b>Free Cash Flow:</b><br>₹{fcf/1e7:,.1f} Cr</div>", unsafe_allow_html=True)
    with m4:
        rsi = hist_df['RSI_14'].iloc[-1]
        st.markdown(f"<div class='metric-box'><b>RSI (Momentum):</b><br>{rsi:.1f}</div>", unsafe_allow_html=True)

    st.divider()

    # --- ROW 2: TABS FOR DEEP ANALYSIS ---
    tab_chart, tab_legal, tab_cash = st.tabs(["📊 INTERACTIVE CHART", "📄 FULL BALANCE SHEET", "💸 CASH FLOW LEDGER"])

    with tab_chart:
        fig = go.Figure()
        fig.add_trace(go.Candlestick(x=hist_df.index, open=hist_df['Open'], high=hist_df['High'], low=hist_df['Low'], close=hist_df['Close'], name='Price'))
        fig.add_trace(go.Scatter(x=hist_df.index, y=hist_df['EMA_50'], line=dict(color='cyan', width=1), name='50 EMA'))
        fig.update_layout(template="plotly_dark", height=500, xaxis_rangeslider_visible=False)
        st.plotly_chart(fig, use_container_width=True)

    with tab_legal:
        st.write("### Official Balance Sheet (Last 4 Years)")
        st.dataframe(stock_obj.balance_sheet, use_container_width=True)

    with tab_cash:
        st.write("### Cash Flow Statement (True Income)")
        st.dataframe(stock_obj.cashflow, use_container_width=True)

else:
    st.warning("Please enter a valid NSE Ticker like TATAMOTORS.NS")

st.markdown("<br><hr><center>© 2026 Kunal Wealth-Tech | Robert Kiyosaki Principles</center>", unsafe_allow_html=True)
