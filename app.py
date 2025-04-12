import streamlit as st
st.set_page_config(page_title="Stock Market Dashboard", layout="wide")

import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
from chatbot import generate_prompt_response
from trend_prediction import trend_prediction
from wishlist import wishlist_page, get_wishlist, update_wishlist, stock_notifications
from news import get_stock_news
from sector import sector_heatmap
from constant import SECTORS
from streamlit_extras.switch_page_button import switch_page
import ssl
from intrinsic import intrinsic_value_page
from stock_screener import stock_screener_page
from earnings_calender import earnings_calendar_page
from nasdaq_visualization import nasdaq_visualization
from stock_options import stock_options_page

ssl._create_default_https_context = ssl._create_unverified_context

# ✅ Initialize session state
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False
if "wishlist" not in st.session_state:
    st.session_state.wishlist = []
if "page" not in st.session_state:
    st.session_state.page = "login"
# ✅ Redirect to Login Page if Not Authenticated
if not st.session_state.authenticated:
    # Hide sidebar completely when user is not authenticated
    hide_sidebar = """
        <style>
            [data-testid="stSidebar"] {display: none;}
            [data-testid="collapsedControl"] {display: none;}
        </style>
    """
    st.markdown(hide_sidebar, unsafe_allow_html=True)

    switch_page("login")
    st.stop()

# ✅ Load wishlist and user info
st.session_state.wishlist = get_wishlist(st.session_state.get("username", ""))
first_name = st.session_state.get("username", "").split()[0] if st.session_state.get("username") else "User"

# 🔹 Top Navigation
col1, col2, col3 = st.columns([5, 1, 1])
with col1:
    st.title("📊 Stock Market Dashboard")
    st.subheader(f"👋 Hi, Welcome {first_name}!")
with col3:
    if st.button(f"🌟 Wishlist ({len(st.session_state.wishlist)})", key="wishlist_button"):
        st.session_state["page"] = "wishlist"
        st.rerun()

# ✅ Wishlist Page
if st.session_state["page"] == "wishlist":
    wishlist_page()
    if st.button("🔙 Back to Dashboard"):
        st.session_state["page"] = "dashboard"
        st.rerun()
    st.stop()

# ✅ Notifications
stock_notifications()

# ✅ Sidebar Navigation
st.sidebar.header("Navigation")
selected_tab = st.sidebar.radio("Select a section:", [
    "Stock Analysis", "Nasdaq Stock Visualization", "News Update", "Stock Assistant",
    "Quarterly Analysis", "Sector heatmap", "Intrinsic Value", "Stock Screener",
    "Earnings Calendar", "Stock Options"
])

# ✅ Handle Tabs
if selected_tab == "Stock Analysis":
    st.sidebar.header("Select Sector")
    sector = st.sidebar.selectbox("Choose a sector:", list(SECTORS.keys()))
    stock_symbol = st.sidebar.selectbox("Enter Stock Symbol:", SECTORS[sector])
    period = st.sidebar.selectbox("Select Period:", ['1d', '1wk', '1mo', '6mo', '1y', '5y', '10y'])

    stock_data = yf.Ticker(stock_symbol).history(period=period)
    if stock_data.empty:
        st.error(f"No data available for {stock_symbol}. Try another stock.")
    else:
        st.subheader(f"{stock_symbol} Stock Price Data - {period}")
        st.dataframe(stock_data.tail(5))

        fig = go.Figure(data=[go.Candlestick(
            x=stock_data.index,
            open=stock_data['Open'],
            high=stock_data['High'],
            low=stock_data['Low'],
            close=stock_data['Close']
        )])
        fig.update_layout(title=f'{stock_symbol} Closing Prices - {period}',
                          xaxis_title='Date',
                          yaxis_title='Stock Price',
                          xaxis_rangeslider_visible=False)
        st.plotly_chart(fig, use_container_width=True)

        if stock_symbol not in st.session_state.wishlist:
            if st.button("➕ Add to Wishlist"):
                st.session_state.wishlist.append(stock_symbol)
                update_wishlist(st.session_state.get("username", ""), st.session_state.wishlist)
                st.rerun()

elif selected_tab == "News Update":
    st.header("📰 Latest Stock Market News")
    user_input = st.text_input("Enter Stock Symbol to Search News:")
    if user_input:
        news_articles = get_stock_news(user_input)
        if news_articles:
            for news in news_articles:
                st.write(f"### [{news['headline']}]({news['url']})")
                st.write(f"{news.get('datetime', 'Unknown date')}")
                st.write(f"{news['summary']}")
                st.write("---")
        else:
            st.error(f"No recent news available for {user_input}.")

elif selected_tab == "Stock Assistant":
    st.header("🤖 AI Stock Market Chatbot")
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []

    for role, message in st.session_state.chat_history:
        with st.chat_message(role):
            st.write(message)

    user_input = st.chat_input("Ask me about stocks, sectors, or market trends...")
    if user_input:
        st.session_state.chat_history.append(("user", user_input))
        with st.chat_message("user"):
            st.write(user_input)

        try:
            ai_response = generate_prompt_response(user_input)
        except Exception as e:
            ai_response = f"Error generating response: {e}"

        st.session_state.chat_history.append(("assistant", ai_response))
        with st.chat_message("assistant"):
            st.write(ai_response)

elif selected_tab == "Nasdaq Stock Visualization":
    nasdaq_visualization()

elif selected_tab == "Sector heatmap":
    selected_sector = st.selectbox("Choose a Sector:", list(SECTORS.keys()))
    sector_heatmap(selected_sector)

elif selected_tab == "Quarterly Analysis":
    st.markdown("""
    **"Quarterly"** refers to a period of **three months** in a financial or business context:
    
    - **Q1**: January – March  
    - **Q2**: April – June  
    - **Q3**: July – September  
    - **Q4**: October – December  
    
    ### Importance in Finance
    - 📈 Companies report earnings quarterly  
    - 💰 EPS trends help investors  
    - 🔍 Analysts use it to predict future performance  
    """)
    trend_prediction()

elif selected_tab == "Intrinsic Value":
    intrinsic_value_page()

elif selected_tab == "Stock Screener":
    stock_screener_page()

elif selected_tab == "Earnings Calendar":
    earnings_calendar_page()

elif selected_tab == "Stock Options":
    stock_options_page()

# ✅ Logout
st.sidebar.markdown("---")
if st.sidebar.button("🚪 Logout"):
    st.session_state.authenticated = False
    st.session_state.username = None
    st.session_state.page = "login"
    switch_page("login")
    st.stop()
