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
st.write("Get real-time market intelligence for any stock/ETF or forex pair")

# --- Side Bar ---
st.sidebar.header("Controls")

# Asset Type
asset_type = st.sidebar.selectbox(
    "Select an asset type",
    ["Stock / ETF", "Forex"],
    index=0 # Default to Stock / ETF
)

# --- Ticker Input ---
ticker = st.sidebar.text_input("Enter a stock, ETF, or forex pair:", value="VOO")
st.sidebar.caption("Examples: VOO, QQQM, AAPL, NVDA, EURUSD=X, GBPUSD=X, USDJPY=X")

# --- Historical Range Selection ---
period = st.sidebar.selectbox(
    "Select historical range",
    ["1d", "5d", "1mo", "3mo", "6mo", "1y", "2y", "5y"],
    index=5
)

# Candle Stick Interval
time_interval = st.sidebar.selectbox(
    "Select timeframe",
    ["1m", "2m", "5m", "15m", "30m", "1h", "1d", "5d", "1wk", "1mo", "3mo"],
    index=6 # Default to 1 day
)

# --- Data Fetching Function ---
def get_stock_data(ticker_symbol, period, interval):

    stock = yf.Ticker(ticker_symbol)

    data = stock.history(
        period=period,
        interval=interval
    )

    return data

# normalize forex inputs
def normalize_inputs(user_input, asset_type):
    symbol = user_input.upper().replace("/", "").replace(" ", "")
    
    if asset_type == "Forex":
        if not symbol.endswith("=X"):
            symbol = symbol + "=X"

    return symbol

# --- Button ---
analyze_button = st.sidebar.button("Analyze")

# --- Session State for Analysis ---
if "analysis_ready" not in st.session_state:
    st.session_state.analysis_ready = False

if analyze_button:
    st.session_state.analysis_ready = True

# AI Market Intelligence Summary
def generate_ai_summary(market_context):

    prompt = f"""
You are MahkiVision AI, an institutional-grade market intelligence engine.

Your role is to interpret structured financial market data and explain what current conditions MAY suggest.

You are NOT:
- a financial advisor
- a portfolio manager
- a signal service
- a guarantee engine

You MUST:
- use probability-based reasoning
- speak cautiously and professionally
- explain uncertainty clearly
- avoid hype or emotional language
- avoid guaranteeing outcomes
- avoid direct trade instructions

You specialize in:
- trend analysis
- momentum analysis
- RSI interpretation
- volatility assessment
- market regime analysis
- risk evaluation
- setup quality scoring

Market Context:
{market_context}

Return the analysis using EXACTLY this structure:

# Market Read
Explain the broader market condition in 2-4 professional sentences.

# Trend & Momentum Analysis
Explain:
- moving average behavior
- RSI condition
- momentum quality
- signal score interpretation
- whether trend conditions appear healthy or weakening

# Risk Factors
Explain:
- conflicting signals
- volatility concerns
- momentum exhaustion risk
- trend failure risks
- any signs of weakening structure

# Trader Watchlist
Provide 3-5 things a trader should monitor next.

Examples:
- RSI behavior
- moving average holds
- volatility expansion
- trend continuation
- price rejection
- support/resistance reactions

# Confidence Assessment
Provide:
- Confidence Score: X/100
- A 2-3 sentence explanation justifying the score.

Your tone should sound like:
- an institutional analyst
- a hedge-fund research assistant
- a professional market intelligence system
"""

    response = client.chat.completions.create(
        model="gpt-5.5",
        messages=[
            {
                "role": "system",
                "content": """
You are MahkiVision AI.

A professional market intelligence and probabilistic analysis system designed for educational and research purposes.

You analyze:
- stocks
- ETFs
- forex pairs

You provide structured market interpretation without giving financial advice.
"""
            },
            {
                "role": "user",
                "content": prompt
            }
        ]
    )

    return response.choices[0].message.content

