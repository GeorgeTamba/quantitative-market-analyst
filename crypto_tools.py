"""
Crypto tool functions for Gemini function calling.
Data sources: Yahoo Finance (yfinance) + Alternative.me Fear & Greed Index.
All functions return JSON-serializable dicts (no numpy / pandas types).
"""

from datetime import datetime, timezone
import pandas as pd
import requests
import yfinance as yf

FNG_URL = "https://api.alternative.me/fng/?limit=1"
REQUEST_TIMEOUT = 10

# ----------------------------------------------------------------------
# Helpers (not exposed to the model)
# ----------------------------------------------------------------------
def _normalize_ticker(ticker: str) -> str:
    """Convert 'btc', 'BTC', 'BTCUSD', 'BTCUSDT' -> 'BTC-USD'."""
    t = ticker.strip().upper().replace("/", "-")
    
    if t.endswith("-USD"):
        return t
    
    # FIX: Handle Binance-style USDT pairs
    if t.endswith("USDT"):
        return f"{t[:-4]}-USD"
        
    if t.endswith("USD") and len(t) > 3:
        return f"{t[:-3]}-USD"
        
    return f"{t}-USD"

def _safe_float(value, digits: int = 4):
    try:
        if value is None or pd.isna(value):
            return None
        return round(float(value), digits)
    except (TypeError, ValueError):
        return None

def _get_history(symbol: str, period: str = "1mo") -> pd.DataFrame:
    # FIX: Defaulted to '1mo' period, removed 'start' for safer fetching
    tk = yf.Ticker(symbol)
    df = tk.history(period=period, interval="1d", auto_adjust=False)
    if df is None or df.empty:
        raise ValueError(f"No price data found for '{symbol}'. Check the ticker symbol.")
    return df

def _pct_change(current: float, past: float):
    if past is None or past == 0:
        return None
    return round((current - past) / past * 100, 2)

def _price_on_or_before(close: pd.Series, target: pd.Timestamp):
    """Last close on or before a target date (handles gaps in data)."""
    subset = close[close.index <= target]
    return float(subset.iloc[-1]) if not subset.empty else None


# ----------------------------------------------------------------------
# 1. Technical indicators
# ----------------------------------------------------------------------
def get_technical_indicators(ticker: str, days: int = 90) -> dict:
    # ... (Your original code here is perfect) ...
    try:
        symbol = _normalize_ticker(ticker)
        days = max(int(days), 60)
        df = _get_history(symbol, period=f"{days + 60}d")
        close = df["Close"]

        sma_50 = close.rolling(window=50).mean()

        delta = close.diff()
        gain = delta.clip(lower=0)
        loss = -delta.clip(upper=0)
        avg_gain = gain.ewm(alpha=1 / 14, min_periods=14, adjust=False).mean()
        avg_loss = loss.ewm(alpha=1 / 14, min_periods=14, adjust=False).mean()
        rs = avg_gain / avg_loss
        rsi = 100 - (100 / (1 + rs))

        current_price = float(close.iloc[-1])
        current_sma = _safe_float(sma_50.iloc[-1])
        current_rsi = _safe_float(rsi.iloc[-1], 2)

        if current_rsi is None:
            rsi_signal = "unknown"
        elif current_rsi >= 70:
            rsi_signal = "overbought"
        elif current_rsi <= 30:
            rsi_signal = "oversold"
        else:
            rsi_signal = "neutral"

        trend = None
        if current_sma is not None:
            trend = "bullish (price above SMA-50)" if current_price > current_sma \
                else "bearish (price below SMA-50)"

        window = df.tail(days)
        return {
            "ticker": symbol,
            "as_of": window.index[-1].strftime("%Y-%m-%d"),
            "current_price_usd": _safe_float(current_price),
            "sma_50": current_sma,
            "price_vs_sma50_pct": _pct_change(current_price, current_sma) if current_sma else None,
            "rsi_14": current_rsi,
            "rsi_signal": rsi_signal,
            "trend": trend,
            "period_days": days,
            "period_open": _safe_float(window["Open"].iloc[0]),
            "period_high": _safe_float(window["High"].max()),
            "period_low": _safe_float(window["Low"].min()),
            "avg_daily_volume_usd": _safe_float(window["Volume"].mean(), 0),
        }
    except Exception as e:
        return {"error": str(e), "ticker": ticker}

