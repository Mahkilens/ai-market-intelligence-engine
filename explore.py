import yfinance as yf

stock = yf.Ticker("VOO")
data = stock.history(period="1y")

print(data)
