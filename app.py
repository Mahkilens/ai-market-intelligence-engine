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

        # Moving averages
        data["MA20"] = data["Close"].rolling(window=20).mean()
        data["MA50"] = data["Close"].rolling(window=50).mean()

        current_ma20 = data["MA20"].iloc[-1]
        current_ma50 = data["MA50"].iloc[-1]

        # Signal Score
        # Market Intelligence Summary v2
        # This version focuses on providing a clear, actionable summary of the market data.

        signal_score = 0
        positive_signals = []
        negative_signals = []

        if current_price > current_ma20:
            signal_score += 25
            positive_signals.append("Price is above the 20-day moving average.")
        else:
            negative_signals.append("Price is below the 20-day moving average.")

        if current_price > current_ma50:
            signal_score += 25
            positive_signals.append("Price is above the 50-day moving average.")
        else:
            negative_signals.append("Price is below the 50-day moving average.")

        if period_return > 0:
            signal_score += 25
            positive_signals.append("Period return is positive.")
        else:
            negative_signals.append("Period return is negative.")

        if daily_change > 0:
            signal_score += 25
            positive_signals.append("Daily change is positive.")
        else:
            negative_signals.append("Daily change is negative.")


        # --- Display Metrics --- 
        col1, col2, col3, col4, col5 = st.columns(5)

        col1.metric("Current Price", f"${current_price:.2f}")
        col2.metric("Daily Change", f"{daily_change:.2f}%")
        col3.metric("Signal Score", f"{signal_score}/100")
        col4.metric("Period High", f"${period_high:.2f}")
        col5.metric("Volatility", f"{volatility:.2f}%")

        left_col, right_col = st.columns([2, 1])

        with left_col:
            st.header("Price Movement")

            # Displaying rolling/moving averages 
            data["MA20"] = data["Close"].rolling(window=20).mean()
            data["MA50"] = data["Close"].rolling(window=50).mean()

            chart_data = data.reset_index()

            # Creating the line chart with Plotly
            fig = px.line(
                chart_data,
                x="Date",
                y=["Close", "MA20", "MA50"],
                title=f"{ticker} Price with Moving Averages"
            )

            # Display the chart
            st.plotly_chart(fig, use_container_width=True)

        # --- Display AI Summary --- 
        with right_col:

            # Signal Breakdown
            st.subheader("Signal Breakdown")
            st.write(f"Signal Score: {signal_score}/100")

            # Positive Signals
            st.write("Positive Signals")
            for signal in positive_signals:
                st.success(signal)

            # Negative Signals
            st.write("Negative Signals")
            for signal in negative_signals:
                st.warning(signal)

        # Displaying raw market data
        st.header("Raw Market Data")
        st.dataframe(data.tail(10))

else:
    st.info("Enter a ticker and click 'Get Intelligence'. Try VOO or QQQM.")