# ----------------------------------------------------------------------
# 2. Market sentiment (Unchanged - Perfect)
# ----------------------------------------------------------------------
def get_market_sentiment(ticker: str) -> dict:
    # ... (Your original code here is perfect) ...
    symbol = _normalize_ticker(ticker)
    result = {"ticker": symbol, "headlines": [], "fear_and_greed": None}
    try:
        raw_news = yf.Ticker(symbol).news or []
        for item in raw_news[:5]:
            content = item.get("content", item)
            provider = content.get("provider") or {}
            url_obj = content.get("canonicalUrl") or content.get("clickThroughUrl") or {}
            published = content.get("pubDate")
            if published is None and item.get("providerPublishTime"):
                published = datetime.fromtimestamp(item["providerPublishTime"], tz=timezone.utc).isoformat()
            result["headlines"].append({
                "title": content.get("title"),
                "publisher": provider.get("displayName") if isinstance(provider, dict) else item.get("publisher"),
                "published": published,
                "url": url_obj.get("url") if isinstance(url_obj, dict) else item.get("link"),
            })
        if not result["headlines"]:
            result["news_note"] = "No recent headlines found for this ticker."
    except Exception as e:
        result["news_error"] = str(e)

    try:
        resp = requests.get(FNG_URL, timeout=REQUEST_TIMEOUT)
        resp.raise_for_status()
        data = resp.json()["data"][0]
        result["fear_and_greed"] = {
            "value": int(data["value"]),
            "classification": data["value_classification"],
            "date": datetime.fromtimestamp(int(data["timestamp"]), tz=timezone.utc).strftime("%Y-%m-%d"),
        }
    except Exception as e:
        result["fear_and_greed_error"] = str(e)
    return result

# ----------------------------------------------------------------------
# 3. Fundamental data (Unchanged - Perfect)
# ----------------------------------------------------------------------
def get_fundamental_data(ticker: str) -> dict:
    # ... (Your original code here is perfect) ...
    try:
        symbol = _normalize_ticker(ticker)
        tk = yf.Ticker(symbol)
        info = tk.info or {}

        price = info.get("regularMarketPrice") or info.get("previousClose")
        market_cap = info.get("marketCap")
        volume_24h = info.get("volume24Hr") or info.get("regularMarketVolume")
        circ_supply = info.get("circulatingSupply")

        if price is None or volume_24h is None:
            hist = _get_history(symbol, period="5d")
            price = price or float(hist["Close"].iloc[-1])
            volume_24h = volume_24h or float(hist["Volume"].iloc[-1])
        if market_cap is None and circ_supply and price:
            market_cap = price * circ_supply

        vol_mcap_ratio = None
        liquidity = "unknown"
        if market_cap and volume_24h:
            vol_mcap_ratio = round(volume_24h / market_cap * 100, 2)
            if volume_24h < 1_000_000:
                liquidity = "very low (under $1M daily volume, high slippage risk)"
            elif vol_mcap_ratio < 1:
                liquidity = "low (volume under 1% of market cap)"
            elif vol_mcap_ratio <= 25:
                liquidity = "healthy"
            else:
                liquidity = "very high turnover (possible speculation or wash trading)"

        return {
            "ticker": symbol,
            "name": info.get("name") or info.get("shortName"),
            "price_usd": _safe_float(price),
            "market_cap_usd": _safe_float(market_cap, 0),
            "volume_24h_usd": _safe_float(volume_24h, 0),
            "circulating_supply": _safe_float(circ_supply, 0),
            "volume_to_market_cap_pct": vol_mcap_ratio,
            "liquidity_assessment": liquidity,
        }
    except Exception as e:
        return {"error": str(e), "ticker": ticker}

