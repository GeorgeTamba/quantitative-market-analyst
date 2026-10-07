# QuantAI Analyst

A production-ready quantitative cryptocurrency analytics dashboard and decision-support platform. The application combines real-time asset screening, TradingView-style candlestick charting, and an autonomous AI market strategist powered by Google Gemini and custom quantitative analysis tools.

---

## Overview

QuantAI Analyst is architected to bridge the gap between raw market data and quantitative trade ideation. It pairs a high-performance FastAPI asynchronous backend with a responsive React/Vite interface, allowing traders to screen assets, inspect multi-timeframe price action, and generate structured quantitative risk assessments on demand.

---

## Key Features

- **Autonomous Quantitative Strategist**: Integrates Gemini 3.5 with function calling across custom Python quantitative analysis engines to output structured technical assessments, directional stances, risk evaluations, and execution tactics.
- **Dynamic Candlestick Terminal**: Interactive financial charting powered by TradingView Lightweight Charts supporting multi-timeframe analysis (15M, 1H, 1D, 1W) with dynamic crosshair time-formatting.
- **High-Throughput Market Screener**: Live market monitor tracking top-ranked crypto assets by volume, market capitalization, and 24-hour delta using CoinPaprika endpoints.
- **In-Memory Response Caching**: Time-based backend caching layer (300-second TTL) preventing third-party API rate-limiting and optimizing multi-client throughput.
- **Production-Hardened Infrastructure**: Configured with dynamic Cross-Origin Resource Sharing (CORS), environment variable isolation, structured Python logging, and automated test coverage via Pytest.

---

## Technical Stack

### Frontend
- **Framework**: React 18 (Vite build system)
- **Styling**: Tailwind CSS
- **Charting**: TradingView Lightweight Charts
- **Iconography**: Lucide React
- **State Management**: React Hooks (Lifted State Architecture)

### Backend
- **Framework**: FastAPI (Python 3.12)
- **AI Engine**: Google GenAI SDK (`gemini-3.5-flash-lite`)
- **Data Providers**: Yahoo Finance (`yfinance`), CoinPaprika API
- **Data Validation & Schemas**: Pydantic v2
- **Testing**: Pytest, FastAPI TestClient (`httpx`)
- **Web Server**: Uvicorn ASGI

---

## Quantitative Tool Suite

The Gemini model accesses an integrated suite of 8 quantitative tools implemented in `crypto_tools.py` via structured function calling:

| Tool | Function Name | Purpose |
| :--- | :--- | :--- |
| **Technical Indicators** | `get_technical_indicators` | Computes the 50-day SMA and 14-period RSI (overbought/oversold signal), determines the SMA-50 trend direction, and summarizes period open/high/low and average daily volume. |
| **Market Sentiment** | `get_market_sentiment` | Fetches the latest news headlines from Yahoo Finance and the Alternative.me Crypto Fear & Greed Index. |
| **Fundamental Data** | `get_fundamental_data` | Retrieves price, market cap, 24h volume, and circulating supply, then assesses liquidity via the volume-to-market-cap ratio. |
| **Historical Performance** | `get_historical_performance` | Calculates 7-day, 30-day, and year-to-date returns, benchmarked against Bitcoin (BTC) to flag outperformance or underperformance. |
| **Derivatives Data** | `get_derivatives_data` | Analyzes perpetual futures data (Binance, with Bybit fallback): funding rates, open interest, long/short ratio, and long/short squeeze risk. |
| **On-Chain Metrics** | `get_onchain_metrics` | Gathers on-chain and DeFi activity (TVL, DEX volume, fees, stablecoin supply, network activity) from DefiLlama, Blockchain.com, and Blockchair. |
| **Support & Resistance** | `get_support_resistance_levels` | Calculates daily/weekly pivot points and Fibonacci retracement/extension levels to identify the nearest supports and resistances. |
| **Asset Correlation** | `get_asset_correlation` | Measures correlation and beta of an asset's daily returns against a benchmark (BTC by default, or S&P 500, Gold, DXY, etc.), including downside-day behavior. |

---

## Local Setup

### Prerequisites
- Node.js (v18 or higher)
- Python 3.10+
- Google Gemini API Key

### 1. Clone the Repository
```bash
git clone https://github.com/GeorgeTamba/quantitative-market-analyst.git
cd quantitative-market-analyst