import streamlit as st
import yfinance as yf
import pandas as pd
import streamlit.components.v1 as components

# --- 1. PAGE SETUP ---
st.set_page_config(page_title="Kunal Pro Terminal", page_icon="📊", layout="wide")

st.markdown("""
    <style>
    .header-bar { background-color: #013366; color: white; padding: 15px; font-weight: bold; border-bottom: 5px solid #ffcc00; }
    .strategy-box { background-color: #e3f2fd; padding: 15px; border-radius: 10px; border-left: 5px solid #1e88e5; margin-bottom: 20px; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. LOGIC FUNCTIONS ---
def get_backtest_report(hist_data):
    """Simple Logic: 50-day Moving Average Cross Backtest"""
    hist_data['MA50'] = hist_data['Close'].rolling(window=50).mean()
    initial_price = hist_data['Close'].iloc[0]
    final_price = hist_data['Close'].iloc[-1]
    total_return = ((final_price - initial_price) / initial_price) * 100
    return total_return

# --- 3. SIDEBAR: STRATEGY & TIME FRAME ---
st.markdown("<div class='header-bar'>KUNAL WEALTH-TECH | STRATEGIC TERMINAL</div>", unsafe_allow_html=True)

with st.sidebar:
    st.header("🎯 Trading Strategy")
    mode = st.radio(
        "Select Your Goal:",
        ["Intraday (1 Day)", "Swing (1-4 Weeks)", "Long Term (1 Year+)"]
    )
    
    # Mapping Mode to Chart Interval
    if mode == "Intraday (1 Day)":
        tv_interval = "5" # 5 minutes
        yf_period = "1d"
    elif mode == "Swing (1-4 Weeks)":
        tv_interval = "D" # Daily
        yf_period = "3mo"
    else:
        tv_interval = "W" # Weekly
        yf_period = "max"

    st.divider()
    user_stock = st.text_input("Enter Stock Ticker:", value="TATAMOTORS").upper()
    if ".NS" not in user_stock: user_stock += ".NS"

# --- 4. DATA FETCHING ---
stock = yf.Ticker(user_stock)
info = stock.info

if 'currentPrice' in info:
    # Top Dashboard
    st.subheader(f"🔍 Analyzing: {info.get('longName')} for {mode}")
    
    col1, col2, col3 = st.columns(3)
    col1.metric("Current Price", f"₹{info.get('currentPrice')}")
    col2.metric("Day High", f"₹{info.get('dayHigh')}")
    col3.metric("52W High", f"₹{info.get('fiftyTwoWeekHigh')}")

    # --- TRADINGVIEW WITH SELECTED TIMEFRAME ---
    tv_symbol = f"NSE:{user_stock.split('.')[0]}"
    tradingview_html = f"""
    <div style="height:500px;">
      <script type="text/javascript" src="https://s3.tradingview.com/tv.js"></script>
      <script type="text/javascript">
      new TradingView.widget({{
        "autosize": true, "symbol": "{tv_symbol}", "interval": "{tv_interval}",
        "timezone": "Asia/Kolkata", "theme": "light", "style": "1",
        "locale": "en", "container_id": "tv_chart"
      }});
      </script>
      <div id="tv_chart" style="height:500px;"></div>
    </div>
    """
    components.html(tradingview_html, height=520)

    # --- BACKTESTING LOGIC ---
    st.divider()
    st.markdown("### 🧪 Historical Backtest (1 Year Performance)")
    hist = stock.history(period="1y")
    if not hist.empty:
        ret = get_backtest_report(hist)
        c_a, c_b = st.columns(2)
        with c_a:
            st.markdown(f"""
            <div class='strategy-box'>
                <h4>Strategy Verdict</h4>
                <p>If you held this stock for the last 1 year:</p>
                <h2 style='color:{"green" if ret>0 else "red"}'>{ret:.2f}% Return</h2>
            </div>
            """, unsafe_allow_html=True)
        with c_b:
            st.write("**Quick Analysis:**")
            if ret > 15: st.success("Strong Bullish Trend. Good for Long Term.")
            elif ret > 0: st.warning("Stable Growth. Best for Swing.")
            else: st.error("Negative Return. Avoid for now or check fundamentals.")

else:
    st.error("Invalid Ticker. Please use TATAMOTORS, SBIN, RELIANCE etc.")

st.markdown("<br><hr><center>© 2026 Kunal Wealth-Tech | Strategy & Backtesting</center>", unsafe_allow_html=True)
