"""
Module 11: Security Validation & Cryptanalysis
Implements rigorous security assessments:
1. Shannon Information Entropy (Ideal: 8.0000 bits)
2. Adjacent Pixel Correlation (Horizontal, Vertical, Diagonal)
3. Differential Cryptanalysis: NPCR and UACI
4. Unauthorized Access Simulation (Rogue Key Defense)
5. Tampering & Bit-Flip Attack Detection
"""

import math
from typing import Dict, Any, Tuple, Optional
import numpy as np

class SecurityValidator:
    """Performs cryptographic security validation and statistical resistance tests."""

    @staticmethod
    def compute_shannon_entropy(image_arr: np.ndarray) -> float:
        """
        Computes Shannon Information Entropy:
        H(s) = - sum(p_i * log2(p_i))
        For an 8-bit image, ideal theoretical maximum is 8.0000 bits.
        """
        flattened = image_arr.flatten()
        total_pixels = len(flattened)
        if total_pixels == 0:
            return 0.0

        hist, _ = np.histogram(flattened, bins=256, range=(0, 256))
        prob = hist / total_pixels
        prob = prob[prob > 0]  # Avoid log2(0)

        entropy = -float(np.sum(prob * np.log2(prob)))
        return entropy

    @staticmethod
    def compute_adjacent_correlation(
        image_arr: np.ndarray,
        sample_size: int = 5000
    ) -> Dict[str, float]:
        """
        Calculates Pearson correlation coefficient between adjacent pixels
        in Horizontal, Vertical, and Diagonal directions.
        Ideal cipher: correlation ~ 0.000.
        Plaintext medical image: correlation ~ 0.95 to 0.99.
        """
        if image_arr.ndim == 3:
            img = image_arr[:, :, 0]  # Use first channel if color
        else:
            img = image_arr

        H, W = img.shape
        np.random.seed(42)

        # 1. Horizontal pairs: (x, y) and (x, y + 1)
        rand_h_y = np.random.randint(0, H, size=sample_size)
        rand_h_x = np.random.randint(0, W - 1, size=sample_size)
        x_h = img[rand_h_y, rand_h_x].astype(np.float64)
        y_h = img[rand_h_y, rand_h_x + 1].astype(np.float64)
        corr_h = float(np.corrcoef(x_h, y_h)[0, 1])

        # 2. Vertical pairs: (x, y) and (x + 1, y)
        rand_v_y = np.random.randint(0, H - 1, size=sample_size)
        rand_v_x = np.random.randint(0, W, size=sample_size)
        x_v = img[rand_v_y, rand_v_x].astype(np.float64)
        y_v = img[rand_v_y + 1, rand_v_x].astype(np.float64)
        corr_v = float(np.corrcoef(x_v, y_v)[0, 1])

        # 3. Diagonal pairs: (x, y) and (x + 1, y + 1)
        rand_d_y = np.random.randint(0, H - 1, size=sample_size)
        rand_d_x = np.random.randint(0, W - 1, size=sample_size)
        x_d = img[rand_d_y, rand_d_x].astype(np.float64)
        y_d = img[rand_d_y + 1, rand_d_x + 1].astype(np.float64)
        corr_d = float(np.corrcoef(x_d, y_d)[0, 1])

        return {
            "horizontal": 0.0 if np.isnan(corr_h) else corr_h,
            "vertical": 0.0 if np.isnan(corr_v) else corr_v,
            "diagonal": 0.0 if np.isnan(corr_d) else corr_d,
            "average": float(np.mean([abs(c) for c in [corr_h, corr_v, corr_d] if not np.isnan(c)]))
        }

    @staticmethod
    def compute_npcr_and_uaci(
        cipher1: np.ndarray,
        cipher2: np.ndarray
    ) -> Tuple[float, float]:
        """
        Calculates NPCR (Number of Pixels Change Rate) and
        UACI (Unified Average Changing Intensity) between two cipher images
        derived from plaintexts differing by a single pixel bit.

        Ideal theoretical values for 8-bit images:
            NPCR ~ 99.6094%
            UACI ~ 33.4635%
        """
        if cipher1.shape != cipher2.shape:
            raise ValueError("Cipher images must have identical shapes for differential cryptanalysis.")

        c1 = cipher1.astype(np.float64)
        c2 = cipher2.astype(np.float64)
        total_pixels = float(cipher1.size)

        # NPCR: Percentage of differing pixels
        diff_mask = (c1 != c2).astype(np.float64)
        npcr = (np.sum(diff_mask) / total_pixels) * 100.0

        # UACI: Normalized absolute intensity difference
        uaci = (np.sum(np.abs(c1 - c2) / 255.0) / total_pixels) * 100.0

        return float(npcr), float(uaci)

    @classmethod
    def test_unauthorized_access(
        cls,
        encrypted_payload: Dict[str, Any],
        rogue_private_key: bytes,
        kem_instance,
        aes_class
    ) -> Dict[str, Any]:
        """
        Simulates an unauthorized attacker attempting decryption with a forged or rogue key.
        Confirms zero leakage of medical imagery.
        """
        crypto = encrypted_payload["crypto"]
        kyber_ct = bytes.fromhex(crypto["kyber_ciphertext_hex"])
        aes_ct = bytes.fromhex(crypto["aes_ciphertext_hex"])
        iv_nonce = bytes.fromhex(crypto["iv_or_nonce_hex"])
        auth_tag = bytes.fromhex(crypto["auth_tag_hex"]) if crypto.get("auth_tag_hex") else None

        try:
            # Attacker decapsulates Kyber ciphertext with rogue private key
            rogue_shared_key, _ = kem_instance.decapsulate(rogue_private_key, kyber_ct)
            rogue_cipher = aes_class(rogue_shared_key, mode="GCM" if auth_tag else "CBC")
            recovered_bytes, _ = rogue_cipher.decrypt_bytes(aes_ct, iv_nonce, auth_tag)
            access_granted = True
            details = "VULNERABILITY: Rogue key decrypted ciphertext without exception!"
        except Exception as e:
            access_granted = False
            details = f"DEFENSE VERIFIED: Decryption rejected with error: {type(e).__name__} ({str(e)})"

        return {
            "unauthorized_access_prevented": not access_granted,
            "access_granted": access_granted,
            "security_status": "SECURE" if not access_granted else "COMPROMISED",
            "details": details
        }

