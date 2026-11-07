import unittest
from logic import AccountManager

class TestAccountManager(unittest.TestCase):
    def setUp(self):
        self.manager = AccountManager()

    def test_deposit_withdraw(self):
        # Valid deposit
        self.assertTrue(self.manager.deposit(1000.0))
        self.assertEqual(self.manager.balance, 1000.0)
        # Valid withdraw
        self.assertTrue(self.manager.withdraw(500.0))
        self.assertEqual(self.manager.balance, 500.0)
        # Invalid withdraw (insufficient funds)
        self.assertFalse(self.manager.withdraw(1000.0))
        # Invalid deposit
        self.assertFalse(self.manager.deposit(-100.0))

    def test_insufficient_funds_buy(self):
        self.manager.deposit(100.0)
        # AAPL is 150.0. Attempting to buy 1 should fail.
        self.assertFalse(self.manager.record_trade("AAPL", 1, True))
        self.assertEqual(self.manager.balance, 100.0)

    def test_sell_without_holdings(self):
        self.manager.deposit(1000.0)
        # Cannot sell what you don't have
        self.assertFalse(self.manager.record_trade("AAPL", 1, False))

    def test_portfolio_calculation(self):
        self.manager.deposit(1000.0)
        # Buy 2 AAPL (2 * 150 = 300)
        self.assertTrue(self.manager.record_trade("AAPL", 2, True))
        # Balance: 1000 - 300 = 700, Holdings: {AAPL: 2}
        self.assertEqual(self.manager.get_portfolio_value(), 300.0)
        self.assertEqual(self.manager.balance, 700.0)
        
        # P/L = (700 + 300) - 1000 = 0
        self.assertEqual(self.manager.get_profit_loss(), 0.0)

    def test_invalid_symbol(self):
        self.manager.deposit(1000.0)
        # Should fail if symbol is not in data
        self.assertFalse(self.manager.record_trade("INVALID", 1, True))

    def test_sell_holdings(self):
        self.manager.deposit(1000.0)
        self.manager.record_trade("AAPL", 1, True)
        # Balance is 850
        self.assertTrue(self.manager.record_trade("AAPL", 1, False))
        # Balance should be 850 + 150 = 1000
        self.assertEqual(self.manager.balance, 1000.0)
        self.assertEqual(self.manager.get_holdings(), {})

if __name__ == '__main__':
    unittest.main()
