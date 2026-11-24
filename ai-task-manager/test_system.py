import sys
import unittest
import asyncio

from vault import CredentialVault
from trading_driver import TradingEngine
from desktop_driver import DesktopDriver

class TestOmniTaskSystem(unittest.TestCase):

    def test_vault_encryption_decryption(self):
        vault = CredentialVault(master_password="TestMasterPassword123")
        vault.set_credential("github", "testuser@example.com", "MySecretPassword123")
        
        cred = vault.get_credential("github")
        self.assertIsNotNone(cred)
        self.assertEqual(cred["username"], "testuser@example.com")
        self.assertEqual(cred["secret"], "MySecretPassword123")

        services = vault.list_services()
        self.assertTrue(any(s["service"] == "github" for s in services))

        vault.delete_credential("github")
        self.assertIsNone(vault.get_credential("github"))

    def test_trading_risk_management(self):
        trading = TradingEngine()
        
        # Test order within limits
        order = trading.prepare_trade_order(
            broker="zerodha",
            symbol="AAPL",
            side="BUY",
            quantity=2,
            order_type="MARKET",
            limit_price=150.0,
            stop_loss=140.0
        )
        self.assertEqual(order["status"], "PENDING_APPROVAL")
        self.assertEqual(order["symbol"], "AAPL")
        self.assertEqual(order["total_value"], 300.0)

        # Test trade execution simulation
        execution = trading.execute_confirmed_trade(order)
        self.assertEqual(execution["status"], "executed")

        # Test order exceeding max risk limit ($1000)
        overlimit_order = trading.prepare_trade_order(
            broker="zerodha",
            symbol="BTC",
            side="BUY",
            quantity=100,
            limit_price=500.0,  # $50,000 total
            stop_loss=450.0
        )
        self.assertEqual(overlimit_order["status"], "rejected")

    def test_desktop_driver(self):
        screenshot = DesktopDriver.take_desktop_screenshot("test_shot")
        self.assertTrue(screenshot.startswith("/screenshots/"))

if __name__ == "__main__":
    unittest.main()
