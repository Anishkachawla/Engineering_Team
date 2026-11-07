# Design Document: Trading Simulation Account Management System

## Overview
A backend-driven trading simulation account management system. It provides user balance tracking, trade recording, portfolio valuation, and historical transaction reporting.

## Module Structure (Single Directory)
All files reside in the root directory of a `uv` project.
*   `logic.py`: Core domain logic and data structures.
*   `app.py`: Gradio 6 frontend implementation.
*   `tests.py`: Unit tests for `logic.py`.
*   `data.py`: Mock implementation of `get_share_price`.

---

## 1. Backend Module (`logic.py`)
Responsible for managing user state, validation, and calculations.

### Class: `AccountManager`
*   `__init__(self)`: Initializes empty state (balance=0, holdings={}, transactions=[]).
*   `deposit(self, amount: float) -> bool`: Adds funds; returns True if successful.
*   `withdraw(self, amount: float) -> bool`: Withdraws funds if balance permits; returns True if successful.
*   `record_trade(self, symbol: str, quantity: int, price: float, is_buy: bool) -> bool`: Records a trade, updates holdings and balance; returns True if successful, False if validation fails (e.g., insufficient funds or holdings).
*   `get_portfolio_value(self) -> float`: Calculates current market value of all shares.
*   `get_holdings(self) -> dict`: Returns mapping of {symbol: quantity}.
*   `get_profit_loss(self) -> float`: Returns (Current Balance + Portfolio Value) - Total Deposits.
*   `get_transactions(self) -> list[dict]`: Returns a chronological list of all trade records.

---

## 2. Frontend Module (`app.py`)
Uses Gradio 6.x to provide the user interface.

**Gradio 6 Implementation Guidelines:**
*   **Blocks Configuration:** App-level settings (theme, css) must be passed to `demo.launch()`, not `gr.Blocks()`.
*   **Components:** Use `gr.Number`, `gr.Dropdown`, `gr.Dataframe`, and `gr.Button`. Ensure labels are explicit.
*   **Event Handling:** Bind functions using `.click()` or `.submit()` on components. Use `gr.State()` to persist the `AccountManager` instance across interactions.

**Functions:**
*   `ui_deposit(manager, amount)`
*   `ui_withdraw(manager, amount)`
*   `ui_trade(manager, symbol, quantity, is_buy)`
*   `refresh_ui(manager)`: Returns updated status, portfolio table, and transaction history.

---

## 3. Mock Data Module (`data.py`)
*   `get_share_price(symbol: str) -> float`: Returns static price (AAPL: 150.0, TSLA: 200.0, GOOGL: 250.0) or raises `ValueError` for unknown symbols.

---

## 4. Test Module (`tests.py`)
*   `test_deposit_withdraw()`
*   `test_insufficient_funds_buy()`
*   `test_sell_without_holdings()`
*   `test_portfolio_calculation()`

---

## Engineer Assignments

### `backend_engineer`
*   **File:** `logic.py`, `data.py`
*   **Task:** Implement `AccountManager` class and validation logic. Implement `get_share_price`.
*   **Signatures:**
    *   `logic.py`: `AccountManager.deposit(amount: float) -> bool`, `AccountManager.withdraw(amount: float) -> bool`, `AccountManager.record_trade(symbol, quantity, is_buy) -> bool`, `AccountManager.get_portfolio_value() -> float`.

### `frontend_engineer`
*   **File:** `app.py`
*   **Task:** Implement Gradio UI.
*   **Requirement:** Integrate with `AccountManager`. Use `gr.Blocks`. Handle events and update components.
*   **Gradio 6 Note:** Ensure `theme` and `css` are provided to `launch()` and not the constructor.

### `test_engineer`
*   **File:** `tests.py`
*   **Task:** Implement unit tests using standard `unittest` framework to verify `logic.py` meets the requirements.
*   **Requirement:** Must cover edge cases (e.g., balance becoming zero, buying more than affordable, selling non-existent shares).