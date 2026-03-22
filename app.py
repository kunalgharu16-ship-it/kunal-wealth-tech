import streamlit as st
import yfinance as yf
import pandas as pd
import requests

# --- 1. PAGE SETUP ---
st.set_page_config(page_title="Kunal Wealth-Tech | Analysis", page_icon="🦁", layout="wide")

# Custom CSS for Professional Look
st.markdown("""
    <style>
    .stApp { background-color: #f8f9fa; }
    .metric-card {
        background-color: white; padding: 15px; border-radius: 12px;
        box-shadow: 0 4px 10px rgba(0,0,0,0.05); border-top: 4px solid #1E88E5;
        text-align: center; margin-bottom: 10px;
    }
    .stTabs [data-baseweb="tab-list"] { gap: 10px; }
    .stTabs [data-baseweb="tab"] {
        background-color: #f0f2f6; border-radius: 5px; padding: 5px 20px;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 2. SEARCH LOGIC ---
def get_suggestions(query):
    if len(query) < 2: return []
    try:
        url = f"https://query2.finance.yahoo.com/v1/finance/search?q={query}"
        headers = {'User-Agent': 'Mozilla/5.0'}
        response = requests.get(url, headers=headers).json()
        return [f"{q['longname']} ({q['symbol']})" for q in response.get('quotes', []) if '.NS' in q.get('symbol', '')]
    except: return []

# --- 3. SIDEBAR ---
with st.sidebar:
    st.markdown("<h1 style='text-align: center;'>🦁 KUNAL</h1>", unsafe_allow_html=True)
    st.divider()
    search_input = st.text_input("Stock Search (e.g. Tata, Reliance):", value="Tata Motors")
    options = get_suggestions(search_input)
    selected_stock = st.selectbox("Select Stock:", options) if options else None
    analyze_btn = st.button("🚀 Analyze Now", use_container_width=True)

# --- 4. MAIN DASHBOARD ---
if selected_stock:
    ticker = selected_stock.split('(')[-1].replace(')', '')
    stock = yf.Ticker(ticker)
    info = stock.info

    if 'currentPrice' in info:
        st.title(f"📈 {info.get('longName', ticker)}")
        
        # KEY METRICS ROW
        m1, m2, m3, m4 = st.columns(4)
        with m1: st.markdown(f"<div class='metric-card'>Price<br><h3>₹{info.get('currentPrice', 0):,.2f}</h3></div>", unsafe_allow_html=True)
        with m2: st.markdown(f"<div class='metric-card'>Market Cap<br><h3>{info.get('marketCap', 0)/1e7:,.0f} Cr</h3></div>", unsafe_allow_html=True)
        with m3: st.markdown(f"<div class='metric-card'>ROE<br><h3>{info.get('returnOnEquity', 0)*100:.1f}%</h3></div>", unsafe_allow_html=True)
        with m4: st.markdown(f"<div class='metric-card'>PE Ratio<br><h3>{info.get('trailingPE', 0):.2f}</h3></div>", unsafe_allow_html=True)

        st.divider()

        # --- NEW: TIME FRAME TABS ---
        st.subheader("Performance Analysis")
        # Creating Tabs for different time periods
        tab1, tab2, tab3, tab4 = st.tabs(["1 Day", "1 Month", "1 Year", "All Time (Max)"])

        with tab1:
            st.write("**Intraday Movement (Today)**")
            d1_hist = stock.history(period="1d", interval="1m") # 1 minute interval for 1 day
            if not d1_hist.empty:
                st.line_chart(d1_hist['Close'])
            else: st.info("Market abhi band hai ya data unavailable hai.")

        with tab2:
            st.write("**Monthly Growth**")
            m1_hist = stock.history(period="1mo")
            st.area_chart(m1_hist['Close'])

        with tab3:
            st.write("**Yearly Performance**")
            y1_hist = stock.history(period="1y")
            st.area_chart(y1_hist['Close'])

        with tab4:
            st.write("**Long Term History**")
            max_hist = stock.history(period="max")
            st.area_chart(max_hist['Close'])

        st.divider()
        
        # FUNDAMENTAL VERDICT
        left, right = st.columns(2)
        with left:
            st.subheader("👨‍🏫 Kunal's Verdict")
            debt = info.get('debtToEquity', 0)
            if debt < 100:
                st.success("💎 **ASSET:** Debt control mein hai, long term ke liye acha ho sakta hai.")
            else:
                st.error("⚠️ **LIABILITY:** Karz (Debt) zyada hai, sambhal kar invest karein.")
        
        with right:
            st.subheader("About Company")
            st.write(info.get('longBusinessSummary', 'Summary not available.')[:400] + "...")

# Footer
st.markdown("<br><hr><center>Developed by Kunal Wealth-Tech © 2026</center>", unsafe_allow_html=True)