# ----------------------------------------------------------------------
# 4. Historical performance
# ----------------------------------------------------------------------
def get_historical_performance(ticker: str) -> dict:
    """Gets historical percentage returns for a cryptocurrency..."""
    def _returns(sym: str) -> dict:
        now = pd.Timestamp.now(tz="UTC")
        
        # FIX: Simply fetch a guaranteed 2-year window to avoid "January bugs"
        df = _get_history(sym, period="2y")
        close = df["Close"]
        
        # FIX: Ensure index is timezone-aware to match 'now'
        if close.index.tz is None:
            close.index = close.index.tz_localize("UTC")

        last_date = close.index[-1]
        current = float(close.iloc[-1])
        
        price_7d = _price_on_or_before(close, last_date - pd.Timedelta(days=7))
        price_30d = _price_on_or_before(close, last_date - pd.Timedelta(days=30))
        
        # YTD baseline = last close of the previous year (Dec 31)
        prev_year_end = pd.Timestamp(f"{now.year - 1}-12-31", tz="UTC")
        price_ytd = _price_on_or_before(close, prev_year_end)
        
        if price_ytd is None:  # asset listed this year
            price_ytd = float(close.iloc[0])

        return {
            "as_of": last_date.strftime("%Y-%m-%d"),
            "current_price_usd": _safe_float(current),
            "return_7d_pct": _pct_change(current, price_7d),
            "return_30d_pct": _pct_change(current, price_30d),
            "return_ytd_pct": _pct_change(current, price_ytd),
        }

    try:
        symbol = _normalize_ticker(ticker)
        asset = _returns(symbol)
        result = {"ticker": symbol, **asset}

        if symbol != "BTC-USD":
            btc = _returns("BTC-USD")
            result["benchmark_btc"] = btc
            if asset["return_ytd_pct"] is not None and btc["return_ytd_pct"] is not None:
                diff = round(asset["return_ytd_pct"] - btc["return_ytd_pct"], 2)
                result["ytd_vs_btc_pct_points"] = diff
                result["outperforming_btc_ytd"] = diff > 0
        return result
    except Exception as e:
        return {"error": str(e), "ticker": ticker}
    

"""
Advanced crypto tools (5-8) for Gemini function calling.
  5. get_derivatives_data          -> Binance Futures (Bybit fallback)
  6. get_onchain_metrics           -> DefiLlama + Blockchain.com + Blockchair
  7. get_support_resistance_levels -> pure math on Yahoo Finance OHLC
  8. get_asset_correlation         -> pure math on Yahoo Finance closes
All free, no API keys. All functions return JSON-serializable dicts.
"""

import time
from urllib.parse import quote

import pandas as pd
import requests

from crypto_tools import _normalize_ticker, _safe_float, _get_history, _pct_change, REQUEST_TIMEOUT

HEADERS = {"User-Agent": "crypto-chatbot/1.0"}
BINANCE_FAPI = "https://fapi.binance.com"
BYBIT_API = "https://api.bybit.com"
LLAMA_API = "https://api.llama.fi"
STABLES_API = "https://stablecoins.llama.fi"
BLOCKCHAIN_INFO = "https://api.blockchain.info/charts"
BLOCKCHAIR_API = "https://api.blockchair.com"

BLOCKCHAIR_CHAINS = {
    "ETH": "ethereum", "LTC": "litecoin", "DOGE": "dogecoin",
    "BCH": "bitcoin-cash", "DASH": "dash", "ZEC": "zcash",
}

BENCHMARK_ALIASES = {
    "SPX": "^GSPC", "SP500": "^GSPC", "S&P500": "^GSPC", "S&P 500": "^GSPC",
    "NASDAQ": "^IXIC", "NDX": "^NDX", "DOW": "^DJI", "DJI": "^DJI",
    "GOLD": "GC=F", "DXY": "DX-Y.NYB", "VIX": "^VIX",
    "SPY": "SPY", "QQQ": "QQQ",
}

# ----------------------------------------------------------------------
# Helpers
# ----------------------------------------------------------------------
def _get_json(url: str, params: dict = None):
    r = requests.get(url, params=params, headers=HEADERS, timeout=REQUEST_TIMEOUT)
    r.raise_for_status()
    return r.json()

_CACHE: dict = {}

def _cached_json(url: str, params: dict = None, ttl: int = 600):
    key = url + str(sorted((params or {}).items()))
    hit = _CACHE.get(key)
    if hit and time.time() - hit[0] < ttl:
        return hit[1]
    data = _get_json(url, params)
    _CACHE[key] = (time.time(), data)
    return data

def _base_symbol(ticker: str) -> str:
    return _normalize_ticker(ticker).replace("-USD", "")

