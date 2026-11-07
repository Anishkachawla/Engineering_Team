from data import get_share_price

class AccountManager:
    def __init__(self):
        self.balance = 0.0
        self.holdings = {}  # {symbol: quantity}
        self.transactions = []
        self.total_deposits = 0.0

    def deposit(self, amount: float) -> bool:
        if amount <= 0:
            return False
        self.balance += amount
        self.total_deposits += amount
        self.transactions.append({"type": "DEPOSIT", "amount": amount})
        return True

    def withdraw(self, amount: float) -> bool:
        if amount <= 0 or amount > self.balance:
            return False
        self.balance -= amount
        self.transactions.append({"type": "WITHDRAW", "amount": amount})
        return True

    def record_trade(self, symbol: str, quantity: int, is_buy: bool) -> bool:
        if quantity <= 0:
            return False
        
        try:
            price = get_share_price(symbol)
        except ValueError:
            return False

        cost = price * quantity

        if is_buy:
            if self.balance < cost:
                return False
            self.balance -= cost
            self.holdings[symbol] = self.holdings.get(symbol, 0) + quantity
        else:
            current_holdings = self.holdings.get(symbol, 0)
            if current_holdings < quantity:
                return False
            self.balance += cost
            self.holdings[symbol] = current_holdings - quantity
            if self.holdings[symbol] == 0:
                del self.holdings[symbol]

        self.transactions.append({
            "type": "BUY" if is_buy else "SELL",
            "symbol": symbol,
            "quantity": quantity,
            "price": price,
            "total": cost
        })
        return True

    def get_portfolio_value(self) -> float:
        total = 0.0
        for symbol, quantity in self.holdings.items():
            total += get_share_price(symbol) * quantity
        return total

    def get_holdings(self) -> dict:
        return self.holdings.copy()

    def get_profit_loss(self) -> float:
        current_equity = self.balance + self.get_portfolio_value()
        return current_equity - self.total_deposits

    def get_transactions(self) -> list[dict]:
        return list(self.transactions)
