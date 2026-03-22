import streamlit as st
import yfinance as yf
import pandas as pd
import requests

# --- 1. NSE OFFICIAL THEME ---
st.set_page_config(page_title="NSE - Kunal Wealth-Tech", page_icon="🏦", layout="wide")

st.markdown("""
    <style>
    .header-bar {
        background-color: #003366; color: white; padding: 15px;
        text-align: left; font-size: 24px; font-weight: bold;
        border-bottom: 5px solid #ffcc00; margin-bottom: 20px;
    }
    .stat-card {
        background-color: #ffffff; border: 1px solid #dee2e6;
        padding: 15px; border-radius: 8px; text-align: center;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    }
    .stat-label { color: #666; font-size: 13px; font-weight: bold; }
    .stat-value { color: #003366; font-size: 24px; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. LIVE SEARCH ENGINE (No Manual List) ---
def get_live_suggestions(query):
    """Jaise hi aap type karoge, ye Yahoo se live options layega"""
    if len(query) < 2:
        return []
    try:
        # Yahoo Finance Search API
        url = f"https://query2.finance.yahoo.com/v1/finance/search?q={query}&quotesCount=10"
        headers = {'User-Agent': 'Mozilla/5.0'}
        response = requests.get(url, headers=headers).json()
        
        # Sirf NSE (.NS) wale stocks filter karna
        suggestions = {}
        for q in response.get('quotes', []):
            symbol = q.get('symbol', '')
            if '.NS' in symbol or q.get('exchDisp') == 'NSE':
                name = q.get('longname', q.get('shortname', symbol))
                suggestions[f"{name} ({symbol})"] = symbol
        return suggestions
    except:
        return {}

# --- 3. UI LAYOUT & SEARCH ---
st.markdown("<div class='header-bar'>National Stock Exchange of Kunal</div>", unsafe_allow_html=True)

with st.sidebar:
    st.markdown("### 🔍 LIVE NSE SEARCH")
    # Step A: User types alphabet
    user_input = st.text_input("Type Stock Name (e.g., 'V', 'Tata', 'Zom'):", value="Tata Motors")
    
    # Step B: Get live suggestions based on input
    suggestions_dict = get_live_suggestions(user_input)
    
    if suggestions_dict:
        selected_display = st.selectbox("Select from Results:", options=list(suggestions_dict.keys()))
        final_ticker = suggestions_dict[selected_display]
    else:
        # Fallback if no suggestions found
        final_ticker = user_input.upper().strip()
        if ".NS" not in final_ticker and len(final_ticker) > 1:
            final_ticker += ".NS"

    st.divider()
    st.caption("Market Data: Real-time NSE India")

# --- 4. DATA DISPLAY ENGINE ---
@st.cache_data(ttl=300)
def fetch_data(ticker):
    try:
        stock = yf.Ticker(ticker)
        return stock.info, stock.history(period="1y")['Close']
    except:
        return None, None

if final_ticker:
    info, hist = fetch_data(final_ticker)
    
    if info and 'currentPrice' in info:
        # Layout like NSE Terminal
        c1, c2, c3, c4 = st.columns([2, 1, 1, 1])
        with c1:
            st.subheader(info.get('longName', final_ticker))
            st.write(f"**Symbol:** {final_ticker} | **Industry:** {info.get('industry', 'N/A')}")
        with c2:
            st.markdown(f"<div class='stat-card'><div class='stat-label'>LTP (₹)</div><div class='stat-value'>{info.get('currentPrice'):,.2f}</div></div>", unsafe_allow_html=True)
        with c3:
            roe = info.get('returnOnEquity', 0) * 100
            st.markdown(f"<div class='stat-card'><div class='stat-label'>ROE %</div><div class='stat-value'>{roe:.2f}%</div></div>", unsafe_allow_html=True)
        with c4:
            debt = info.get('debtToEquity', 0)
            st.markdown(f"<div class='stat-card'><div class='stat-label'>DEBT/EQUITY</div><div class='stat-value'>{debt:.2f}</div></div>", unsafe_allow_html=True)

        st.divider()

        # Tables for Professional Look
        col_l, col_r = st.columns(2)
        with col_l:
            st.markdown("#### 📋 Key Fundamental Data")
            st.table(pd.DataFrame({
                "Attribute": ["Market Cap (Cr)", "Trailing P/E", "Dividend Yield", "Book Value", "Face Value"],
                "Value": [
                    f"{info.get('marketCap', 0)/1e7:,.2f}",
                    f"{info.get('trailingPE', 'N/A')}",
                    f"{info.get('dividendYield', 0)*100:.2f}%",
                    f"₹{info.get('bookValue', 'N/A')}",
                    f"₹{info.get('priceToBook', 'N/A')}"
                ]
            }))
        
        with col_r:
            st.markdown("#### 📈 52-Week Statistics")
            st.table(pd.DataFrame({
                "Attribute": ["52 Week High", "52 Week Low", "Day High", "Day Low", "Volume"],
                "Value": [
                    f"₹{info.get('fiftyTwoWeekHigh'):,.2f}",
                    f"₹{info.get('fiftyTwoWeekLow'):,.2f}",
                    f"₹{info.get('dayHigh'):,.2f}",
                    f"₹{info.get('dayLow'):,.2f}",
                    f"{info.get('volume', 0):,}"
                ]
            }))

        st.markdown("#### 📊 Stock Performance (1 Year)")
        st.area_chart(hist)

    else:
        st.warning("Stock data dhundne mein dikkat ho rahi hai. Kripya pura ticker likhein (e.g. RELIANCE.NS)")

st.markdown("<br><hr><center>© 2026 Kunal Wealth-Tech | Powered by NSE Real-time API</center>", unsafe_allow_html=True)
