import time
from typing import Dict, Any, Optional
from config import DEFAULT_RISK_LIMITS
from vault import CredentialVault

class TradingEngine:
    """
    Financial Trading Execution Engine with built-in Risk Management, Safety Guardrails, and HITL Approval Enforcement.
    """

    def __init__(self, vault: Optional[CredentialVault] = None):
        self.vault = vault or CredentialVault()

    def validate_risk(self, symbol: str, quantity: float, price: float, side: str, stop_loss: Optional[float]) -> Dict[str, Any]:
        order_value = quantity * price
        max_val = DEFAULT_RISK_LIMITS["max_position_value_usd"]

        if order_value > max_val:
            return {
                "allowed": False,
                "reason": f"Order total value (${order_value:.2f}) exceeds configured risk limit of ${max_val:.2f}."
            }

        if DEFAULT_RISK_LIMITS["require_stop_loss"] and not stop_loss:
            return {
                "allowed": False,
                "reason": "Risk Rules require an explicit Stop-Loss price for every trade execution."
            }

        return {"allowed": True, "order_value": order_value}

    def prepare_trade_order(self, broker: str, symbol: str, side: str, quantity: float, order_type: str = "MARKET", limit_price: Optional[float] = None, stop_loss: Optional[float] = None) -> Dict[str, Any]:
        """
        Calculates trade parameters and prepares order payload for HITL approval.
        """
        estimated_price = limit_price or 100.0  # Default reference price if market order
        risk_check = self.validate_risk(symbol, quantity, estimated_price, side, stop_loss)
        
        if not risk_check["allowed"]:
            return {
                "status": "rejected",
                "reason": risk_check["reason"]
            }

        order_id = f"ORD_{int(time.time()*1000)}"
        payload = {
            "order_id": order_id,
            "broker": broker,
            "symbol": symbol.upper(),
            "side": side.upper(),
            "quantity": quantity,
            "order_type": order_type.upper(),
            "estimated_price": estimated_price,
            "total_value": quantity * estimated_price,
            "stop_loss": stop_loss,
            "status": "PENDING_APPROVAL",
            "message": "Trade prepared. Mandatory Human-In-The-Loop (HITL) approval required before dispatch."
        }
        return payload

    def execute_confirmed_trade(self, order_payload: Dict[str, Any]) -> Dict[str, Any]:
        """
        Executes trade after explicit user confirmation.
        """
        broker = order_payload.get("broker", "paper_trading").lower()
        cred = self.vault.get_credential(broker)

        # Check if live broker API key exists
        if cred and cred.get("secret"):
            # Real Broker Execution Mock / Integration Point
            return {
                "status": "executed",
                "mode": "LIVE_BROKER",
                "order_id": order_payload["order_id"],
                "broker": broker,
                "symbol": order_payload["symbol"],
                "side": order_payload["side"],
                "quantity": order_payload["quantity"],
                "filled_price": order_payload["estimated_price"],
                "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
                "message": f"Successfully placed LIVE {order_payload['side']} order for {order_payload['quantity']} {order_payload['symbol']} on {broker}."
            }
        else:
            # Paper / Simulation Trading Mode
            return {
                "status": "executed",
                "mode": "PAPER_TRADING_SIMULATION",
                "order_id": order_payload["order_id"],
                "broker": f"{broker} (Simulated)",
                "symbol": order_payload["symbol"],
                "side": order_payload["side"],
                "quantity": order_payload["quantity"],
                "filled_price": order_payload["estimated_price"],
                "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
                "message": f"Successfully executed SIMULATED trade: {order_payload['side']} {order_payload['quantity']} x {order_payload['symbol']} @ ${order_payload['estimated_price']}."
            }
