# System Design: Trading Simulation Account Management

## Overview
This system provides an account management layer for a trading simulation. It tracks cash balances, stock holdings, and transactional history, ensuring all trades are validated against available funds and inventory.

## Project Structure
All files reside in the root directory:
- `backend.py`: Logic for account management, transaction processing, and portfolio valuation.
- `app.py`: Gradio 6 web interface.
- `tests.py`: Unit tests for the backend logic.

---

## 1. Backend Design (`backend.py`)
**Owner: `backend_engineer`**

This module handles the core business logic.

### Data Structures
- **Account Class**: Stores `balance` (float) and `holdings` (dict: `{symbol: quantity}`).
- **Transaction Class**: Represents a trade (type: BUY/SELL/DEPOSIT/WITHDRAW, symbol, quantity, price, timestamp).

### API / Function Signatures
```python
def get_share_price(symbol: str) -> float:
    """Mock implementation: returns fixed prices for AAPL, TSLA, GOOGL."""
    pass

class TradingAccount:
    def __init__(self):
        self.balance: float = 0.0
        self.holdings: dict[str, int] = {}
        self.transactions: list[dict] = []

    def deposit(self, amount: float) -> bool:
        """Adds funds to the account."""
        pass

    def withdraw(self, amount: float) -> bool:
        """Removes funds. Prevents negative balance."""
        pass

    def execute_trade(self, symbol: str, quantity: int, is_buy: bool) -> bool:
        """
        Validates and records a trade. 
        Checks for sufficient funds (buy) or inventory (sell).
        """
        pass

    def get_portfolio_value(self) -> float:
        """Calculates total cash + (holdings * current price)."""
        pass

    def get_pnl(self) -> float:
        """Calculates profit/loss relative to total deposits."""
        pass

    def get_holdings_summary(self) -> list[dict]:
        """Returns list of current shares owned."""
        pass
```

---

## 2. Frontend Design (`app.py`)
**Owner: `frontend_engineer`**

This module implements the UI using **Gradio 6**.

### Gradio 6 Implementation Notes:
- Use the `gr.Blocks()` context manager for layout.
- **State Management**: Use `gr.State()` to persist the `TradingAccount` object across interaction cycles.
- **Event Handling**: Use `component.on("click", ...)` or `component.on("change", ...)` syntax.
- **Outputs**: Ensure output components (e.g., `gr.Dataframe` for transaction history) are updated by returning values in the event listener functions.

### Key Components:
- `gr.Number` for inputting deposit/withdraw/trade amounts.
- `gr.Dropdown` for symbol selection.
- `gr.Dataframe` for displaying transactions and holdings.
- `gr.Markdown` for status updates (Total Value, PnL).

---

## 3. Testing Design (`tests.py`)
**Owner: `test_engineer`**

Using standard `unittest` framework to validate `backend.py`.

### Test Cases:
- `test_deposit_withdrawal`: Verify balance updates and negative balance prevention.
- `test_buy_limit`: Ensure users cannot buy without sufficient funds.
- `test_sell_limit`: Ensure users cannot sell shares they don't own.
- `test_pnl_calculation`: Verify math against known mock prices.

```python
import unittest
from backend import TradingAccount

class TestTradingAccount(unittest.TestCase):
    def test_insufficient_funds_buy(self): ...
    def test_insufficient_shares_sell(self): ...
    def test_pnl_logic(self): ...
```

---

## Task Assignments

| Engineer | Primary Task | Responsibilities |
| :--- | :--- | :--- |
| **Backend** | `backend.py` | Implement `TradingAccount` class, transaction validation logic, and ensure state persistence. |
| **Frontend** | `app.py` | Build Gradio 6 UI, connect state, manage layouts, and integrate `backend.py` methods as event callbacks. |
| **Test** | `tests.py` | Write comprehensive unit tests covering edge cases (negative balance, overdraft trades) and core business math. |

**Note to Engineers**: Ensure all imports are absolute. Since all files are in the same directory, `from backend import TradingAccount` will work directly in `app.py` and `tests.py`.