# ----------------------------------------------------------------------
# 5. Derivatives data 
# ----------------------------------------------------------------------
def _binance_derivatives(base: str):
    for sym in (f"{base}USDT", f"1000{base}USDT"):
        try:
            prem = _get_json(f"{BINANCE_FAPI}/fapi/v1/premiumIndex", {"symbol": sym})
        except requests.HTTPError as e:
            if e.response is not None and e.response.status_code == 400:
                continue  
            raise  

        oi_now = _get_json(f"{BINANCE_FAPI}/fapi/v1/openInterest", {"symbol": sym})
        oi_hist = _get_json(f"{BINANCE_FAPI}/futures/data/openInterestHist",
                            {"symbol": sym, "period": "1d", "limit": 8})  
        funding = _get_json(f"{BINANCE_FAPI}/fapi/v1/fundingRate", {"symbol": sym, "limit": 50})
        try:
            ls = _get_json(f"{BINANCE_FAPI}/futures/data/globalLongShortAccountRatio",
                           {"symbol": sym, "period": "1h", "limit": 1})
            ls_ratio = float(ls[-1]["longShortRatio"]) if ls else None
        except Exception:
            ls_ratio = None

        return {
            "exchange": "Binance",
            "symbol": sym,
            "mark_price": float(prem["markPrice"]),
            "funding_rate": float(prem["lastFundingRate"]),
            "next_funding_time_ms": int(prem["nextFundingTime"]),
            "funding_history": sorted((int(f["fundingTime"]), float(f["fundingRate"])) for f in funding),
            "oi_contracts": float(oi_now["openInterest"]),
            "oi_contracts_7d_ago": float(oi_hist[0]["sumOpenInterest"]) if len(oi_hist) >= 2 else None,
            "long_short_ratio": ls_ratio,
        }
    return None

def _bybit_derivatives(base: str):
    for sym in (f"{base}USDT", f"1000{base}USDT"):
        t = _get_json(f"{BYBIT_API}/v5/market/tickers", {"category": "linear", "symbol": sym})
        items = (t.get("result") or {}).get("list") or []
        if t.get("retCode") != 0 or not items:
            continue
        tk = items[0]

        oi_hist = _get_json(f"{BYBIT_API}/v5/market/open-interest",
                            {"category": "linear", "symbol": sym, "intervalTime": "1d", "limit": 8})
        oi_list = oi_hist.get("result", {}).get("list", [])  
        funding = _get_json(f"{BYBIT_API}/v5/market/funding/history",
                            {"category": "linear", "symbol": sym, "limit": 50})
        f_list = funding.get("result", {}).get("list", [])
        try:
            ls = _get_json(f"{BYBIT_API}/v5/market/account-ratio",
                           {"category": "linear", "symbol": sym, "period": "1h", "limit": 1})
            row = ls["result"]["list"][0]
            ls_ratio = float(row["buyRatio"]) / float(row["sellRatio"])
        except Exception:
            ls_ratio = None

        return {
            "exchange": "Bybit",
            "symbol": sym,
            "mark_price": float(tk["markPrice"]),
            "funding_rate": float(tk["fundingRate"]),
            "next_funding_time_ms": int(tk["nextFundingTime"]),
            "funding_history": sorted((int(f["fundingRateTimestamp"]), float(f["fundingRate"])) for f in f_list),
            "oi_contracts": float(tk["openInterest"]),
            "oi_contracts_7d_ago": float(oi_list[-1]["openInterest"]) if len(oi_list) >= 2 else None,
            "long_short_ratio": ls_ratio,
        }
    return None

