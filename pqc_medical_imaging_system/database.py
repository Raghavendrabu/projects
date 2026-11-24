"""
Database & Authentication Module for Post-Quantum Medical Imaging System
Uses SQLite to store:
- User accounts (Admin / Doctor vs Patient roles)
- Encrypted medical records & transmission envelopes isolated per patient
"""

import os
import sqlite3
import hashlib
import json
import time
from typing import Dict, Any, List, Optional, Tuple

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "pqc_medical.db")

def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def hash_password(password: str, salt: Optional[bytes] = None) -> str:
    """Hashes password using PBKDF2-HMAC-SHA256."""
    if salt is None:
        salt = os.urandom(16)
    hashed = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, 100_000)
    return salt.hex() + ":" + hashed.hex()

def verify_password(stored_hash: str, password: str) -> bool:
    """Verifies a password against the stored salt:hash string."""
    try:
        salt_hex, key_hex = stored_hash.split(":")
        salt = bytes.fromhex(salt_hex)
        candidate = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, 100_000)
        return candidate.hex() == key_hex
    except Exception:
        return False

def init_db():
    """Initializes tables and seeds default user accounts."""
    conn = get_connection()
    cursor = conn.cursor()

    # Users Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        password_hash TEXT NOT NULL,
        role TEXT NOT NULL CHECK(role IN ('admin', 'patient')),
        full_name TEXT NOT NULL,
        patient_code TEXT,
        created_at REAL NOT NULL
    );
    """)

    # Medical Records Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS medical_records (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        record_uuid TEXT UNIQUE NOT NULL,
        patient_username TEXT NOT NULL,
        doctor_username TEXT NOT NULL,
        scan_title TEXT NOT NULL,
        scan_type TEXT NOT NULL,
        clinical_notes TEXT,
        created_at REAL NOT NULL,
        iso_time TEXT NOT NULL,
        payload_json TEXT NOT NULL,
        original_image_bytes BLOB,
        original_sha256 TEXT NOT NULL,
        kyber_variant TEXT NOT NULL,
        aes_mode TEXT NOT NULL,
        quantum_enabled INTEGER NOT NULL,
        FOREIGN KEY (patient_username) REFERENCES users(username)
    );
    """)

    conn.commit()

    # Seed Default Accounts if empty
    cursor.execute("SELECT COUNT(*) FROM users;")
    count = cursor.fetchone()[0]

    if count == 0:
        now = time.time()
        # Seed 1: Admin
        cursor.execute("""
        INSERT INTO users (username, password_hash, role, full_name, patient_code, created_at)
        VALUES (?, ?, ?, ?, ?, ?);
        """, (
            "admin",
            hash_password("admin123"),
            "admin",
            "Dr. Sarah Chen (Chief Radiologist)",
            "DOC-001",
            now
        ))

        # Seed 2: Patient John Doe
        cursor.execute("""
        INSERT INTO users (username, password_hash, role, full_name, patient_code, created_at)
        VALUES (?, ?, ?, ?, ?, ?);
        """, (
            "john_doe",
            hash_password("patient123"),
            "patient",
            "John Doe",
            "PT-84920",
            now
        ))

        # Seed 3: Patient Alice Smith
        cursor.execute("""
        INSERT INTO users (username, password_hash, role, full_name, patient_code, created_at)
        VALUES (?, ?, ?, ?, ?, ?);
        """, (
            "alice_smith",
            hash_password("patient123"),
            "patient",
            "Alice Smith",
            "PT-91043",
            now
        ))

        conn.commit()

    conn.close()

