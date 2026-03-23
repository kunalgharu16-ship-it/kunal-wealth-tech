import streamlit as st
import yfinance as yf
import pandas as pd
from thefuzz import process # Spelling correction ke liye
import requests

# --- 1. SMART SEARCH DATABASE ---
# Ye list NSE ke popular stocks ki hai, ise hum dynamic bhi bana sakte hain
COMMON_STOCKS = {
    "Reliance Industries": "RELIANCE.NS",
    "Tata Motors": "TATAMOTORS.NS",
    "Zomato": "ZOMATO.NS",
    "State Bank of India": "SBIN.NS",
    "TCS": "TCS.NS",
    "Infosys": "INFY.NS",
    "ITC": "ITC.NS",
    "HDFC Bank": "HDFCBANK.NS",
    "Adani Enterprises": "ADANIENT.NS",
    "Paytm": "PAYTM.NS"
}

def smart_search(user_query):
    # 1. Direct Search in our dictionary
    match, score = process.extractOne(user_query, COMMON_STOCKS.keys())
    
    # 2. Agar match 80% se zyada sahi hai, toh wahi uthalo
    if score > 80:
        return COMMON_STOCKS[match]
    
    # 3. Agar dictionary mein nahi hai, toh Yahoo Finance API se pucho
    try:
        url = f"https://query2.finance.yahoo.com/v1/finance/search?q={user_query}"
        res = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'}).json()
        for q in res.get('quotes', []):
            if '.NS' in q['symbol']: # Sirf Indian Stocks
                return q['symbol']
    except:
        pass
    
    # 4. Last resort: Bas .NS laga do
    clean_query = user_query.upper().replace(" ", "")
    if not clean_query.endswith(".NS"):
        clean_query += ".NS"
    return clean_query

# --- 2. UI SETUP ---
st.set_page_config(page_title="Kunal Smart Terminal", layout="wide")

st.markdown("""
    <style>
    .stApp { background: #050a14; color: #ffffff; }
    .search-status { color: #ffd700; font-size: 14px; margin-bottom: 10px; }
    </style>
    """, unsafe_allow_html=True)

st.title("🏦 KUNAL ELITE: SMART SEARCH TERMINAL")

# --- 3. THE SEARCH BOX ---
raw_input = st.text_input("🔍 Type Company Name (e.g., 'tata motr' or 'reliance'):", value="Reliance")

if raw_input:
    # Auto-correction logic
    final_ticker = smart_search(raw_input)
    st.markdown(f"<div class='search-status'>Analyzing: <b>{final_ticker}</b> (Auto-corrected)</div>", unsafe_allow_html=True)

    # --- 4. FETCH & DISPLAY ---
    try:
        stock = yf.Ticker(final_ticker)
        info = stock.info
        
        if 'currentPrice' in info:
            c1, c2, c3 = st.columns(3)
            c1.metric("Current Price", f"₹{info.get('currentPrice')}")
            c2.metric("Company", info.get('longName'))
            c3.metric("Kiyosaki Asset Score", "Positive" if info.get('freeCashflow', 0) > 0 else "Negative")
            
            # Show the official data
            st.subheader("Deep Fundamentals")
            st.dataframe(stock.balance_sheet, use_container_width=True)
        else:
            st.error("Bhai, ye stock nahi mil raha. Thoda sahi naam likho!")
    except:
        st.error("Server Busy! Please try again in a second.")
