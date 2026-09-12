# 🛡️ AURA-Forensics
**Automated Unallocated Recovery & Analysis Platform**  
*Developed for Smart India Hackathon (NTRO PS 26150)*

AURA-Forensics is an edge-deployed, vendor-agnostic digital forensics station designed for law enforcement. It bypasses corrupted or proprietary DVR/NVR file systems using zero-copy memory mapping to directly extract and rebuild video evidence. By integrating multimodal Vision-Language Models (VLMs) and cryptographic ledgering, AURA reduces a 14-day manual extraction cycle to 45 minutes while guaranteeing judicial admissibility.

### ⚖️ Core Capabilities
* **Zero-Copy Disk Carving:** Bypasses proprietary OS structures (Dahua/Hikvision) via `mmap` to recover deleted or orphaned H.264 video frames directly from unallocated physical sectors.
* **Explainable AI (XAI) Search:** Links VLM semantic query detections mathematically back to their raw hexadecimal Logical Block Address (LBA), eliminating "black-box" courtroom defenses.
* **Routine Activity Mapping:** Correlates spatial movement across discontinuous camera arrays to visualize suspect trajectories based on criminological Routine Activity Theory.
* **Statutory Compliance Export:** Anchors every extraction to an SQLite Merkle DAG and automatically compiles a cryptographically hashed certificate compliant with **Section 63 of the Bharatiya Sakshya Adhiniyam (BSA), 2023**.

### ⚙️ Technical Stack
* **Frontend UI:** Streamlit (Cognitive Ergonomic Dark-Slate Theme)
* **Forensic Engine:** Python `ThreadPoolExecutor`, `mmap`, `hashlib`
* **Data Processing:** OpenCV, Pandas, Plotly
* **Chain of Custody:** SQLite (Merkle DAG implementation)
* **Reporting:** FPDF2

### 🚀 Quick Start
1. Clone the repository: `git clone https://github.com/Anusha751/SIH26150-Nexora-AURA-Forensics.git`
2. Navigate to the directory: `cd AURA-Forensics`
3. Install dependencies: `pip install -r requirements.txt`
4. Create the required data directories:
   ```bash
   mkdir data\raw_images
   mkdir data\output_clips
   mkdir data\real_evidence
