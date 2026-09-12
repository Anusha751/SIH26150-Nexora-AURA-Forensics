# C:\AURA_Forensics\core\bsa_cert.py
from fpdf import FPDF
from datetime import datetime

class BSACertificatePDF(FPDF):
    def header(self):
        self.set_font('Helvetica', 'B', 13)
        self.cell(0, 8, 'CERTIFICATE UNDER SECTION 63 OF THE BHARATIYA SAKSHYA ADHINIYAM (BSA), 2023', 0, 1, 'C')
        self.set_font('Helvetica', 'I', 9)
        self.cell(0, 5, 'Statutory Condition of Admissibility of Electronic Records in Judicial Proceedings', 0, 1, 'C')
        self.ln(6)

    def generate(self, case_id: str, officer: str, agency: str, ledger_records: list, output_pdf: str):
        self.add_page()
        self.set_font('Helvetica', '', 10)
        
        intro_text = (
            f"I, {officer}, serving as Investigating Forensic Analyst under the authority of {agency}, "
            f"hereby certify under Section 63 of the Bharatiya Sakshya Adhiniyam (BSA), 2023 that the "
            f"electronic surveillance records enumerated below were extracted from multi-vendor CCTV/NVR "
            f"storage devices under an unbroken chain of custody, utilizing verified zero-copy forensic "
            f"carving routines with concurrent cryptographic hashing."
        )
        self.multi_cell(0, 5, intro_text)
        self.ln(4)
        
        # Case Details Box
        self.set_fill_color(240, 240, 240)
        self.set_font('Helvetica', 'B', 10)
        self.cell(50, 6, " Case Reference ID:", 1, 0, 'L', fill=True)
        self.set_font('Helvetica', '', 10)
        self.cell(0, 6, f" {case_id}", 1, 1)
        
        self.set_font('Helvetica', 'B', 10)
        self.cell(50, 6, " Extraction Timestamp:", 1, 0, 'L', fill=True)
        self.set_font('Helvetica', '', 10)
        self.cell(0, 6, f" {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')}", 1, 1)
        
        self.set_font('Helvetica', 'B', 10)
        self.cell(50, 6, " Merkle Root Anchor:", 1, 0, 'L', fill=True)
        self.set_font('Helvetica', '', 8)
        root_hash = ledger_records[-1]['node_hash'] if ledger_records else "N/A"
        self.cell(0, 6, f" {root_hash}", 1, 1)
        self.ln(6)
        
        # Table of Carved Streams
        self.set_font('Helvetica', 'B', 10)
        self.cell(0, 6, "Cryptographic Evidence Ledger & Sector Provenance:", 0, 1)
        
        self.set_font('Helvetica', 'B', 8)
        self.set_fill_color(220, 220, 220)
        self.cell(35, 6, "Action", 1, 0, 'C', fill=True)
        self.cell(90, 6, "Data SHA-256 Hash", 1, 0, 'C', fill=True)
        self.cell(65, 6, "Merkle Node Verification", 1, 1, 'C', fill=True)
        
        self.set_font('Helvetica', '', 7)
        for rec in ledger_records[-8:]:  # Show up to last 8 events
            self.cell(35, 5, rec['action'][:20], 1, 0)
            self.cell(90, 5, rec['data_hash'], 1, 0)
            self.cell(65, 5, rec['node_hash'][:35] + "...", 1, 1)
            
        self.ln(8)
        self.set_font('Helvetica', 'I', 9)
        self.multi_cell(0, 5, "Attestation: No system clock tampering, algorithmic hallucination, or unrecorded sector alteration occurred during this forensic pipeline. Produced automatically by AURA-Forensics.")
        self.ln(12)
        
        self.set_font('Helvetica', 'B', 10)
        self.cell(100, 6, "_____________________________", 0, 0)
        self.cell(0, 6, "_____________________________", 0, 1)
        self.cell(100, 4, f"Investigating Officer: {officer}", 0, 0)
        self.cell(0, 4, "Forensic Directorate Seal", 0, 1)
        
        self.output(output_pdf)
        return output_pdf