import datetime

def get_share_price(symbol: str) -> float:
    """Mock implementation: returns fixed prices for AAPL, TSLA, GOOGL."""
    prices = {
        "AAPL": 150.0,
        "TSLA": 700.0,
        "GOOGL": 2800.0
    }
    return prices.get(symbol, 0.0)

class TradingAccount:
    def __init__(self):
        self.balance: float = 0.0
        self.holdings: dict[str, int] = {}
        self.transactions: list[dict] = []
        self.total_deposited: float = 0.0

    def deposit(self, amount: float) -> bool:
        """Adds funds to the account."""
        if amount <= 0:
            return False
        self.balance += amount
        self.total_deposited += amount
        self._record_transaction("DEPOSIT", None, 0, amount)
        return True

    def withdraw(self, amount: float) -> bool:
        """Removes funds. Prevents negative balance."""
        if amount <= 0 or amount > self.balance:
            return False
        self.balance -= amount
        self._record_transaction("WITHDRAW", None, 0, amount)
        return True

    def execute_trade(self, symbol: str, quantity: int, is_buy: bool) -> bool:
        """
        Validates and records a trade. 
        Checks for sufficient funds (buy) or inventory (sell).
        """
        price = get_share_price(symbol)
        if price == 0 or quantity <= 0:
            return False

        cost = price * quantity

        if is_buy:
            if cost > self.balance:
                return False
            self.balance -= cost
            self.holdings[symbol] = self.holdings.get(symbol, 0) + quantity
            self._record_transaction("BUY", symbol, quantity, price)
            return True
        else:
            if self.holdings.get(symbol, 0) < quantity:
                return False
            self.balance += cost
            self.holdings[symbol] -= quantity
            if self.holdings[symbol] == 0:
                del self.holdings[symbol]
            self._record_transaction("SELL", symbol, quantity, price)
            return True

    def _record_transaction(self, t_type: str, symbol: str | None, quantity: int, price: float):
        self.transactions.append({
            "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "type": t_type,
            "symbol": symbol,
            "quantity": quantity,
            "price": price,
            "total": quantity * price if symbol else price
        })

    def get_portfolio_value(self) -> float:
        """Calculates total cash + (holdings * current price)."""
        value = self.balance
        for symbol, qty in self.holdings.items():
            value += qty * get_share_price(symbol)
        return value

    def get_pnl(self) -> float:
        """Calculates profit/loss relative to total deposits."""
        return self.get_portfolio_value() - self.total_deposited

    def get_holdings_summary(self) -> list[dict]:
        """Returns list of current shares owned."""
        return [{"symbol": s, "quantity": q} for s, q in self.holdings.items()]
