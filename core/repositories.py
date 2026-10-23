import json
import os
import sqlite3
import datetime
from pathlib import Path
from typing import Optional, Dict, Any
from dotenv import load_dotenv

load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")

DATA_DIR = Path(__file__).resolve().parent.parent / "data"
EVIDENCE_DIR = DATA_DIR / "evidence"
SQLITE_DB_PATH = DATA_DIR / "haiox_research.db"


def _ensure_local_dirs():
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    EVIDENCE_DIR.mkdir(parents=True, exist_ok=True)


def _init_sqlite_db():
    _ensure_local_dirs()
    conn = sqlite3.connect(str(SQLITE_DB_PATH))
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS evidence (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            project_id INTEGER,
            source_url TEXT,
            content TEXT,
            content_sha256 TEXT,
            metadata TEXT,
            extracted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    """)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS research_reports (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            evidence_id INTEGER,
            tokenomics TEXT,
            risk_analysis TEXT,
            verification_result TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(evidence_id) REFERENCES evidence(id)
        );
    """)
    conn.commit()
    conn.close()


def get_pg_connection():
    if not DATABASE_URL:
        return None
    try:
        import psycopg2
        conn = psycopg2.connect(DATABASE_URL, connect_timeout=3)
        return conn
    except Exception:
        return None


def save_evidence(
    project_id: int, 
    source_url: str, 
    raw_content: str, 
    sha256: Optional[str] = None, 
    metadata: Optional[Dict[str, Any]] = None
) -> Optional[int]:
    """
    Stores raw data in Postgres if available, otherwise falls back gracefully to SQLite and local disk.
    """
    _ensure_local_dirs()
    
    # 1. Try PostgreSQL if DATABASE_URL is configured
    pg_conn = get_pg_connection()
    if pg_conn:
        try:
            with pg_conn.cursor() as cur:
                try:
                    cur.execute("""
                        INSERT INTO evidence (project_id, source_url, content, content_sha256, metadata)
                        VALUES (%s, %s, %s, %s, %s)
                        RETURNING id;
                    """, (1, source_url, raw_content, sha256 or "", json.dumps(metadata or {})))
                except Exception:
                    pg_conn.rollback()
                    cur.execute("""
                        INSERT INTO evidence (project_id, source_url, content)
                        VALUES (%s, %s, %s)
                        RETURNING id;
                    """, (1, source_url, raw_content))
                
                evidence_id = cur.fetchone()[0]
                pg_conn.commit()
                print(f"✅ [Repository:Postgres] Evidence saved successfully! Evidence ID: {evidence_id}")
                return evidence_id
        except Exception as e:
            print(f"⚠️ [Repository:Postgres] Failed to write to Postgres: {e}. Falling back to SQLite...")
        finally:
            pg_conn.close()

    # 2. SQLite Local Fallback
    try:
        _init_sqlite_db()
        conn = sqlite3.connect(str(SQLITE_DB_PATH))
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO evidence (project_id, source_url, content, content_sha256, metadata)
            VALUES (?, ?, ?, ?, ?);
        """, (project_id or 1, source_url, raw_content, sha256 or "", json.dumps(metadata or {})))
        evidence_id = cur.lastrowid
        conn.commit()
        conn.close()

        # Save local JSON artifact for direct provenance verification
        audit_file = EVIDENCE_DIR / f"evidence_{evidence_id}.json"
        with open(audit_file, "w", encoding="utf-8") as f:
            json.dump({
                "id": evidence_id,
                "project_id": project_id,
                "source_url": source_url,
                "content_sha256": sha256,
                "extracted_at": datetime.datetime.utcnow().isoformat(),
                "content_preview": raw_content[:500] if raw_content else "",
                "metadata": metadata or {}
            }, f, indent=2)

        print(f"✅ [Repository:SQLite] Evidence saved locally! Evidence ID: {evidence_id}")
        return evidence_id

    except Exception as e:
        print(f"❌ [Repository:SQLite] Local storage fallback error: {e}")
        return None


def get_evidence_by_id(evidence_id: int) -> Optional[Dict[str, Any]]:
    """
    Retrieves evidence by ID from Postgres or SQLite fallback.
    """
    pg_conn = get_pg_connection()
    if pg_conn:
        try:
            with pg_conn.cursor() as cur:
                cur.execute("SELECT id, project_id, source_url, content FROM evidence WHERE id = %s;", (evidence_id,))
                row = cur.fetchone()
                if row:
                    return {
                        "id": row[0],
                        "project_id": row[1],
                        "source_url": row[2],
                        "content": row[3]
                    }
        except Exception as e:
            print(f"⚠️ [Repository:Postgres] Error fetching evidence: {e}. Trying SQLite...")
        finally:
            pg_conn.close()

    # Fallback SQLite
    try:
        _init_sqlite_db()
        conn = sqlite3.connect(str(SQLITE_DB_PATH))
        cur = conn.cursor()
        cur.execute("SELECT id, project_id, source_url, content, content_sha256, metadata FROM evidence WHERE id = ?;", (evidence_id,))
        row = cur.fetchone()
        conn.close()

        if row:
            meta = {}
            if row[5]:
                try:
                    meta = json.loads(row[5])
                except Exception:
                    meta = {}
            return {
                "id": row[0],
                "project_id": row[1],
                "source_url": row[2],
                "content": row[3],
                "content_sha256": row[4],
                "metadata": meta
            }
        return None
    except Exception as e:
        print(f"❌ [Repository:SQLite] Error fetching evidence: {e}")
        return None


def save_research_report(
    evidence_id: int, 
    tokenomics: dict, 
    risk: dict, 
    verification: dict
) -> Optional[int]:
    """
    Stores the final verified report in Postgres or SQLite fallback.
    """
    pg_conn = get_pg_connection()
    if pg_conn:
        try:
            with pg_conn.cursor() as cur:
                cur.execute("""
                    INSERT INTO research_reports (evidence_id, tokenomics, risk_analysis, verification_result)
                    VALUES (%s, %s, %s, %s)
                    RETURNING id;
                """, (
                    evidence_id, 
                    json.dumps(tokenomics), 
                    json.dumps(risk), 
                    json.dumps(verification)
                ))
                report_id = cur.fetchone()[0]
                pg_conn.commit()
                print(f"💾 [Repository:Postgres] Research Report saved! Report ID: {report_id}")
                return report_id
        except Exception as e:
            print(f"⚠️ [Repository:Postgres] Error saving research report: {e}. Trying SQLite...")
        finally:
            pg_conn.close()

    # Fallback SQLite
    try:
        _init_sqlite_db()
        conn = sqlite3.connect(str(SQLITE_DB_PATH))
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO research_reports (evidence_id, tokenomics, risk_analysis, verification_result)
            VALUES (?, ?, ?, ?);
        """, (
            evidence_id,
            json.dumps(tokenomics),
            json.dumps(risk),
            json.dumps(verification)
        ))
        report_id = cur.lastrowid
        conn.commit()
        conn.close()
        print(f"💾 [Repository:SQLite] Research Report saved locally! Report ID: {report_id}")
        return report_id
    except Exception as e:
        print(f"❌ [Repository:SQLite] Error saving report locally: {e}")
        return None
