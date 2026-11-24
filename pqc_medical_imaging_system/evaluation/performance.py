"""
Module 9: Performance Analysis
Benchmarks execution times, memory/key sizes, throughput (MB/s), and latency
across all cryptographic stages: Kyber KEM, Dilithium DSA, Quantum Layer, and AES-256.
"""

from typing import Dict, Any, List
import pandas as pd

class PerformanceAnalyzer:
    """Collects, aggregates, and formats system performance metrics."""

    def __init__(self):
        self.metrics: Dict[str, float] = {}

    def record_stage(self, stage_name: str, elapsed_ms: float):
        self.metrics[stage_name] = elapsed_ms

    def compute_summary(
        self,
        image_bytes_len: int,
        payload_bytes_len: int
    ) -> Dict[str, Any]:
        """
        Computes aggregate metrics, throughputs, and overheads.
        """
        # Time in seconds
        enc_time_s = max(self.metrics.get("aes_encryption_ms", 0.0) / 1000.0, 1e-6)
        dec_time_s = max(self.metrics.get("aes_decryption_ms", 0.0) / 1000.0, 1e-6)
        total_e2e_ms = sum(self.metrics.values())

        # Throughput in MB/s (1 MB = 10^6 bytes or 2^20 bytes)
        image_mb = image_bytes_len / (1024.0 * 1024.0)
        enc_throughput = image_mb / enc_time_s
        dec_throughput = image_mb / dec_time_s

        sender_time_ms = (
            self.metrics.get("kyber_encaps_ms", 0.0)
            + self.metrics.get("quantum_forward_ms", 0.0)
            + self.metrics.get("aes_encryption_ms", 0.0)
            + self.metrics.get("dilithium_sign_ms", 0.0)
        )

        receiver_time_ms = (
            self.metrics.get("kyber_decaps_ms", 0.0)
            + self.metrics.get("aes_decryption_ms", 0.0)
            + self.metrics.get("quantum_inverse_ms", 0.0)
            + self.metrics.get("dilithium_verify_ms", 0.0)
        )

        expansion_ratio = payload_bytes_len / max(image_bytes_len, 1)

        summary = {
            "stage_latencies_ms": dict(self.metrics),
            "sender_pipeline_ms": sender_time_ms,
            "receiver_pipeline_ms": receiver_time_ms,
            "total_e2e_latency_ms": total_e2e_ms,
            "encryption_throughput_mb_s": enc_throughput,
            "decryption_throughput_mb_s": dec_throughput,
            "image_size_bytes": image_bytes_len,
            "transmission_packet_size_bytes": payload_bytes_len,
            "ciphertext_expansion_ratio": expansion_ratio
        }
        return summary

    def to_dataframe(self) -> pd.DataFrame:
        """Converts stage timings to a clean DataFrame."""
        stages = []
        for k, v in self.metrics.items():
            stages.append({"Operation Stage": k.replace("_", " ").title(), "Latency (ms)": round(v, 3)})
        return pd.DataFrame(stages)

