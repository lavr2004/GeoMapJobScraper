import sqlite3
import json

import bin.parsers.urzadpracy.urzadpracy_parser


class Database_urzadpracy:
    def __init__(self, database_filepath):
        self.connection = sqlite3.connect(database_filepath)
        self.cursor = self.connection.cursor()

    def create_database(self):
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS jobs (
                id TEXT PRIMARY KEY,
                stanowisko TEXT,
                miejscePracy TEXT,
                miejscowoscId TEXT,
                miejscowoscNazwa TEXT,
                pracodawca TEXT,
                typOferty TEXT,
                rodzajUmowy TEXT,
                dataWaznOd TEXT,
                dataWaznDo TEXT,
                dataRozpoczecia TEXT,
                wymiarZatrud TEXT,
                placowkaOpis TEXT,
                dataDodaniaCbop TEXT,
                wynagrodzenie TEXT,
                zakresObowiazkow TEXT,
                wymagania TEXT,
                stopienDopasowania TEXT,
                mapaGoogleUrl TEXT,
                mapaOsmUrl TEXT,
                telefon TEXT,
                email TEXT,
                liczbaWolnychMiejscDlaNiepeln INTEGER,
                niepelnosprawni BOOLEAN,
                dlaOsobZarej BOOLEAN,
                typPropozycji TEXT,
                dodanePrzez TEXT,
                ikonyOferty TEXT,
                popularnosc TEXT,
                parseriteration_id INTEGER,
                job_latitude REAL,
                job_longitude REAL,
                job_country TEXT,
                job_locality TEXT,
                job_street TEXT,
                job_building TEXT,
                FOREIGN KEY (parseriteration_id) REFERENCES parseriteration (id)
            )
        """)

        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS parseriteration (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                parseriterationfile TEXT,
                timestamp TEXT,
                new_jobs_count INTEGER,
                response_status_code INTEGER
            )
        """)
        self.connection.commit()

    def save_parser_iteration(self, file_name, timestamp, response_status_code, new_jobs_count):
        self.cursor.execute("""
            INSERT INTO parseriteration (parseriterationfile, timestamp, response_status_code, new_jobs_count)
            VALUES (?, ?, ?, ?)
        """, (file_name, timestamp, response_status_code, new_jobs_count))
        self.connection.commit()
        return self.cursor.lastrowid

    def save_jobs_to_database(self, jobs, parseriteration_id):
        new_jobs = 0
        for job in jobs:
            try:
                self.cursor.execute("""
                    INSERT INTO jobs (
                        id, stanowisko, miejscePracy, miejscowoscId, miejscowoscNazwa, 
                        pracodawca, typOferty, rodzajUmowy, dataWaznOd, dataWaznDo, 
                        dataRozpoczecia, wymiarZatrud, placowkaOpis, dataDodaniaCbop, 
                        wynagrodzenie, zakresObowiazkow, wymagania, stopienDopasowania, 
                        mapaGoogleUrl, mapaOsmUrl, telefon, email, liczbaWolnychMiejscDlaNiepeln, 
                        niepelnosprawni, dlaOsobZarej, typPropozycji, dodanePrzez, ikonyOferty, 
                        popularnosc, parseriteration_id
                    )
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    job["id"],
                    job["stanowisko"],
                    job["miejscePracy"],
                    job.get("miejscowoscId"),
                    job.get("miejscowoscNazwa"),
                    job["pracodawca"],
                    job.get("typOferty"),
                    job.get("rodzajUmowy"),
                    job.get("dataWaznOd"),
                    job.get("dataWaznDo"),
                    job.get("dataRozpoczecia"),
                    job.get("wymiarZatrud"),
                    job.get("placowkaOpis"),
                    job.get("dataDodaniaCbop"),
                    job.get("wynagrodzenie"),
                    job.get("zakresObowiazkow"),
                    job.get("wymagania"),
                    job.get("stopienDopasowania"),
                    job.get("mapaGoogleUrl"),
                    job.get("mapaOsmUrl"),
                    job.get("telefon"),
                    job.get("email"),
                    job.get("liczbaWolnychMiejscDlaNiepeln"),
                    job.get("niepelnosprawni"),
                    job.get("dlaOsobZarej"),
                    job.get("typPropozycji"),
                    job.get("dodanePrzez"),
                    json.dumps(job.get("ikonyOferty", [])),
                    job.get("popularnosc"),
                    parseriteration_id
                ))
                new_jobs += 1

                geo_data = bin.parsers.urzadpracy.urzadpracy_parser.fetch_geolocation(job)
                if geo_data:
                    self.cursor.execute("""
                        UPDATE jobs
                        SET job_latitude = ?, job_longitude = ?, job_country = ?, job_locality = ?, job_street = ?, job_building = ?
                        WHERE id = ?
                    """, (
                        geo_data["job_latitude"],
                        geo_data["job_longitude"],
                        geo_data["job_country"],
                        geo_data["job_locality"],
                        geo_data["job_street"],
                        geo_data["job_building"],
                        job["id"]
                    ))
            except sqlite3.IntegrityError:
                continue
        self.connection.commit()
        return new_jobs

    def update_count_of_new_vacancies_added(self, new_jobs_count, parseriteration_id):
        self.cursor.execute("""
            UPDATE parseriteration
            SET new_jobs_count = ?
            WHERE id = ?
        """, (new_jobs_count, parseriteration_id))
        self.connection.commit()

    def commit_and_close(self):
        self.connection.commit()
        self.connection.close()



# import sqlite3
# import json
#
# import bin.parsers.urzadpracy.urzadpracy_parser
#
# # Функция для создания базы данных
# def create_database(database_filepath_str):
#     with sqlite3.connect(database_filepath_str) as conn:
#         cursor = conn.cursor()
#         cursor.execute("""
#             CREATE TABLE IF NOT EXISTS jobs (
#                 id TEXT PRIMARY KEY,
#                 stanowisko TEXT,
#                 miejscePracy TEXT,
#                 miejscowoscId TEXT,
#                 miejscowoscNazwa TEXT,
#                 pracodawca TEXT,
#                 typOferty TEXT,
#                 rodzajUmowy TEXT,
#                 dataWaznOd TEXT,
#                 dataWaznDo TEXT,
#                 dataRozpoczecia TEXT,
#                 wymiarZatrud TEXT,
#                 placowkaOpis TEXT,
#                 dataDodaniaCbop TEXT,
#                 wynagrodzenie TEXT,
#                 zakresObowiazkow TEXT,
#                 wymagania TEXT,
#                 stopienDopasowania TEXT,
#                 mapaGoogleUrl TEXT,
#                 mapaOsmUrl TEXT,
#                 telefon TEXT,
#                 email TEXT,
#                 liczbaWolnychMiejscDlaNiepeln INTEGER,
#                 niepelnosprawni BOOLEAN,
#                 dlaOsobZarej BOOLEAN,
#                 typPropozycji TEXT,
#                 dodanePrzez TEXT,
#                 ikonyOferty TEXT,
#                 popularnosc TEXT,
#                 parseriteration_id INTEGER,
#                 job_latitude REAL,
#                 job_longitude REAL,
#                 job_country TEXT,
#                 job_locality TEXT,
#                 job_street TEXT,
#                 job_building TEXT,
#                 FOREIGN KEY (parseriteration_id) REFERENCES parseriteration (id)
#             )
#         """)
#         cursor.execute("""
#             CREATE TABLE IF NOT EXISTS parseriteration (
#                 id INTEGER PRIMARY KEY AUTOINCREMENT,
#                 parseriterationfile TEXT,
#                 timestamp TEXT,
#                 new_jobs_count INTEGER,
#                 response_status_code INTEGER
#             )
#         """)
#         conn.commit()
#
#
# # Функция для сохранения информации о запуске парсера
# def save_parser_iteration(database_filepath_str, file_name, timestamp, response_status_code, new_jobs_count):
#     with sqlite3.connect(database_filepath_str) as conn:
#         cursor = conn.cursor()
#         cursor.execute("""
#             INSERT INTO parseriteration (parseriterationfile, timestamp, response_status_code, new_jobs_count)
#             VALUES (?, ?, ?, ?)
#         """, (file_name, timestamp, response_status_code, new_jobs_count))
#         conn.commit()
#         return cursor.lastrowid
#
# def save_jobs_to_database(database_filepath_str, jobs, parseriteration_id):
#     with sqlite3.connect(database_filepath_str) as conn:
#         cursor = conn.cursor()
#         new_jobs = 0
#         for job in jobs:
#             try:
#                 cursor.execute("""
#                     INSERT INTO jobs (
#                         id, stanowisko, miejscePracy, miejscowoscId, miejscowoscNazwa,
#                         pracodawca, typOferty, rodzajUmowy, dataWaznOd, dataWaznDo,
#                         dataRozpoczecia, wymiarZatrud, placowkaOpis, dataDodaniaCbop,
#                         wynagrodzenie, zakresObowiazkow, wymagania, stopienDopasowania,
#                         mapaGoogleUrl, mapaOsmUrl, telefon, email, liczbaWolnychMiejscDlaNiepeln,
#                         niepelnosprawni, dlaOsobZarej, typPropozycji, dodanePrzez, ikonyOferty,
#                         popularnosc, parseriteration_id
#                     )
#                     VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
#                 """, (
#                     job["id"],
#                     job["stanowisko"],
#                     job["miejscePracy"],
#                     job.get("miejscowoscId"),
#                     job.get("miejscowoscNazwa"),
#                     job["pracodawca"],
#                     job.get("typOferty"),
#                     job.get("rodzajUmowy"),
#                     job.get("dataWaznOd"),
#                     job.get("dataWaznDo"),
#                     job.get("dataRozpoczecia"),
#                     job.get("wymiarZatrud"),
#                     job.get("placowkaOpis"),
#                     job.get("dataDodaniaCbop"),
#                     job.get("wynagrodzenie"),
#                     job.get("zakresObowiazkow"),
#                     job.get("wymagania"),
#                     job.get("stopienDopasowania"),
#                     job.get("mapaGoogleUrl"),
#                     job.get("mapaOsmUrl"),
#                     job.get("telefon"),
#                     job.get("email"),
#                     job.get("liczbaWolnychMiejscDlaNiepeln"),
#                     job.get("niepelnosprawni"),
#                     job.get("dlaOsobZarej"),
#                     job.get("typPropozycji"),
#                     job.get("dodanePrzez"),
#                     json.dumps(job.get("ikonyOferty", [])),
#                     job.get("popularnosc"),
#                     parseriteration_id
#                 ))
#                 new_jobs += 1
#
#                 # Получаем геолокационные данные
#                 geo_data = bin.parsers.urzadpracy.urzadpracy_parser.fetch_geolocation(job)
#                 if geo_data:
#                     print(geo_data)
#                     cursor.execute("""
#                         UPDATE jobs
#                         SET job_latitude = ?, job_longitude = ?, job_country = ?, job_locality = ?, job_street = ?, job_building = ?
#                         WHERE id = ?
#                     """, (
#                         geo_data["job_latitude"],
#                         geo_data["job_longitude"],
#                         geo_data["job_country"],
#                         geo_data["job_locality"],
#                         geo_data["job_street"],
#                         geo_data["job_building"],
#                         job["id"]
#                     ))
#                     #input("Next...")
#             except sqlite3.IntegrityError:
#                 continue
#         conn.commit()
#     return new_jobs
#
#
# def update_count_of_new_vacancies_added(database_filepath, new_jobs_count, parseriteration_id):
#     # Обновляем количество новых вакансий в таблице parseriteration
#     with sqlite3.connect(database_filepath) as conn:
#         cursor = conn.cursor()
#         cursor.execute("""
#                 UPDATE parseriteration
#                 SET new_jobs_count = ?
#                 WHERE id = ?
#             """, (new_jobs_count, parseriteration_id))
#         conn.commit()