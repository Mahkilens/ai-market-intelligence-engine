import streamlit as st
import pandas as pd
import yfinance as yf
import plotly.express as px

# --- Page Configuration ---
st.set_page_config(
    page_title="AI Market Intelligence Engine",
    page_icon="🤖",
    layout="wide"
)

# --- Header ---
st.title("AI Market Intelligence Engine")
st.write("Get real-time market intelligence for any stock or ETF")

# --- Side Bar ---
st.sidebar.header("Controls")

ticker = st.sidebar.text_input("Enter a stock or ETF ticker: VOO")

time_period = st.sidebar.selectbox(
    "Select a time period",
    ["1mo", "3mo", "6mo", "1y", "5y", "max"],
    index=3 # Default to 1 year
)

def get_stock_data(ticker_symbol, period): # Fetch stock data from Yahoo Finance
    stock = yf.Ticker(ticker_symbol) # Create a Ticker object for the stock
    data = stock.history(period=period) # Get historical data
    return data

analyze_button = st.sidebar.button("Analyze")

if analyze_button:
    data = get_stock_data(ticker, time_period)

    if data.empty:
        st.error("No data found for the given ticker and time period.")
    else: 
        st.subheader(f"Market Intelligence for: {ticker.upper()}")

        current_price = data["Close"].iloc[-1]
        previous_price = data["Close"].iloc[-2]
        daily_change = ((current_price - previous_price) / previous_price) * 100

        col1, col2, col3, col4 = st.columns(4)

        col1.metric("Current Price", f"${current_price:.2f}")
        col2.metric("Daily Change", f"{daily_change:.2f}%")
        col3.metric("Signal Score", "---/100")
        col4.metric("Sentiment", "Neutral")

        left_col, right_col = st.columns([2, 1])

        with left_col:
            st.header("Price Movement")

            chart_data = data.reset_index()

            fig = px.line(
                chart_data,
                x="Date",
                y="Close",
                title=f"{ticker} Closing Price"
            )

            st.plotly_chart(fig, use_container_width=True)

        with right_col:
            st.header("AI Summary")
            st.info("AI-generated explanation will go here later.")

        st.header("Raw Market Data")
        st.dataframe(data.tail(10))
else:
    st.info("Enter a ticker and click 'Get Intelligence'. Try VOO or QQQM.")

st.header("Market Events")
st.dataframe({
    "Event": ["Placeholder news event"],
    "Importance": ["High"],
    "Reason": ["This is where ranked market-moving events will appear."]
})
