"""
Seeds initial encrypted medical records for John Doe and Alice Smith.
"""

import os
import sys
import uuid
import numpy as np

PROJECT_ROOT = os.path.abspath(os.path.dirname(__file__))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from database import get_connection, save_medical_record
from pipeline import PQCMedicalPipeline
from core.acquisition import MedicalImageAcquisition

def seed_demo_records():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM medical_records;")
    count = cursor.fetchone()[0]
    conn.close()

    if count > 0:
        print("[*] Medical records already seeded.")
        return

    print("[*] Seeding initial encrypted records for John Doe and Alice Smith...")
    samples_dir = os.path.join(PROJECT_ROOT, "sample_images")

    # 1. John Doe - Brain MRI
    mri_path = os.path.join(samples_dir, "brain_mri.png")
    if os.path.exists(mri_path):
        pipe = PQCMedicalPipeline(kyber_variant="Kyber768", dilithium_variant="Dilithium2", aes_mode="GCM", enable_quantum_layer=True)
        rep = pipe.run(mri_path, target_size=(256, 256), simulate_network_delay_ms=0)
        
        # Build transport envelope with private keys stored in envelope for demo receiver decapsulation
        packet = rep["channel_telemetry"]
        # In this demo model, the envelope holds the encrypted crypto fields plus receiver private key token
        transport_payload = {
            "packet_id": str(uuid.uuid4()),
            "crypto": {
                "kyber_ciphertext_hex": rep["keys"]["shared_session_key_hex"],  # used in envelope
            },
            "pipeline_report": {
                "kyber_variant": "Kyber768",
                "dilithium_variant": "Dilithium2",
                "aes_mode": "GCM",
                "quantum_layer_enabled": True,
                "shared_session_key_hex": rep["keys"]["shared_session_key_hex"],
                "channel_telemetry": rep["channel_telemetry"],
                "images": {
                    "original": rep["images"]["original"].tolist(),
                    "quantum_transformed": rep["images"]["quantum_transformed"].tolist() if rep["images"]["quantum_transformed"] is not None else None,
                    "encrypted_visual": rep["images"]["encrypted_visual"].tolist(),
                    "decrypted": rep["images"]["decrypted"].tolist()
                },
                "quality": rep["quality"],
                "security": rep["security"],
                "performance": rep["performance"]
            }
        }

        save_medical_record(
            record_uuid=str(uuid.uuid4()),
            patient_username="john_doe",
            doctor_username="admin",
            scan_title="Brain MRI - Axial T2-Weighted Slice",
            scan_type="Brain MRI",
            clinical_notes="Patient presented with intermittent headaches. Scan reveals normal ventricular size, clear sulci, and no acute intracranial hemorrhage or mass effect.",
            payload_dict=transport_payload,
            original_image_bytes=MedicalImageAcquisition.to_bytes(rep["images"]["original"]),
            original_sha256=rep["security"]["signature_verification"].get("recomputed_hash_match", True) and "verified_hash_mri",
            kyber_variant="Kyber768",
            aes_mode="GCM",
            quantum_enabled=True
        )
        print("[+] Seeded Brain MRI for john_doe")

    # 2. Alice Smith - Chest X-Ray
    xray_path = os.path.join(samples_dir, "chest_xray.png")
    if os.path.exists(xray_path):
        pipe = PQCMedicalPipeline(kyber_variant="Kyber768", dilithium_variant="Dilithium2", aes_mode="GCM", enable_quantum_layer=True)
        rep = pipe.run(xray_path, target_size=(256, 256), simulate_network_delay_ms=0)
        
        transport_payload = {
            "packet_id": str(uuid.uuid4()),
            "pipeline_report": {
                "kyber_variant": "Kyber768",
                "dilithium_variant": "Dilithium2",
                "aes_mode": "GCM",
                "quantum_layer_enabled": True,
                "shared_session_key_hex": rep["keys"]["shared_session_key_hex"],
                "channel_telemetry": rep["channel_telemetry"],
                "images": {
                    "original": rep["images"]["original"].tolist(),
                    "quantum_transformed": rep["images"]["quantum_transformed"].tolist() if rep["images"]["quantum_transformed"] is not None else None,
                    "encrypted_visual": rep["images"]["encrypted_visual"].tolist(),
                    "decrypted": rep["images"]["decrypted"].tolist()
                },
                "quality": rep["quality"],
                "security": rep["security"],
                "performance": rep["performance"]
            }
        }

        save_medical_record(
            record_uuid=str(uuid.uuid4()),
            patient_username="alice_smith",
            doctor_username="admin",
            scan_title="Routine Pre-Operative Chest X-Ray (PA View)",
            scan_type="Chest X-Ray",
            clinical_notes="Clear bilateral lung fields. Cardiothoracic ratio is within normal physiological limits. Normal osseous structures of the thorax.",
            payload_dict=transport_payload,
            original_image_bytes=MedicalImageAcquisition.to_bytes(rep["images"]["original"]),
            original_sha256="verified_hash_chest_xray",
            kyber_variant="Kyber768",
            aes_mode="GCM",
            quantum_enabled=True
        )
        print("[+] Seeded Chest X-Ray for alice_smith")

if __name__ == "__main__":
    seed_demo_records()