def get_derivatives_data(ticker: str) -> dict:
    base = _base_symbol(ticker)
    data, errors = None, []
    for fetcher in (_binance_derivatives, _bybit_derivatives):
        try:
            data = fetcher(base)
            if data:
                break
        except Exception as e:
            errors.append(f"{fetcher.__name__}: {e}")
    if not data:
        return {"error": f"No perpetual futures market found for {base}.",
                "ticker": base, "details": errors}

    try:
        hist = data["funding_history"]
        times = [t for t, _ in hist]
        diffs = pd.Series(times).diff().dropna()
        interval_h = round(diffs.median() / 3_600_000) if not diffs.empty else 8
        interval_h = interval_h or 8
        periods_per_day = 24 / interval_h

        rate = data["funding_rate"]
        cutoff = times[-1] - 7 * 86_400_000 if times else 0
        last_7d = [r for t, r in hist if t >= cutoff]
        avg_7d = sum(last_7d) / len(last_7d) if last_7d else None
        rate_8h = rate * 8 / interval_h  

        oi_usd = data["oi_contracts"] * data["mark_price"]
        oi_chg = _pct_change(data["oi_contracts"], data["oi_contracts_7d_ago"]) \
            if data["oi_contracts_7d_ago"] else None

        price_chg = None
        try:
            closes = _get_history(f"{base}-USD", period="10d")["Close"]
            # FIX: Check length before using .iloc[-8] to prevent IndexError
            if len(closes) >= 8:
                price_chg = _pct_change(float(closes.iloc[-1]), float(closes.iloc[-8]))
        except Exception:
            pass

        if rate_8h >= 0.0005:
            funding_signal = "Very high positive funding: longs are crowded and paying heavily. Elevated long-squeeze / liquidation-cascade risk on a dip."
        elif rate_8h > 0.0001:
            funding_signal = "Above the 0.01% baseline: bullish leverage is building."
        elif rate_8h >= 0:
            funding_signal = "Near the neutral 0.01% baseline: leverage is balanced."
        elif rate_8h > -0.0003:
            funding_signal = "Negative funding: shorts are paying longs, positioning leans bearish."
        else:
            funding_signal = "Deeply negative funding: shorts are crowded. Classic short-squeeze setup."

        oi_signal = None
        if oi_chg is not None and price_chg is not None:
            if oi_chg > 5 and price_chg > 0:
                oi_signal = "OI rising with price: new longs opening, rally is leverage-fueled."
            elif oi_chg > 5 and price_chg <= 0:
                oi_signal = "OI rising while price falls: new shorts piling in."
            elif oi_chg < -5 and price_chg > 0:
                oi_signal = "OI falling while price rises: short-covering rally."
            elif oi_chg < -5 and price_chg <= 0:
                oi_signal = "OI and price both falling: longs being liquidated / deleveraging."
            else:
                oi_signal = "OI roughly flat: no major change in leverage this week."

        if rate_8h < -0.0003 and (oi_chg or 0) > 5:
            short_squeeze = "high"
        elif rate_8h < 0:
            short_squeeze = "moderate"
        else:
            short_squeeze = "low"

        if rate_8h >= 0.0005 or (rate_8h > 0.0001 and (oi_chg or 0) > 10):
            long_squeeze = "high"
        elif rate_8h > 0.0001:
            long_squeeze = "moderate"
        else:
            long_squeeze = "low"

        return {
            "ticker": base,
            "exchange": data["exchange"],
            "contract": data["symbol"],
            "mark_price_usd": _safe_float(data["mark_price"]),
            "open_interest_usd": _safe_float(oi_usd, 0),
            "open_interest_change_7d_pct": oi_chg,
            "price_change_7d_pct": price_chg,
            "funding_rate_pct": round(rate * 100, 4),
            "funding_interval_hours": interval_h,
            "funding_rate_7d_avg_pct": round(avg_7d * 100, 4) if avg_7d is not None else None,
            "funding_annualized_pct": round(rate * periods_per_day * 365 * 100, 2),
            "next_funding_time_utc": pd.to_datetime(data["next_funding_time_ms"], unit="ms", utc=True)
                                       .strftime("%Y-%m-%d %H:%M"),
            "long_short_account_ratio": _safe_float(data["long_short_ratio"], 3),
            "funding_signal": funding_signal,
            "open_interest_signal": oi_signal,
            "short_squeeze_risk": short_squeeze,
            "long_squeeze_risk": long_squeeze,
            "note": "Data from a single exchange; aggregate OI across exchanges is larger.",
        }
    except Exception as e:
        return {"error": str(e), "ticker": base}

# ----------------------------------------------------------------------
# 6. On-chain metrics (Unchanged - Perfect)
# ----------------------------------------------------------------------
def _btc_activity() -> dict:
    out = {}
    for chart, key in (("n-unique-addresses", "active_addresses"),
                       ("n-transactions", "daily_transactions")):
        d = _get_json(f"{BLOCKCHAIN_INFO}/{chart}",
                      {"timespan": "60days", "format": "json", "sampled": "false"})
        s = pd.Series([v["y"] for v in d["values"]])
        recent = s.tail(7).mean()
        prior = s.iloc[-37:-30].mean() if len(s) >= 37 else None
        out[f"{key}_7d_avg"] = _safe_float(recent, 0)
        out[f"{key}_change_vs_30d_ago_pct"] = _pct_change(recent, prior) if prior else None
    out["source"] = "blockchain.com"
    return out

