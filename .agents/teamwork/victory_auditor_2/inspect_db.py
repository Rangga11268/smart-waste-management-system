import sqlite3
import os
import bcrypt

print("--- RAW SQLITE FORENSICS ---")
for db_rel in ["swms_dev.db", "backend/swms_dev.db"]:
    db_path = os.path.join(r"D:\Ngoding\interviewWeb\BillcodeTech", db_rel)
    if os.path.exists(db_path):
        print(f"\nExamining Database: {db_path}")
        conn = sqlite3.connect(db_path)
        cur = conn.cursor()
        cur.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = [r[0] for r in cur.fetchall()]
        print("Tables Found:", tables)
        
        # Check categories
        if "categories" in tables:
            cur.execute("SELECT id, slug, name, badge_color FROM categories")
            cats = cur.fetchall()
            print(f"Categories ({len(cats)} rows):")
            for c in cats:
                print(f"  id={c[0]}, slug={c[1]}, name={c[2]}, badge_color={c[3]}")
                
        # Check users
        if "users" in tables:
            cur.execute("SELECT id, email, role, is_active, password_hash FROM users")
            users = cur.fetchall()
            print(f"Users ({len(users)} rows):")
            for u in users:
                pw_hash = u[4]
                # verify seed passwords
                admin_pw_ok = bcrypt.checkpw(b"Admin123!", pw_hash.encode("utf-8")) if u[1] == "admin@bilcode.id" else None
                user_pw_ok = bcrypt.checkpw(b"User123!", pw_hash.encode("utf-8")) if u[1] == "user@bilcode.id" else None
                print(f"  email={u[1]}, role={u[2]}, active={u[3]}, hash={pw_hash[:15]}...")
                if admin_pw_ok is not None:
                    print(f"    Admin123! matches hash: {admin_pw_ok}")
                if user_pw_ok is not None:
                    print(f"    User123! matches hash: {user_pw_ok}")

        conn.close()
