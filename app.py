import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go

# --- 1. UI SETUP ---
st.set_page_config(page_title="Kunal Elite Terminal", layout="wide")

st.markdown("""
    <style>
    .stApp { background: #050a14; color: #ffffff; }
    .kiyosaki-card { background: rgba(255, 215, 0, 0.05); border: 1px solid #ffd700; padding: 15px; border-radius: 10px; }
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

# --- 3. UI ---
st.title("🏦 KUNAL ELITE: FINANCIAL TERMINAL")

u_ticker = st.text_input("🔍 ENTER NSE SYMBOL (e.g. RELIANCE.NS):", value="RELIANCE.NS").upper()
stock_obj, hist_df = fetch_data_safe(u_ticker)

if stock_obj and not hist_df.empty:
    info = stock_obj.info
    
    # Kiyosaki Quick Check
    st.subheader("💰 Rich Dad Fundamentals")
    c1, c2, c3 = st.columns(3)
    c1.metric("Debt/Equity", f"{info.get('debtToEquity', 0):.2f}")
    c2.metric("Dividend Yield", f"{info.get('dividendYield', 0)*100:.2f}%")
    c3.metric("RSI (Momentum)", f"{hist_df['RSI'].iloc[-1]:.1f}")

    tab_chart, tab_bs, tab_cf = st.tabs(["📊 CHART", "📄 BALANCE SHEET", "💸 CASH FLOW"])
    
    with tab_chart:
        fig = go.Figure(data=[go.Candlestick(x=hist_df.index, open=hist_df['Open'], high=hist_df['High'], low=hist_df['Low'], close=hist_df['Close'])])
        fig.update_layout(template="plotly_dark", height=500, xaxis_rangeslider_visible=False)
        st.plotly_chart(fig, use_container_width=True)
    
    with tab_bs:
        st.write("### Full Balance Sheet (Legal)")
        st.dataframe(stock_obj.balance_sheet)
        
    with tab_cf:
        st.write("### Cash Flow (Kiyosaki Focus)")
        st.dataframe(stock_obj.cashflow)
else:
    st.error("Error fetching data. Ensure ticker ends with .NS")