def authenticate_user(username: str, password: str) -> Optional[Dict[str, Any]]:
    """Authenticates a user and returns user info dictionary if valid."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE username = ?;", (username.strip(),))
    row = cursor.fetchone()
    conn.close()

    if row and verify_password(row["password_hash"], password):
        return {
            "id": row["id"],
            "username": row["username"],
            "role": row["role"],
            "full_name": row["full_name"],
            "patient_code": row["patient_code"]
        }
    return None

def create_user(
    username: str,
    password: str,
    role: str,
    full_name: str,
    patient_code: Optional[str] = None
) -> Tuple[bool, str]:
    """Creates a new user account."""
    if not username or not password or not full_name:
        return False, "Username, password, and full name are required."

    if role not in ("admin", "patient"):
        return False, "Role must be 'admin' or 'patient'."

    conn = get_connection()
    cursor = conn.cursor()
    try:
        now = time.time()
        pwd_hash = hash_password(password)
        cursor.execute("""
        INSERT INTO users (username, password_hash, role, full_name, patient_code, created_at)
        VALUES (?, ?, ?, ?, ?, ?);
        """, (username.strip(), pwd_hash, role, full_name.strip(), patient_code, now))
        conn.commit()
        conn.close()
        return True, "User registered successfully."
    except sqlite3.IntegrityError:
        conn.close()
        return False, f"Username '{username}' already exists."
    except Exception as e:
        conn.close()
        return False, str(e)

def list_patients() -> List[Dict[str, Any]]:
    """Lists all registered patients."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, username, full_name, patient_code, created_at FROM users WHERE role = 'patient' ORDER BY full_name ASC;")
    rows = cursor.fetchall()
    conn.close()
    return [dict(r) for r in rows]

def save_medical_record(
    record_uuid: str,
    patient_username: str,
    doctor_username: str,
    scan_title: str,
    scan_type: str,
    clinical_notes: str,
    payload_dict: Dict[str, Any],
    original_image_bytes: bytes,
    original_sha256: str,
    kyber_variant: str,
    aes_mode: str,
    quantum_enabled: bool
) -> int:
    """Saves a newly encrypted medical record to the database."""
    conn = get_connection()
    cursor = conn.cursor()
    now = time.time()
    iso_time = time.strftime("%Y-%m-%d %H:%M:%S UTC", time.gmtime(now))

    cursor.execute("""
    INSERT INTO medical_records (
        record_uuid, patient_username, doctor_username, scan_title, scan_type,
        clinical_notes, created_at, iso_time, payload_json, original_image_bytes,
        original_sha256, kyber_variant, aes_mode, quantum_enabled
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
    """, (
        record_uuid,
        patient_username,
        doctor_username,
        scan_title,
        scan_type,
        clinical_notes,
        now,
        iso_time,
        json.dumps(payload_dict),
        original_image_bytes,
        original_sha256,
        kyber_variant,
        aes_mode,
        1 if quantum_enabled else 0
    ))

    conn.commit()
    record_id = cursor.lastrowid
    conn.close()
    return record_id

def get_records_for_patient(patient_username: str) -> List[Dict[str, Any]]:
    """Retrieves all medical records assigned to a specific patient."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
    SELECT id, record_uuid, patient_username, doctor_username, scan_title, scan_type,
           clinical_notes, created_at, iso_time, payload_json, original_sha256,
           kyber_variant, aes_mode, quantum_enabled
    FROM medical_records
    WHERE patient_username = ?
    ORDER BY created_at DESC;
    """, (patient_username,))
    rows = cursor.fetchall()
    conn.close()

    records = []
    for r in rows:
        item = dict(r)
        item["payload"] = json.loads(item["payload_json"])
        records.append(item)
    return records

def get_all_records() -> List[Dict[str, Any]]:
    """Retrieves all medical records for admin audit."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
    SELECT id, record_uuid, patient_username, doctor_username, scan_title, scan_type,
           clinical_notes, created_at, iso_time, original_sha256,
           kyber_variant, aes_mode, quantum_enabled
    FROM medical_records
    ORDER BY created_at DESC;
    """)
    rows = cursor.fetchall()
    conn.close()
    return [dict(r) for r in rows]

def get_record_by_id(record_id: int) -> Optional[Dict[str, Any]]:
    """Fetches a single medical record by its ID."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM medical_records WHERE id = ?;", (record_id,))
    row = cursor.fetchone()
    conn.close()
    if row:
        item = dict(row)
        item["payload"] = json.loads(item["payload_json"])
        return item
    return None

def delete_record(record_id: int) -> bool:
    """Deletes a medical record."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM medical_records WHERE id = ?;", (record_id,))
    conn.commit()
    deleted = cursor.rowcount > 0
    conn.close()
    return deleted

# Auto-initialize on import
init_db()

