import unittest
from logic import AccountManager

class TestAccountManager(unittest.TestCase):
    def setUp(self):
        self.manager = AccountManager()

    def test_deposit_withdraw(self):
        self.assertTrue(self.manager.deposit(1000.0))
        self.assertEqual(self.manager.balance, 1000.0)
        self.assertTrue(self.manager.withdraw(500.0))
        self.assertEqual(self.manager.balance, 500.0)
        self.assertFalse(self.manager.withdraw(1000.0))

    def test_insufficient_funds_buy(self):
        self.manager.deposit(100.0)
        # AAPL is 150.0
        self.assertFalse(self.manager.record_trade("AAPL", 1, True))
        self.assertEqual(self.manager.balance, 100.0)

    def test_sell_without_holdings(self):
        self.manager.deposit(1000.0)
        self.assertFalse(self.manager.record_trade("AAPL", 1, False))

    def test_portfolio_calculation(self):
        self.manager.deposit(1000.0)
        self.manager.record_trade("AAPL", 2, True)  # 2 * 150 = 300
        # Balance: 700, Holdings: AAPL: 2
        self.assertEqual(self.manager.get_portfolio_value(), 300.0)
        self.assertEqual(self.manager.balance, 700.0)
        
        # P/L = (700 + 300) - 1000 = 0
        self.assertEqual(self.manager.get_profit_loss(), 0.0)

if __name__ == '__main__':
    unittest.main()
