"""
Module 10: Image Quality Assessment
Computes Peak Signal-to-Noise Ratio (PSNR), Structural Similarity Index (SSIM),
Mean Squared Error (MSE), histogram distributions, and residual difference maps.
"""

from typing import Dict, Any, Tuple
import numpy as np
from skimage.metrics import peak_signal_noise_ratio as compute_psnr
from skimage.metrics import structural_similarity as compute_ssim

class QualityAssessment:
    """Evaluates reconstructed image fidelity and ciphertext visual divergence."""

    @staticmethod
    def calculate_metrics(
        original: np.ndarray,
        target: np.ndarray,
        data_range: int = 255
    ) -> Dict[str, float]:
        """
        Calculates MSE, PSNR, and SSIM between two image arrays.
        """
        if original.shape != target.shape:
            raise ValueError(f"Shape mismatch: {original.shape} vs {target.shape}")

        orig_f = original.astype(np.float64)
        targ_f = target.astype(np.float64)

        # 1. Mean Squared Error (MSE)
        mse = float(np.mean((orig_f - targ_f) ** 2))

        # 2. PSNR
        if mse == 0.0:
            psnr = 100.0  # Perfect reconstruction convention
        else:
            psnr = float(compute_psnr(original, target, data_range=data_range))

        # 3. SSIM
        channel_axis = -1 if original.ndim == 3 else None
        ssim = float(compute_ssim(original, target, data_range=data_range, channel_axis=channel_axis))

        # 4. Maximum Absolute Error
        max_error = float(np.max(np.abs(orig_f - targ_f)))

        return {
            "mse": mse,
            "psnr_db": psnr,
            "ssim": ssim,
            "max_absolute_pixel_error": max_error
        }

    @classmethod
    def evaluate_pipeline_quality(
        cls,
        original_img: np.ndarray,
        encrypted_img: np.ndarray,
        decrypted_img: np.ndarray
    ) -> Dict[str, Any]:
        """
        Performs full comparative assessment:
        - Fidelity of Decrypted Image vs Original (Target: PSNR=100dB, SSIM=1.000, MSE=0)
        - Confusion of Encrypted Image vs Original (Target: Low PSNR, SSIM ~ 0)
        """
        recovery_metrics = cls.calculate_metrics(original_img, decrypted_img)
        encryption_metrics = cls.calculate_metrics(original_img, encrypted_img)

        # Check visual preservation
        is_lossless = (recovery_metrics["mse"] == 0.0)

        # Histogram analysis
        orig_hist, _ = np.histogram(original_img, bins=256, range=(0, 256))
        enc_hist, _ = np.histogram(encrypted_img, bins=256, range=(0, 256))
        dec_hist, _ = np.histogram(decrypted_img, bins=256, range=(0, 256))

        # Variance of cipher histogram (a flat uniform distribution has very low variance)
        enc_hist_variance = float(np.var(enc_hist))

        return {
            "recovery_metrics": recovery_metrics,
            "encryption_metrics": encryption_metrics,
            "is_lossless": is_lossless,
            "histograms": {
                "original": orig_hist.tolist(),
                "encrypted": enc_hist.tolist(),
                "decrypted": dec_hist.tolist(),
                "encrypted_histogram_variance": enc_hist_variance
            }
        }

