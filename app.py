import streamlit as st
import yfinance as yf
import pandas as pd
import pandas_ta as ta  # Advanced Technical Analysis
import plotly.graph_objects as go # Professional Charts
import streamlit.components.v1 as components

# --- 1. PRO TERMINAL UI ---
st.set_page_config(page_title="Kunal Wealth-Tech | Deep Intelligence", layout="wide")

st.markdown("""
    <style>
    .stApp { background: #000d1a; color: #e6f2ff; }
    .metric-container { background: rgba(255, 255, 255, 0.05); padding: 20px; border-radius: 15px; border-left: 5px solid #00d4ff; }
    .kiyosaki-gold { color: #ffd700; font-weight: bold; font-size: 20px; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. ADVANCED DATA ENGINE ---
@st.cache_data(ttl=3600)
def get_full_analysis(symbol):
    try:
        stock = yf.Ticker(symbol)
        df = stock.history(period="2y")
        
        # Adding Technical Indicators (RSI, EMAs)
        df.ta.rsi(append=True)
        df.ta.ema(length=50, append=True)
        df.ta.ema(length=200, append=True)
        
        return stock.info, df, stock.balance_sheet, stock.cashflow
    except: return None, None, None, None

# --- 3. HOME PAGE CONTROLS ---
st.title("💎 KUNAL ELITE: DEEP ANALYSIS TERMINAL")

c1, c2, c3 = st.columns([2, 1, 1])
with c1:
    ticker_input = st.text_input("🔍 ENTER STOCK SYMBOL (e.g. TATAMOTORS.NS, RELIANCE.NS):", value="TATAMOTORS.NS").upper()
with c2:
    t_unit = st.selectbox("TIMEFRAME:", ["Days", "Weeks", "Months", "Years"], index=2)
with c3:
    t_qty = st.number_input("DURATION:", min_value=1, value=1)

# --- 4. EXECUTION & VISUALIZATION ---
info, hist, bs, cf = get_full_analysis(ticker_input)

if info and not hist.empty:
    # --- TABBED INTERFACE ---
    tab1, tab2, tab3 = st.tabs(["📊 STRATEGIC CHART", "💰 CASH FLOW (RICH DAD)", "📑 LEGAL FINANCIALS"])

    with tab1:
        st.subheader("Technical & Trend Analysis")
        # Professional Plotly Chart with RSI & EMAs
        fig = go.Figure()
        fig.add_trace(go.Candlestick(x=hist.index, open=hist['Open'], high=hist['High'], low=hist['Low'], close=hist['Close'], name='Price'))
        fig.add_trace(go.Scatter(x=hist.index, y=hist['EMA_50'], line=dict(color='yellow', width=1), name='50 EMA (Swing)'))
        fig.add_trace(go.Scatter(x=hist.index, y=hist['EMA_200'], line=dict(color='red', width=2), name='200 EMA (Long Term)'))
        fig.update_layout(template="plotly_dark", height=600, xaxis_rangeslider_visible=False)
        st.plotly_chart(fig, use_container_width=True)
        
        # Technical Verdict
        last_rsi = hist['RSI_14'].iloc[-1]
        st.write(f"**RSI (Momentum):** {last_rsi:.2f}")
        if last_rsi > 70: st.warning("⚠️ OVERBOUGHT: Market is too greedy, wait for dip.")
        elif last_rsi < 30: st.success("✅ OVERSOLD: Potential 'Rich Dad' entry point.")

    with tab2:
        st.subheader("Kiyosaki's Cash Flow Quadrant Analysis")
        
        # Deep Metrics Calculation
        operating_cash = cf.loc['Operating Cash Flow'].iloc[0] if cf is not None else 0
        investing_cash = cf.loc['Investing Cash Flow'].iloc[0] if cf is not None else 0
        
        col_k1, col_k2 = st.columns(2)
        with col_k1:
            st.markdown("<div class='metric-container'>", unsafe_allow_html=True)
            st.write("<span class='kiyosaki-gold'>ASSET TEST:</span>", unsafe_allow_html=True)
            st.write(f"**Operating Cash Flow:** ₹{operating_cash:,.0f}")
            st.info("Kiyosaki Rule: This must be POSITIVE. It means the business actually brings in cash.")
            st.markdown("</div>", unsafe_allow_html=True)

        with col_k2:
            debt_ratio = info.get('debtToEquity', 0)
            st.markdown("<div class='metric-container'>", unsafe_allow_html=True)
            st.write("<span class='kiyosaki-gold'>LIABILITY TEST:</span>", unsafe_allow_html=True)
            st.write(f"**Debt to Equity:** {debt_ratio:.2f}")
            if debt_ratio < 100: st.success("Safe Leverage: Company is not a slave to the banks.")
            else: st.error("High Debt: This could be a Liability in a recession.")
            st.markdown("</div>", unsafe_allow_html=True)

    with tab3:
        st.subheader("Official Company Ledger (Balance Sheet)")
        st.write("Below is the raw data as filed by the company. Analyze the 'Total Assets' vs 'Total Liabilities'.")
        st.dataframe(bs.style.highlight_max(axis=1), use_container_width=True)

else:
    st.error("Invalid Symbol! Please use the full ticker (e.g., RELIANCE.NS, SBIN.NS)")

st.markdown("<br><hr><center>Kunal Wealth-Tech Elite V8.0 | Deep Forensic Analysis</center>", unsafe_allow_html=True)
