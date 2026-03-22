import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go

# --- 1. UI SETUP ---
st.set_page_config(page_title="Kunal Elite Terminal", layout="wide")

st.markdown("""
    <style>
    .stApp { background: #050a14; color: #ffffff; }
    .header-text { color: #ffd700; font-size: 35px; font-weight: bold; text-align: center; margin-bottom: 20px; }
    .kiyosaki-box { background: rgba(255, 215, 0, 0.05); padding: 20px; border-radius: 15px; border: 1px solid #ffd700; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. FIXED ANALYTICS ENGINE ---
def get_rsi(series, period=14):
    delta = series.diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
    rs = gain / loss
    return 100 - (100 / (1 + rs))

@st.cache_data(ttl=3600)
def fetch_deep_financials(ticker):
    """Hum sirf raw data return karenge, object nahi, taaki cache error na aaye"""
    try:
        stock = yf.Ticker(ticker)
        hist = stock.history(period="2y")
        if not hist.empty:
            hist['RSI'] = get_rsi(hist['Close'])
            hist['EMA50'] = hist['Close'].ewm(span=50, adjust=False).mean()
        
        # Sari legal statements fetch karo
        info = stock.info
        bs = stock.balance_sheet
        cf = stock.cashflow
        return info, hist, bs, cf
    except Exception as e:
        return None, None, None, None

# --- 3. UI LAYOUT ---
st.markdown("<div class='header-text'>🏦 KUNAL ELITE: FINANCIAL INTELLIGENCE</div>", unsafe_allow_html=True)

u_ticker = st.text_input("🔍 ENTER NSE SYMBOL (e.g. RELIANCE.NS, ZOMATO.NS):", value="RELIANCE.NS").upper()

# Data fetching
info, hist_df, bs_df, cf_df = fetch_deep_financials(u_ticker)

if info and hist_df is not None:
    # --- ROW 1: RICH DAD METRICS ---
    st.subheader("💰 Robert Kiyosaki's Asset Test")
    c1, c2, c3, c4 = st.columns(4)
    
    with c1:
        debt = info.get('debtToEquity', 0)
        st.metric("Debt/Equity", f"{debt:.2f}")
        if debt > 100: st.error("Liability Alert!")
    with c2:
        div = info.get('dividendYield', 0) * 100
        st.metric("Dividend Yield", f"{div:.2f}%")
    with c3:
        fcf = info.get('freeCashflow', 0)
        st.metric("Free Cash Flow", f"₹{fcf/1e7:,.1f} Cr")
    with c4:
        rsi_val = hist_df['RSI'].iloc[-1]
        st.metric("RSI (Momentum)", f"{rsi_val:.1f}")

    st.divider()

    # --- ROW 2: DEEP DATA TABS ---
    tab_chart, tab_legal, tab_cash = st.tabs(["📊 ANALYSIS CHART", "📋 BALANCE SHEET", "💸 CASH FLOW"])

    with tab_chart:
        fig = go.Figure(data=[go.Candlestick(x=hist_df.index, open=hist_df['Open'], high=hist_df['High'], low=hist_df['Low'], close=hist_df['Close'], name='Price')])
        fig.add_trace(go.Scatter(x=hist_df.index, y=hist_df['EMA50'], line=dict(color='yellow', width=1.5), name='50 EMA'))
        fig.update_layout(template="plotly_dark", height=500, xaxis_rangeslider_visible=False, margin=dict(l=0, r=0, t=0, b=0))
        st.plotly_chart(fig, use_container_width=True)

    with tab_legal:
        st.write("### Raw Balance Sheet (Company Assets & Debt)")
        if bs_df is not None and not bs_df.empty:
            st.dataframe(bs_df, use_container_width=True)
        else:
            st.warning("Balance sheet data not available for this ticker.")

    with tab_cash:
        st.write("### Raw Cash Flow (Actual Money In/Out)")
        if cf_df is not None and not cf_df.empty:
            st.dataframe(cf_df, use_container_width=True)
        else:
            st.warning("Cash flow data not available for this ticker.")

else:
    st.error("⚠️ Ticker Error: Please ensure you are using '.NS' (e.g., TATAMOTORS.NS) and check your internet connection.")

st.markdown("<br><hr><center>© 2026 Kunal Wealth-Tech | Powered by Legal NSE Feed</center>", unsafe_allow_html=True)
