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

# --- Ticker Input ---
ticker = st.sidebar.text_input("Enter a stock or ETF ticker: VOO")

# --- Time Period Selection ---
time_period = st.sidebar.selectbox(
    "Select a time period",
    ["1mo", "3mo", "6mo", "1y", "5y", "max"],
    index=3 # Default to 1 year
)

# --- Data Fetching Function ---
def get_stock_data(ticker_symbol, period): # Fetch stock data from Yahoo Finance
    stock = yf.Ticker(ticker_symbol) # Create a Ticker object for the stock
    data = stock.history(period=period) # Get historical data
    return data

# --- Button ---
analyze_button = st.sidebar.button("Analyze")

# --- Main Logic --- 
if analyze_button:
    data = get_stock_data(ticker, time_period)

    if data.empty:
        st.error("No data found for the given ticker and time period.")
    else: 
        st.subheader(f"Market Intelligence for: {ticker.upper()}")

        # Calculate current price and daily change (from previous close)
        current_price = data["Close"].iloc[-1]
        previous_price = data["Close"].iloc[-2]
        daily_change = ((current_price - previous_price) / previous_price) * 100

        # Calculate period return (from start to end of period)
        start_price = data["Close"].iloc[0]
        period_return = ((current_price - start_price) / start_price) * 100

        # Calculate period high and low (over the entire period)
        period_high = data["Close"].max()
        period_low = data["Close"].min()

        # Calculate volatility (standard deviation of daily returns)
        daily_returns = data["Close"].pct_change()
        volatility = daily_returns.std() * 100


        # --- Display Metrics --- 
        col1, col2, col3, col4, col5 = st.columns(5)

        col1.metric("Current Price", f"${current_price:.2f}")
        col2.metric("Daily Change", f"{daily_change:.2f}%")
        col3.metric("Period Return", f"{period_return:.2f}%")
        col4.metric("Period High", f"${period_high:.2f}")
        col5.metric("Volatility", f"{volatility:.2f}%")

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
