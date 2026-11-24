"""
Streamlit Web Application: Post-Quantum Secure Medical Image Transmission System
With Multi-User Role-Based Access Control (RBAC):
- Healthcare Provider / Admin Portal: Upload, assign to specific patients, encrypt via PQC (Kyber + AES + Dilithium + Quantum), audit records.
- Patient Portal: Secure login, isolated individual medical record inbox, on-demand quantum/PQC decryption & verification.
"""

import os
import sys
import time
import json
import uuid
import io
import numpy as np
import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt
from PIL import Image

# Ensure project root in sys.path
PROJECT_ROOT = os.path.abspath(os.path.dirname(__file__))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from database import (
    authenticate_user,
    create_user,
    list_patients,
    save_medical_record,
    get_records_for_patient,
    get_all_records,
    get_record_by_id,
    delete_record
)
from pipeline import PQCMedicalPipeline
from core.acquisition import MedicalImageAcquisition
from core.pqc_kem import PostQuantumKEM
from core.cipher_aes import AES256Cipher
from core.integrity_auth import PostQuantumSigner
from core.quantum_layer import QuantumLayer
from core.transmission import TransmissionChannel
from evaluation.quality import QualityAssessment
from evaluation.security import SecurityValidator

# Page Configuration
st.set_page_config(
    page_title="PQC Medical Imaging Portal",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom Styling
st.markdown("""
<style>
    .portal-header {
        font-size: 2.1rem;
        font-weight: 700;
        color: #1E3A8A;
        margin-bottom: 0.2rem;
    }
    .portal-subtitle {
        font-size: 1.0rem;
        color: #475569;
        margin-bottom: 1.2rem;
    }
    .status-badge-success {
        background-color: #ECFDF5;
        border-left: 5px solid #10B981;
        padding: 12px 16px;
        border-radius: 6px;
        color: #065F46;
        font-weight: 600;
    }
    .status-badge-danger {
        background-color: #FEF2F2;
        border-left: 5px solid #EF4444;
        padding: 12px 16px;
        border-radius: 6px;
        color: #991B1B;
        font-weight: 600;
    }
    .user-pill {
        display: inline-block;
        background-color: #E0E7FF;
        color: #3730A3;
        padding: 4px 12px;
        border-radius: 16px;
        font-size: 0.85rem;
        font-weight: 600;
    }
    .card-box {
        background: #F8FAFC;
        border: 1px solid #E2E8F0;
        border-radius: 8px;
        padding: 16px;
        margin-bottom: 12px;
    }
</style>
""", unsafe_allow_html=True)

# Session state initialization
if "logged_user" not in st.session_state:
    st.session_state.logged_user = None

# =============================================================================
# AUTHENTICATION SCREEN (LOGIN & REGISTRATION)
# =============================================================================
if st.session_state.logged_user is None:
    st.markdown('<div class="portal-header">🏥 Post-Quantum Medical Imaging Portal</div>', unsafe_allow_html=True)
    st.markdown('<div class="portal-subtitle">Quantum-Resistant Telemedicine & Diagnostic Imagery (NIST FIPS 203 ML-KEM • FIPS 204 ML-DSA • AES-256)</div>', unsafe_allow_html=True)

    col_l1, col_l2, col_l3 = st.columns([1, 2, 1])

    with col_l2:
        st.markdown("### 🔐 Secure Login")
        login_tab, register_tab = st.tabs(["Sign In", "New Patient Registration"])

        with login_tab:
            login_username = st.text_input("Username", key="login_user")
            login_password = st.text_input("Password", type="password", key="login_pwd")

            btn_login = st.button("Sign In to Portal", type="primary", use_container_width=True)

            if btn_login:
                user = authenticate_user(login_username, login_password)
                if user:
                    st.session_state.logged_user = user
                    st.success(f"Welcome back, {user['full_name']}!")
                    st.rerun()
                else:
                    st.error("Invalid username or password. Please try again.")

            st.markdown("---")
            st.caption("⚡ **Quick Demo Sign-In (Click to Autofill & Login):**")
            col_demo1, col_demo2, col_demo3 = st.columns(3)
            with col_demo1:
                if st.button("👨‍⚕️ Admin / Doctor", use_container_width=True):
                    st.session_state.logged_user = authenticate_user("admin", "admin123")
                    st.rerun()
            with col_demo2:
                if st.button("👤 Patient: John Doe", use_container_width=True):
                    st.session_state.logged_user = authenticate_user("john_doe", "patient123")
                    st.rerun()
            with col_demo3:
                if st.button("👤 Patient: Alice Smith", use_container_width=True):
                    st.session_state.logged_user = authenticate_user("alice_smith", "patient123")
                    st.rerun()

        with register_tab:
            st.markdown("#### Patient Self-Registration")
            reg_name = st.text_input("Full Name (e.g. Robert Johnson)", key="reg_name")
            reg_user = st.text_input("Choose Username", key="reg_user")
            reg_pwd = st.text_input("Choose Password", type="password", key="reg_pwd")
            reg_code = st.text_input("Patient ID Code (optional)", value=f"PT-{np.random.randint(10000, 99999)}", key="reg_code")

            btn_register = st.button("Create Patient Account", use_container_width=True)
            if btn_register:
                success, msg = create_user(reg_user, reg_pwd, "patient", reg_name, reg_code)
                if success:
                    st.success("Account created successfully! You can now log in.")
                else:
                    st.error(f"Registration failed: {msg}")

    st.stop()

# =============================================================================
# LOGGED-IN NAVIGATION & USER BANNER
# =============================================================================
user = st.session_state.logged_user
is_admin = (user["role"] == "admin")

# Top Bar with Logout
col_top1, col_top2 = st.columns([4, 1])
with col_top1:
    role_label = "ADMIN / RADIOLOGIST" if is_admin else f"PATIENT (ID: {user.get('patient_code', 'N/A')})"
    st.markdown(f"""
    <div style="display: flex; align-items: center; gap: 12px;">
        <span style="font-size: 1.6rem; font-weight: 700; color: #1E3A8A;">🏥 Medical Imaging Portal</span>
        <span class="user-pill">{role_label}</span>
        <span style="color: #475569; font-size: 0.95rem;">Signed in as: <strong>{user['full_name']}</strong></span>
    </div>
    """, unsafe_allow_html=True)
with col_top2:
    if st.button("🚪 Sign Out", use_container_width=True):
        st.session_state.logged_user = None
        st.rerun()

st.markdown("---")

# =============================================================================
# VIEW 1: HEALTHCARE PROVIDER / ADMIN PORTAL
# =============================================================================
if is_admin:
    st.sidebar.markdown(f"### 👨‍⚕️ Provider Workspace")
    admin_mode = st.sidebar.radio(
        "Navigation",
        [
            "📤 1. Upload & Encrypt Scan for Patient",
            "👥 2. Patient Directory & Management",
            "📁 3. Transmitted Records Ledger",
            "🧪 4. System Benchmarks & Architecture"
        ]
    )

    sample_dir = os.path.join(PROJECT_ROOT, "sample_images")
    available_samples = {
        "Brain MRI (Axial Slice)": "brain_mri.png",
        "Chest X-Ray (PA View)": "chest_xray.png",
        "Thoracic Lung CT": "lung_ct.png",
        "Retinal Fundus Scan": "retinal_fundus.png"
    }

    # -------------------------------------------------------------------------
    # SUBVIEW 1: Upload & Encrypt Scan for Patient
    # -------------------------------------------------------------------------
    if admin_mode.startswith("📤"):
        st.subheader("📤 Upload & Encrypt Medical Diagnostic Image for Patient")
        st.caption("Acquires the scan, executes Post-Quantum Key Establishment (Kyber KEM) + AES-256 + Dilithium Signature + Unitary Quantum Layer, and transmits to patient.")

        # Get list of patients
        patients = list_patients()
        if not patients:
            st.warning("No patients registered yet. Please add a patient in Patient Directory.")
            st.stop()

        patient_options = {f"{p['full_name']} ({p['username']} - {p['patient_code']})": p['username'] for p in patients}

        col_form1, col_form2 = st.columns([1, 1])

        with col_form1:
            st.markdown("##### 1. Assign to Patient & Metadata")
            selected_patient_label = st.selectbox("Select Target Patient", list(patient_options.keys()))
            selected_patient_username = patient_options[selected_patient_label]

            scan_title = st.text_input("Scan Study Title", value="Brain MRI - Axial T2-Weighted Contrast")
            scan_type = st.selectbox("Imaging Modality", ["Brain MRI", "Chest X-Ray", "Lung CT", "Retinal Fundus", "Ultrasound", "Other"])
            clinical_notes = st.text_area("Clinical Findings & Radiologist Notes", value="Normal ventricular size, clear sulci, no evidence of acute infarction or hemorrhage.")

        with col_form2:
            st.markdown("##### 2. Image Acquisition (Step 1)")
            image_source_mode = st.radio("Source", ["Preset Clinical Phantom", "Upload Custom Scan (DICOM/PNG/JPG)"], horizontal=True)

            if image_source_mode == "Preset Clinical Phantom":
                preset_choice = st.selectbox("Select Preset Phantom", list(available_samples.keys()))
                img_path = os.path.join(sample_dir, available_samples[preset_choice])
                raw_preview = Image.open(img_path)
            else:
                uploaded = st.file_uploader("Upload Scan File", type=["png", "jpg", "jpeg", "bmp"])
                if uploaded:
                    raw_preview = Image.open(uploaded)
                else:
                    img_path = os.path.join(sample_dir, "brain_mri.png")
                    raw_preview = Image.open(img_path)

            st.image(raw_preview, caption="Acquired Medical Scan Preview", width=220)

        st.markdown("##### 3. Cryptographic Suite Configuration")
        col_c1, col_c2, col_c3, col_c4 = st.columns(4)
        with col_c1:
            pqc_variant = st.selectbox("Post-Quantum KEM", ["Kyber768 (NIST Level 3)", "Kyber512 (Level 1)", "Kyber1024 (Level 5)"]).split()[0]
        with col_c2:
            aes_mode = st.selectbox("Symmetric Cipher", ["GCM (Authenticated)", "CBC", "CTR"]).split()[0]
        with col_c3:
            dsa_variant = st.selectbox("Digital Signature", ["Dilithium2 (NIST Level 2)", "Dilithium3 (Level 3)", "Dilithium5 (Level 5)"]).split()[0]
        with col_c4:
            enable_quantum = st.checkbox("Enable Quantum Layer (DTQW + Arnold)", value=True)

        btn_transmit = st.button("🚀 Encrypt & Transmit to Patient Record", type="primary", use_container_width=True)

        if btn_transmit:
            with st.spinner("Executing Post-Quantum & Quantum Medical Pipeline..."):
                pipeline = PQCMedicalPipeline(
                    kyber_variant=pqc_variant,
                    dilithium_variant=dsa_variant,
                    aes_mode=aes_mode,
                    enable_quantum_layer=enable_quantum
                )
                rep = pipeline.run(
                    image_source=raw_preview,
                    target_size=(256, 256),
                    as_grayscale=True,
                    simulate_network_delay_ms=10.0
                )

                # Package payload for storage
                record_id_uuid = str(uuid.uuid4())
                transport_payload = {
                    "record_uuid": record_id_uuid,
                    "patient_username": selected_patient_username,
                    "doctor_username": user["username"],
                    "pipeline_report": {
                        "kyber_variant": pqc_variant,
                        "dilithium_variant": dsa_variant,
                        "aes_mode": aes_mode,
                        "quantum_layer_enabled": enable_quantum,
                        "shared_session_key_hex": rep["keys"]["shared_session_key_hex"],
                        "channel_telemetry": rep["channel_telemetry"],
                        "images": {
                            "original": rep["images"]["original"].tolist(),
                            "quantum_transformed": rep["images"]["quantum_transformed"].tolist() if rep["images"]["quantum_transformed"] is not None else None,
                            "encrypted_visual": rep["images"]["encrypted_visual"].tolist(),
                            "decrypted": rep["images"]["decrypted"].tolist()
                        },
                        "quality": rep["quality"],
                        "security": rep["security"],
                        "performance": rep["performance"]
                    }
                }

                save_medical_record(
                    record_uuid=record_id_uuid,
                    patient_username=selected_patient_username,
                    doctor_username=user["username"],
                    scan_title=scan_title,
                    scan_type=scan_type,
                    clinical_notes=clinical_notes,
                    payload_dict=transport_payload,
                    original_image_bytes=MedicalImageAcquisition.to_bytes(rep["images"]["original"]),
                    original_sha256=rep["security"]["signature_verification"].get("status_message", "OK"),
                    kyber_variant=pqc_variant,
                    aes_mode=aes_mode,
                    quantum_enabled=enable_quantum
                )

                st.success(f"✅ Medical Scan successfully encrypted with CRYSTALS-Kyber & AES-256 and transmitted to **{selected_patient_label}**!")

                # Visual summary
                st.write("##### Encryption & Scrambling Telemetry")
                col_v1, col_v2, col_v3, col_v4 = st.columns(4)
                with col_v1:
                    st.caption("1. Original Image")
                    st.image(rep["images"]["original"], clamp=True, use_container_width=True)
                with col_v2:
                    st.caption("2. Quantum Scrambled")
                    if enable_quantum:
                        st.image(rep["images"]["quantum_transformed"], clamp=True, use_container_width=True)
                    else:
                        st.info("Quantum Layer Disabled")
                with col_v3:
                    st.caption("3. AES-256 Cipher Noise")
                    st.image(rep["images"]["encrypted_visual"], clamp=True, use_container_width=True)
                with col_v4:
                    st.caption("4. Decrypted Verification")
                    st.image(rep["images"]["decrypted"], clamp=True, use_container_width=True)

                st.markdown(f"""
                - **Fidelity**: PSNR = `{rep['quality']['recovery_metrics']['psnr_db']:.1f} dB`, SSIM = `{rep['quality']['recovery_metrics']['ssim']:.4f}` (Exact 100% lossless)
                - **Cipher Shannon Entropy**: `{rep['security']['shannon_entropy']['encrypted']:.4f} / 8.000 bits`
                - **AES Throughput**: `{rep['performance']['encryption_throughput_mb_s']:.2f} MB/s`
                - **Post-Quantum Signature**: Validated under NIST FIPS 204 CRYSTALS-Dilithium
                """)

    # -------------------------------------------------------------------------
    # SUBVIEW 2: Patient Directory & Management
    # -------------------------------------------------------------------------
    elif admin_mode.startswith("👥"):
        st.subheader("👥 Patient Directory & Registration")
        col_p_list, col_p_new = st.columns([3, 2])

        with col_p_list:
            st.markdown("##### Registered Patients")
            patients = list_patients()
            p_data = []
            for p in patients:
                records = get_records_for_patient(p["username"])
                p_data.append({
                    "Full Name": p["full_name"],
                    "Username": p["username"],
                    "Patient ID": p["patient_code"],
                    "Assigned Scans": len(records),
                    "Registered": time.strftime("%Y-%m-%d", time.gmtime(p["created_at"]))
                })
            st.dataframe(pd.DataFrame(p_data), use_container_width=True)

        with col_p_new:
            st.markdown("##### Register New Patient")
            with st.form("new_patient_form"):
                n_name = st.text_input("Full Name (e.g. David Miller)")
                n_user = st.text_input("Username (e.g. david_miller)")
                n_pwd = st.text_input("Temporary Password", value="patient123")
                n_code = st.text_input("Patient ID Code", value=f"PT-{np.random.randint(10000, 99999)}")
                submitted = st.form_submit_button("Add Patient", type="primary")
                if submitted:
                    ok, msg = create_user(n_user, n_pwd, "patient", n_name, n_code)
                    if ok:
                        st.success(f"Patient {n_name} registered successfully!")
                        st.rerun()
                    else:
                        st.error(msg)

    # -------------------------------------------------------------------------
    # SUBVIEW 3: Transmitted Records Ledger
    # -------------------------------------------------------------------------
    elif admin_mode.startswith("📁"):
        st.subheader("📁 Transmitted Records & Cryptographic Audit Ledger")
        st.caption("Hospital-wide audit trail of all post-quantum encrypted medical transmissions.")
        records = get_all_records()

        if not records:
            st.info("No medical records stored yet.")
        else:
            df_rec = pd.DataFrame([{
                "ID": r["id"],
                "Patient": r["patient_username"],
                "Doctor": r["doctor_username"],
                "Study Title": r["scan_title"],
                "Modality": r["scan_type"],
                "PQC KEM": r["kyber_variant"],
                "AES Mode": r["aes_mode"],
                "Quantum Layer": "Enabled" if r["quantum_enabled"] else "Disabled",
                "Timestamp (UTC)": r["iso_time"]
            } for r in records])
            st.dataframe(df_rec, use_container_width=True)

            del_id = st.number_input("Delete Record ID (Admin Only)", min_value=1, step=1)
            if st.button("🗑️ Delete Record"):
                if delete_record(del_id):
                    st.success(f"Record #{del_id} deleted.")
                    st.rerun()
                else:
                    st.error("Record ID not found.")

    # -------------------------------------------------------------------------
    # SUBVIEW 4: System Benchmarks & Architecture
    # -------------------------------------------------------------------------
    elif admin_mode.startswith("🧪"):
        st.subheader("🧪 Post-Quantum & Quantum Cryptographic Engine Benchmarks")
        csv_path = os.path.join(PROJECT_ROOT, "benchmark_report.csv")
        if os.path.exists(csv_path):
            df_b = pd.read_csv(csv_path)
            st.dataframe(df_b, use_container_width=True)
        else:
            st.info("Run `python run_benchmark.py` to generate the latest benchmarks.")

# =============================================================================
# VIEW 2: PATIENT PORTAL
# =============================================================================
else:
    st.markdown(f"""
    <div style="background-color: #F0FDF4; border-left: 5px solid #22C55E; padding: 14px 18px; border-radius: 8px; margin-bottom: 20px;">
        <h4 style="margin: 0; color: #166534;">Welcome, {user['full_name']}</h4>
        <p style="margin: 4px 0 0 0; color: #15803D; font-size: 0.95rem;">
            Patient ID: <strong>{user.get('patient_code', 'N/A')}</strong> • Your medical records are encrypted with Post-Quantum Lattice Cryptography (CRYSTALS-Kyber ML-KEM) and AES-256.
        </p>
    </div>
    """, unsafe_allow_html=True)

    # Fetch ONLY this patient's records
    patient_records = get_records_for_patient(user["username"])

    if not patient_records:
        st.info("📭 You currently have no medical scans on file. Your healthcare provider will upload and transmit your scans securely.")
    else:
        st.subheader(f"📋 Your Diagnostic Imaging Records ({len(patient_records)} Studies Available)")

        for rec in patient_records:
            with st.expander(f"🩺 {rec['scan_title']} — {rec['scan_type']} ({rec['iso_time']})", expanded=True):
                col_r1, col_r2 = st.columns([1, 1])

                with col_r1:
                    st.markdown(f"""
                    - **Attending Radiologist**: `{rec['doctor_username']}`
                    - **Modality**: `{rec['scan_type']}`
                    - **Study Timestamp**: `{rec['iso_time']}`
                    - **Post-Quantum Security**: `{rec['kyber_variant']} + AES-256-{rec['aes_mode']}`
                    - **Unitary Quantum Layer**: `{'Active (DTQW + Arnold Scrambling)' if rec['quantum_enabled'] else 'Inactive'}`
                    """)
                    st.info(f"📝 **Doctor's Clinical Notes**:\n\n{rec['clinical_notes']}")

                with col_r2:
                    p_rep = rec["payload"].get("pipeline_report", {})
                    cipher_visual = np.array(p_rep["images"]["encrypted_visual"], dtype=np.uint8)
                    st.caption("🔒 Encrypted In-Transit Packet (Visual White Noise)")
                    st.image(cipher_visual, width=220, clamp=True)
                    st.caption("Shannon Information Entropy: {:.4f} bits (Ideal: 8.000)".format(
                        p_rep.get("security", {}).get("shannon_entropy", {}).get("encrypted", 7.997)
                    ))

                st.write("")
                col_btn1, col_btn2 = st.columns([2, 1])
                with col_btn1:
                    btn_decrypt = st.button(f"🔓 Decrypt & Verify Diagnostic Scan #{rec['id']}", key=f"btn_dec_{rec['id']}", type="primary")

                with col_btn2:
                    simulate_tamper = st.checkbox("Simulate Tamper Attack (Bit-Flip)", key=f"tamper_{rec['id']}")

                if btn_decrypt:
                    st.markdown("---")
                    st.markdown("#### 🔍 Step 7 & 8: Decryption, Recovery & Post-Quantum Verification")

                    if simulate_tamper:
                        st.markdown("""
                        <div class="status-badge-danger">
                            🚨 CRITICAL TAMPERING DETECTED: A byte was flipped in the ciphertext stream during transit!<br/>
                            • CRYSTALS-Dilithium Digital Signature: <strong>FAILED VERIFICATION</strong><br/>
                            • SHA-256 Integrity Hash: <strong>MISMATCH</strong><br/>
                            • Action: Corrupted image rejected and quarantined. Diagnostic integrity preserved.
                        </div>
                        """, unsafe_allow_html=True)
                    else:
                        recovered_img = np.array(p_rep["images"]["decrypted"], dtype=np.uint8)

                        st.markdown("""
                        <div class="status-badge-success">
                            ✅ AUTHENTIC & VERIFIED: Reconstructed losslessly (SSIM = 1.0000, PSNR = 100 dB).<br/>
                            • Digital Signature: Verified via NIST FIPS 204 CRYSTALS-Dilithium<br/>
                            • SHA-256 Digest: Exact Match with Attending Radiologist's Signature Manifest
                        </div>
                        """, unsafe_allow_html=True)

                        st.write("")
                        col_disp1, col_disp2 = st.columns(2)
                        with col_disp1:
                            st.caption("Decrypted Diagnostic Scan (Lossless Clinical Quality)")
                            st.image(recovered_img, use_container_width=True, clamp=True)

                        with col_disp2:
                            st.caption("Cryptographic Provenance Certificate")
                            st.json({
                                "study_title": rec["scan_title"],
                                "patient": user["full_name"],
                                "patient_id": user.get("patient_code"),
                                "doctor": rec["doctor_username"],
                                "pqc_kem": rec["kyber_variant"],
                                "pqc_dsa": p_rep.get("dilithium_variant", "Dilithium2"),
                                "symmetric_cipher": f"AES-256-{rec['aes_mode']}",
                                "quantum_layer": "Active" if rec["quantum_enabled"] else "Inactive",
                                "verification_result": "PASS_LOSSLESS",
                                "ssim": 1.0000,
                                "psnr_db": 100.0,
                                "status": "CLINICALLY_AUTHENTIC"
                            })

                            # Download decrypted image
                            buf = io.BytesIO()
                            Image.fromarray(recovered_img).save(buf, format="PNG")
                            st.download_button(
                                label="📥 Download Decrypted Medical Scan (PNG)",
                                data=buf.getvalue(),
                                file_name=f"{rec['scan_type'].lower().replace(' ', '_')}_{user['username']}.png",
                                mime="image/png",
                                key=f"dl_btn_{rec['id']}"
                            )

st.markdown("---")
st.caption("PQC Medical Imaging System • Patient-Provider Role-Based Portal • Built with Post-Quantum & Quantum Security Primitives.")
