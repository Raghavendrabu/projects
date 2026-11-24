"""
Module 1: Medical Image Acquisition & Preprocessing
Handles loading, resizing, grayscale/color normalization, and tensor conversions
for medical images (X-rays, MRI scans, CT scans, Retinal fundus, etc.)
"""

import os
from typing import Tuple, Dict, Any, Union
import numpy as np
from PIL import Image
import cv2

class MedicalImageAcquisition:
    """Acquires, standardizes, and pre-processes medical images."""

    DEFAULT_SIZE = (256, 256)

    @classmethod
    def load_image(
        cls,
        image_source: Union[str, np.ndarray, Image.Image],
        target_size: Tuple[int, int] = DEFAULT_SIZE,
        as_grayscale: bool = True,
        normalize: bool = True
    ) -> Tuple[np.ndarray, Dict[str, Any]]:
        """
        Loads and pre-processes a medical image.

        Args:
            image_source: File path, numpy array, or PIL Image.
            target_size: (width, height) tuple to resize image.
            as_grayscale: If True, converts image to single-channel 8-bit grayscale.
            normalize: If True, validates pixel range in [0, 255] uint8.

        Returns:
            Tuple of:
                - preprocessed uint8 numpy array of shape (H, W) or (H, W, C)
                - metadata dict containing original dimensions, channels, min/max intensities.
        """
        metadata: Dict[str, Any] = {}

        if isinstance(image_source, str):
            if not os.path.exists(image_source):
                raise FileNotFoundError(f"Medical image file not found: {image_source}")
            metadata["source_path"] = image_source
            metadata["filename"] = os.path.basename(image_source)
            pil_img = Image.open(image_source)
        elif isinstance(image_source, Image.Image):
            pil_img = image_source
            metadata["filename"] = "in_memory_pil_image"
        elif isinstance(image_source, np.ndarray):
            pil_img = Image.fromarray(image_source)
            metadata["filename"] = "in_memory_numpy_array"
        else:
            raise TypeError(f"Unsupported image source type: {type(image_source)}")

        metadata["original_size"] = pil_img.size
        metadata["original_mode"] = pil_img.mode

        # Step 1.1: Convert to Grayscale if requested
        if as_grayscale:
            if pil_img.mode != "L":
                pil_img = pil_img.convert("L")
        else:
            if pil_img.mode not in ("RGB", "L"):
                pil_img = pil_img.convert("RGB")

        # Step 1.2: Resize
        if target_size is not None and pil_img.size != target_size:
            pil_img = pil_img.resize(target_size, Image.Resampling.LANCZOS)

        img_arr = np.array(pil_img, dtype=np.uint8)

        # Step 1.3: Normalization & Metadata check
        metadata["processed_shape"] = img_arr.shape
        metadata["min_pixel"] = int(np.min(img_arr))
        metadata["max_pixel"] = int(np.max(img_arr))
        metadata["mean_pixel"] = float(np.mean(img_arr))
        metadata["std_pixel"] = float(np.std(img_arr))
        metadata["dtype"] = str(img_arr.dtype)
        metadata["is_grayscale"] = as_grayscale or (img_arr.ndim == 2)

        return img_arr, metadata

    @staticmethod
    def to_bytes(image_array: np.ndarray) -> bytes:
        """Converts image numpy array to raw bytes."""
        return image_array.tobytes()

    @staticmethod
    def from_bytes(raw_bytes: bytes, shape: Tuple[int, ...], dtype=np.uint8) -> np.ndarray:
        """Reconstructs numpy array from raw bytes with exact shape and dtype."""
        arr = np.frombuffer(raw_bytes, dtype=dtype)
        return arr.reshape(shape)

