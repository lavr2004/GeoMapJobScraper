import sqlite3
import os
from datetime import datetime
from bin.settings import FOLDERPATH_RESULTS_ALL

BASE_DIR = FOLDERPATH_RESULTS_ALL
OUTPUT_DB = os.path.join(BASE_DIR, "combined_jobs.sqlite")

COMMON_FIELDS = [
    'id', 'title', 'employer', 'salary', 'latitude', 'longitude', 'address',
    'date_added', 'date_parsing', 'source', 'parseiteration_id', 'processed_iteration_id'
]

def create_combined_database():
    conn = sqlite3.connect(OUTPUT_DB)
    cursor = conn.cursor()

    # Обновляем таблицу jobs с новым полем processed_iteration_id
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS jobs (
            id TEXT PRIMARY KEY,
            title TEXT,
            employer TEXT,
            salary TEXT,
            latitude REAL,
            longitude REAL,
            address TEXT,
            date_added TEXT,
            date_parsing TEXT,
            source TEXT,
            parseiteration_id INTEGER,  -- Оригинальный parseiteration_id из источника
            processed_iteration_id INTEGER,  -- Новый внешний ключ на processed_iterations
            FOREIGN KEY (processed_iteration_id) REFERENCES processed_iterations(id)
        )
    ''')

    # Обновляем таблицу processed_iterations с новым уникальным id
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS processed_iterations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,  -- Уникальный ID для каждой записи
            source TEXT,
            parseiteration_id INTEGER,  -- Оригинальный parseiteration_id из источника
            timestamp TEXT
        )
    ''')

    conn.commit()
    conn.close()

def get_latest_iteration(db_path):
    conn = sqlite3.connect(OUTPUT_DB)
    cursor = conn.cursor()
    source = os.path.basename(db_path)
    # Получаем максимальный parseiteration_id для данного источника
    cursor.execute('SELECT MAX(parseiteration_id) FROM processed_iterations WHERE source = ?', (source,))
    result = cursor.fetchone()[0]
    conn.close()
    return result if result else 0

def process_database(db_path):
    source = os.path.basename(db_path)
    last_processed_iteration = get_latest_iteration(db_path)

    src_conn = sqlite3.connect(db_path)
    src_cursor = src_conn.cursor()

    src_cursor.execute('SELECT MAX(id) FROM parseiteration')
    max_iteration = src_cursor.fetchone()[0] or 0

    if max_iteration <= last_processed_iteration:
        src_conn.close()
        return 0

    src_cursor.execute("PRAGMA table_info(jobs)")
    columns = [col[1] for col in src_cursor.fetchall()]

    field_mapping = {}
    if 'stanowisko' in columns:  # jobs_urzadpracy.sqlite
        field_mapping = {
            'id': 'id',
            'title': 'stanowisko',
            'employer': 'pracodawca',
            'salary': 'wynagrodzenie',
            'latitude': 'job_latitude',
            'longitude': 'job_longitude',
            'address': "miejscePracy || ', ' || miejscowoscNazwa",
            'date_added': 'dataDodaniaCbop',
            'parseiteration_id': 'parseiteration_id'
        }
    elif 'job_title' in columns:  # jobs_pracujpl_all.sqlite
        field_mapping = {
            'id': 'id',
            'title': 'job_title',
            'employer': 'company_name',
            'salary': 'salary',
            'latitude': 'job_latitude',
            'longitude': 'job_longitude',
            'address': "job_street || ', ' || job_locality",
            'date_added': 'last_publicated',
            'parseiteration_id': 'parseiteration_id'
        }

    # Извлекаем новые вакансии с датой парсинга из parseiteration
    query = f"""
        SELECT j.{', j.'.join(field_mapping.values())}, p.timestamp
        FROM jobs j
        JOIN parseiteration p ON j.parseiteration_id = p.id
        WHERE j.parseiteration_id > ?
    """
    src_cursor.execute(query, (last_processed_iteration,))
    new_jobs = src_cursor.fetchall()

    dest_conn = sqlite3.connect(OUTPUT_DB)
    dest_cursor = dest_conn.cursor()

    # Сначала добавляем запись в processed_iterations и получаем её id
    dest_cursor.execute('''
        INSERT INTO processed_iterations (source, parseiteration_id, timestamp)
        VALUES (?, ?, ?)
    ''', (source, max_iteration, datetime.now().isoformat()))
    processed_iteration_id = dest_cursor.lastrowid  # Получаем уникальный id новой записи

    # Добавляем вакансии с привязкой к processed_iteration_id
    for job in new_jobs:
        values = {
            'id': job[0],
            'title': job[1],
            'employer': job[2],
            'salary': job[3],
            'latitude': job[4],
            'longitude': job[5],
            'address': job[6],
            'date_added': job[7],
            'date_parsing': job[9],  # timestamp из parseiteration
            'source': source,
            'parseiteration_id': job[8],  # Оригинальный parseiteration_id
            'processed_iteration_id': processed_iteration_id  # Ссылка на processed_iterations
        }

        dest_cursor.execute('''
            INSERT OR IGNORE INTO jobs (id, title, employer, salary, latitude, longitude, address, date_added, date_parsing, source, parseiteration_id, processed_iteration_id)
            VALUES (:id, :title, :employer, :salary, :latitude, :longitude, :address, :date_added, :date_parsing, :source, :parseiteration_id, :processed_iteration_id)
        ''', values)

    dest_conn.commit()
    src_conn.close()
    dest_conn.close()

    return len(new_jobs)

