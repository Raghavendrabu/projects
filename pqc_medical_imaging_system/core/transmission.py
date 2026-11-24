"""
Module 6: Secure Transmission Layer (Network / Internet)
Packages cryptographic components into secure transmission envelopes.
Supports network channel simulation with latency, packet loss, bit-flip tampering attacks,
and unauthorized interception demonstrations.
"""

import time
import json
import uuid
from typing import Dict, Any, Tuple, Optional
import numpy as np

class TransmissionChannel:
    """
    Simulates or conducts secure transmission over Network / Internet
    between Sender (Medical Facility) and Receiver (Diagnostic Center).
    """

    @staticmethod
    def pack_payload(
        kyber_ciphertext: bytes,
        aes_ciphertext: bytes,
        iv_or_nonce: bytes,
        auth_tag: Optional[bytes],
        sha256_hash: str,
        dilithium_signature: bytes,
        sender_dilithium_pubkey: bytes,
        quantum_enabled: bool,
        image_shape: Tuple[int, ...],
        image_dtype: str = "uint8",
        extra_meta: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Packages all cryptographic items into a transmission envelope."""
        payload = {
            "packet_id": str(uuid.uuid4()),
            "timestamp": time.time(),
            "iso_time": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "protocol": "PQC-Medical-Secure-v1.0",
            "quantum_layer_enabled": quantum_enabled,
            "image_meta": {
                "shape": list(image_shape),
                "dtype": image_dtype
            },
            "crypto": {
                "kyber_ciphertext_hex": kyber_ciphertext.hex(),
                "aes_ciphertext_hex": aes_ciphertext.hex(),
                "iv_or_nonce_hex": iv_or_nonce.hex(),
                "auth_tag_hex": auth_tag.hex() if auth_tag is not None else None,
                "sha256_hash": sha256_hash,
                "dilithium_signature_hex": dilithium_signature.hex(),
                "sender_dilithium_pubkey_hex": sender_dilithium_pubkey.hex(),
            },
            "extra_meta": extra_meta or {}
        }
        return payload

    @staticmethod
    def unpack_payload(payload: Dict[str, Any]) -> Tuple[bytes, bytes, bytes, Optional[bytes], str, bytes, bytes, bool, Tuple[int, ...]]:
        """Unpacks the transmission envelope into raw bytes."""
        crypto = payload["crypto"]
        kyber_ct = bytes.fromhex(crypto["kyber_ciphertext_hex"])
        aes_ct = bytes.fromhex(crypto["aes_ciphertext_hex"])
        iv_nonce = bytes.fromhex(crypto["iv_or_nonce_hex"])
        tag = bytes.fromhex(crypto["auth_tag_hex"]) if crypto.get("auth_tag_hex") else None
        sha_hash = crypto["sha256_hash"]
        signature = bytes.fromhex(crypto["dilithium_signature_hex"])
        sender_pk = bytes.fromhex(crypto["sender_dilithium_pubkey_hex"])
        quantum_enabled = payload.get("quantum_layer_enabled", False)
        shape = tuple(payload["image_meta"]["shape"])
        return kyber_ct, aes_ct, iv_nonce, tag, sha_hash, signature, sender_pk, quantum_enabled, shape

    @classmethod
    def transmit(
        cls,
        payload: Dict[str, Any],
        simulate_network_delay_ms: float = 20.0,
        tamper_mode: Optional[str] = None
    ) -> Tuple[Dict[str, Any], Dict[str, Any]]:
        """
        Transmits payload across the network channel.

        Args:
            payload: Transmission packet dict.
            simulate_network_delay_ms: Simulated network latency.
            tamper_mode: None, "bit_flip_ciphertext", "alter_hash", or "corrupt_signature".

        Returns:
            Tuple of (received_payload, transmission_telemetry)
        """
        start = time.perf_counter()

        # Deep copy payload to prevent in-place mutation of sender's record
        received = json.loads(json.dumps(payload))
        telemetry = {
            "channel": "Simulated Secure WAN / Internet (TLS 1.3 + Post-Quantum Hybrid)",
            "packet_id": payload["packet_id"],
            "tampered": False,
            "tamper_mode": tamper_mode,
            "payload_size_bytes": len(json.dumps(payload).encode('utf-8'))
        }

        # Apply simulated network delay
        if simulate_network_delay_ms > 0:
            time.sleep(simulate_network_delay_ms / 1000.0)

        # Apply simulated attacks if requested
        if tamper_mode == "bit_flip_ciphertext":
            # Attacker flips a byte in the AES ciphertext stream
            ct_hex = received["crypto"]["aes_ciphertext_hex"]
            ct_bytes = bytearray(bytes.fromhex(ct_hex))
            flip_pos = len(ct_bytes) // 2
            ct_bytes[flip_pos] ^= 0xFF  # Invert all 8 bits at midpoint
            received["crypto"]["aes_ciphertext_hex"] = ct_bytes.hex()
            telemetry["tampered"] = True
            telemetry["tamper_detail"] = f"MITM Attack: Inverted byte at offset {flip_pos} in ciphertext."

        elif tamper_mode == "alter_hash":
            # Attacker replaces the SHA-256 hash manifest
            received["crypto"]["sha256_hash"] = "00" * 32
            telemetry["tampered"] = True
            telemetry["tamper_detail"] = "MITM Attack: Replaced SHA-256 digest with forged string."

        elif tamper_mode == "corrupt_signature":
            # Attacker damages the Dilithium digital signature
            sig_hex = received["crypto"]["dilithium_signature_hex"]
            sig_bytes = bytearray(bytes.fromhex(sig_hex))
            sig_bytes[10] ^= 0xAA
            received["crypto"]["dilithium_signature_hex"] = sig_bytes.hex()
            telemetry["tampered"] = True
            telemetry["tamper_detail"] = "MITM Attack: Corrupted Dilithium digital signature bytes."

        telemetry["elapsed_ms"] = (time.perf_counter() - start) * 1000.0
        return received, telemetry

