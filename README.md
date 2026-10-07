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
| **Price Action & OHLCV** | `get_current_price` | Retrieves spot price, 24h high/low, and volume metrics. |
| **Trend Identification** | `calculate_moving_averages` | Evaluates short-term and long-term trend alignment using 20/50/200 SMAs and EMAs. |
| **Momentum Gauge** | `calculate_rsi` | Computes 14-period Relative Strength Index to detect overbought and oversold divergence. |
| **Trend Convergence** | `calculate_macd` | Evaluates MACD line, signal line, and histogram momentum crossovers. |
| **Volatility Bands** | `calculate_bollinger_bands` | Analyzes price dispersion, band squeezes, and standard deviation breakouts. |
| **Volatility & Risk** | `calculate_atr` | Measures Average True Range to benchmark stop-loss thresholds and current volatility. |
| **Key Levels** | `get_support_resistance` | Identifies historical swing highs, swing lows, and liquidity zones. |
| **Risk / Reward Modeling**| `evaluate_risk_reward` | Computes theoretical risk-to-reward ratios and expected value metrics for trade setups. |

---

## Local Setup

### Prerequisites
- Node.js (v18 or higher)
- Python 3.10+
- Google Gemini API Key

### 1. Clone the Repository
```bash
git clone [https://github.com/your-username/Quantitative-Market-Analyst.git](https://github.com/your-username/Quantitative-Market-Analyst.git)
cd Quantitative-Market-Analyst