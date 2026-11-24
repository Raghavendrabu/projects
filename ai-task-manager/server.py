import asyncio
import json
from pathlib import Path
from typing import Dict, Any, List, Optional

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel

from config import BASE_DIR, SCREENSHOTS_DIR, SERVER_HOST, SERVER_PORT
from vault import CredentialVault
from browser_driver import BrowserDriver
from agent_orchestrator import AgentOrchestrator

app = FastAPI(title="OmniTask AI Server")

# Mount screenshot directory and static frontend
app.mount("/screenshots", StaticFiles(directory=str(SCREENSHOTS_DIR)), name="screenshots")
frontend_dir = BASE_DIR / "frontend"
app.mount("/static", StaticFiles(directory=str(frontend_dir)), name="static")

# WebSocket Connection Manager
class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)

    async def broadcast(self, message: Dict[str, Any]):
        for connection in self.active_connections:
            try:
                await connection.send_json(message)
            except Exception:
                pass

manager = ConnectionManager()
vault = CredentialVault()
browser_driver = BrowserDriver(headless=False)
orchestrator = AgentOrchestrator(browser_driver)

# Models
class CommandRequest(BaseModel):
    command: str

class VaultItemRequest(BaseModel):
    service_name: str
    username: str
    secret: str
    extra_data: Optional[Dict[str, Any]] = None

@app.get("/")
async def get_index():
    return FileResponse(frontend_dir / "index.html")

@app.get("/styles.css")
async def get_styles():
    return FileResponse(frontend_dir / "styles.css")

@app.get("/app.js")
async def get_app_js():
    return FileResponse(frontend_dir / "app.js")

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            # Keep socket alive
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(websocket)

async def send_log_broadcast(text: str, data: Dict[str, Any]):
    level = "info"
    if "error" in text.lower() or "rejected" in text.lower():
        level = "error"
    elif "warning" in text.lower() or "requires" in text.lower():
        level = "warning"
    elif "success" in text.lower() or "executed" in text.lower():
        level = "success"

    await manager.broadcast({
        "type": "log",
        "text": text,
        "level": level,
        "data": data
    })

    # If screenshot is provided in log payload, broadcast it too
    if data and "screenshot" in data:
        await manager.broadcast({
            "type": "screenshot",
            "url": data["screenshot"]
        })
    elif data and "result" in data and isinstance(data["result"], dict) and "screenshot" in data["result"]:
        await manager.broadcast({
            "type": "screenshot",
            "url": data["result"]["screenshot"]
        })

@app.post("/api/execute")
async def execute_task(req: CommandRequest):
    async def callback(msg: str, data: Dict[str, Any]):
        await send_log_broadcast(msg, data)
        if data.get("approval_required"):
            await manager.broadcast({
                "type": "approval_required",
                "approval_id": data.get("approval_id"),
                "details": data.get("details")
            })

    result = await orchestrator.parse_and_execute(req.command, log_callback=callback)
    return result

@app.post("/api/approve/{approval_id}")
async def approve_task(approval_id: str):
    res = await orchestrator.approve_pending_action(approval_id)
    await send_log_broadcast(f"Task '{approval_id}' Approved & Executed.", res)
    return res

@app.post("/api/reject/{approval_id}")
async def reject_task(approval_id: str):
    res = await orchestrator.reject_pending_action(approval_id)
    await send_log_broadcast(f"Task '{approval_id}' Rejected.", {"status": "warning"})
    return res

@app.get("/api/vault")
async def get_vault_credentials():
    return vault.list_services()

@app.post("/api/vault")
async def save_vault_credential(item: VaultItemRequest):
    vault.set_credential(item.service_name, item.username, item.secret, item.extra_data)
    return {"status": "success", "message": f"Credential for '{item.service_name}' saved."}

@app.delete("/api/vault/{service_name}")
async def delete_vault_credential(service_name: str):
    success = vault.delete_credential(service_name)
    if success:
        return {"status": "success"}
    raise HTTPException(status_code=404, detail="Service credential not found")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("server:app", host=SERVER_HOST, port=SERVER_PORT, reload=True)