# AI Trade Setup Intelligence
def generate_trade_setup_analysis(market_context):

    prompt = f"""
You are MahkiVision AI, an institutional-grade trading intelligence engine.

Your purpose is to evaluate market structure and describe what type of setup MAY be forming.

You are NOT:
- a financial advisor
- a signal seller
- a trade execution engine

You MUST:
- avoid direct buy/sell instructions
- avoid guaranteeing outcomes
- explain uncertainty honestly
- use cautious market language
- think like a professional market analyst

Market Context:
{market_context}

Return the response using EXACTLY this structure:

# Setup Classification
Classify the current structure as ONE of the following:
- Bullish Continuation Watch
- Pullback Risk
- Neutral / No Clear Edge
- Bearish Weakness Watch
- High Volatility / Unstable Conditions

Then explain WHY.

# Setup Strength Assessment
Provide:
- Setup Score: X/100

Then explain:
- trend quality
- momentum quality
- signal alignment
- volatility conditions
- whether conditions appear strengthening or weakening

# Confirmation Signals
List 3-6 things traders should monitor for confirmation.

Examples:
- RSI continuation
- moving average support
- volatility contraction
- breakout continuation
- price rejection
- trend acceleration
- volume expansion

# Risk & Invalidation
Explain:
- what could weaken the setup
- what could invalidate trend structure
- warning signs traders should monitor
- momentum failure conditions

# Human Review Checklist
Provide 3-5 manual review checks.

Examples:
- higher timeframe trend
- macroeconomic events
- news catalysts
- major resistance zones
- support integrity
- market correlation behavior

Your tone should sound:
- professional
- analytical
- institutional
- probability-focused
"""

    response = client.chat.completions.create(
        model="gpt-5.5",
        messages=[
            {
                "role": "system",
                "content": """
You are MahkiVision AI.

An institutional-grade market intelligence system designed to evaluate:
- stocks
- ETFs
- forex markets

You provide structured probabilistic analysis for educational and research purposes only.

You never provide financial advice or guaranteed outcomes.
"""
            },
            {
                "role": "user",
                "content": prompt
            }
        ]
    )

    return response.choices[0].message.content

# --- Normalize ticker symbols based on asset type ---
def normalize_ticker(ticker, asset_type):

    ticker = ticker.upper().strip()

    # Forex handling
    if asset_type == "Forex":

        # If user enters EURUSD
        if len(ticker) == 6 and "-" not in ticker:
            return f"{ticker}=X"

        # If user enters EUR/USD
        if "/" in ticker:
            clean_pair = ticker.replace("/", "")
            return f"{clean_pair}=X"

        # If user already entered EURUSD=X
        if "=X" in ticker:
            return ticker

    # Default stock/ETF behavior
    return ticker

# --- Validate ticker input based on asset type ---
def validate_ticker(ticker, asset_type):

    ticker = ticker.upper().strip()

    # Forex validation
    if asset_type == "Forex":

        # Remove formatting
        clean_ticker = ticker.replace("/", "").replace("=X", "")

        # Forex pairs should be 6 letters
        if len(clean_ticker) != 6:
            return False

        # Must contain only letters
        if not clean_ticker.isalpha():
            return False

        return True

    # Stock/ETF validation
    else:

        # Stocks usually shorter
        if len(ticker) > 5:
            return False

        # Stocks should not contain slash
        if "/" in ticker:
            return False

        # Stocks should not contain =X
        if "=X" in ticker:
            return False

        return True

# Validate ticker input
if not validate_ticker(ticker, asset_type):

    st.error(
        f"Invalid ticker format for {asset_type}."
    )

    st.stop()

