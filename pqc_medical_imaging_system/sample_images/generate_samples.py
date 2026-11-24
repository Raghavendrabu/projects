"""
Script to generate synthetic medical images for testing and benchmarking:
1. Brain MRI (Axial slice)
2. Chest X-Ray (PA view)
3. Lung CT Scan (Axial thoracic slice)
4. Retinal Fundus Scan
"""

import numpy as np
import cv2
from PIL import Image
import os

def generate_brain_mri(size=256):
    img = np.zeros((size, size), dtype=np.float32)
    center = (size // 2, size // 2)
    
    # Outer skull ellipse
    y, x = np.ogrid[:size, :size]
    mask_skull = ((x - center[0])**2 / (size*0.38)**2 + (y - center[1])**2 / (size*0.44)**2) <= 1.0
    mask_inner = ((x - center[0])**2 / (size*0.35)**2 + (y - center[1])**2 / (size*0.41)**2) <= 1.0
    mask_brain = ((x - center[0])**2 / (size*0.34)**2 + (y - center[1])**2 / (size*0.40)**2) <= 1.0
    
    # Bone skull intensity
    img[mask_skull] = 0.8
    img[mask_inner] = 0.1  # CSF / space
    
    # Brain tissue (gray and white matter)
    np.random.seed(42)
    noise = cv2.GaussianBlur(np.random.rand(size, size).astype(np.float32), (15, 15), 3.0)
    gyri = np.sin(x / 4.0) * np.cos(y / 4.0) * 0.15
    brain_parenchyma = 0.55 + 0.2 * noise + gyri
    img[mask_brain] = brain_parenchyma[mask_brain]
    
    # Central longitudinal fissure
    cv2.line(img, (center[0], int(size*0.12)), (center[0], int(size*0.88)), 0.15, 2)
    
    # Lateral Ventricles (crescent butterfly shapes)
    v1_center = (int(size * 0.44), int(size * 0.48))
    v2_center = (int(size * 0.56), int(size * 0.48))
    cv2.ellipse(img, v1_center, (int(size*0.04), int(size*0.12)), -15, 0, 360, 0.1, -1)
    cv2.ellipse(img, v2_center, (int(size*0.04), int(size*0.12)), 15, 0, 360, 0.1, -1)
    
    # Smooth edges
    img = cv2.GaussianBlur(img, (3, 3), 0.5)
    img = np.clip(img * 255.0, 0, 255).astype(np.uint8)
    return img

def generate_chest_xray(size=256):
    img = np.zeros((size, size), dtype=np.float32)
    y, x = np.ogrid[:size, :size]
    center_x = size // 2
    
    # Thoracic cavity background
    cavity = ((x - center_x)**2 / (size*0.42)**2 + (y - size*0.52)**2 / (size*0.42)**2) <= 1.0
    img[cavity] = 0.15
    
    # Lungs (darker areas)
    left_lung = ((x - size*0.35)**2 / (size*0.15)**2 + (y - size*0.50)**2 / (size*0.32)**2) <= 1.0
    right_lung = ((x - size*0.65)**2 / (size*0.15)**2 + (y - size*0.50)**2 / (size*0.32)**2) <= 1.0
    img[left_lung] = 0.08
    img[right_lung] = 0.08
    
    # Spine column
    spine_mask = (np.abs(x - center_x) <= size * 0.035) & (y > size * 0.1) & (y < size * 0.9)
    img[spine_mask] += 0.35
    
    # Cardiac silhouette (heart shadow tilted left)
    heart_center = (int(size * 0.54), int(size * 0.60))
    cv2.ellipse(img, heart_center, (int(size*0.14), int(size*0.16)), -25, 0, 360, 0.5, -1)
    
    # Clavicles
    cv2.line(img, (int(size*0.15), int(size*0.22)), (int(size*0.48), int(size*0.26)), 0.65, 5)
    cv2.line(img, (int(size*0.85), int(size*0.22)), (int(size*0.52), int(size*0.26)), 0.65, 5)
    
    # Ribs
    for r in range(4, 10):
        y_pos = int(size * (0.22 + r * 0.065))
        cv2.ellipse(img, (center_x, y_pos), (int(size*0.38), int(size*0.14)), 0, 20, 160, 0.42, 3)
        
    # Vascular broncho-pulmonary markings
    np.random.seed(99)
    branch = cv2.GaussianBlur(np.random.rand(size, size).astype(np.float32), (7, 7), 1.5)
    img[left_lung | right_lung] += branch[left_lung | right_lung] * 0.18
    
    # Diaphragm domes
    cv2.ellipse(img, (int(size*0.32), int(size*0.82)), (int(size*0.18), int(size*0.12)), 0, 180, 360, 0.7, -1)
    cv2.ellipse(img, (int(size*0.68), int(size*0.84)), (int(size*0.18), int(size*0.12)), 0, 180, 360, 0.7, -1)
    
    img = cv2.GaussianBlur(img, (3, 3), 0.7)
    img = np.clip(img * 255.0, 0, 255).astype(np.uint8)
    return img

def generate_lung_ct(size=256):
    img = np.zeros((size, size), dtype=np.float32)
    center = (size // 2, size // 2)
    y, x = np.ogrid[:size, :size]
    
    # Body contour
    body = ((x - center[0])**2 / (size*0.43)**2 + (y - center[1])**2 / (size*0.37)**2) <= 1.0
    img[body] = 0.35  # soft tissue
    
    # Rib bones around chest wall
    for angle in np.linspace(0, 2*np.pi, 16, endpoint=False):
        bx = int(center[0] + size * 0.40 * np.cos(angle))
        by = int(center[1] + size * 0.34 * np.sin(angle))
        cv2.circle(img, (bx, by), 4, 0.9, -1)
        
    # Spine vertebra
    cv2.circle(img, (center[0], int(size*0.75)), int(size*0.06), 0.92, -1)
    cv2.circle(img, (center[0], int(size*0.75)), int(size*0.02), 0.1, -1)
    
    # Lungs (negative Hounsfield units / black)
    left_lung = ((x - size*0.33)**2 / (size*0.14)**2 + (y - size*0.48)**2 / (size*0.22)**2) <= 1.0
    right_lung = ((x - size*0.67)**2 / (size*0.14)**2 + (y - size*0.48)**2 / (size*0.22)**2) <= 1.0
    img[left_lung] = 0.05
    img[right_lung] = 0.05
    
    # Pulmonary vessels & bronchioles
    np.random.seed(12)
    vessels = (np.random.rand(size, size) > 0.96).astype(np.float32)
    img[left_lung | right_lung] += vessels[left_lung | right_lung] * 0.6
    
    # Mediastinum and great vessels
    cv2.ellipse(img, (center[0], int(size*0.45)), (int(size*0.08), int(size*0.14)), 0, 0, 360, 0.45, -1)
    
    img = cv2.GaussianBlur(img, (3, 3), 0.5)
    img = np.clip(img * 255.0, 0, 255).astype(np.uint8)
    return img

def generate_retinal_fundus(size=256):
    img = np.zeros((size, size), dtype=np.float32)
    center = (size // 2, size // 2)
    y, x = np.ogrid[:size, :size]
    
    # Fundus boundary (circle)
    circle = ((x - center[0])**2 + (y - center[1])**2) <= (size*0.45)**2
    img[circle] = 0.45
    
    # Optic disc (bright circle)
    disc_center = (int(size * 0.35), int(size * 0.50))
    cv2.circle(img, disc_center, int(size * 0.08), 0.85, -1)
    
    # Macula (dark spot)
    macula_center = (int(size * 0.62), int(size * 0.50))
    cv2.circle(img, macula_center, int(size * 0.05), 0.25, -1)
    
    # Branching vessels
    for angle in np.linspace(-np.pi/3, np.pi/3, 7):
        ex = int(disc_center[0] + size * 0.5 * np.cos(angle))
        ey = int(disc_center[1] + size * 0.5 * np.sin(angle))
        cv2.line(img, disc_center, (ex, ey), 0.22, 2)
        # bifurcations
        cv2.line(img, (int((disc_center[0]+ex)/2), int((disc_center[1]+ey)/2)), 
                 (int(ex*0.9), int(ey*1.1)), 0.22, 1)

    img = cv2.GaussianBlur(img, (3, 3), 0.6)
    img = np.clip(img * 255.0, 0, 255).astype(np.uint8)
    return img

if __name__ == "__main__":
    out_dir = r"c:\Projects\pqc_medical_imaging_system\sample_images"
    os.makedirs(out_dir, exist_ok=True)
    
    samples = {
        "brain_mri.png": generate_brain_mri(),
        "chest_xray.png": generate_chest_xray(),
        "lung_ct.png": generate_lung_ct(),
        "retinal_fundus.png": generate_retinal_fundus(),
    }
    
    for filename, data in samples.items():
        filepath = os.path.join(out_dir, filename)
        Image.fromarray(data).save(filepath)
        print(f"Generated sample image: {filepath} ({data.shape}, min={data.min()}, max={data.max()})")

