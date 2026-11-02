"""Forensic analysis script for SQLite databases in SWMS."""

import sqlite3
from pathlib import Path
import bcrypt

db_paths = [
    Path("swms_dev.db"),
    Path("backend/swms_dev.db"),
]

for db_path in db_paths:
    print(f"\n=======================================================")
    print(f"DATABASE PATH: {db_path.resolve()} (Exists: {db_path.exists()})")
    print(f"=======================================================")
    if not db_path.exists():
        continue

    conn = sqlite3.connect(str(db_path))
    cursor = conn.cursor()

    # 1. Tables list
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name;")
    tables = [r[0] for r in cursor.fetchall()]
    print(f"Tables Found ({len(tables)}): {tables}")

    for t in tables:
        print(f"\n--- TABLE: {t} ---")
        cursor.execute(f"PRAGMA table_info('{t}');")
        cols = cursor.fetchall()
        for col in cols:
            cid, name, col_type, notnull, dflt_value, pk = col
            print(f"  Column: {name:<20} Type: {col_type:<15} PK: {pk} NotNull: {notnull} Default: {dflt_value}")

        cursor.execute(f"SELECT COUNT(*) FROM '{t}';")
        count = cursor.fetchone()[0]
        print(f"  Total Rows: {count}")

        if count > 0:
            cursor.execute(f"SELECT * FROM '{t}' LIMIT 5;")
            rows = cursor.fetchall()
            print(f"  Sample Rows (up to 5):")
            col_names = [c[1] for c in cols]
            for r in rows:
                row_dict = dict(zip(col_names, r))
                # Truncate password_hash display for cleanliness
                if "password_hash" in row_dict and row_dict["password_hash"]:
                    row_dict["password_hash_prefix"] = row_dict["password_hash"][:15] + "..."
                    del row_dict["password_hash"]
                print(f"    {row_dict}")

    # Specific forensic validation for users table
    if "users" in tables:
        print(f"\n[FORENSIC USER CHECK on {db_path.name}]:")
        cursor.execute("SELECT email, password_hash, role, is_active FROM users;")
        users = cursor.fetchall()
        for email, pwhash, role, active in users:
            is_bcrypt = pwhash.startswith("$2b$") or pwhash.startswith("$2a$")
            valid_admin = False
            valid_user = False
            if email == "admin@bilcode.id":
                valid_admin = bcrypt.checkpw(b"Admin123!", pwhash.encode("utf-8"))
            elif email == "user@bilcode.id":
                valid_user = bcrypt.checkpw(b"User123!", pwhash.encode("utf-8"))
            print(f"  User: {email} | Role: {role} | Active: {active} | IsBcrypt: {is_bcrypt} | MatchSeedPW: {valid_admin or valid_user}")

    conn.close()