# --- Main Logic --- 
if st.session_state.analysis_ready or analyze_button:
    normalized_ticker = normalize_ticker(ticker, asset_type)
    data = get_stock_data(
        normalized_ticker,
        period,
        time_interval
    )

    if "ai_summary" not in st.session_state:
        st.session_state.ai_summary = ""

    if "trade_setup" not in st.session_state:
        st.session_state.trade_setup = ""

    if data.empty:
        st.error("No data found for the given ticker and time period.")
    else: 
        st.subheader(f"Market Intelligence for: {normalized_ticker}")
        st.caption(f"Symbol used by data provider: {normalized_ticker}")

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

        # Trade Setup Intelligence
        setup_type = "" # "Long", "Short", "Neutral"
        setup_score = 0 # 0-100
        risk_level = "" # "Low", "Medium", "High"
        confirmation_signals = [] # List of strings describing confirmation signals
        invalidation_notes = [] # List of strings describing invalidation signals

        # Bullish Setup
        if signal_score >= 75 and current_rsi < 70:
            setup_type = "Bullish Continuation Watch"
            setup_score = signal_score
            risk_level = "Medium"
            confirmation_signals.append("Strong signal score suggests multiple bullish conditions are active.")
            confirmation_signals.append("RSI is below overbought territory, suggesting momentum may not be stretched yet.")
            invalidation_notes.append("A move below the 20-day moving average may weaken the bullish setup.")
            invalidation_notes.append("A sharp rise in volatility may increase downside risk.")
        elif signal_score >= 75 and current_rsi >= 70:
            setup_type = "Bullish but Overextended" 
            setup_score = signal_score - 10 # Reduce score to reflect higher risk
            risk_level = "High" # Higher risk due to overextension
            confirmation_signals.append("Signal score is strong, showing positive trend structure.")
            invalidation_notes.append("RSI above 70 suggests the move may be overextended.")
            invalidation_notes.append("Short-term pullback risk is elevated.")
        elif signal_score <= 25:
            setup_type = "Bearish Weakness Watch" 
            setup_score = signal_score
            risk_level = "High"
            confirmation_signals.append("Low signal score suggests weak technical conditions.")
            invalidation_notes.append("A move back above key moving averages may invalidate the bearish view.")
        else:
            setup_type = "Neutral / No Clear Edge"
            setup_score = signal_score
            risk_level = "Medium"
            confirmation_signals.append("Signals are mixed, so there is no clear directional setup.")
            invalidation_notes.append("Wait for clearer confirmation from price, trend, RSI, or volume.")
        
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

        st.header("Trade Setup Intelligence")

        col_a, col_b, col_c = st.columns(3)

        col_a.metric("Setup Type", setup_type)
        col_b.metric("Setup Score", f"{setup_score}/100")
        col_c.metric("Risk Level", risk_level)

        st.write("Confirmation Signals")
        for signal in confirmation_signals:
            st.success(signal)

        st.write("Invalidation Notes")
        for note in invalidation_notes:
            st.warning(note)


        # Displaying raw market data
        st.header("Raw Market Data")
        st.dataframe(data.tail(10))

        st.header("Market Summary")
        market_context = f"""
        Ticker: {ticker}\n
        Asset Type: {asset_type}\n
        Symbol Used: {normalized_ticker}\n
        Current Price: ${current_price:.2f}\n
        Daily Change: {daily_change:.2f}%\n
        Signal Score: {signal_score}/100\n
        RSI: {current_rsi:.2f}\n
        Market Regime: {market_regime}\n
        Positive Signals: {positive_signals}\n
        Negative Signals: {negative_signals}\n
        Setup Type: {setup_type}\n
        Setup Score: {setup_score}/100\n
        Risk Level: {risk_level}\n
        Confirmation Signals: {confirmation_signals}\n
        Invalidation Notes: {invalidation_notes}
        """
        st.info(market_context)

        if st.button("Generate AI Summary"):
            with st.spinner("Generating AI market analysis..."):
                st.session_state.ai_summary = generate_ai_summary(market_context)

        if st.session_state.ai_summary:
            st.subheader("AI Market Analyst Summary")
            st.write(st.session_state.ai_summary)

        if st.button("Generate Trade Setup Analysis"):
            with st.spinner("Analyzing trade setup..."):
                st.session_state.trade_setup = generate_trade_setup_analysis(market_context)

        if st.session_state.trade_setup:
            st.subheader("AI Trade Setup Analysis")
            st.write(st.session_state.trade_setup)

        if st.button("Clear AI Outputs"):
            st.session_state.ai_summary = ""
            st.session_state.trade_setup = ""
            st.rerun()

else:
    st.info("Enter a ticker and click 'Get Intelligence'. Try VOO or QQQM.")


