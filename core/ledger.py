# C:\AURA_Forensics\core\ledger.py
import sqlite3
import hashlib
from datetime import datetime
from typing import List, Dict

DB_PATH = r"C:\AURA_Forensics\data\aura_forensics.db"

class MerkleDAGNode:
    def __init__(self, action: str, data_hash: str, parent_hash: str = ""):
        self.timestamp = datetime.utcnow().isoformat() + "Z"
        self.action = action
        self.data_hash = data_hash
        self.parent_hash = parent_hash
        self.node_hash = self._calc_hash()

    def _calc_hash(self) -> str:
        payload = f"{self.timestamp}|{self.action}|{self.data_hash}|{self.parent_hash}"
        return hashlib.sha256(payload.encode()).hexdigest()

def init_ledger():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS evidence_ledger (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT,
            action TEXT,
            data_hash TEXT,
            parent_hash TEXT,
            node_hash TEXT
        )
    """)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS carved_evidence (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            camera_id TEXT,
            vendor TEXT,
            sector_offset TEXT,
            status TEXT,
            tamper_flag TEXT,
            rtc_drift_sec INTEGER,
            sha256 TEXT,
            file_path TEXT
        )
    """)
    conn.commit()
    conn.close()

def log_event(action: str, data_hash: str) -> str:
    init_ledger()
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    
    cur.execute("SELECT node_hash FROM evidence_ledger ORDER BY id DESC LIMIT 1")
    row = cur.fetchone()
    parent_hash = row[0] if row else "0000000000000000000000000000000000000000000000000000000000000000"
    
    node = MerkleDAGNode(action, data_hash, parent_hash)
    cur.execute("""
        INSERT INTO evidence_ledger (timestamp, action, data_hash, parent_hash, node_hash)
        VALUES (?, ?, ?, ?, ?)
    """, (node.timestamp, node.action, node.data_hash, node.parent_hash, node.node_hash))
    
    conn.commit()
    conn.close()
    return node.node_hash

def get_ledger_history() -> List[Dict]:
    init_ledger()
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("SELECT timestamp, action, data_hash, parent_hash, node_hash FROM evidence_ledger ORDER BY id ASC")
    rows = cur.fetchall()
    conn.close()
    return [
        {"timestamp": r[0], "action": r[1], "data_hash": r[2], "parent_hash": r[3], "node_hash": r[4]}
        for r in rows
    ]