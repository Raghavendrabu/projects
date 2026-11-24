"""
Module 3 & 7: AES-256 Image Encryption & Decryption
Uses the 256-bit shared session key established via CRYSTALS-Kyber
Supports GCM (Authenticated Encryption), CBC, and CTR modes.
"""

import os
import time
from typing import Tuple, Dict, Any, Optional
import numpy as np
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad

class AES256Cipher:
    """
    AES-256 Image Encryption and Decryption engine.
    Compatible with keys derived from CRYSTALS-Kyber KEM.
    """

    SUPPORTED_MODES = ["GCM", "CBC", "CTR"]

    def __init__(self, key: bytes, mode: str = "GCM"):
        if len(key) != 32:
            raise ValueError(f"AES-256 requires exactly 32 bytes (256 bits) key. Got {len(key)} bytes.")
        if mode not in self.SUPPORTED_MODES:
            raise ValueError(f"Unsupported mode '{mode}'. Choose from {self.SUPPORTED_MODES}")
        self.key = key
        self.mode = mode

    def encrypt_bytes(self, plaintext_bytes: bytes) -> Tuple[bytes, bytes, Optional[bytes], float]:
        """
        Encrypts plaintext bytes with AES-256.

        Returns:
            Tuple of:
                - ciphertext (bytes)
                - iv_or_nonce (bytes)
                - auth_tag (bytes if GCM else None)
                - elapsed_ms (float)
        """
        start = time.perf_counter()

        if self.mode == "GCM":
            nonce = os.urandom(12)  # 96-bit nonce standard for GCM
            cipher = AES.new(self.key, AES.MODE_GCM, nonce=nonce)
            ciphertext, tag = cipher.encrypt_and_digest(plaintext_bytes)
            elapsed_ms = (time.perf_counter() - start) * 1000.0
            return ciphertext, nonce, tag, elapsed_ms

        elif self.mode == "CBC":
            iv = os.urandom(16)
            cipher = AES.new(self.key, AES.MODE_CBC, iv=iv)
            padded_data = pad(plaintext_bytes, AES.block_size)
            ciphertext = cipher.encrypt(padded_data)
            elapsed_ms = (time.perf_counter() - start) * 1000.0
            return ciphertext, iv, None, elapsed_ms

        elif self.mode == "CTR":
            nonce = os.urandom(8)
            cipher = AES.new(self.key, AES.MODE_CTR, nonce=nonce)
            ciphertext = cipher.encrypt(plaintext_bytes)
            elapsed_ms = (time.perf_counter() - start) * 1000.0
            return ciphertext, nonce, None, elapsed_ms

        raise ValueError(f"Unknown mode: {self.mode}")

    def decrypt_bytes(
        self,
        ciphertext: bytes,
        iv_or_nonce: bytes,
        auth_tag: Optional[bytes] = None
    ) -> Tuple[bytes, float]:
        """
        Decrypts ciphertext bytes with AES-256.

        Returns:
            Tuple of:
                - recovered plaintext bytes
                - elapsed_ms (float)
        """
        start = time.perf_counter()

        if self.mode == "GCM":
            if auth_tag is None:
                raise ValueError("AES-GCM mode requires an authentication tag for decryption.")
            cipher = AES.new(self.key, AES.MODE_GCM, nonce=iv_or_nonce)
            plaintext = cipher.decrypt_and_verify(ciphertext, auth_tag)
            elapsed_ms = (time.perf_counter() - start) * 1000.0
            return plaintext, elapsed_ms

        elif self.mode == "CBC":
            cipher = AES.new(self.key, AES.MODE_CBC, iv=iv_or_nonce)
            padded_data = cipher.decrypt(ciphertext)
            plaintext = unpad(padded_data, AES.block_size)
            elapsed_ms = (time.perf_counter() - start) * 1000.0
            return plaintext, elapsed_ms

        elif self.mode == "CTR":
            cipher = AES.new(self.key, AES.MODE_CTR, nonce=iv_or_nonce)
            plaintext = cipher.decrypt(ciphertext)
            elapsed_ms = (time.perf_counter() - start) * 1000.0
            return plaintext, elapsed_ms

        raise ValueError(f"Unknown mode: {self.mode}")

    @staticmethod
    def ciphertext_to_image_array(ciphertext: bytes, target_shape: Tuple[int, ...]) -> np.ndarray:
        """
        Converts the first N bytes of ciphertext into a visual representation
        with the same shape as the original image (for visualization & entropy).
        """
        num_pixels = np.prod(target_shape)
        if len(ciphertext) >= num_pixels:
            slice_bytes = ciphertext[:num_pixels]
        else:
            # Pad cyclically if needed
            repeats = int(np.ceil(num_pixels / len(ciphertext)))
            slice_bytes = (ciphertext * repeats)[:num_pixels]
        return np.frombuffer(slice_bytes, dtype=np.uint8).reshape(target_shape)

