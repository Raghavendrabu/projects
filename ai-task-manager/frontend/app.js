let socket = null;
let currentApprovalId = null;

// Initialize WebSocket and Load Vault Items on DOM Load
document.addEventListener('DOMContentLoaded', () => {
  connectWebSocket();
  loadVaultItems();

  // Allow Enter key to trigger task execution
  document.getElementById('command-input').addEventListener('keypress', (e) => {
    if (e.key === 'Enter') {
      executeCommand();
    }
  });
});

// WebSocket Live Streaming Connection
function connectWebSocket() {
  const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
  const wsUrl = `${protocol}//${window.location.host}/ws`;

  socket = new WebSocket(wsUrl);

  socket.onopen = () => {
    console.log('[WS] Connected to OmniTask Server');
    document.getElementById('ws-status').innerHTML = '<span class="dot green"></span> System Connected';
  };

  socket.onmessage = (event) => {
    try {
      const data = JSON.parse(event.data);
      handleIncomingMessage(data);
    } catch (e) {
      console.error('[WS] Parse Error:', e);
    }
  };

  socket.onclose = () => {
    document.getElementById('ws-status').innerHTML = '<span class="dot red" style="background:#ef4444;"></span> Offline (Reconnecting...)';
    setTimeout(connectWebSocket, 3000);
  };
}

function handleIncomingMessage(msg) {
  if (msg.type === 'log') {
    appendLog(msg.text, msg.level || 'info');
  } else if (msg.type === 'screenshot') {
    updateScreenshot(msg.url);
  } else if (msg.type === 'approval_required') {
    showApprovalBox(msg.approval_id, msg.details);
  }
}

function appendLog(text, level = 'info') {
  const container = document.getElementById('log-container');
  const entry = document.createElement('div');
  const now = new Date().toLocaleTimeString();
  
  entry.className = `log-entry ${level}`;
  entry.innerHTML = `<span class="time">[${now}]</span> ${text}`;
  
  container.appendChild(entry);
  container.scrollTop = container.scrollHeight;
}

function updateScreenshot(url) {
  if (!url) return;
  const img = document.getElementById('preview-image');
  // Cache-busting timestamp
  img.src = `${url}?t=${Date.now()}`;
}

function clearLogs() {
  document.getElementById('log-container').innerHTML = '';
  appendLog('Logs cleared.', 'system');
}

function setCommand(cmd) {
  document.getElementById('command-input').value = cmd;
}

// Execute Task Command
async function executeCommand() {
  const input = document.getElementById('command-input');
  const command = input.value.trim();
  
  if (!command) return;
  
  appendLog(`User Command Submitted: "${command}"`, 'system');
  input.value = '';

  try {
    const res = await fetch('/api/execute', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ command })
    });
    
    const data = await res.json();
    
    if (data.status === 'awaiting_approval') {
      showApprovalBox(data.approval_id, data.details);
    } else if (data.result && data.result.screenshot) {
      updateScreenshot(data.result.screenshot);
    }
  } catch (err) {
    appendLog(`Failed to send command: ${err.message}`, 'error');
  }
}

// HITL Approval Controls
function showApprovalBox(approvalId, details) {
  currentApprovalId = approvalId;
  const box = document.getElementById('approval-box');
  const content = document.getElementById('approval-details');
  
  const d = details.payload || {};
  content.innerHTML = `
    <strong>Action:</strong> ${details.type}<br/>
    <strong>Description:</strong> ${details.description}<br/>
    <strong>Broker:</strong> ${d.broker || 'N/A'}<br/>
    <strong>Symbol:</strong> ${d.symbol || 'N/A'} | <strong>Side:</strong> ${d.side || 'N/A'} | <strong>Quantity:</strong> ${d.quantity || 0}<br/>
    <strong>Est. Total Value:</strong> $${(d.total_value || 0).toFixed(2)}<br/>
    <strong>Stop Loss Price:</strong> $${d.stop_loss || 'Not Set'}
  `;
  
  box.classList.remove('hidden');
}

async function approveAction() {
  if (!currentApprovalId) return;
  appendLog(`Approving action ${currentApprovalId}...`, 'system');
  
  try {
    const res = await fetch(`/api/approve/${currentApprovalId}`, { method: 'POST' });
    const data = await res.json();
    appendLog(`Trade Execution Result: ${JSON.stringify(data.result.message || data.result)}`, 'success');
    document.getElementById('approval-box').classList.add('hidden');
    currentApprovalId = null;
  } catch (err) {
    appendLog(`Approval failed: ${err.message}`, 'error');
  }
}

async function rejectAction() {
  if (!currentApprovalId) return;
  appendLog(`Rejecting action ${currentApprovalId}...`, 'warning');
  
  try {
    await fetch(`/api/reject/${currentApprovalId}`, { method: 'POST' });
    document.getElementById('approval-box').classList.add('hidden');
    currentApprovalId = null;
  } catch (err) {
    appendLog(`Rejection failed: ${err.message}`, 'error');
  }
}

// Vault Modal Functions
function openVaultModal() {
  document.getElementById('vault-modal').classList.remove('hidden');
  loadVaultItems();
}

function closeVaultModal() {
  document.getElementById('vault-modal').classList.add('hidden');
}

async function loadVaultItems() {
  try {
    const res = await fetch('/api/vault');
    const items = await res.json();
    const list = document.getElementById('vault-items-list');
    
    if (items.length === 0) {
      list.innerHTML = '<li class="empty-state">No credentials stored yet.</li>';
      return;
    }
    
    list.innerHTML = items.map(i => `
      <li class="vault-item">
        <div>
          <div class="service">${i.service}</div>
          <div class="user">${i.username}</div>
        </div>
        <button class="btn btn-sm btn-danger" onclick="deleteVaultCredential('${i.service}')">Delete</button>
      </li>
    `).join('');
  } catch (err) {
    console.error('Failed to load vault items:', err);
  }
}

async function saveVaultCredential(e) {
  e.preventDefault();
  const service = document.getElementById('vault-service').value;
  const username = document.getElementById('vault-username').value;
  const secret = document.getElementById('vault-secret').value;

  try {
    await fetch('/api/vault', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ service_name: service, username, secret })
    });
    
    appendLog(`Saved credentials for service '${service}' in AES-256 Vault.`, 'success');
    document.getElementById('vault-form').reset();
    loadVaultItems();
  } catch (err) {
    appendLog(`Vault save error: ${err.message}`, 'error');
  }
}

async function deleteVaultCredential(service) {
  try {
    await fetch(`/api/vault/${service}`, { method: 'DELETE' });
    loadVaultItems();
    appendLog(`Deleted credentials for '${service}' from Vault.`, 'warning');
  } catch (err) {
    appendLog(`Failed to delete credential: ${err.message}`, 'error');
  }
}
