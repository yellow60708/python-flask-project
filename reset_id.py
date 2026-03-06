import sqlite3

DB_path = r"C:\Users\user\Desktop\fast2\example.db"

conn = sqlite3.connect(DB_path)
cursor = conn.cursor()

cursor.execute("""
UPDATE sqlite_sequence
SET seq = 80888
WHERE name = 'shoesjohn'
""")

conn.commit()
conn.close()