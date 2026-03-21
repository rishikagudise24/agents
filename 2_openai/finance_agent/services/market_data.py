import yfinance as yf
import pandas as pd


def get_stock_data(ticker: str):
    stock = yf.Ticker(ticker)
    df = stock.history(period="1y")

    return df


def compute_basic_metrics(df: pd.DataFrame):
    df["returns"] = df["Close"].pct_change()

    avg_return = df["returns"].mean()
    volatility = df["returns"].std() * (252 ** 0.5)  # annualized

    recent_price = df["Close"].iloc[-1]
    price_1y_ago = df["Close"].iloc[0]

    total_return = (recent_price / price_1y_ago) - 1

    return {
        "recent_price": round(recent_price, 2),
        "annual_return_pct": round(total_return * 100, 2),
        "volatility_pct": round(volatility * 100, 2),
    }


def get_market_summary(ticker: str):
    df = get_stock_data(ticker)
    metrics = compute_basic_metrics(df)

    return metrics