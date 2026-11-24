import asyncio
import re
import json
from typing import Dict, Any, List, Callable, Optional
from vault import CredentialVault
from browser_driver import BrowserDriver
from desktop_driver import DesktopDriver
from trading_driver import TradingEngine
from config import HUMAN_APPROVAL_REQUIRED_FOR

class AgentOrchestrator:
    """
    Core Autonomous Agent Task Orchestrator & Execution Loop.
    Decomposes natural language requests into structured tool calls:
    - Vault Service (Creds lookup)
    - Browser Driver (Web navigation, login, scraping)
    - Desktop Driver (App launches, hotkeys, keyboard/mouse)
    - Trading Engine (Order execution & Risk management)
    """

    def __init__(self, browser_driver: Optional[BrowserDriver] = None):
        self.vault = CredentialVault()
        self.browser = browser_driver or BrowserDriver(headless=False)
        self.trading = TradingEngine(self.vault)
        self.pending_approvals: Dict[str, Dict[str, Any]] = {}

    async def parse_and_execute(self, user_command: str, log_callback: Optional[Callable[[str, Dict[str, Any]], None]] = None) -> Dict[str, Any]:
        """
        Parses natural language user command and executes corresponding autonomous plan.
        """
        cmd_clean = user_command.strip()
        cmd_lower = cmd_clean.lower()

        async def log(msg: str, data: Optional[Dict[str, Any]] = None):
            print(f"[Agent] {msg}")
            if log_callback:
                res = log_callback(msg, data or {})
                if asyncio.iscoroutine(res):
                    await res

        await log(f"Received Command: '{cmd_clean}'")

        # -------------------------------------------------------------
        # 1. TRADING COMMAND PATTERN MATCHING
        # -------------------------------------------------------------
        if any(w in cmd_lower for w in ["trade", "buy", "sell", "place order", "stock", "crypto"]):
            await log("Detected Financial Trading Intent.")
            
            # Simple NLP Extraction
            side = "BUY" if "buy" in cmd_lower else ("SELL" if "sell" in cmd_lower else "BUY")
            
            # Match symbol
            symbol_match = re.search(r'\b([a-zA-Z]{2,6})\b', cmd_clean.replace("buy", "").replace("sell", "").replace("trade", ""))
            symbol = symbol_match.group(1).upper() if symbol_match else "AAPL"

            # Match quantity
            qty_match = re.search(r'(\d+)\s*(shares|units|coins|qty|quant)?', cmd_lower)
            qty = float(qty_match.group(1)) if qty_match else 1.0

            # Match stop loss
            sl_match = re.search(r'stop\s*loss\s*(?:of|at)?\s*(\d+(?:\.\d+)?)', cmd_lower)
            sl_price = float(sl_match.group(1)) if sl_match else 95.0

            broker_match = "zerodha" if "zerodha" in cmd_lower else ("binance" if "binance" in cmd_lower else "alpaca")

            order_prepared = self.trading.prepare_trade_order(
                broker=broker_match,
                symbol=symbol,
                side=side,
                quantity=qty,
                order_type="MARKET",
                limit_price=100.0,
                stop_loss=sl_price
            )

            if order_prepared.get("status") == "rejected":
                await log(f"Trade Rejected by Risk Engine: {order_prepared['reason']}")
                return {"status": "error", "message": order_prepared["reason"]}

            # Save to pending approvals for HITL
            approval_id = order_prepared["order_id"]
            self.pending_approvals[approval_id] = {
                "type": "EXECUTE_TRADE",
                "payload": order_prepared,
                "description": f"Execute {side} trade of {qty} {symbol} on {broker_match} with Stop-Loss ${sl_price}"
            }

            await log(f"Trade Prepared. High-risk action requires Human-In-The-Loop Approval.", {"approval_required": True, "approval_id": approval_id, "details": self.pending_approvals[approval_id]})
            
            return {
                "status": "awaiting_approval",
                "approval_id": approval_id,
                "details": self.pending_approvals[approval_id]
            }

        # -------------------------------------------------------------
        # 2. WEB BROWSER LOGIN & WEBSITE COMMANDS
        # -------------------------------------------------------------
        elif "open" in cmd_lower and ("website" in cmd_lower or "http" in cmd_lower or "www" in cmd_lower or ".com" in cmd_lower or ".org" in cmd_lower or "login" in cmd_lower):
            await log("Detected Web Navigation / Login Intent.")
            
            # Extract target domain/url
            url_match = re.search(r'(https?://[^\s]+|www\.[^\s]+|[a-zA-Z0-9-]+\.(?:com|org|net|io|co|in))', cmd_clean)
            target_url = url_match.group(1) if url_match else "https://google.com"
            if not target_url.startswith("http"):
                target_url = "https://" + target_url

            # Extract service name for vault lookup
            service_name = target_url.split("//")[-1].split(".")[0].lower()

            if "login" in cmd_lower or "sign in" in cmd_lower or "id" in cmd_lower:
                await log(f"Checking Vault for stored credentials for '{service_name}'...")
                cred = self.vault.get_credential(service_name)
                
                if cred:
                    await log(f"Found Vault credentials for '{cred['username']}'. Executing automated login on {target_url}...")
                    result = await self.browser.auto_login_service(service_name, target_url, cred['username'], cred['secret'])
                    await log("Login task executed.", result)
                    return {"status": "success", "result": result}
                else:
                    await log(f"No stored credentials found in Vault for '{service_name}'. Navigating to target site for manual login...")
                    result = await self.browser.open_url(target_url)
                    await log("Loaded web page.", result)
                    return {
                        "status": "partial_success",
                        "message": f"Opened {target_url}. You can add credentials for '{service_name}' in the Vault for auto-login next time.",
                        "result": result
                    }
            else:
                await log(f"Opening URL: {target_url}")
                result = await self.browser.open_url(target_url)
                await log("Navigation complete.", result)
                return {"status": "success", "result": result}

        # -------------------------------------------------------------
        # 3. DESKTOP / OS CONTROL COMMANDS
        # -------------------------------------------------------------
        elif any(w in cmd_lower for w in ["app", "application", "launch", "desktop", "type", "press", "shortcut"]):
            await log("Detected Desktop OS Automation Intent.")
            
            if "open" in cmd_lower or "launch" in cmd_lower:
                app_name = cmd_clean.lower().replace("open", "").replace("launch", "").replace("app", "").replace("application", "").strip()
                if not app_name:
                    app_name = "notepad"
                res = DesktopDriver.open_application(app_name)
                await log(f"Launched {app_name}", res)
                return {"status": "success", "result": res}

            elif "type" in cmd_lower:
                text_to_type = cmd_clean.split("type")[-1].strip(' "\'')
                res = DesktopDriver.type_keys(text_to_type)
                await log(f"Typed '{text_to_type}'", res)
                return {"status": "success", "result": res}

            elif "press" in cmd_lower or "hotkey" in cmd_lower:
                hotkey = cmd_clean.split("press")[-1].replace("hotkey", "").strip()
                res = DesktopDriver.press_shortcut(hotkey)
                await log(f"Pressed hotkey {hotkey}", res)
                return {"status": "success", "result": res}

        # -------------------------------------------------------------
        # 4. DEFAULT GENERAL ASSISTANT & BROWSER SEARCH
        # -------------------------------------------------------------
        else:
            await log(f"Treating task as web search query: '{cmd_clean}'")
            search_url = f"https://www.google.com/search?q={cmd_clean.replace(' ', '+')}"
            result = await self.browser.open_url(search_url)
            await log("Search completed.", result)
            return {"status": "success", "result": result}

    async def approve_pending_action(self, approval_id: str) -> Dict[str, Any]:
        """
        Confirms and executes a pending HITL high-risk task (e.g. placing trade).
        """
        if approval_id not in self.pending_approvals:
            return {"status": "error", "message": f"Approval ID '{approval_id}' not found or expired."}

        item = self.pending_approvals.pop(approval_id)
        action_type = item["type"]
        payload = item["payload"]

        if action_type == "EXECUTE_TRADE":
            result = self.trading.execute_confirmed_trade(payload)
            return {"status": "success", "result": result}
        
        return {"status": "error", "message": f"Unknown action type '{action_type}'"}

    async def reject_pending_action(self, approval_id: str) -> Dict[str, Any]:
        if approval_id in self.pending_approvals:
            del self.pending_approvals[approval_id]
            return {"status": "success", "message": f"Rejected task '{approval_id}'."}
        return {"status": "error", "message": "Approval ID not found."}
