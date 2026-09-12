# C:\AURA_Forensics\core\generator.py
import os
import cv2
import numpy as np
import hashlib
import zipfile

# Proprietary OEM Magic Bytes
SIG_DHAV = b"\x44\x48\x41\x56"  # Dahua / CP Plus
SIG_HIKV = b"\x48\x49\x4B\x56"  # Hikvision

def generate_mock_video(filepath: str, label: str, box_coords: tuple):
    """Generates a valid 5-second MP4 test video with an annotated moving box (suspect)."""
    width, height, fps = 640, 480, 20
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter(filepath, fourcc, fps, (width, height))
    
    for frame_idx in range(fps * 5): # 100 frames = 5 seconds
        frame = np.zeros((height, width, 3), dtype=np.uint8)
        frame[:] = (30, 30, 30) # Dark background
        
        # Moving box coordinates
        x, y, w, h = box_coords
        shift_x = int(x + (frame_idx * 2))
        
        # Draw target entity
        cv2.rectangle(frame, (shift_x, y), (shift_x + w, y + h), (0, 0, 255), 2)
        cv2.putText(frame, f"AURA TARGET: {label}", (shift_x, max(20, y - 10)),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1)
        cv2.putText(frame, f"PTS: 00:00:{frame_idx//fps:02d}.{frame_idx%fps:02d}", (20, 40),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
        out.write(frame)
        
    out.release()

def create_synthetic_multicam_pack(output_dir: str):
    """Packs 3 camera streams into 3 separate zip archives simulating multi-vendor dumps."""
    os.makedirs(output_dir, exist_ok=True)
    
    cams = [
        {"name": "CAM_01_LOBBY", "oem": "Dahua", "sig": SIG_DHAV, "box": (50, 150, 80, 160), "drift": 0, "deleted": False},
        {"name": "CAM_02_CORRIDOR", "oem": "Hikvision", "sig": SIG_HIKV, "box": (100, 180, 70, 140), "drift": 0, "deleted": True},
        {"name": "CAM_03_EXIT", "oem": "Dahua", "sig": SIG_DHAV, "box": (80, 120, 90, 170), "drift": 120, "deleted": False}
    ]
    
    zip_paths = []
    
    for c in cams:
        temp_mp4 = os.path.join(output_dir, f"{c['name']}_stream.mp4")
        generate_mock_video(temp_mp4, c['name'], c['box'])
        
        with open(temp_mp4, "rb") as f:
            video_bytes = f.read()
        os.remove(temp_mp4) # Clean raw mp4
        
        # Create a raw proprietary binary disk image (.bin)
        bin_path = os.path.join(output_dir, f"{c['name']}_PHYSICAL_DUMP.bin")
        with open(bin_path, "wb") as f:
            # Write 5MB pseudo unallocated padding
            f.write(os.urandom(5 * 1024 * 1024))
            
            if c['deleted']:
                # Simulate deliberate anti-forensics wipe: 2KB of zeroes right before signature
                f.write(b"\x00" * 2048)
                
            # Write vendor signature + raw payload
            f.write(c['sig'])
            f.write(b"|PTS_OFFSET:00:00:00|RTC_DRIFT:" + str(c['drift']).encode() + b"|DATA:")
            f.write(video_bytes)
            
            # Trailing unallocated space
            f.write(os.urandom(2 * 1024 * 1024))
            
        # Package into a ZIP file for upload simulation
        zip_path = os.path.join(output_dir, f"{c['name']}_{c['oem']}_DUMP.zip")
        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            zipf.write(bin_path, arcname=os.path.basename(bin_path))
            
        os.remove(bin_path) # Retain only the uploaded zip
        zip_paths.append(zip_path)
        print(f"[+] Created synthetic archive: {zip_path}")
        
    return zip_paths

if __name__ == "__main__":
    out_dir = r"C:\AURA_Forensics\data\raw_images"
    create_synthetic_multicam_pack(out_dir)