def _blockchair_activity(chain: str) -> dict:
    d = _get_json(f"{BLOCKCHAIR_API}/{chain}/stats").get("data", {})
    return {
        "daily_transactions_24h": d.get("transactions_24h"),
        "addresses_with_balance": d.get("hodling_addresses"),
        "avg_tx_fee_usd_24h": _safe_float(d.get("average_transaction_fee_usd_24h")),
        "source": "blockchair.com",
    }

def _llama_overview(kind: str, chain: str, data_type: str = None) -> dict:
    params = {"excludeTotalDataChart": "true", "excludeTotalDataChartBreakdown": "true"}
    if data_type:
        params["dataType"] = data_type
    d = _get_json(f"{LLAMA_API}/overview/{kind}/{quote(chain)}", params)
    return {
        "total_24h_usd": _safe_float(d.get("total24h"), 0),
        "total_7d_usd": _safe_float(d.get("total7d"), 0),
        "total_30d_usd": _safe_float(d.get("total30d"), 0),
        "change_1d_pct": _safe_float(d.get("change_1d"), 2),
        "change_7d_pct": _safe_float(d.get("change_7d"), 2),
        "change_30d_pct": _safe_float(d.get("change_1m"), 2),
    }

def get_onchain_metrics(ticker: str) -> dict:
    base = _base_symbol(ticker)
    result = {"ticker": base, "type": None}
    growth_signals = []

    try:
        chains = _cached_json(f"{LLAMA_API}/v2/chains")
        matches = [c for c in chains if (c.get("tokenSymbol") or "").upper() == base]
        chain = max(matches, key=lambda c: c.get("tvl") or 0) if matches else None

        if chain:
            name = chain["name"]
            result.update({"type": "blockchain", "chain_name": name,
                           "tvl_usd": _safe_float(chain.get("tvl"), 0)})
            try:
                hist = _get_json(f"{LLAMA_API}/v2/historicalChainTvl/{quote(name)}")
                tvl = pd.Series([h["tvl"] for h in hist])
                if len(tvl) > 31:
                    chg = _pct_change(float(tvl.iloc[-1]), float(tvl.iloc[-31]))
                    result["tvl_change_30d_pct"] = chg
                    growth_signals.append(chg)
            except Exception as e:
                result["tvl_history_error"] = str(e)
            for kind, key, dtype in (("dexs", "dex_volume", None), ("fees", "network_fees", "dailyFees")):
                try:
                    result[key] = _llama_overview(kind, name, dtype)
                except Exception:
                    result[key] = None
            try:
                stables = _cached_json(f"{STABLES_API}/stablecoinchains")
                row = next((s for s in stables if s.get("name") == name), None)
                if row:
                    result["stablecoin_supply_usd"] = _safe_float(
                        (row.get("totalCirculatingUSD") or {}).get("peggedUSD"), 0)
            except Exception:
                pass

        else:
            protocols = _cached_json(f"{LLAMA_API}/protocols")
            p_matches = [p for p in protocols if (p.get("symbol") or "").upper() == base]
            proto = max(p_matches, key=lambda p: p.get("tvl") or 0) if p_matches else None
            if proto:
                tvl, mcap = proto.get("tvl"), proto.get("mcap")
                result.update({
                    "type": "defi_protocol",
                    "protocol_name": proto.get("name"),
                    "category": proto.get("category"),
                    "chains": (proto.get("chains") or [])[:10],
                    "tvl_usd": _safe_float(tvl, 0),
                    "tvl_change_1d_pct": _safe_float(proto.get("change_1d"), 2),
                    "tvl_change_7d_pct": _safe_float(proto.get("change_7d"), 2),
                    "mcap_to_tvl_ratio": round(mcap / tvl, 2) if mcap and tvl else None,
                })
                if proto.get("change_7d") is not None:
                    growth_signals.append(proto["change_7d"])
                try:
                    f = _get_json(f"{LLAMA_API}/summary/fees/{proto['slug']}", {"dataType": "dailyFees"})
                    result["fees_24h_usd"] = _safe_float(f.get("total24h"), 0)
                    result["fees_30d_usd"] = _safe_float(f.get("total30d"), 0)
                except Exception:
                    pass

        try:
            if base == "BTC":
                result["type"] = result["type"] or "blockchain"
                result["network_activity"] = _btc_activity()
                chg = result["network_activity"].get("active_addresses_change_vs_30d_ago_pct")
                if chg is not None:
                    growth_signals.append(chg)
            elif base in BLOCKCHAIR_CHAINS:
                result["network_activity"] = _blockchair_activity(BLOCKCHAIR_CHAINS[base])
        except Exception as e:
            result["network_activity_error"] = str(e)

        if result["type"] is None and "network_activity" not in result:
            return {"ticker": base, "error": f"No on-chain or DeFi data found for {base}."}

        if growth_signals:
            avg = sum(growth_signals) / len(growth_signals)
            result["usage_trend"] = ("growing" if avg > 5 else
                                     "declining" if avg < -5 else "stable")
        else:
            result["usage_trend"] = "insufficient data"
        result["note"] = ("TVL is priced in USD, so it partly rises/falls with token prices. "
                          "Compare with price change to judge real usage growth.")
        return result
    except Exception as e:
        return {"error": str(e), "ticker": base}

