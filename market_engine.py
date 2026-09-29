import yfinance as yf
import pandas as pd
import numpy as np

def get_market_data(ticker: str, days: int) -> dict:
    """Fetches market data and calculates 50-SMA and 14-RSI."""
    print(f"Fetching {days} days of data for {ticker}...\n")
    
    # 1. Fetch historical data
    stock = yf.Ticker(ticker)
    df = stock.history(period=f"{days}d")
    
    if df.empty:
        return {"error": f"No data found for {ticker}"}
        
    # 2. Calculate 50-day Simple Moving Average (SMA)
    df['SMA_50'] = df['Close'].rolling(window=50).mean()
    
    # 3. Calculate 14-day Relative Strength Index (RSI)
    delta = df['Close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
    rs = gain / loss
    df['RSI_14'] = 100 - (100 / (1 + rs))
    
    # 4. Extract the most recent trading day's metrics
    latest_day = df.iloc[-1]
    
    return {
        "ticker": ticker,
        "current_price": round(latest_day['Close'], 2),
        "sma_50": round(latest_day['SMA_50'], 2) if not pd.isna(latest_day['SMA_50']) else None,
        "rsi_14": round(latest_day['RSI_14'], 2) if not pd.isna(latest_day['RSI_14']) else None
    }

# Test the engine locally
if __name__ == "__main__":
    # Fetch 100 days of Bitcoin data to ensure our 50-day SMA has enough data to calculate
    result = get_market_data("BTC-USD", 100) 
    print(result)