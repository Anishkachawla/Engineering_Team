def get_share_price(symbol: str) -> float:
    prices = {
        "AAPL": 150.0,
        "TSLA": 200.0,
        "GOOGL": 250.0
    }
    if symbol in prices:
        return prices[symbol]
    raise ValueError(f"Unknown symbol: {symbol}")
