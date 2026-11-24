"""
Module 5: Optional Quantum Layer (Quantum Transformation)
Implements quantum-inspired reversible transformations:
1. Discrete-time Quantum Walk (DTQW) with Hadamard coin diffusion.
2. Quantum 2D Arnold Symplectic Coordinate Permutation.
Guarantees strict unitarity (U^dagger * U = I), enabling lossless recovery.
"""

import time
from typing import Tuple, Dict, Any, Optional
import numpy as np

class QuantumRandomWalk:
    """
    Simulates a 1D Discrete-Time Quantum Walk (DTQW) on a circular lattice.
    Evolution operator: U = S * (C tensor I)
    where C is the Hadamard coin operator and S is the conditional shift operator.
    Produces quantum probability distributions with ballistic spreading (sigma ~ t).
    """

    @staticmethod
    def hadamard_coin() -> np.ndarray:
        return np.array([[1.0, 1.0], [1.0, -1.0]], dtype=np.complex128) / np.sqrt(2.0)

    @classmethod
    def simulate_walk(cls, steps: int = 128, lattice_size: int = 256) -> np.ndarray:
        """
        Runs quantum walk for `steps` on `lattice_size` nodes.
        Returns normalized probability distribution array of length `lattice_size`.
        """
        # Quantum state: shape (2, lattice_size) -> [|0>, |1>] coin states
        psi = np.zeros((2, lattice_size), dtype=np.complex128)
        # Initial symmetric superposition state: (|0> + i|1>)/sqrt(2) at lattice center
        center = lattice_size // 2
        psi[0, center] = 1.0 / np.sqrt(2.0)
        psi[1, center] = 1j / np.sqrt(2.0)

        coin = cls.hadamard_coin()

        for _ in range(steps):
            # 1. Apply Coin operator to each spatial position
            # psi[c, x]
            psi = np.einsum('ij,jx->ix', coin, psi)

            # 2. Apply Shift operator: |0> moves left (-1), |1> moves right (+1)
            new_psi = np.zeros_like(psi)
            new_psi[0, :] = np.roll(psi[0, :], -1)
            new_psi[1, :] = np.roll(psi[1, :], 1)
            psi = new_psi

        # Measurement: Born rule P(x) = |<0|psi(x)>|^2 + |<1|psi(x)>|^2
        prob = np.abs(psi[0, :])**2 + np.abs(psi[1, :])**2
        prob_sum = np.sum(prob)
        if prob_sum > 0:
            prob = prob / prob_sum
        return prob


class QuantumArnoldPermutation:
    """
    Quantum-inspired 2D Arnold Cat Map coordinate transformation.
    Unitary symplectic matrix: [ [1, p], [q, pq + 1] ] mod N
    where p, q are integers derived from session key seed.
    """

    @staticmethod
    def get_arnold_params(seed_bytes: bytes) -> Tuple[int, int, int]:
        """Derives positive integer parameters (p, q, rounds) from key seed."""
        if len(seed_bytes) < 4:
            seed_bytes = seed_bytes.ljust(4, b'\x42')
        p = 1 + (seed_bytes[0] % 5)
        q = 1 + (seed_bytes[1] % 5)
        rounds = 2 + (seed_bytes[2] % 3)  # 2 to 4 rounds
        return p, q, rounds

    @classmethod
    def permute_forward(cls, img: np.ndarray, p: int, q: int, rounds: int) -> np.ndarray:
        H, W = img.shape[:2]
        if H != W:
            # Handle non-square by tile padding or skipping permutation
            return img

        N = H
        out = img.copy()
        y_coords, x_coords = np.indices((N, N))

        for _ in range(rounds):
            # [x', y']^T = [ [1, p], [q, pq + 1] ] [x, y]^T mod N
            new_x = (x_coords + p * y_coords) % N
            new_y = (q * x_coords + (p * q + 1) * y_coords) % N
            temp = np.zeros_like(out)
            temp[new_y, new_x] = out[y_coords, x_coords]
            out = temp

        return out

    @classmethod
    def permute_inverse(cls, img: np.ndarray, p: int, q: int, rounds: int) -> np.ndarray:
        H, W = img.shape[:2]
        if H != W:
            return img

        N = H
        out = img.copy()
        y_coords, x_coords = np.indices((N, N))

        for _ in range(rounds):
            # Inverse matrix: [ [pq + 1, -p], [-q, 1] ] mod N
            new_x = ((p * q + 1) * x_coords - p * y_coords) % N
            new_y = (-q * x_coords + y_coords) % N
            temp = np.zeros_like(out)
            temp[new_y, new_x] = out[y_coords, x_coords]
            out = temp

        return out


