import streamlit as st
import yfinance as yf
import pandas as pd
from thefuzz import process
import requests

# --- 1. SMART MAPPING ---
# Popular Indian stocks ka short-cut database
STOCK_MAP = {
    "RELIANCE": "RELIANCE.NS",
    "TATA MOTORS": "TATAMOTORS.NS",
    "ZOMATO": "ZOMATO.NS",
    "SBIN": "SBIN.NS",
    "TATA STEEL": "TATASTEEL.NS",
    "ADANI": "ADANIENT.NS",
    "INFOSYS": "INFY.NS",
    "PAYTM": "PAYTM.NS"
}

def get_clean_ticker(user_input):
    user_input = user_input.upper().strip()
    
    # 1. Direct Check in Map
    if user_input in STOCK_MAP:
        return STOCK_MAP[user_input]
    
    # 2. Fuzzy Matching (Spelling mistake handling)
    match, score = process.extractOne(user_input, list(STOCK_MAP.keys()))
    if score > 85:
        return STOCK_MAP[match]
    
    # 3. Default: Bas .NS laga do agar nahi hai
    if not user_input.endswith(".NS"):
        return f"{user_input}.NS"
    return user_input

# --- 2. UI SETUP ---
st.set_page_config(page_title="Kunal Smart Terminal", layout="wide")

st.markdown("""
    <style>
    .stApp { background: #050a14; color: #ffffff; }
    .search-box { background: #1a222d; padding: 20px; border-radius: 15px; border: 1px solid #ffd700; }
    </style>
    """, unsafe_allow_html=True)

st.title("🏦 KUNAL ELITE: NO-FRICTION SEARCH")

# --- 3. SEARCH INPUT ---
user_query = st.text_input("🔍 Company ka naam likho (e.g. 'tata' or 'zomto'):", value="Reliance")

if user_query:
    ticker = get_clean_ticker(user_query)
    st.info(f"Searching for: **{ticker}**")

    # Fetch Data
    try:
        stock = yf.Ticker(ticker)
        # Displaying Basic Metrics to confirm it works
        info = stock.info
        if 'currentPrice' in info:
            st.success(f"Found: {info.get('longName')} | Price: ₹{info.get('currentPrice')}")
            
            tab1, tab2 = st.tabs(["Fundamentals", "Cash Flow"])
            with tab1:
                st.dataframe(stock.balance_sheet, use_container_width=True)
            with tab2:
                st.dataframe(stock.cashflow, use_container_width=True)
        else:
            st.error("Bhai, symbol sahi nahi lag raha. Check karo!")
    except:
        st.error("Technical Error! Refresh karke dekho.")

st.markdown("<hr><center>Kunal Wealth-Tech © 2026</center>", unsafe_allow_html=True)
