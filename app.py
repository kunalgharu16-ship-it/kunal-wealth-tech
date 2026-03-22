import streamlit as st
import yfinance as yf
import pandas as pd
import requests

# --- 1. PAGE SETUP ---
st.set_page_config(page_title="Kunal Wealth-Tech | Pro", page_icon="🦁", layout="wide")

# Custom CSS
st.markdown("""
    <style>
    .stApp { background-color: #f8f9fa; }
    .metric-card {
        background-color: white; padding: 20px; border-radius: 12px;
        box-shadow: 0 4px 10px rgba(0,0,0,0.05); border-top: 5px solid #1E88E5;
        text-align: center;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 2. FIXED CACHING LOGIC ---
@st.cache_data(ttl=3600) # 1 hour cache
def get_clean_data(symbol):
    try:
        ticker = yf.Ticker(symbol)
        # Sirf zaroori data fetch karo (Serializable data)
        info = ticker.info
        hist_1mo = ticker.history(period="1mo")['Close']
        hist_1y = ticker.history(period="1y")['Close']
        hist_max = ticker.history(period="max")['Close']
        
        return info, hist_1mo, hist_1y, hist_max
    except:
        return None, None, None, None

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
    search_input = st.text_input("Stock Search:", value="Tata Motors")
    options = get_suggestions(search_input)
    selected_stock = st.selectbox("Select Stock:", options) if options else None
    analyze_btn = st.button("🚀 Analyze Now", use_container_width=True)

# --- 4. MAIN DASHBOARD ---
if selected_stock:
    ticker_symbol = selected_stock.split('(')[-1].replace(')', '')
    
    # Fetching only clean data
    info, h1m, h1y, hmax = get_clean_data(ticker_symbol)

    if info and 'currentPrice' in info:
        st.title(f"📈 {info.get('longName', ticker_symbol)}")
        
        # Row 1: Key Metrics
        m1, m2, m3, m4 = st.columns(4)
        with m1: st.metric("Live Price", f"₹{info.get('currentPrice', 0):,.2f}")
        with m2: st.metric("Market Cap", f"{info.get('marketCap', 0)/1e7:,.0f} Cr")
        with m3: st.metric("ROE", f"{info.get('returnOnEquity', 0)*100:.1f}%")
        with m4: st.metric("PE Ratio", f"{info.get('trailingPE', 0):.2f}")

        st.divider()

        # Row 2: Performance Tabs
        tab1, tab2, tab3 = st.tabs(["1 Month", "1 Year", "Max History"])
        with tab1: st.area_chart(h1m)
        with tab2: st.area_chart(h1y)
        with tab3: st.area_chart(hmax)

        st.divider()
        
        # Row 3: Verdict & About
        l, r = st.columns(2)
        with l:
            st.subheader("👨‍🏫 Kunal's Verdict")
            debt = info.get('debtToEquity', 0)
            if debt < 100: st.success(f"💎 **ASSET:** Low Debt ({debt:.2f})")
            else: st.warning(f"⚠️ **LIABILITY:** High Debt ({debt:.2f})")
        with r:
            st.subheader("About")
            st.write(info.get('longBusinessSummary', 'No summary available.')[:350] + "...")

    else:
        st.error("Data fetch nahi ho raha. 2-3 minute baad try karein ya 'Manage App' mein jaake 'Reboot' karein.")

st.markdown("<br><hr><center>Developed by Kunal Wealth-Tech © 2026</center>", unsafe_allow_html=True)
