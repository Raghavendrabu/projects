import os
from pathlib import Path

# Base directories
BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
LOGS_DIR = BASE_DIR / "logs"
DATA_DIR.mkdir(exist_ok=True)
LOGS_DIR.mkdir(exist_ok=True)

# Vault configuration
VAULT_FILE = DATA_DIR / "encrypted_vault.json"
VAULT_KEY_FILE = DATA_DIR / ".vault_key"

# Browser storage configuration
BROWSER_STORAGE_DIR = DATA_DIR / "browser_sessions"
BROWSER_STORAGE_DIR.mkdir(exist_ok=True)
SCREENSHOTS_DIR = DATA_DIR / "screenshots"
SCREENSHOTS_DIR.mkdir(exist_ok=True)

# Security and Safety Controls
HUMAN_APPROVAL_REQUIRED_FOR = [
    "EXECUTE_TRADE",
    "ENTER_PASSWORD",
    "FINANCIAL_TRANSFER",
    "DELETE_FILES"
]

# Risk Management Defaults for Trading Tasks
DEFAULT_RISK_LIMITS = {
    "max_position_value_usd": 1000.0,
    "require_stop_loss": True,
    "default_stop_loss_pct": 2.0,
    "require_approval": True
}

# Web Server Settings
SERVER_HOST = "127.0.0.1"
SERVER_PORT = 8000
