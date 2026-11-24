"""
CLI Benchmark Runner for Post-Quantum Medical Image Transmission System
Processes all sample images across multiple Kyber parameter sets (512, 768, 1024),
evaluates Performance (Step 9), Quality (Step 10), and Security (Step 11).
"""

import os
import sys
import time
import json
import pandas as pd
import numpy as np

# Add project root to sys.path
PROJECT_ROOT = os.path.abspath(os.path.dirname(__file__))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from pipeline import PQCMedicalPipeline

def run_all_benchmarks():
    samples_dir = os.path.join(PROJECT_ROOT, "sample_images")
    image_files = [
        "brain_mri.png",
        "chest_xray.png",
        "lung_ct.png",
        "retinal_fundus.png"
    ]

    print("=" * 80)
    print("      POST-QUANTUM MEDICAL IMAGE TRANSMISSION SYSTEM BENCHMARK")
    print("=" * 80)

    results = []

    for img_name in image_files:
        img_path = os.path.join(samples_dir, img_name)
        if not os.path.exists(img_path):
            print(f"[!] Warning: Image {img_path} not found. Skipping.")
            continue

        for variant in ["Kyber512", "Kyber768"]:
            for q_layer in [True, False]:
                q_label = "Quantum ON" if q_layer else "Quantum OFF"
                print(f"\n[*] Running pipeline on {img_name} | {variant} | {q_label}...")

                pipeline = PQCMedicalPipeline(
                    kyber_variant=variant,
                    dilithium_variant="Dilithium2",
                    aes_mode="GCM",
                    enable_quantum_layer=q_layer
                )

                rep = pipeline.run(
                    image_source=img_path,
                    target_size=(256, 256),
                    as_grayscale=True,
                    simulate_network_delay_ms=10.0,
                    tamper_mode=None
                )

                q_metrics = rep["quality"]["recovery_metrics"]
                perf = rep["performance"]
                sec = rep["security"]

                row = {
                    "Image": img_name.replace(".png", "").replace("_", " ").title(),
                    "PQC Variant": variant,
                    "Quantum Layer": q_label,
                    "PSNR (dB)": q_metrics["psnr_db"],
                    "SSIM": round(q_metrics["ssim"], 4),
                    "MSE": q_metrics["mse"],
                    "Enc Entropy": round(sec["shannon_entropy"]["encrypted"], 4),
                    "Orig Corr (Avg)": round(sec["pixel_correlation"]["original"]["average"], 4),
                    "Enc Corr (Avg)": round(sec["pixel_correlation"]["encrypted"]["average"], 4),
                    "NPCR (%)": round(sec["differential_attack"]["npcr_percent"], 2),
                    "UACI (%)": round(sec["differential_attack"]["uaci_percent"], 2),
                    "Enc Throughput (MB/s)": round(perf["encryption_throughput_mb_s"], 2),
                    "Total Latency (ms)": round(perf["total_e2e_latency_ms"], 2),
                    "Integrity Verified": rep["verification"]["integrity_verified"]
                }
                results.append(row)

    df = pd.DataFrame(results)
    print("\n" + "=" * 80)
    print("                         COMPREHENSIVE BENCHMARK RESULTS")
    print("=" * 80)
    print(df.to_string(index=False))

    # Save CSV and JSON report
    report_csv = os.path.join(PROJECT_ROOT, "benchmark_report.csv")
    df.to_csv(report_csv, index=False)
    print(f"\n[+] Benchmark CSV saved to: {report_csv}")

    return df

if __name__ == "__main__":
    run_all_benchmarks()

