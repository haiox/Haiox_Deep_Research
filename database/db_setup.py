import os
import sys
import sqlite3
from pathlib import Path
from dotenv import load_dotenv

sys.stdout.reconfigure(encoding='utf-8')
load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
DATA_DIR = Path(__file__).resolve().parent.parent / "data"
SQLITE_DB_PATH = DATA_DIR / "haiox_research.db"

def init_db():
    print("⏳ Initializing Research database...")
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    
    # 1. Try PostgreSQL
    if DATABASE_URL:
        try:
            import psycopg2
            print("Connecting to PostgreSQL database...")
            conn = psycopg2.connect(DATABASE_URL)
            cursor = conn.cursor()
            try:
                cursor.execute("CREATE EXTENSION IF NOT EXISTS vector;")
            except Exception:
                conn.rollback()

            cursor.execute("""
                CREATE TABLE IF NOT EXISTS projects (
                    id SERIAL PRIMARY KEY,
                    project_name VARCHAR(255) NOT NULL,
                    website_url VARCHAR(255),
                    description TEXT,
                    risk_score INTEGER,
                    analyzed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
            """)

            cursor.execute("""
                CREATE TABLE IF NOT EXISTS evidence (
                    id SERIAL PRIMARY KEY,
                    project_id INTEGER,
                    source_url VARCHAR(255),
                    content TEXT NOT NULL,
                    content_sha256 VARCHAR(64),
                    metadata JSONB,
                    extracted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
            """)

            cursor.execute("""
                CREATE TABLE IF NOT EXISTS research_reports (
                    id SERIAL PRIMARY KEY,
                    evidence_id INTEGER,
                    tokenomics JSONB,
                    risk_analysis JSONB,
                    verification_result JSONB,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
            """)

            conn.commit()
            cursor.close()
            conn.close()
            print("✅ PostgreSQL setup successful! Tables ready.")
            return
        except Exception as e:
            print(f"⚠️ PostgreSQL setup failed: {e}. Falling back to SQLite...")

    # 2. Local SQLite setup
    try:
        conn = sqlite3.connect(str(SQLITE_DB_PATH))
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS projects (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                project_name TEXT NOT NULL,
                website_url TEXT,
                description TEXT,
                risk_score REAL,
                analyzed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS evidence (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                project_id INTEGER,
                source_url TEXT,
                content TEXT NOT NULL,
                content_sha256 TEXT,
                metadata TEXT,
                extracted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)
        cursor.execute("""
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
        cursor.close()
        conn.close()
        print(f"✅ Local SQLite setup successful! Database ready at: {SQLITE_DB_PATH}")
    except Exception as e:
        print(f"❌ SQLite database setup error: {e}")

if __name__ == "__main__":
    init_db()