# ----------------------------------------------------------------------
# 7. Support / resistance
# ----------------------------------------------------------------------
def get_support_resistance_levels(ticker: str, lookback_days: int = 90) -> dict:
    try:
        symbol = _normalize_ticker(ticker)
        lookback_days = max(int(lookback_days), 14)
        df = _get_history(symbol, period=f"{lookback_days + 10}d")
        
        # FIX: Guard clause for newly listed tokens with insufficient data
        if len(df) < 2:
            return {"error": "Not enough historical data to calculate support/resistance.", "ticker": symbol}
            
        current = float(df["Close"].iloc[-1])
        completed = df.iloc[:-1]  

        def _pivots(h, l, c):
            p = (h + l + c) / 3
            return {
                "R3": h + 2 * (p - l), "R2": p + (h - l), "R1": 2 * p - l,
                "P": p,
                "S1": 2 * p - h, "S2": p - (h - l), "S3": l - 2 * (h - p),
            }

        y = completed.iloc[-1]
        daily = _pivots(float(y["High"]), float(y["Low"]), float(y["Close"]))
        w = completed.tail(7)
        weekly = _pivots(float(w["High"].max()), float(w["Low"].min()), float(w["Close"].iloc[-1]))

        win = completed.tail(lookback_days)
        hi, lo = float(win["High"].max()), float(win["Low"].min())
        hi_date, lo_date = win["High"].idxmax(), win["Low"].idxmin()
        rng = hi - lo
        uptrend = hi_date > lo_date  

        fib = {}
        for r in (0.236, 0.382, 0.5, 0.618, 0.786):
            fib[f"retracement_{r}"] = hi - r * rng if uptrend else lo + r * rng
        for r in (1.272, 1.618):
            fib[f"extension_{r}"] = lo + r * rng if uptrend else hi - r * rng

        levels = [(f"daily_{k}", v) for k, v in daily.items()] + \
                 [(f"weekly_{k}", v) for k, v in weekly.items()] + \
                 [(f"fib_{k}", v) for k, v in fib.items()] + \
                 [("swing_high", hi), ("swing_low", lo)]

        def _fmt(name, price):
            return {"level": name, "price": _safe_float(price),
                    "distance_pct": _pct_change(price, current)}

        supports = sorted([l for l in levels if l[1] < current], key=lambda x: -x[1])[:4]
        resistances = sorted([l for l in levels if l[1] > current], key=lambda x: x[1])[:4]

        return {
            "ticker": symbol,
            "current_price_usd": _safe_float(current),
            "nearest_supports": [_fmt(*s) for s in supports],
            "nearest_resistances": [_fmt(*r) for r in resistances],
            "daily_pivots": {k: _safe_float(v) for k, v in daily.items()},
            "weekly_pivots": {k: _safe_float(v) for k, v in weekly.items()},
            "fibonacci": {
                "swing_high": _safe_float(hi), "swing_high_date": hi_date.strftime("%Y-%m-%d"),
                "swing_low": _safe_float(lo), "swing_low_date": lo_date.strftime("%Y-%m-%d"),
                "swing_direction": "up (measuring pullback from high)" if uptrend
                                   else "down (measuring bounce from low)",
                "levels": {k: _safe_float(v) for k, v in fib.items()},
            },
            "note": "Levels where several methods cluster close together are the strongest.",
        }
    except Exception as e:
        return {"error": str(e), "ticker": ticker}

