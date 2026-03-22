import streamlit as st
import yfinance as yf
import pandas as pd
import pandas_ta as ta  # Advanced Technicals
import plotly.graph_objects as go # Professional Charts
import streamlit.components.v1 as components

# --- 1. ELITE UI SETUP ---
st.set_page_config(page_title="Kunal Wealth-Tech Elite", layout="wide")

st.markdown("""
    <style>
    .stApp { background: #050a14; color: #ffffff; }
    .metric-card { 
        background: rgba(255, 255, 255, 0.05); 
        padding: 20px; border-radius: 15px; 
        border-top: 4px solid #ffd700; 
        text-align: center;
    }
    .status-text { font-size: 18px; font-weight: bold; color: #ffd700; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. THE ANALYTICS ENGINE ---
@st.cache_data(ttl=3600)
def fetch_deep_intel(ticker):
    try:
        stock = yf.Ticker(ticker)
        # 1 Year data for Technicals
        hist = stock.history(period="1y")
        if not hist.empty:
            hist.ta.rsi(append=True)
            hist.ta.ema(length=50, append=True)
            hist.ta.ema(length=200, append=True)
        
        return stock, hist
    except: return None, None

# --- 3. HOME CONTROLS ---
st.title("🏦 KUNAL ELITE: DEEP FORENSIC TERMINAL")
st.write("---")

c1, c2, c3 = st.columns([2, 1, 1])
with c1:
    user_ticker = st.text_input("🔍 ENTER NSE SYMBOL (e.g. RELIANCE.NS):", value="TATAMOTORS.NS").upper()
with c2:
    t_unit = st.selectbox("TIMEFRAME UNIT:", ["Days", "Weeks", "Months", "Years"], index=2)
with c3:
    t_val = st.number_input("DURATION:", min_value=1, value=1)

# --- 4. DATA RENDERING ---
stock_obj, hist_df = fetch_deep_intel(user_ticker)

if stock_obj and not hist_df.empty:
    info = stock_obj.info
    
    # --- KIYOSAKI SUMMARY ---
    st.markdown("### 💰 Robert Kiyosaki's Asset vs Liability Check")
    k1, k2, k3, k4 = st.columns(4)
    
    with k1:
        debt_equity = info.get('debtToEquity', 0)
        st.markdown(f"<div class='metric-card'><p>Debt/Equity</p><p class='status-text'>{debt_equity:.2f}</p></div>", unsafe_allow_html=True)
        if debt_equity > 100: st.error("High Debt (Liability)")
        else: st.success("Healthy Leverage")

    with k2:
        div_yield = info.get('dividendYield', 0) * 100
        st.markdown(f"<div class='metric-card'><p>Cash Flow (Div %)</p><p class='status-text'>{div_yield:.2f}%</p></div>", unsafe_allow_html=True)

    with k3:
        fcf = info.get('freeCashflow', 0)
        st.markdown(f"<div class='metric-card'><p>Free Cash Flow</p><p class='status-text'>₹{fcf/1e7:,.1f} Cr</p></div>", unsafe_allow_html=True)
    
    with k4:
        rsi = hist_df['RSI_14'].iloc[-1]
        st.markdown(f"<div class='metric-card'><p>RSI (Momentum)</p><p class='status-text'>{rsi:.1f}</p></div>", unsafe_allow_html=True)

    # --- TABS FOR DEEP DATA ---
    tab_tech, tab_fin, tab_cash = st.tabs(["📊 TECHNICAL CHART", "📄 BALANCE SHEET", "💸 CASH FLOW STATEMENT"])

    with tab_tech:
        # Professional Interactive Chart
        fig = go.Figure()
        fig.add_trace(go.Candlestick(x=hist_df.index, open=hist_df['Open'], high=hist_df['High'], low=hist_df['Low'], close=hist_df['Close'], name='Market Price'))
        fig.add_trace(go.Scatter(x=hist_df.index, y=hist_df['EMA_50'], line=dict(color='#00d4ff', width=1.5), name='50 EMA (Trend)'))
        fig.update_layout(template="plotly_dark", height=500, xaxis_rangeslider_visible=False)
        st.plotly_chart(fig, use_container_width=True)

    with tab_fin:
        st.subheader("Official Balance Sheet (Legal)")
        st.dataframe(stock_obj.balance_sheet, use_container_width=True)

    with tab_cash:
        st.subheader("Cash Flow (Kiyosaki's Main Focus)")
        st.dataframe(stock_obj.cashflow, use_container_width=True)

else:
    st.error("Ticker not found! Please check if you added '.NS' for Indian stocks.")

st.markdown("<br><hr><center>© 2026 Kunal Wealth-Tech | Powered by Pandas-TA & YFinance</center>", unsafe_allow_html=True)
