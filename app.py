import streamlit as st
import pandas as pd
import yfinance as yf
import plotly.express as ps

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
    

# --- Main layout ---
st.subheader(f"Market Intelligence for: {ticker.upper()}")

# Top Metrics Row
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("Current Price", "$---")
with col2:
    st.metric("Daily Change", "---%")
with col3:
    st.metric("Signal Score", "--/100")
with col4:
    st.metric("Sentiment", "Neutral")

# Main Dashboard section
left_col, right_col = st.columns([2, 1])

with left_col:
    st.header("Price Chart")
    st.info("Price chart will appear here")

with right_col:
    st.header("AI Analysis")
    st.info("AI analysis will appear here")

st.header("Market Events")
st.dataframe({
    "Event": ["Placeholder news event"],
    "Importance": ["High"],
    "Reason": ["This is where ranked market-moving events will appear."]
})
