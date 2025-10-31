#!/usr/bin/env python3
import sqlite3
import os

# Nếu bạn lưu script vào repository root, dùng đường dẫn bên dưới:
DB_PATH = os.path.join('LibraryManageSystem', 'instance', 'library.db')
# Nếu bạn lưu script vào thư mục LibraryManageSystem thì thay bằng:
# DB_PATH = os.path.join(os.path.dirname(__file__), 'instance', 'library.db')

DB_PATH = os.path.normpath(DB_PATH)

if not os.path.exists(DB_PATH):
    print(f"Database not found: {DB_PATH}")
    raise SystemExit(1)

conn = sqlite3.connect(DB_PATH)
conn.row_factory = sqlite3.Row
cur = conn.cursor()

# Lấy danh sách bảng (loại trừ bảng nội bộ sqlite_)
cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%';")
tables = [r['name'] for r in cur.fetchall()]

print(f"Connected to: {DB_PATH}")
print(f"Found tables: {tables}\n")

for table in tables:
    print(f"--- Table: {table} ---")
    cur.execute(f"PRAGMA table_info('{table}');")
    cols = [r['name'] for r in cur.fetchall()]
    print("Columns:", cols)
    try:
        cur.execute(f"SELECT * FROM '{table}' LIMIT 5;")
        rows = cur.fetchall()
        if not rows:
            print("(no rows)")
        else:
            for r in rows:
                rowd = {k: r[k] for k in r.keys()}
                print(rowd)
    except Exception as e:
        print("Failed to read rows:", e)
    print()

conn.close()