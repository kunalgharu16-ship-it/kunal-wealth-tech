import streamlit as st
import yfinance as yf
import pandas as pd
import requests

# --- 1. NSE OFFICIAL THEME SETUP ---
st.set_page_config(page_title="NSE - Kunal Wealth-Tech", page_icon="🏦", layout="wide")

st.markdown("""
    <style>
    /* NSE Blue Header */
    .header-bar {
        background-color: #003366; color: white; padding: 15px;
        text-align: left; font-size: 24px; font-weight: bold;
        border-bottom: 5px solid #ffcc00; margin-bottom: 20px;
    }
    /* Dashboard Cards */
    .stat-card {
        background-color: #f8f9fa; border: 1px solid #dee2e6;
        padding: 10px; border-radius: 4px; text-align: center;
    }
    .stat-label { color: #666; font-size: 12px; text-transform: uppercase; }
    .stat-value { color: #003366; font-size: 22px; font-weight: bold; }
    
    /* Option Chain Style Table */
    .nse-table {
        width: 100%; border-collapse: collapse; margin-top: 10px;
    }
    .nse-table td {
        padding: 12px; border: 1px solid #eee; font-size: 14px;
    }
    .nse-table tr:nth-child(even) { background-color: #fafafa; }
    .table-header { background-color: #efefef; font-weight: bold; color: #333; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. DATA ENGINE ---
@st.cache_data(ttl=300)
def get_stock_data(ticker_symbol):
    try:
        # Auto-append .NS if not present for Indian stocks
        if "." not in ticker_symbol:
            ticker_symbol += ".NS"
        stock = yf.Ticker(ticker_symbol)
        info = stock.info
        if 'currentPrice' not in info: return None
        return info
    except: return None

def get_suggestions(query):
    if len(query) < 2: return []
    try:
        url = f"https://query2.finance.yahoo.com/v1/finance/search?q={query}"
        headers = {'User-Agent': 'Mozilla/5.0'}
        r = requests.get(url, headers=headers).json()
        return [f"{q['longname']} ({q['symbol']})" for q in r.get('quotes', [])]
    except: return []

# --- 3. TOP NAVIGATION ---
st.markdown("<div class='header-bar'>National Stock Exchange of Kunal</div>", unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.markdown("### 🔍 Search Equity")
    raw_query = st.text_input("Enter Company Name:", value="Tata Motors")
    sugg = get_suggestions(raw_query)
    selected = st.selectbox("Search Results:", sugg) if sugg else None
    
    # Final Symbol selection
    if selected:
        final_ticker = selected.split('(')[-1].replace(')', '')
    else:
        final_ticker = raw_query.upper() # Fallback for manual entry

    st.divider()
    st.info("Tip: Search 'Reliance' or 'Zomato'")

# --- 4. DASHBOARD LAYOUT ---
info = get_stock_data(final_ticker)

if info:
    # --- HEADER INFO ---
    c1, c2, c3 = st.columns([3, 1, 1])
    with c1:
        st.subheader(info.get('longName', final_ticker))
        st.write(f"**Series:** EQ | **Symbol:** {final_ticker} | **Status:** Listed")
    with c2:
        st.markdown(f"<div class='stat-card'><div class='stat-label'>LTP (₹)</div><div class='stat-value'>{info.get('currentPrice'):,.2f}</div></div>", unsafe_allow_html=True)
    with c3:
        change = info.get('currentPrice', 0) - info.get('previousClose', 0)
        color = "green" if change >= 0 else "red"
        st.markdown(f"<div class='stat-card'><div class='stat-label'>Change</div><div style='color:{color}; font-size:22px; font-weight:bold;'>{change:+.2f}</div></div>", unsafe_allow_html=True)

    st.divider()

    # --- KEY STATISTICS (NSE STYLE GRID) ---
    col_left, col_right = st.columns(2)

    with col_left:
        st.markdown("#### 📋 Fundamental Data")
        data1 = {
            "Attribute": ["Market Cap (Cr)", "Enterprise Value", "P/E Ratio", "P/B Ratio", "ROE %", "Dividend Yield"],
            "Value": [
                f"{info.get('marketCap', 0)/1e7:,.2f}",
                f"{info.get('enterpriseValue', 0)/1e7:,.2f}",
                f"{info.get('trailingPE', 'N/A')}",
                f"{info.get('priceToBook', 'N/A')}",
                f"{info.get('returnOnEquity', 0)*100:.2f}%",
                f"{info.get('dividendYield', 0)*100:.2f}%"
            ]
        }
        st.table(pd.DataFrame(data1))

    with col_right:
        st.markdown("#### 📈 Price Information")
        data2 = {
            "Attribute": ["52W High", "52W Low", "Today's High", "Today's Low", "Previous Close", "Volume"],
            "Value": [
                f"₹{info.get('fiftyTwoWeekHigh'):,.2f}",
                f"₹{info.get('fiftyTwoWeekLow'):,.2f}",
                f"₹{info.get('dayHigh'):,.2f}",
                f"₹{info.get('dayLow'):,.2f}",
                f"₹{info.get('previousClose'):,.2f}",
                f"{info.get('volume', 0):,}"
            ]
        }
        st.table(pd.DataFrame(data2))

    # --- CHART ---
    st.markdown("#### 📊 Technical Chart")
    hist = yf.Ticker(final_ticker).history(period="1y")
    st.area_chart(hist['Close'])

    # --- VERDICT ---
    st.divider()
    debt = info.get('debtToEquity', 0)
    if debt < 100:
        st.success(f"💎 **FINANCIAL VERDICT:** ASSET (Strong Balance Sheet with Debt/Equity: {debt:.2f})")
    else:
        st.error(f"⚠️ **FINANCIAL VERDICT:** LIABILITY (Caution! High Debt/Equity: {debt:.2f})")

else:
    st.warning("⚠️ Stock data not found. Try searching with a proper name or symbol (e.g., RELIANCE).")

# Footer
st.markdown("<br><hr><center>© 2026 Kunal Wealth-Tech | NSE Data Dashboard</center>", unsafe_allow_html=True)
