"""
Pipeline Orchestrator: End-to-End Post-Quantum Medical Image Transmission System
Implements the complete workflow from the system architecture diagram:
- Steps 1-5: Sender (Medical Facility)
- Step 6: Secure Transmission Channel
- Steps 7-8: Receiver (Diagnostic Center)
- Steps 9-11: Evaluation & Validation
"""

import time
from typing import Dict, Any, Optional, Tuple, Union
import numpy as np
from PIL import Image

from core.acquisition import MedicalImageAcquisition
from core.pqc_kem import PostQuantumKEM
from core.cipher_aes import AES256Cipher
from core.integrity_auth import PostQuantumSigner
from core.quantum_layer import QuantumLayer
from core.transmission import TransmissionChannel
from evaluation.performance import PerformanceAnalyzer
from evaluation.quality import QualityAssessment
from evaluation.security import SecurityValidator

class PQCMedicalPipeline:
    """
    Executes and evaluates the full Post-Quantum Medical Image Transmission workflow.
    """

    def __init__(
        self,
        kyber_variant: str = "Kyber768",
        dilithium_variant: str = "Dilithium2",
        aes_mode: str = "GCM",
        enable_quantum_layer: bool = True
    ):
        self.kyber_variant = kyber_variant
        self.dilithium_variant = dilithium_variant
        self.aes_mode = aes_mode
        self.enable_quantum_layer = enable_quantum_layer

        # Initialize crypto engines
        self.kem = PostQuantumKEM(variant=kyber_variant)
        self.signer = PostQuantumSigner(variant=dilithium_variant)
        self.quantum = QuantumLayer(enabled=enable_quantum_layer)

    def run(
        self,
        image_source: Union[str, np.ndarray, Image.Image],
        target_size: Tuple[int, int] = (256, 256),
        as_grayscale: bool = True,
        simulate_network_delay_ms: float = 20.0,
        tamper_mode: Optional[str] = None,
        simulate_unauthorized_attacker: bool = True
    ) -> Dict[str, Any]:
        """
        Executes complete pipeline: Steps 1 through 11.
        """
        perf = PerformanceAnalyzer()

        # =========================================================================
        # 1. RECEIVER SETUP: Key Generation for Key Establishment (Step 2 Prep)
        # =========================================================================
        rec_pk, rec_sk, t_kyber_kg = self.kem.generate_keypair()
        perf.record_stage("kyber_keygen_ms", t_kyber_kg)

        # Sender also generates Dilithium signing keypair (Step 4 Prep)
        sender_dsa_pk, sender_dsa_sk, t_dsa_kg = self.signer.generate_keypair()
        perf.record_stage("dilithium_keygen_ms", t_dsa_kg)

        # =========================================================================
        # STEP 1: Medical Image Acquisition (Resize, Normalize, Grayscale)
        # =========================================================================
        t0 = time.perf_counter()
        original_img, img_meta = MedicalImageAcquisition.load_image(
            image_source=image_source,
            target_size=target_size,
            as_grayscale=as_grayscale
        )
        t_acq = (time.perf_counter() - t0) * 1000.0
        perf.record_stage("image_acquisition_ms", t_acq)
        raw_img_bytes = MedicalImageAcquisition.to_bytes(original_img)

        # =========================================================================
        # STEP 2: Post-Quantum Key Establishment (CRYSTALS-Kyber)
        # Sender encapsulates shared session key using Receiver's Public Key
        # =========================================================================
        shared_session_key, kyber_ciphertext, t_encaps = self.kem.encapsulate(rec_pk)
        perf.record_stage("kyber_encaps_ms", t_encaps)

        # =========================================================================
        # STEP 5 (Applied at Sender): Optional Quantum Layer (Quantum Transformation)
        # Permutation via Quantum Arnold Map + Diffusion via Quantum Walk
        # =========================================================================
        quantum_transformed_img, quantum_meta, t_q_fwd = self.quantum.forward_transform(
            original_img,
            key_seed=shared_session_key
        )
        perf.record_stage("quantum_forward_ms", t_q_fwd)
        quantum_bytes = MedicalImageAcquisition.to_bytes(quantum_transformed_img)

        # =========================================================================
        # STEP 3: Image Encryption (AES-256)
        # Encrypting transformed image bytes with 256-bit shared session key
        # =========================================================================
        aes_cipher_sender = AES256Cipher(key=shared_session_key, mode=self.aes_mode)
        aes_ciphertext, iv_or_nonce, auth_tag, t_aes_enc = aes_cipher_sender.encrypt_bytes(quantum_bytes)
        perf.record_stage("aes_encryption_ms", t_aes_enc)

        # Cipher image array for visualization & cryptanalysis
        cipher_img_array = AES256Cipher.ciphertext_to_image_array(aes_ciphertext, original_img.shape)

        # =========================================================================
        # STEP 4: Integrity & Authentication (SHA-256 Hashing, Digital Signature)
        # Sender signs the payload using CRYSTALS-Dilithium
        # =========================================================================
        # Digest computed on ciphertext package
        signature_material = aes_ciphertext + kyber_ciphertext
        dsa_signature, sha256_hash, t_sign = self.signer.sign_message(
            private_key=sender_dsa_sk,
            message=signature_material
        )
        perf.record_stage("dilithium_sign_ms", t_sign)
        original_image_hash = self.signer.compute_sha256(raw_img_bytes)

        # =========================================================================
        # STEP 6: Secure Transmission (Network / Internet Channel)
        # =========================================================================
        packed_packet = TransmissionChannel.pack_payload(
            kyber_ciphertext=kyber_ciphertext,
            aes_ciphertext=aes_ciphertext,
            iv_or_nonce=iv_or_nonce,
            auth_tag=auth_tag,
            sha256_hash=sha256_hash,
            dilithium_signature=dsa_signature,
            sender_dilithium_pubkey=sender_dsa_pk,
            quantum_enabled=self.enable_quantum_layer,
            image_shape=original_img.shape,
            image_dtype=str(original_img.dtype),
            extra_meta={"original_image_hash": original_image_hash}
        )

        transmitted_packet, channel_telemetry = TransmissionChannel.transmit(
            payload=packed_packet,
            simulate_network_delay_ms=simulate_network_delay_ms,
            tamper_mode=tamper_mode
        )
        perf.record_stage("transmission_latency_ms", channel_telemetry["elapsed_ms"])

        # =========================================================================
        # STEP 7 & 8: RECEIVER (Diagnostic Center)
        # 7. Decryption & Recovery (Kyber Decaps + AES-256 Decrypt + Inverse Quantum)
        # 8. Verification (Verify Digital Signature, Recompute Hash)
        # =========================================================================
        (
            rx_kyber_ct,
            rx_aes_ct,
            rx_iv_nonce,
            rx_tag,
            rx_hash,
            rx_signature,
            rx_sender_pk,
            rx_q_enabled,
            rx_shape
        ) = TransmissionChannel.unpack_payload(transmitted_packet)

        # 8.1: Verify Digital Signature & Integrity
        rx_sig_material = rx_aes_ct + rx_kyber_ct
        is_sig_valid, is_hash_valid, auth_status, t_verify = self.signer.verify_signature(
            public_key=rx_sender_pk,
            message=rx_sig_material,
            signature=rx_signature,
            expected_sha256=rx_hash
        )
        perf.record_stage("dilithium_verify_ms", t_verify)

        # 7.1: Key Recovery via Kyber Decapsulation
        recovered_session_key, t_decaps = self.kem.decapsulate(rec_sk, rx_kyber_ct)
        perf.record_stage("kyber_decaps_ms", t_decaps)

        # 7.2: AES-256 Decryption
        aes_cipher_receiver = AES256Cipher(key=recovered_session_key, mode=self.aes_mode)
        decryption_success = True
        decryption_error_msg = None
        try:
            decrypted_quantum_bytes, t_aes_dec = aes_cipher_receiver.decrypt_bytes(
                ciphertext=rx_aes_ct,
                iv_or_nonce=rx_iv_nonce,
                auth_tag=rx_tag
            )
            perf.record_stage("aes_decryption_ms", t_aes_dec)
            decrypted_intermediate_arr = MedicalImageAcquisition.from_bytes(
                decrypted_quantum_bytes,
                shape=rx_shape
            )
        except Exception as e:
            decryption_success = False
            decryption_error_msg = str(e)
            perf.record_stage("aes_decryption_ms", 0.0)
            # In case of corruption / tampering failure, fill with zeros
            decrypted_intermediate_arr = np.zeros(rx_shape, dtype=np.uint8)

        # 7.3: Inverse Quantum Transformation (if enabled)
        if decryption_success:
            recovered_img, t_q_inv = self.quantum.inverse_transform(
                decrypted_intermediate_arr,
                key_seed=recovered_session_key
            )
            perf.record_stage("quantum_inverse_ms", t_q_inv)
        else:
            recovered_img = decrypted_intermediate_arr
            perf.record_stage("quantum_inverse_ms", 0.0)

        # Recompute hash of recovered image
        recomputed_recovered_hash = self.signer.compute_sha256(MedicalImageAcquisition.to_bytes(recovered_img))
        is_reconstructed_hash_match = (recomputed_recovered_hash == original_image_hash)

        # =========================================================================
        # STEP 9: Performance Analysis
        # =========================================================================
        perf_summary = perf.compute_summary(
            image_bytes_len=len(raw_img_bytes),
            payload_bytes_len=channel_telemetry["payload_size_bytes"]
        )

        # =========================================================================
        # STEP 10: Image Quality Assessment (PSNR, SSIM, Visual, Histograms)
        # =========================================================================
        quality_summary = QualityAssessment.evaluate_pipeline_quality(
            original_img=original_img,
            encrypted_img=cipher_img_array,
            decrypted_img=recovered_img
        )

        # =========================================================================
        # STEP 11: Security Validation & Cryptanalysis
        # (Shannon Entropy, Correlation, Differential NPCR/UACI, Rogue Key Test)
        # =========================================================================
        entropy_original = SecurityValidator.compute_shannon_entropy(original_img)
        entropy_encrypted = SecurityValidator.compute_shannon_entropy(cipher_img_array)
        entropy_decrypted = SecurityValidator.compute_shannon_entropy(recovered_img)

        corr_original = SecurityValidator.compute_adjacent_correlation(original_img)
        corr_encrypted = SecurityValidator.compute_adjacent_correlation(cipher_img_array)

        # Differential Cryptanalysis: Modify 1 single pixel in original and re-encrypt
        img_single_bit_flip = original_img.copy()
        img_single_bit_flip[0, 0] = img_single_bit_flip[0, 0] ^ 0x01
        q_diff, _, _ = self.quantum.forward_transform(img_single_bit_flip, key_seed=shared_session_key)
        diff_cipher_bytes, _, _, _ = aes_cipher_sender.encrypt_bytes(MedicalImageAcquisition.to_bytes(q_diff))
        cipher2_arr = AES256Cipher.ciphertext_to_image_array(diff_cipher_bytes, original_img.shape)
        npcr, uaci = SecurityValidator.compute_npcr_and_uaci(cipher_img_array, cipher2_arr)

        # Unauthorized access defense simulation (Rogue Key)
        rogue_test = None
        if simulate_unauthorized_attacker:
            _, rogue_sk, _ = self.kem.generate_keypair()
            rogue_test = SecurityValidator.test_unauthorized_access(
                encrypted_payload=transmitted_packet,
                rogue_private_key=rogue_sk,
                kem_instance=self.kem,
                aes_class=AES256Cipher
            )

        security_summary = {
            "shannon_entropy": {
                "original": entropy_original,
                "encrypted": entropy_encrypted,
                "decrypted": entropy_decrypted,
                "ideal_maximum": 8.0000
            },
            "pixel_correlation": {
                "original": corr_original,
                "encrypted": corr_encrypted
            },
            "differential_attack": {
                "npcr_percent": npcr,
                "npcr_ideal_percent": 99.6094,
                "uaci_percent": uaci,
                "uaci_ideal_percent": 33.4635
            },
            "unauthorized_access_defense": rogue_test,
            "signature_verification": {
                "is_signature_valid": is_sig_valid,
                "is_hash_valid": is_hash_valid,
                "status_message": auth_status,
                "recomputed_hash_match": is_reconstructed_hash_match
            }
        }

        # Package full pipeline execution report
        report = {
            "timestamp": time.time(),
            "pipeline_config": {
                "kyber_variant": self.kyber_variant,
                "dilithium_variant": self.dilithium_variant,
                "aes_mode": self.aes_mode,
                "quantum_layer_enabled": self.enable_quantum_layer,
                "tamper_mode": tamper_mode
            },
            "images": {
                "original": original_img,
                "quantum_transformed": quantum_transformed_img if self.enable_quantum_layer else None,
                "encrypted_visual": cipher_img_array,
                "decrypted": recovered_img
            },
            "metadata": img_meta,
            "keys": {
                "receiver_kyber_public_key_bytes": len(rec_pk),
                "receiver_kyber_secret_key_bytes": len(rec_sk),
                "sender_dilithium_public_key_bytes": len(sender_dsa_pk),
                "sender_dilithium_secret_key_bytes": len(sender_dsa_sk),
                "shared_session_key_hex": shared_session_key.hex(),
                "shared_session_key_bits": len(shared_session_key) * 8
            },
            "channel_telemetry": channel_telemetry,
            "verification": {
                "decryption_success": decryption_success,
                "decryption_error": decryption_error_msg,
                "integrity_verified": is_sig_valid and is_hash_valid and is_reconstructed_hash_match
            },
            "performance": perf_summary,
            "quality": quality_summary,
            "security": security_summary
        }
        return report

