import gradio as gr
from logic import AccountManager

# Define CSS for professional theme
css = """
body { background-color: #f9f9f9; }
.gradio-container { border-radius: 8px !important; }
#status-display { font-size: 1.2em; font-weight: bold; color: #209dd7; }
"""

def ui_deposit(manager, amount):
    if amount is None or amount <= 0:
        return "Please enter a valid amount.", manager
    if manager.deposit(amount):
        return f"Deposited ${amount:.2f}", manager
    return "Deposit failed.", manager

def ui_withdraw(manager, amount):
    if amount is None or amount <= 0:
        return "Please enter a valid amount.", manager
    if manager.withdraw(amount):
        return f"Withdrew ${amount:.2f}", manager
    return "Withdrawal failed (insufficient funds).", manager

def ui_trade(manager, symbol, quantity, trade_type):
    if quantity is None or quantity <= 0:
        return "Invalid quantity.", manager
    is_buy = (trade_type == "BUY")
    if manager.record_trade(symbol, int(quantity), is_buy):
        return f"Trade executed: {trade_type} {int(quantity)} {symbol}", manager
    return "Trade failed (check funds/holdings).", manager

def refresh_ui(manager):
    holdings = manager.get_holdings()
    holdings_list = [[s, q] for s, q in holdings.items()]
    transactions = manager.get_transactions()
    trans_list = [[t.get("type"), t.get("symbol", "N/A"), t.get("quantity", "N/A"), 
                   t.get("price", "N/A"), t.get("total", "N/A"), t.get("amount", "N/A")] for t in transactions]
    
    status = f"Balance: ${manager.balance:.2f} | Portfolio Value: ${manager.get_portfolio_value():.2f} | P/L: ${manager.get_profit_loss():.2f}"
    return status, holdings_list, trans_list

with gr.Blocks(css=css, theme=gr.themes.Soft()) as demo:
    manager_state = gr.State(AccountManager())
    
    gr.Markdown("# Trading Simulation Dashboard")
    status_display = gr.Markdown("Status: Initialized", elem_id="status-display")
    
    with gr.Tab("Account Operations"):
        with gr.Row():
            deposit_input = gr.Number(label="Amount ($)", scale=2)
            deposit_btn = gr.Button("Deposit", variant="primary")
            withdraw_input = gr.Number(label="Amount ($)", scale=2)
            withdraw_btn = gr.Button("Withdraw", variant="secondary")
        
    with gr.Tab("Market Trading"):
        with gr.Row():
            symbol_input = gr.Dropdown(["AAPL", "TSLA", "GOOGL"], label="Symbol")
            qty_input = gr.Number(label="Quantity", value=1)
            type_input = gr.Dropdown(["BUY", "SELL"], label="Action", value="BUY")
            trade_btn = gr.Button("Execute Trade", variant="primary")
        
    with gr.Row():
        holdings_table = gr.Dataframe(headers=["Symbol", "Quantity"], label="Current Holdings", interactive=False)
        transactions_table = gr.Dataframe(headers=["Type", "Symbol", "Qty", "Price", "Total", "Amount"], label="Transaction History", interactive=False)

    msg_display = gr.Markdown("")

    def update_all(manager):
        status, holdings, trans = refresh_ui(manager)
        return status, holdings, trans, manager

    deposit_btn.click(ui_deposit, [manager_state, deposit_input], [msg_display, manager_state]) \
               .then(update_all, [manager_state], [status_display, holdings_table, transactions_table, manager_state])
               
    withdraw_btn.click(ui_withdraw, [manager_state, withdraw_input], [msg_display, manager_state]) \
                .then(update_all, [manager_state], [status_display, holdings_table, transactions_table, manager_state])

    trade_btn.click(ui_trade, [manager_state, symbol_input, qty_input, type_input], [msg_display, manager_state]) \
             .then(update_all, [manager_state], [status_display, holdings_table, transactions_table, manager_state])
