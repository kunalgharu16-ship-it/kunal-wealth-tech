import streamlit as st
import yfinance as yf
import pandas as pd
import requests

# --- 1. PAGE SETUP ---
st.set_page_config(page_title="Kunal Wealth-Tech | Pro", page_icon="🦁", layout="wide")

# --- 2. SMART CACHING (The Fix) ---
# Ye function data ko 1 ghante tak save rakhega taaki Rate Limit na aaye
@st.cache_data(ttl=3600) 
def fetch_stock_data(symbol):
    try:
        stock = yf.Ticker(symbol)
        # HACK: Info fetch karne se pehle history call karne se block kam hote hain
        _ = stock.history(period="1d") 
        return stock.info, stock
    except:
        return None, None

def get_suggestions(query):
    if len(query) < 2: return []
    try:
        url = f"https://query2.finance.yahoo.com/v1/finance/search?q={query}"
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
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
    ticker = selected_stock.split('(')[-1].replace(')', '')
    
    # Using the Cached function
    info, stock_obj = fetch_stock_data(ticker)

    if info and 'currentPrice' in info:
        st.title(f"📈 {info.get('longName', ticker)}")
        
        # KEY METRICS ROW
        m1, m2, m3, m4 = st.columns(4)
        with m1: st.metric("Live Price", f"₹{info.get('currentPrice', 0):,.2f}")
        with m2: st.metric("Market Cap", f"{info.get('marketCap', 0)/1e7:,.0f} Cr")
        with m3: st.metric("ROE", f"{info.get('returnOnEquity', 0)*100:.1f}%")
        with m4: st.metric("PE Ratio", f"{info.get('trailingPE', 0):.2f}")

        st.divider()

        # TIME FRAME TABS
        tab1, tab2, tab3 = st.tabs(["1 Month", "1 Year", "Max History"])
        
        with tab1:
            st.area_chart(stock_obj.history(period="1mo")['Close'])
        with tab2:
            st.area_chart(stock_obj.history(period="1y")['Close'])
        with tab3:
            st.area_chart(stock_obj.history(period="max")['Close'])

        st.divider()
        
        # FUNDAMENTAL VERDICT
        debt = info.get('debtToEquity', 0)
        if debt < 100:
            st.success(f"💎 **ASSET:** Debt/Equity is {debt:.2f} (Low)")
        else:
            st.warning(f"⚠️ **LIABILITY:** Debt/Equity is {debt:.2f} (High)")

    else:
        st.error("Yahoo Finance is temporarily busy. Please wait 2 minutes and try again.")

st.markdown("<br><hr><center>Developed by Kunal Wealth-Tech © 2026</center>", unsafe_allow_html=True)