# ----------------------------------------------------------------------
# 8. Asset correlation 
# ----------------------------------------------------------------------
def _resolve_candidates(t: str) -> list:
    key = t.strip().upper()
    if key in BENCHMARK_ALIASES:
        return [BENCHMARK_ALIASES[key]]
    if key.startswith("^") or "=" in key or "-" in key:
        return [key]
    return [_normalize_ticker(key), key]  

def _load_closes(t: str, days: int):
    last_err = None
    for sym in _resolve_candidates(t):
        try:
            s = _get_history(sym, period=f"{days + 15}d")["Close"].copy()
            s.index = pd.to_datetime(s.index.date)  
            return sym, s[~s.index.duplicated(keep="last")]
        except Exception as e:
            last_err = e
    raise ValueError(f"No data for '{t}': {last_err}")

def get_asset_correlation(ticker: str, benchmark_ticker: str = "BTC", days: int = 90) -> dict:
    try:
        days = max(int(days), 30)
        a_sym, a = _load_closes(ticker, days)
        b_sym, b = _load_closes(benchmark_ticker, days)

        df = pd.concat([a.rename("asset"), b.rename("bench")], axis=1, join="inner").dropna()
        df = df[df.index >= df.index[-1] - pd.Timedelta(days=days)]
        rets = df.pct_change().dropna()
        if len(rets) < 20:
            return {"error": "Not enough overlapping data points to compute correlation.",
                    "ticker": a_sym, "benchmark": b_sym}

        # FIX: Guard against ZeroDivisionError and NaN JSON serialization
        bench_var = rets["bench"].var()
        if bench_var == 0 or pd.isna(bench_var):
            beta = None
        else:
            beta = _safe_float(rets["asset"].cov(rets["bench"]) / bench_var, 2)
            
        corr = _safe_float(rets["asset"].corr(rets["bench"]), 3)
        corr_30 = _safe_float(rets.tail(30)["asset"].corr(rets.tail(30)["bench"]), 3) if len(rets) >= 30 else None

        worst = rets.nsmallest(5, "bench")
        down_days = rets[rets["bench"] < 0]

        abs_c = abs(corr) if corr is not None else 0
        strength = ("very strong" if abs_c >= 0.8 else "strong" if abs_c >= 0.6 else
                    "moderate" if abs_c >= 0.4 else "weak" if abs_c >= 0.2 else "little to no")
        direction = "positive" if (corr or 0) > 0 else "negative"

        return {
            "ticker": a_sym,
            "benchmark": b_sym,
            "period_days": days,
            "data_points": len(rets),
            "correlation": corr,
            "correlation_last_30_points": corr_30,
            "beta": beta,
            "interpretation": f"{strength} {direction} correlation",
            "beta_meaning": f"When {b_sym} moves 1%, {a_sym} has moved about {beta}% on average." if beta is not None else "Cannot calculate beta.",
            "avg_asset_move_on_benchmark_down_days_pct": round(down_days["asset"].mean() * 100, 2)
                                                        if not down_days.empty else None,
            "avg_asset_move_on_benchmark_5_worst_days_pct": round(worst["asset"].mean() * 100, 2),
            "benchmark_5_worst_days_avg_pct": round(worst["bench"].mean() * 100, 2),
            "asset_period_return_pct": _pct_change(float(df["asset"].iloc[-1]), float(df["asset"].iloc[0])),
            "benchmark_period_return_pct": _pct_change(float(df["bench"].iloc[-1]), float(df["bench"].iloc[0])),
            "note": "Correlation uses daily returns, not raw prices (price correlation is misleading for trending assets).",
        }
    except Exception as e:
        return {"error": str(e), "ticker": ticker, "benchmark": benchmark_ticker}


CRYPTO_TOOLS = [
    get_technical_indicators,
    get_market_sentiment,
    get_fundamental_data,
    get_historical_performance,
]

ADVANCED_CRYPTO_TOOLS = [
    get_derivatives_data,
    get_onchain_metrics,
    get_support_resistance_levels,
    get_asset_correlation,
]