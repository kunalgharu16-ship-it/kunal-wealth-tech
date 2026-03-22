import streamlit as st
import yfinance as yf
import pandas as pd
import requests

# --- 1. PAGE SETUP & STYLE ---
st.set_page_config(page_title="Kunal Wealth-Tech | NSE Full Access", page_icon="🦁", layout="wide")

st.markdown("""
    <style>
    .stApp { background-color: #f8f9fa; }
    .metric-card {
        background-color: white; padding: 20px; border-radius: 12px;
        box-shadow: 0 4px 10px rgba(0,0,0,0.05); border-top: 5px solid #1E88E5;
        text-align: center;
    }
    .stTextInput>div>div>input { border-radius: 10px; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. NSE SEARCH ENGINE LOGIC ---
def get_stock_suggestions(search_query):
    """Yahoo Finance se search suggestions nikalna"""
    if len(search_query) < 2: return []
    try:
        url = f"https://query2.finance.yahoo.com/v1/finance/search?q={search_query}&quotesCount=10"
        headers = {'User-Agent': 'Mozilla/5.0'}
        response = requests.get(url, headers=headers).json()
        # Sirf NSE wale (.NS) stocks filter karna
        suggestions = [
            f"{q['longname']} ({q['symbol']})" 
            for q in response.get('quotes', []) 
            if '.NS' in q.get('symbol', '') or q.get('exchange') == 'NSI'
        ]
        return suggestions
    except:
        return []

# --- 3. SIDEBAR: THE DYNAMIC SEARCH ---
with st.sidebar:
    st.markdown("<h1 style='text-align: center;'>🦁 KUNAL</h1>", unsafe_allow_html=True)
    st.divider()
    
    st.write("🔍 **NSE Market Search**")
    user_input = st.text_input("Stock ka naam likhein (e.g. Tata, SBI, Adani):", placeholder="Type here...")
    
    options = get_stock_suggestions(user_input)
    
    selected_stock = None
    if options:
        selected_stock = st.selectbox("Inmein se chunein:", options)
    elif len(user_input) >= 2:
        st.caption("Searching in NSE database...")

    analyze_btn = st.button("🚀 Analyze Now", use_container_width=True)

# --- 4. DATA FETCHING & DISPLAY ---
if analyze_btn and selected_stock:
    # Symbol nikalna (Brackets ke andar wala part)
    ticker_symbol = selected_stock.split('(')[-1].replace(')', '')
    
    try:
        with st.spinner(f'Fetching {ticker_symbol} Data...'):
            stock = yf.Ticker(ticker_symbol)
            info = stock.info
            
            if not info or 'currentPrice' not in info:
                st.error("Data fetch nahi ho pa raha. Kripya dusra stock chunein.")
            else:
                # --- DISPLAY ---
                st.title(f"{info.get('longName', ticker_symbol)}")
                st.write(f"**Exchange:** NSE | **Industry:** {info.get('industry', 'N/A')}")

                # Metrics
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    st.markdown(f"<div class='metric-card'>Price<br><h3>₹{info.get('currentPrice', 0):,.2f}</h3></div>", unsafe_allow_html=True)
                with col2:
                    st.markdown(f"<div class='metric-card'>Market Cap<br><h3>{info.get('marketCap', 0)/1e7:,.0f} Cr</h3></div>", unsafe_allow_html=True)
                with col3:
                    st.markdown(f"<div class='metric-card'>P/E Ratio<br><h3>{info.get('trailingPE', 0):.2f}</h3></div>", unsafe_allow_html=True)
                with col4:
                    st.markdown(f"<div class='metric-card'>ROE<br><h3>{info.get('returnOnEquity', 0)*100:.2f}%</h3></div>", unsafe_allow_html=True)

                st.divider()

                # Chart & Verdict
                l, r = st.columns([2, 1])
                with l:
                    st.subheader("Price Action (1 Year)")
                    hist = stock.history(period="1y")
                    st.area_chart(hist['Close'])
                
                with r:
                    st.subheader("👨‍🏫 Kunal's Verdict")
                    debt = info.get('debtToEquity', 0)
                    roe = info.get('returnOnEquity', 0)*100
                    
                    if roe > 15 and debt < 100:
                        st.success("💎 **STRONG ASSET**\n\nFundamentals bohot majboot hain.")
                    elif debt > 150:
                        st.error("⚠️ **HIGH DEBT**\n\nKiyosaki ke mutabik ye 'Liability' ho sakti hai.")
                    else:
                        st.warning("⚖️ **NEUTRAL**\n\nSafe side par rahein.")
                    
                    st.write(f"**Debt/Equity:** {debt:.2f}")

    except Exception as e:
        st.error(f"Error: {e}")

# Footer
st.markdown("<br><hr><center>Developed by Kunal Wealth-Tech © 2026 | All NSE Listed Stocks</center>", unsafe_allow_html=True)
