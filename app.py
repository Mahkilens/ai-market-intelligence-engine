import streamlit as st
import pandas as pd
import yfinance as yf
import plotly.express as px
from openai import OpenAI
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

# Initialize OpenAI client
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

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

# --- Session State for Analysis ---
if "analysis_ready" not in st.session_state:
    st.session_state.analysis_ready = False

if analyze_button:
    st.session_state.analysis_ready = True

# AI Analysis Function
def generate_ai_summary(market_context):
    prompt = f"""
    You are an AI financial analyst assistant.

    Your job is to explain market data in plain English.
    Do not give financial advice.
    Do not tell the user to buy, sell, or hold.
    Explain the trend, momentum, risks, and key signals.

    Market context:
    {market_context}

    Write a concise analysis with:
    1. Overall summary
    2. Trend interpretation
    3. Momentum/RSI interpretation
    4. Risk note
    """

    response = client.chat.completions.create(
        model="gpt-5.5",
        messages=[
            {"role": "system", "content": "You are a financial analyst assistant."},
            {"role": "user", "content": prompt}
        ]
    )

    return response.choices[0].message.content

def generate_trade_setup_analysis(market_context):
    prompt = f"""
    You are an AI trading assistant.
    
    Your job is to analyze market data and provide a trade setup recommendation.
    
    Market context:
    {market_context}
    
    Write a concise trade setup with:
    1. Entry price
    2. Stop loss
    3. Take profit
    4. Rationale
    """
    
    response = client.chat.completions.create(
        model="gpt-5.5",
        messages=[
            {"role": "system", "content": "You are a trading assistant."},
            {"role": "user", "content": prompt}
        ]
    )
    
    return response.choices[0].message.content


# --- Main Logic --- 
if st.session_state.analysis_ready or analyze_button:
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

        # RSI Calculations
        delta = data["Close"].diff() # Calculate the difference between each price and the previous price

        gain = delta.clip(lower=0) # All negative values become 0
        loss = -delta.clip(upper=0) # All positive values become 0

        average_gain = gain.rolling(window=14).mean() # Calculate the average gain over the last 14 days
        average_loss = loss.rolling(window=14).mean() # Calculate the average loss over the last 14 days

        rs = average_gain / average_loss
        data["RSI"] = 100 - (100 / (1 + rs))

        current_rsi = data["RSI"].iloc[-1]

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

        # Market Regime:
        market_regime = ""
        market_regime_explanation = ""
        market_regime_type = ""

        if current_rsi > 70:
            market_regime = "Overbought Rally"
            market_regime_explanation = "RSI is above 70, suggesting strong momentum but possible overextension."
            market_regime_type = "warning"

        elif signal_score >= 75 and current_rsi <= 70:
            market_regime = "Strong Bullish Momentum"
            market_regime_explanation = "The signal score is strong and RSI is not yet overbought."
            market_regime_type = "success"

        elif signal_score <= 25 and current_rsi < 40:
            market_regime = "Bearish Weakness"
            market_regime_explanation = "The signal score is weak and RSI suggests poor momentum."
            market_regime_type = "warning"

        else:
            market_regime = "Neutral Consolidation"
            market_regime_explanation = "Signals are mixed, suggesting no clear directional edge."
            market_regime_type = "info"

        # --- Display Metrics --- 
        col1, col2, col3, col4, col5, col6 = st.columns(6)

        col1.metric("Current Price", f"${current_price:.2f}")
        col2.metric("Daily Change", f"{daily_change:.2f}%")
        col3.metric("Signal Score", f"{signal_score}/100")
        col4.metric("Period High", f"${period_high:.2f}")
        col5.metric("Volatility", f"{volatility:.2f}%")
        col6.metric("RSI", f"{current_rsi:.2f}")

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
            st.write(f"Signal Score: {signal_score}/100") # this is the overall score of the stock

            # Positive Signals
            st.subheader("Positive Signals") # the stock is performing well
            for signal in positive_signals:
                st.success(signal)

            # Negative Signals
            st.subheader("Negative Signals") # the stock is not performing well
            for signal in negative_signals:
                st.warning(signal)
            
            # RSI Interpretation
            st.subheader("RSI Interpretation")
            if current_rsi > 70:
                st.warning("RSI is above 70 > Market may be Overbought")
            elif current_rsi < 30:
                st.success("RSI is below 30 > Market may be Oversold")
            else:
                st.info("RSI is between 30 & 70 > Market is in neutral range")
            
            # Market Regime
            st.subheader("Market Regime")

            if market_regime_type == "success":
                st.success(market_regime)
            elif market_regime_type == "warning":
                st.warning(market_regime)
            else:
                st.info(market_regime)

        # Displaying raw market data
        st.header("Raw Market Data")
        st.dataframe(data.tail(10))

        st.header("Market Summary")
        market_context = f"""
        Ticker: {ticker}\n
        Current Price: ${current_price:.2f}\n
        Daily Change: {daily_change:.2f}%\n
        Signal Score: {signal_score}/100\n
        RSI: {current_rsi:.2f}\n
        Market Regime: {market_regime}\n
        Positive Signals: {positive_signals}\n
        Negative Signals: {negative_signals}
        """
        st.info(market_context)

        if st.button("Generate AI Summary"):
            ai_summary = generate_ai_summary(market_context)
            st.subheader("AI Market Analyst Summary")
            st.write(ai_summary)

else:
    st.info("Enter a ticker and click 'Get Intelligence'. Try VOO or QQQM.")


