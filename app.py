import streamlit as st
import yfinance as yf
import pandas as pd
import requests

# --- 1. NSE STYLE CONFIG ---
st.set_page_config(page_title="Kunal Wealth-Tech | NSE Mode", page_icon="🏦", layout="wide")

# NSE Blue & Grey Theme CSS
st.markdown("""
    <style>
    .stApp { background-color: #f0f2f5; }
    .nse-header {
        background-color: #003366; padding: 10px; border-radius: 5px;
        color: white; text-align: center; font-weight: bold; margin-bottom: 20px;
    }
    .data-table {
        background-color: white; border-collapse: collapse; width: 100%;
        border-radius: 10px; overflow: hidden; box-shadow: 0 2px 5px rgba(0,0,0,0.1);
    }
    .metric-box {
        border: 1px solid #dee2e6; padding: 15px; border-radius: 5px;
        background-color: #ffffff; text-align: center;
    }
    .label { color: #666; font-size: 14px; font-weight: bold; }
    .value { color: #003366; font-size: 20px; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. LOGIC FUNCTIONS ---
@st.cache_data(ttl=600) # 10 mins cache for live feel
def get_nse_data(symbol):
    try:
        ticker = yf.Ticker(symbol)
        info = ticker.info
        hist = ticker.history(period="1mo")
        return info, hist
    except: return None, None

def get_suggestions(query):
    if len(query) < 2: return []
    try:
        url = f"https://query2.finance.yahoo.com/v1/finance/search?q={query}"
        headers = {'User-Agent': 'Mozilla/5.0'}
        response = requests.get(url, headers=headers).json()
        return [f"{q['longname']} ({q['symbol']})" for q in response.get('quotes', []) if '.NS' in q.get('symbol', '')]
    except: return []

# --- 3. TOP NAVIGATION (NSE LOOK) ---
st.markdown("<div class='nse-header'>KUNAL WEALTH-TECH | EQUITY DERIVATIVES & FUNDAMENTALS</div>", unsafe_allow_html=True)

# Sidebar Search
with st.sidebar:
    st.markdown("### 🔍 MARKET TRACKER")
    search_input = st.text_input("Search Stock Name:", value="Tata Motors")
    options = get_suggestions(search_input)
    selected = st.selectbox("Select from NSE List:", options) if options else None
    go = st.button("VIEW DETAILED REPORT", use_container_width=True)

# --- 4. MAIN LAYOUT ---
if selected:
    ticker_sym = selected.split('(')[-1].replace(')', '')
    info, hist = get_nse_data(ticker_sym)

    if info and 'currentPrice' in info:
        # Title Row
        c1, c2 = st.columns([3, 1])
        with c1:
            st.subheader(f"{info.get('longName')} ({ticker_sym})")
            st.caption(f"Sector: {info.get('sector')} | ISIN: {info.get('isin', 'INE000000000')}")
        with c2:
            st.markdown(f"<div class='metric-box'><span class='label'>Last Traded Price</span><br><span class='value'>₹{info.get('currentPrice'):,.2f}</span></div>", unsafe_allow_html=True)

        st.divider()

        # --- OPTION CHAIN STYLE LAYOUT (Side-by-Side Metrics) ---
        st.markdown("### 📊 KEY MARKET STATISTICS")
        
        col_a, col_b = st.columns(2)
        
        # Left Side (Fundamentals / 'Calls' Feel)
        with col_a:
            data_left = {
                "Metric": ["Market Cap (Cr)", "P/E Ratio", "Dividend Yield", "ROE %"],
                "Value": [
                    f"{info.get('marketCap', 0)/1e7:,.2f}",
                    f"{info.get('trailingPE', 0):.2f}",
                    f"{info.get('dividendYield', 0)*100:.2f}%",
                    f"{info.get('returnOnEquity', 0)*100:.2f}%"
                ]
            }
            st.table(pd.DataFrame(data_left))

        # Right Side (Price Range / 'Puts' Feel)
        with col_b:
            data_right = {
                "Price Statistics": ["52 Week High", "52 Week Low", "Day High", "Day Low"],
                "Value": [
                    f"₹{info.get('fiftyTwoWeekHigh', 0):,.2f}",
                    f"₹{info.get('fiftyTwoWeekLow', 0):,.2f}",
                    f"₹{info.get('dayHigh', 0):,.2f}",
                    f"₹{info.get('dayLow', 0):,.2f}"
                ]
            }
            st.table(pd.DataFrame(data_right))

        # --- CHART SECTION ---
        st.markdown("### 📈 INTRADAY / HISTORICAL CHART")
        st.area_chart(hist['Close'])

        # --- VERDICT ---
        st.divider()
        debt = info.get('debtToEquity', 0)
        if debt < 100:
            st.success(f"✅ NSE ANALYSIS: Strong Fundamentals. Debt/Equity ({debt:.2f}) is stable.")
        else:
            st.warning(f"⚠️ NSE ANALYSIS: High Leverage Detected. Debt/Equity ({debt:.2f}) is above average.")

    else:
        st.error("Server busy! Please refresh after 10 seconds.")

# Footer
st.markdown("<br><hr><center>Market data as per NSE India Guidelines | Powered by Kunal Wealth-Tech</center>", unsafe_allow_html=True)
