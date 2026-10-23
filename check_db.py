import os
import sys
import psycopg2
import sqlite3
from pathlib import Path
from dotenv import load_dotenv

sys.stdout.reconfigure(encoding='utf-8')

load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")
SQLITE_DB_PATH = Path(__file__).resolve().parent / "data" / "haiox_research.db"

def check_db():
    print("🔍 Fetching data from research evidence repository...\n")
    
    # 1. Check PostgreSQL if configured
    if DATABASE_URL:
        try:
            print("Trying PostgreSQL / Supabase connection...")
            conn = psycopg2.connect(DATABASE_URL, connect_timeout=3)
            cursor = conn.cursor()
            cursor.execute("SELECT id, project_id, source_url, content, extracted_at FROM evidence ORDER BY id DESC LIMIT 3;")
            rows = cursor.fetchall()
            print("🔹 Source: PostgreSQL")
            _print_rows(rows)
            cursor.close()
            conn.close()
            return
        except Exception as e:
            print(f"⚠️ PostgreSQL check failed: {e}. Falling back to SQLite...")

    # 2. Check SQLite
    if SQLITE_DB_PATH.exists():
        try:
            conn = sqlite3.connect(str(SQLITE_DB_PATH))
            cursor = conn.cursor()
            cursor.execute("SELECT id, project_id, source_url, content, extracted_at, content_sha256 FROM evidence ORDER BY id DESC LIMIT 3;")
            rows = cursor.fetchall()
            print(f"🔹 Source: Local SQLite ({SQLITE_DB_PATH})")
            if not rows:
                print("📭 Table is empty! Nothing saved yet.")
            else:
                for row in rows:
                    print(f"🔹 ID: {row[0]} | Project: {row[1]} | URL: {row[2]}")
                    print(f"   🕒 Time: {row[4]}")
                    print(f"   🔒 SHA-256: {row[5] if len(row) > 5 else 'N/A'}")
                    print(f"   📄 Content Snippet: {row[3][:100]}...\n")
            cursor.close()
            conn.close()
        except Exception as e:
            print(f"❌ SQLite database error: {e}")
    else:
        print("📭 No local SQLite database found at:", SQLITE_DB_PATH)

def _print_rows(rows):
    if not rows:
        print("📭 Table is empty! Nothing saved yet.")
    else:
        for row in rows:
            print(f"🔹 ID: {row[0]} | Project: {row[1]} | URL: {row[2]}")
            print(f"   🕒 Time: {row[4]}")
            print(f"   📄 Content Snippet: {row[3][:100]}...\n")

if __name__ == "__main__":
    check_db()
