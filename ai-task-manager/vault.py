import os
import json
import base64
from typing import Dict, Any, Optional
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from config import VAULT_FILE, VAULT_KEY_FILE

class CredentialVault:
    """
    AES-256 Encrypted Local Vault for Personal Credentials & API Keys.
    """

    def __init__(self, master_password: str = "OmniTaskDefaultKey2026"):
        self.key = self._generate_key(master_password)
        self.fernet = Fernet(self.key)
        self._ensure_vault_exists()

    def _generate_key(self, password: str) -> bytes:
        salt = b'omni_task_salt_2026_secure'
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100_000,
        )
        return base64.urlsafe_b64encode(kdf.derive(password.encode()))

    def _ensure_vault_exists(self):
        if not VAULT_FILE.exists():
            self._save_encrypted_vault({})

    def _load_encrypted_vault(self) -> Dict[str, Any]:
        if not VAULT_FILE.exists():
            return {}
        try:
            with open(VAULT_FILE, "rb") as f:
                encrypted_data = f.read()
            if not encrypted_data:
                return {}
            decrypted_data = self.fernet.decrypt(encrypted_data).decode('utf-8')
            return json.loads(decrypted_data)
        except Exception as e:
            print(f"[Vault Warning] Failed to decrypt vault: {e}")
            return {}

    def _save_encrypted_vault(self, data: Dict[str, Any]):
        json_bytes = json.dumps(data, indent=2).encode('utf-8')
        encrypted_bytes = self.fernet.encrypt(json_bytes)
        with open(VAULT_FILE, "wb") as f:
            f.write(encrypted_bytes)

    def set_credential(self, service_name: str, username: str, secret: str, extra_data: Optional[Dict[str, Any]] = None):
        vault_data = self._load_encrypted_vault()
        vault_data[service_name.lower()] = {
            "service": service_name,
            "username": username,
            "secret": secret,
            "extra_data": extra_data or {}
        }
        self._save_encrypted_vault(vault_data)
        return True

    def get_credential(self, service_name: str) -> Optional[Dict[str, Any]]:
        vault_data = self._load_encrypted_vault()
        return vault_data.get(service_name.lower())

    def list_services(self) -> list:
        vault_data = self._load_encrypted_vault()
        return [{"service": v.get("service"), "username": v.get("username")} for v in vault_data.values()]

    def delete_credential(self, service_name: str) -> bool:
        vault_data = self._load_encrypted_vault()
        key = service_name.lower()
        if key in vault_data:
            del vault_data[key]
            self._save_encrypted_vault(vault_data)
            return True
        return False
