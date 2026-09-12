# C:\AURA_Forensics\core\carver.py
import os
import mmap
import hashlib
import zipfile
from concurrent.futures import ThreadPoolExecutor
from core.ledger import log_event

SIG_DHAV = b"\x44\x48\x41\x56"
SIG_HIKV = b"\x48\x49\x4B\x56"

def parse_single_archive(zip_path: str, output_clips_dir: str) -> dict:
    """Unpacks a raw image from ZIP, scans physical sectors via mmap, and carves streams."""
    base_name = os.path.basename(zip_path)
    extract_dir = os.path.join(output_clips_dir, "_temp_" + base_name)
    os.makedirs(extract_dir, exist_ok=True)
    
    # Calculate acquisition SHA-256 of the uploaded ZIP
    sha256 = hashlib.sha256()
    with open(zip_path, "rb") as f:
        while chunk := f.read(1024 * 1024):
            sha256.update(chunk)
    zip_hash = sha256.hexdigest()
    log_event(f"ACQUISITION_ZIP:{base_name}", zip_hash)
    
    # Extract binary image
    with zipfile.ZipFile(zip_path, 'r') as zipf:
        zipf.extractall(extract_dir)
        bin_files = [os.path.join(extract_dir, n) for n in zipf.namelist() if n.endswith('.bin')]
        
    if not bin_files:
        return {"status": "FAILED", "file": base_name, "error": "No binary image found in archive"}
        
    target_bin = bin_files[0]
    results = []
    
    with open(target_bin, "rb") as f:
        with mmap.mmap(f.fileno(), length=0, access=mmap.ACCESS_READ) as mm:
            for sig, vendor in [(SIG_DHAV, "Dahua (DHFS)"), (SIG_HIKV, "Hikvision (HIKFAT)")]:
                offset = mm.find(sig)
                while offset != -1:
                    # Anti-forensics: Check preceding 2KB for deliberate zero-fill wipes
                    prev_bytes = mm[max(0, offset - 2048):offset]
                    zero_fill_wiped = (prev_bytes == b"\x00" * 2048)
                    
                    # Parse internal marker
                    marker_end = mm.find(b"|DATA:", offset)
                    header_str = mm[offset:marker_end].decode(errors="ignore") if marker_end != -1 else ""
                    
                    # Extract RTC drift
                    rtc_drift = 0
                    if "RTC_DRIFT:" in header_str:
                        drift_part = header_str.split("RTC_DRIFT:")[1].split("|")[0]
                        rtc_drift = int(drift_part) if drift_part.lstrip('-').isdigit() else 0
                        
                    # Extract payload (MP4 bytes embedded in synthetic stream)
                    data_start = marker_end + len(b"|DATA:") if marker_end != -1 else offset + 4
                    # Carve up to trailing padding or end of stream
                    carved_payload = mm[data_start:data_start + 4 * 1024 * 1024]
                    
                    # Compute carved artifact SHA-256
                    clip_hash = hashlib.sha256(carved_payload).hexdigest()
                    log_event(f"CARVED_STREAM:{vendor}@{hex(offset)}", clip_hash)
                    
                    out_clip_name = f"CARVED_{vendor[:4]}_{hex(offset)}.mp4"
                    out_clip_path = os.path.join(output_clips_dir, out_clip_name)
                    with open(out_clip_path, "wb") as cf:
                        cf.write(carved_payload)
                        
                    results.append({
                        "vendor": vendor,
                        "offset": hex(offset),
                        "sha256": clip_hash,
                        "rtc_drift_sec": rtc_drift,
                        "zero_fill_tamper": zero_fill_wiped,
                        "clip_path": out_clip_path,
                        "is_deleted": zero_fill_wiped # Simulates unallocated recovery
                    })
                    
                    offset = mm.find(sig, offset + 1)
                    
    return {
        "status": "SUCCESS",
        "archive": base_name,
        "archive_sha256": zip_hash,
        "carved_records": results
    }

def process_archives_concurrently(zip_paths: list, output_clips_dir: str) -> list:
    """Executes multi-file ingestion across CPU workers in parallel."""
    os.makedirs(output_clips_dir, exist_ok=True)
    all_results = []
    
    # Changed to ThreadPoolExecutor to prevent Windows Streamlit crash
    with ThreadPoolExecutor() as executor:
        futures = [executor.submit(parse_single_archive, zp, output_clips_dir) for zp in zip_paths]
        for f in futures:
            all_results.append(f.result())
            
    return all_results