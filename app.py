import streamlit as st
import yfinance as yf
import pandas as pd
import requests
import streamlit.components.v1 as components

# --- 1. ULTRA-ATTRACTIVE THEME SETUP ---
st.set_page_config(page_title="Kunal Wealth-Tech | Elite", page_icon="💎", layout="wide")

# Custom CSS for Glassmorphism & Modern UI
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;700&display=swap');
    
    html, body, [class*="css"] { font-family: 'Inter', sans-serif; }
    
    .main { background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%); color: white; }
    
    /* Glowing Header */
    .top-header {
        background: rgba(255, 255, 255, 0.05);
        backdrop-filter: blur(10px);
        padding: 30px; border-radius: 20px;
        border: 1px solid rgba(255, 255, 255, 0.1);
        text-align: center; margin-bottom: 30px;
        box-shadow: 0 8px 32px 0 rgba(31, 38, 135, 0.37);
    }
    
    .hero-text {
        background: linear-gradient(90deg, #38bdf8, #818cf8);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-size: 42px; font-weight: 800;
    }

    /* Control Panel Box */
    .control-card {
        background: rgba(255, 255, 255, 0.03);
        padding: 25px; border-radius: 15px;
        border: 1px solid rgba(255, 255, 255, 0.1);
        margin-bottom: 25px;
    }

    /* Glass Metric Cards */
    .metric-card {
        background: rgba(255, 255, 255, 0.05);
        padding: 20px; border-radius: 15px;
        border-left: 5px solid #38bdf8;
        transition: transform 0.3s;
    }
    .metric-card:hover { transform: translateY(-5px); background: rgba(255, 255, 255, 0.08); }
    
    .label { color: #94a3b8; font-size: 14px; font-weight: 600; text-transform: uppercase; }
    .value { color: #f8fafc; font-size: 26px; font-weight: 700; margin-top: 5px; }

    /* Hide Streamlit Header/Footer */
    header {visibility: hidden;}
    footer {visibility: hidden;}
    </style>
    """, unsafe_allow_html=True)

# --- 2. LOGIC FUNCTIONS ---
def get_live_suggestions(query):
    if len(query) < 2: return {}
    try:
        url = f"https://query2.finance.yahoo.com/v1/finance/search?q={query}&quotesCount=10"
        headers = {'User-Agent': 'Mozilla/5.0'}
        r = requests.get(url, headers=headers).json()
        return {f"{q.get('longname', q.get('symbol'))}": q['symbol'] for q in r.get('quotes', []) if '.NS' in q.get('symbol', '')}
    except: return {}

# --- 3. TOP HERO SECTION ---
st.markdown("""
    <div class='top-header'>
        <div class='hero-text'>KUNAL WEALTH-TECH</div>
        <p style='color: #94a3b8; font-size: 18px;'>Elite NSE Market Intelligence & Backtesting Terminal</p>
    </div>
    """, unsafe_allow_html=True)

# --- 4. INTERACTIVE CONTROLS (Main UI) ---
with st.container():
    col_search, col_unit, col_num = st.columns([2, 1, 1])
    
    with col_search:
        user_input = st.text_input("🔍 SEARCH ANY NSE STOCK", value="Tata Motors", help="Type stock name and wait for suggestions")
        sugg = get_live_suggestions(user_input)
        if sugg:
            selected_stock = st.selectbox("Confirm Selection:", options=list(sugg.keys()))
            ticker = sugg[selected_stock]
        else:
            ticker = f"{user_input.upper().strip()}.NS" if ".NS" not in user_input.upper() else user_input.upper()

    with col_unit:
        t_unit = st.selectbox("TIMEFRAME UNIT", ["Days", "Weeks", "Months", "Years"], index=2)
    
    with col_num:
        t_qty = st.number_input("DURATION", min_value=1, value=6)

# --- 5. DATA ENGINE ---
period_map = {"Days": "d", "Weeks": "wk", "Months": "mo", "Years": "y"}
final_period = f"{t_qty}{period_map[t_unit]}"

@st.cache_data(ttl=300)
def fetch_elite_data(sym, period):
    try:
        s = yf.Ticker(sym)
        return s.info, s.history(period=period)
    except: return None, None

info, hist = fetch_elite_data(ticker, final_period)

if info and 'currentPrice' in info:
    # --- METRICS GRID ---
    st.markdown("<br>", unsafe_allow_html=True)
    m1, m2, m3, m4 = st.columns(4)
    
    metrics = [
        ("Live Price", f"₹{info.get('currentPrice', 0):,.2f}"),
        ("Market Cap", f"{info.get('marketCap', 0)/1e7:,.0f} Cr"),
        ("ROE", f"{info.get('returnOnEquity', 0)*100:.2f}%"),
        ("D/E Ratio", f"{info.get('debtToEquity', 0):.2f}")
    ]
    
    cols = [m1, m2, m3, m4]
    for i, (lab, val) in enumerate(metrics):
        cols[i].markdown(f"""
            <div class='metric-card'>
                <div class='label'>{lab}</div>
                <div class='value'>{val}</div>
            </div>
        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # --- MAIN CONTENT: CHART & BACKTEST ---
    c_left, c_right = st.columns([2, 1])

    with c_left:
        st.markdown(f"#### ⚡ LIVE TRADINGVIEW CHART ({ticker})")
        tv_symbol = f"NSE:{ticker.split('.')[0]}"
        tv_interval = "D" if t_unit == "Days" else "W"
        
        tv_widget = f"""
        <div style="height:550px; width:100%; border-radius:15px; overflow:hidden; border: 1px solid rgba(255,255,255,0.1);">
            <script type="text/javascript" src="https://s3.tradingview.com/tv.js"></script>
            <script type="text/javascript">
            new TradingView.widget({{
                "autosize": true, "symbol": "{tv_symbol}", "interval": "{tv_interval}",
                "timezone": "Asia/Kolkata", "theme": "dark", "style": "1", "locale": "en",
                "toolbar_bg": "#1e293b", "enable_publishing": false, "container_id": "tv_chart"
            }});
            </script>
            <div id="tv_chart" style="height:550px;"></div>
        </div>
        """
        components.html(tv_widget, height=550)

    with c_right:
        st.markdown(f"#### 🧪 PERFORMANCE: {t_qty} {t_unit}")
        if not hist.empty:
            start_p = hist['Close'].iloc[0]
            end_p = hist['Close'].iloc[-1]
            ret = ((end_p - start_p) / start_p) * 100
            color = "#4ade80" if ret > 0 else "#f87171"
            
            st.markdown(f"""
                <div style='background: rgba(255,255,255,0.03); padding:30px; border-radius:20px; text-align:center; border: 1px solid rgba(255,255,255,0.1);'>
                    <p style='color:#94a3b8; font-weight:600;'>Return Analysis</p>
                    <h1 style='color:{color}; font-size:48px; margin:10px 0;'>{ret:+.2f}%</h1>
                    <hr style='opacity:0.1; margin:20px 0;'>
                    <div style='display:flex; justify-content:space-between; color:#cbd5e1;'>
                        <span>Entry: <b>₹{start_p:,.1f}</b></span>
                        <span>Exit: <b>₹{end_p:,.1f}</b></span>
                    </div>
                </div>
            """, unsafe_allow_html=True)
            
            st.divider()
            # Dynamic Suggestion Based on Return
            if ret > 20: st.success("🚀 Parabolic Growth! Momentum is very strong.")
            elif ret > 0: st.info("📈 Steady Growth. Consistent performer.")
            else: st.warning("📉 Downtrend Detected. Check fundamentals before entry.")

else:
    st.error("⚠️ Ticker not found. Please try a valid NSE stock name.")

st.markdown("<br><br><center style='color:#64748b;'>Kunal Wealth-Tech Elite © 2026 | All Rights Reserved</center>", unsafe_allow_html=True)
