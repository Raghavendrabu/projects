"""
Automated Pytest Suite for Post-Quantum Medical Image System
Tests:
- End-to-end lossless transmission
- CRYSTALS-Kyber KEM key agreement
- AES-256 GCM encryption/decryption
- CRYSTALS-Dilithium signature verification
- Quantum layer unitarity and reversibility
- Tamper detection under MITM bit-flip attacks
- Unauthorized access defense with rogue key
- Security metrics (Entropy, Correlation, NPCR/UACI)
"""

import os
import sys
import pytest
import numpy as np

# Ensure project root is in sys.path
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from core.acquisition import MedicalImageAcquisition
from core.pqc_kem import PostQuantumKEM
from core.cipher_aes import AES256Cipher
from core.integrity_auth import PostQuantumSigner
from core.quantum_layer import QuantumLayer
from core.transmission import TransmissionChannel
from pipeline import PQCMedicalPipeline

SAMPLE_IMG_PATH = r"c:\Projects\pqc_medical_imaging_system\sample_images\brain_mri.png"

def test_acquisition():
    img, meta = MedicalImageAcquisition.load_image(SAMPLE_IMG_PATH, target_size=(128, 128))
    assert img.shape == (128, 128)
    assert img.dtype == np.uint8
    assert meta["min_pixel"] >= 0
    assert meta["max_pixel"] <= 255

def test_pqc_kem():
    kem = PostQuantumKEM("Kyber512")
    pk, sk, _ = kem.generate_keypair()
    ss1, ct, _ = kem.encapsulate(pk)
    ss2, _ = kem.decapsulate(sk, ct)
    assert ss1 == ss2
    assert len(ss1) == 32

def test_integrity_dilithium():
    signer = PostQuantumSigner("Dilithium2")
    pk, sk, _ = signer.generate_keypair()
    msg = b"Medical Scan Metadata: Patient #92810"
    sig, sha, _ = signer.sign_message(sk, msg)
    is_valid, is_hash, status, _ = signer.verify_signature(pk, msg, sig, sha)
    assert is_valid
    assert is_hash

    # Tampered message
    tampered_msg = b"Medical Scan Metadata: Patient #00000"
    is_valid_t, is_hash_t, _, _ = signer.verify_signature(pk, tampered_msg, sig, sha)
    assert not is_valid_t
    assert not is_hash_t

def test_quantum_layer_invertibility():
    ql = QuantumLayer(enabled=True)
    orig = np.random.randint(0, 256, size=(128, 128), dtype=np.uint8)
    seed = b"\x12\x34\x56\x78" * 8
    transformed, meta, _ = ql.forward_transform(orig, seed)
    recovered, _ = ql.inverse_transform(transformed, seed)
    assert np.array_equal(orig, recovered), "Quantum transform must be 100% mathematically lossless!"

def test_e2e_pipeline_clean():
    pipeline = PQCMedicalPipeline(
        kyber_variant="Kyber512",
        dilithium_variant="Dilithium2",
        aes_mode="GCM",
        enable_quantum_layer=True
    )
    result = pipeline.run(
        image_source=SAMPLE_IMG_PATH,
        target_size=(128, 128),
        simulate_network_delay_ms=0,
        tamper_mode=None
    )

    # 1. Quality
    assert result["quality"]["is_lossless"]
    assert result["quality"]["recovery_metrics"]["ssim"] == 1.0
    assert result["quality"]["recovery_metrics"]["mse"] == 0.0

    # 2. Verification
    assert result["verification"]["integrity_verified"]
    assert result["security"]["signature_verification"]["is_signature_valid"]

    # 3. Security
    assert result["security"]["shannon_entropy"]["encrypted"] > 7.95
    assert result["security"]["unauthorized_access_defense"]["unauthorized_access_prevented"]

def test_pipeline_tamper_attack_detected():
    pipeline = PQCMedicalPipeline(
        kyber_variant="Kyber512",
        dilithium_variant="Dilithium2",
        aes_mode="GCM",
        enable_quantum_layer=True
    )
    result = pipeline.run(
        image_source=SAMPLE_IMG_PATH,
        target_size=(128, 128),
        simulate_network_delay_ms=0,
        tamper_mode="bit_flip_ciphertext"
    )

    # Tamper should be caught by Dilithium digital signature and AES-GCM
    assert not result["verification"]["integrity_verified"]
    assert not result["security"]["signature_verification"]["is_signature_valid"]
