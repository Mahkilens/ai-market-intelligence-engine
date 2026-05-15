import yfinance as yf

stock = yf.Ticker("VOO")
data = stock.history(period="1y")
new_data = data.rolling(window=30).mean()
delta = data["Close"].diff()


print(delta)