def combine_databases():
    create_combined_database()
    processed_count = 0
    for filename in os.listdir(BASE_DIR):
        if filename.endswith('.sqlite') and filename != 'combined_jobs.sqlite':
            db_path = os.path.join(BASE_DIR, filename)
            print(f"Processing {filename}...")
            count = process_database(db_path)
            processed_count += count
            print(f"Added {count} new jobs from {filename}")
    print(f"Total new jobs added: {processed_count}")

if __name__ == "__main__":
    combine_databases()



# import sqlite3
# import os
# from datetime import datetime
# from bin.settings import FOLDERPATH_RESULTS_ALL
#
# #BASE_DIR = r"D:\!DEV_APPS\000_scripts_for-different-things\001_python_scripts-for-requesting-jobs\GeoMapJobScraper\results"
# BASE_DIR = FOLDERPATH_RESULTS_ALL
# OUTPUT_DB = os.path.join(BASE_DIR, "combined_jobs.sqlite")
#
# COMMON_FIELDS = [
#     'id', 'title', 'employer', 'salary', 'latitude', 'longitude', 'address',
#     'date_added', 'date_parsing', 'source', 'parseiteration_id'
# ]
#
# def create_combined_database():
#     conn = sqlite3.connect(OUTPUT_DB)
#     cursor = conn.cursor()
#
#     cursor.execute('''
#         CREATE TABLE IF NOT EXISTS jobs (
#             id TEXT PRIMARY KEY,
#             title TEXT,
#             employer TEXT,
#             salary TEXT,
#             latitude REAL,
#             longitude REAL,
#             address TEXT,
#             date_added TEXT,
#             date_parsing TEXT,  -- Новое поле для даты парсинга
#             source TEXT,
#             parseiteration_id INTEGER
#         )
#     ''')
#
#     cursor.execute('''
#         CREATE TABLE IF NOT EXISTS processed_iterations (
#             source TEXT,
#             parseiteration_id INTEGER,
#             timestamp TEXT,
#             PRIMARY KEY (source, parseiteration_id)
#         )
#     ''')
#
#     conn.commit()
#     conn.close()
#
# def get_latest_iteration(db_path):
#     conn = sqlite3.connect(OUTPUT_DB)
#     cursor = conn.cursor()
#     source = os.path.basename(db_path)
#     cursor.execute('SELECT MAX(parseiteration_id) FROM processed_iterations WHERE source = ?', (source,))
#     result = cursor.fetchone()[0]
#     conn.close()
#     return result if result else 0
#
# def process_database(db_path):
#     source = os.path.basename(db_path)
#     last_processed_iteration = get_latest_iteration(db_path)
#
#     src_conn = sqlite3.connect(db_path)
#     src_cursor = src_conn.cursor()
#
#     src_cursor.execute('SELECT MAX(id) FROM parseiteration')
#     max_iteration = src_cursor.fetchone()[0] or 0
#
#     if max_iteration <= last_processed_iteration:
#         src_conn.close()
#         return 0
#
#     src_cursor.execute("PRAGMA table_info(jobs)")
#     columns = [col[1] for col in src_cursor.fetchall()]
#
#     field_mapping = {}
#     if 'stanowisko' in columns:  # jobs_urzadpracy.sqlite
#         field_mapping = {
#             'id': 'id',
#             'title': 'stanowisko',
#             'employer': 'pracodawca',
#             'salary': 'wynagrodzenie',
#             'latitude': 'job_latitude',
#             'longitude': 'job_longitude',
#             'address': "miejscePracy || ', ' || miejscowoscNazwa",
#             'date_added': 'dataDodaniaCbop',
#             'parseiteration_id': 'parseiteration_id'
#         }
#     elif 'job_title' in columns:  # jobs_pracujpl_all.sqlite
#         field_mapping = {
#             'id': 'id',
#             'title': 'job_title',
#             'employer': 'company_name',
#             'salary': 'salary',
#             'latitude': 'job_latitude',
#             'longitude': 'job_longitude',
#             'address': "job_street || ', ' || job_locality",
#             'date_added': 'last_publicated',
#             'parseiteration_id': 'parseiteration_id'
#         }
#
#     # Извлекаем новые вакансии с датой парсинга из parseiteration
#     query = f"""
#         SELECT j.{', j.'.join(field_mapping.values())}, p.timestamp
#         FROM jobs j
#         JOIN parseiteration p ON j.parseiteration_id = p.id
#         WHERE j.parseiteration_id > ?
#     """
#     src_cursor.execute(query, (last_processed_iteration,))
#     new_jobs = src_cursor.fetchall()
#
#     dest_conn = sqlite3.connect(OUTPUT_DB)
#     dest_cursor = dest_conn.cursor()
#
#     for job in new_jobs:
#         values = {
#             'id': job[0],
#             'title': job[1],
#             'employer': job[2],
#             'salary': job[3],
#             'latitude': job[4],
#             'longitude': job[5],
#             'address': job[6],
#             'date_added': job[7],
#             'date_parsing': job[9],  # timestamp из parseiteration
#             'source': source,
#             'parseiteration_id': job[8]
#         }
#
#         dest_cursor.execute('''
#             INSERT OR IGNORE INTO jobs (id, title, employer, salary, latitude, longitude, address, date_added, date_parsing, source, parseiteration_id)
#             VALUES (:id, :title, :employer, :salary, :latitude, :longitude, :address, :date_added, :date_parsing, :source, :parseiteration_id)
#         ''', values)
#
#     dest_cursor.execute('''
#         INSERT OR REPLACE INTO processed_iterations (source, parseiteration_id, timestamp)
#         VALUES (?, ?, ?)
#     ''', (source, max_iteration, datetime.now().isoformat()))
#
#     dest_conn.commit()
#     src_conn.close()
#     dest_conn.close()
#
#     return len(new_jobs)
#
# def combine_databases():
#     create_combined_database()
#     processed_count = 0
#     for filename in os.listdir(BASE_DIR):
#         if filename.endswith('.sqlite') and filename != 'combined_jobs.sqlite':
#             db_path = os.path.join(BASE_DIR, filename)
#             print(f"Processing {filename}...")
#             count = process_database(db_path)
#             processed_count += count
#             print(f"Added {count} new jobs from {filename}")
#     print(f"Total new jobs added: {processed_count}")
#
# if __name__ == "__main__":
#     combine_databases()