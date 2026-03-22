import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go

# --- 1. UI SETUP ---
st.set_page_config(page_title="Kunal Elite Terminal", layout="wide")

st.markdown("""
    <style>
    .stApp { background: #050a14; color: #ffffff; }
    .header-text { color: #ffd700; font-size: 35px; font-weight: bold; text-align: center; }
    .data-card { background: rgba(255, 255, 255, 0.05); padding: 15px; border-radius: 10px; border-left: 5px solid #ffd700; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. MANUAL ANALYTICS (No extra library needed) ---
def get_rsi(series, period=14):
    delta = series.diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
    rs = gain / loss
    return 100 - (100 / (1 + rs))

@st.cache_data(ttl=3600)
def fetch_data_safe(ticker):
    try:
        stock = yf.Ticker(ticker)
        hist = stock.history(period="1y")
        if not hist.empty:
            hist['RSI'] = get_rsi(hist['Close'])
            hist['EMA50'] = hist['Close'].ewm(span=50, adjust=False).mean()
            return stock, hist
    except: return None, None

# --- 3. UI LAYOUT ---
st.markdown("<div class='header-text'>🏦 KUNAL ELITE: FINANCIAL TERMINAL</div>", unsafe_allow_html=True)

u_ticker = st.text_input("🔍 ENTER NSE SYMBOL (e.g. RELIANCE.NS, ZOMATO.NS):", value="RELIANCE.NS").upper()
stock_obj, hist_df = fetch_data_safe(u_ticker)

if stock_obj and not hist_df.empty:
    info = stock_obj.info
    
    # Kiyosaki Quick Highlights
    st.subheader("💰 Asset vs Liability Check")
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Debt/Equity", f"{info.get('debtToEquity', 0):.2f}")
    c2.metric("Dividend Yield", f"{info.get('dividendYield', 0)*100:.2f}%")
    c3.metric("Free Cash Flow", f"₹{info.get('freeCashflow', 0)/1e7:,.1f} Cr")
    c4.metric("RSI (Momentum)", f"{hist_df['RSI'].iloc[-1]:.1f}")

    # Tabs for Organization
    tab_chart, tab_bs, tab_cf = st.tabs(["📊 INTERACTIVE CHART", "📄 BALANCE SHEET", "💸 CASH FLOW"])
    
    with tab_chart:
        fig = go.Figure(data=[go.Candlestick(x=hist_df.index, open=hist_df['Open'], high=hist_df['High'], low=hist_df['Low'], close=hist_df['Close'])])
        fig.add_trace(go.Scatter(x=hist_df.index, y=hist_df['EMA50'], line=dict(color='yellow', width=1), name='50 EMA'))
        fig.update_layout(template="plotly_dark", height=500, xaxis_rangeslider_visible=False)
        st.plotly_chart(fig, use_container_width=True)
    
    with tab_bs:
        st.write("### Official Balance Sheet (Deep Data)")
        st.dataframe(stock_obj.balance_sheet, use_container_width=True)
        
    with tab_cf:
        st.write("### Cash Flow Statement (Rich Dad Analysis)")
        st.dataframe(stock_obj.cashflow, use_container_width=True)
else:
    st.error("Error: Stock not found. Make sure to use '.NS' for Indian stocks.")

st.markdown("<br><hr><center>© 2026 Kunal Wealth-Tech | Robert Kiyosaki Principles</center>", unsafe_allow_html=True)
