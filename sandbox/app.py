import gradio as gr
from backend import TradingAccount

def create_ui():
    # CSS to support custom theme colors in both modes
    custom_css = """
    .gradio-container {background-color: #f9f9f9;}
    .dark .gradio-container {background-color: #121212;}
    .primary-btn {background-color: #ecad0a !important; color: white !important;}
    .secondary-btn {background-color: #209dd7 !important; color: white !important;}
    .accent-btn {background-color: #753991 !important; color: white !important;}
    """
    
    with gr.Blocks(css=custom_css) as demo:
        state = gr.State(TradingAccount())
        
        gr.Markdown("# Trading Simulation")
        
        with gr.Row():
            balance_display = gr.Number(label="Cash Balance", interactive=False)
            portfolio_value = gr.Number(label="Total Portfolio Value", interactive=False)
            pnl_display = gr.Number(label="PnL", interactive=False)
        
        with gr.Row():
            with gr.Column(variant="panel"):
                gr.Markdown("### Cash Operations")
                amount_input = gr.Number(label="Amount", value=0)
                with gr.Row():
                    deposit_btn = gr.Button("Deposit", elem_classes="secondary-btn")
                    withdraw_btn = gr.Button("Withdraw", elem_classes="accent-btn")
            with gr.Column(variant="panel"):
                gr.Markdown("### Trade Operations")
                symbol_input = gr.Dropdown(["AAPL", "TSLA", "GOOGL"], label="Symbol")
                qty_input = gr.Number(label="Quantity", value=1, step=1)
                with gr.Row():
                    buy_btn = gr.Button("Buy", elem_classes="primary-btn")
                    sell_btn = gr.Button("Sell", elem_classes="primary-btn")
        
        holdings_table = gr.Dataframe(label="Current Holdings", headers=["symbol", "quantity"], interactive=False)
        transactions_table = gr.Dataframe(label="Transaction History", headers=["timestamp", "type", "symbol", "quantity", "price", "total"], interactive=False)

        def update_ui(account):
            holdings = [[h['symbol'], h['quantity']] for h in account.get_holdings_summary()]
            transactions = [[t['timestamp'], t['type'], t['symbol'], t['quantity'], t['price'], t['total']] for t in account.transactions]
            return (
                account.balance,
                account.get_portfolio_value(),
                account.get_pnl(),
                holdings,
                transactions
            )

        def deposit(account, amount):
            account.deposit(float(amount))
            return (account, *update_ui(account))

        def withdraw(account, amount):
            account.withdraw(float(amount))
            return (account, *update_ui(account))
        
        def buy(account, symbol, qty):
            account.execute_trade(symbol, int(qty), True)
            return (account, *update_ui(account))
            
        def sell(account, symbol, qty):
            account.execute_trade(symbol, int(qty), False)
            return (account, *update_ui(account))

        deposit_btn.click(deposit, [state, amount_input], [state, balance_display, portfolio_value, pnl_display, holdings_table, transactions_table])
        withdraw_btn.click(withdraw, [state, amount_input], [state, balance_display, portfolio_value, pnl_display, holdings_table, transactions_table])
        buy_btn.click(buy, [state, symbol_input, qty_input], [state, balance_display, portfolio_value, pnl_display, holdings_table, transactions_table])
        sell_btn.click(sell, [state, symbol_input, qty_input], [state, balance_display, portfolio_value, pnl_display, holdings_table, transactions_table])

    return demo

if __name__ == "__main__":
    demo = create_ui()
    demo.launch()