class QuantumLayer:
    """
    Unified Optional Quantum Layer for Medical Images.
    Combines:
    1. Quantum Discrete-Time Random Walk (DTQW) Phase Diffusion Mask
    2. Quantum Arnold Symplectic Permutation
    """

    def __init__(self, enabled: bool = True):
        self.enabled = enabled

    def _generate_quantum_diffusion_mask(self, shape: Tuple[int, ...], key_seed: bytes) -> np.ndarray:
        """Generates a pseudo-quantum non-linear mask using DTQW state distribution."""
        total_pixels = int(np.prod(shape))
        steps = 40 + (key_seed[0] % 40)
        lattice_size = max(256, shape[0])
        prob = QuantumRandomWalk.simulate_walk(steps=steps, lattice_size=lattice_size)

        # Scale quantum probability up to 8-bit integer sequence
        # Use PRNG initialized with seed XOR quantum walk distribution
        seed_int = int.from_bytes(key_seed[:4], 'big') ^ int(np.sum(prob * 1e6))
        rng = np.random.RandomState(seed_int % (2**31 - 1))
        
        # Mix quantum distribution into pseudo-random byte stream
        qw_tiled = np.tile(prob, int(np.ceil(total_pixels / len(prob))))[:total_pixels]
        qw_bytes = (qw_tiled * 255.0 * 1000.0).astype(np.uint32) % 256
        rng_bytes = rng.randint(0, 256, size=total_pixels, dtype=np.uint8)
        
        diff_mask = (qw_bytes.astype(np.uint8) ^ rng_bytes).reshape(shape)
        return diff_mask

    def forward_transform(
        self,
        img: np.ndarray,
        key_seed: bytes
    ) -> Tuple[np.ndarray, Dict[str, Any], float]:
        """
        Step 5 (Sender): Forward Quantum Transformation.
        1. Coordinate permutation via Quantum Arnold Symplectic Map
        2. Non-linear diffusion via Quantum Walk Phase Mask
        """
        if not self.enabled:
            return img, {"enabled": False}, 0.0

        start = time.perf_counter()
        p, q, rounds = QuantumArnoldPermutation.get_arnold_params(key_seed)

        # 1. Permutation
        permuted = QuantumArnoldPermutation.permute_forward(img, p, q, rounds)

        # 2. Diffusion with Quantum Random Walk
        diff_mask = self._generate_quantum_diffusion_mask(img.shape, key_seed)
        transformed = np.bitwise_xor(permuted, diff_mask)

        elapsed_ms = (time.perf_counter() - start) * 1000.0
        meta = {
            "enabled": True,
            "arnold_p": p,
            "arnold_q": q,
            "arnold_rounds": rounds,
            "diffusion_method": "Hadamard-Coin-DTQW-Diffusion",
            "elapsed_ms": elapsed_ms
        }
        return transformed, meta, elapsed_ms

    def inverse_transform(
        self,
        transformed_img: np.ndarray,
        key_seed: bytes
    ) -> Tuple[np.ndarray, float]:
        """
        Step 7 (Receiver): Exact Inverse Quantum Transformation.
        1. Invert Quantum Walk Diffusion (XOR is its own inverse)
        2. Invert Quantum Arnold Coordinate Permutation
        """
        if not self.enabled:
            return transformed_img, 0.0

        start = time.perf_counter()
        p, q, rounds = QuantumArnoldPermutation.get_arnold_params(key_seed)

        # 1. Invert Diffusion
        diff_mask = self._generate_quantum_diffusion_mask(transformed_img.shape, key_seed)
        permuted = np.bitwise_xor(transformed_img, diff_mask)

        # 2. Invert Permutation
        recovered = QuantumArnoldPermutation.permute_inverse(permuted, p, q, rounds)

        elapsed_ms = (time.perf_counter() - start) * 1000.0
        return recovered, elapsed_ms

