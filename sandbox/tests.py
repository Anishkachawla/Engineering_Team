import unittest
from backend import TradingAccount

class TestTradingAccount(unittest.TestCase):
    def setUp(self):
        self.account = TradingAccount()

    def test_deposit_withdrawal(self):
        self.assertTrue(self.account.deposit(1000))
        self.assertEqual(self.account.balance, 1000)
        self.assertTrue(self.account.withdraw(500))
        self.assertEqual(self.account.balance, 500)
        self.assertFalse(self.account.withdraw(600))
        self.assertEqual(self.account.balance, 500)
        self.assertFalse(self.account.deposit(-100))
        self.assertEqual(self.account.balance, 500)

    def test_insufficient_funds_buy(self):
        self.account.deposit(100)
        # AAPL is 150, cannot buy
        self.assertFalse(self.account.execute_trade("AAPL", 1, True))
        self.assertEqual(self.account.balance, 100)

    def test_insufficient_shares_sell(self):
        self.account.deposit(1000)
        self.account.execute_trade("AAPL", 1, True)
        # Own 1, try to sell 2
        self.assertFalse(self.account.execute_trade("AAPL", 2, False))

    def test_pnl_logic(self):
        self.account.deposit(1000)
        self.account.execute_trade("AAPL", 1, True)
        # Portfolio: 850 cash + 150 (AAPL) = 1000 value. PnL = 0
        self.assertEqual(self.account.get_pnl(), 0)
        
        self.account.execute_trade("AAPL", 1, False)
        # Portfolio: 1000 cash = 1000 value. PnL = 0
        self.assertEqual(self.account.get_pnl(), 0)

    def test_holdings_summary(self):
        self.account.deposit(1000)
        self.account.execute_trade("AAPL", 2, True)
        summary = self.account.get_holdings_summary()
        self.assertEqual(len(summary), 1)
        self.assertEqual(summary[0]["symbol"], "AAPL")
        self.assertEqual(summary[0]["quantity"], 2)

    def test_transactions(self):
        self.account.deposit(1000)
        self.assertEqual(len(self.account.transactions), 1)
        self.assertEqual(self.account.transactions[0]["type"], "DEPOSIT")
        self.assertEqual(self.account.transactions[0]["total"], 1000)

if __name__ == '__main__':
    unittest.main()
