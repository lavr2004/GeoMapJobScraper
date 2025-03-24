import sqlite3

conn = sqlite3.connect(r"D:\!DEV_APPS\000_scripts_for-different-things\001_python_scripts-for-requesting-jobs\GeoMapJobScraper\results\jobs_pracujpl_all.sqlite")
cursor = conn.cursor()

cursor.execute("PRAGMA table_info(parseiteration);")
columns = cursor.fetchall()

for col in columns:
    print(col)