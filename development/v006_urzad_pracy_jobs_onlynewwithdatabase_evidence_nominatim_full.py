import requests
import sqlite3
import json
import os
from datetime import datetime

from urllib.parse import unquote, urlparse, parse_qs, quote

COUNT_OF_JOBS_TO_REQUEST = 500

# Константы
DATABASE_FILE = "jobs.db"
API_URL = f"https://oferty.praca.gov.pl/portal-api/v3/oferta/wyszukiwanie?page=0&size={COUNT_OF_JOBS_TO_REQUEST}&sort=dataDodania,desc"
HEADERS = {
    "Accept": "*/*",
    "Content-Type": "application/json",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
}
DATA = {
    "miejscowosci": [{"miejscowoscId": "0918123", "zasieg": 0}],
    "kodJezyka": "PL",
    "kodyPocztoweId": ["01-107"],
}
NOMINATIM_URL = "http://localhost:8080/search"  # Укажите адрес вашего локального сервера Nominatim


# Функция для создания базы данных
def create_database():
    with sqlite3.connect(DATABASE_FILE) as conn:
        cursor = conn.cursor()
        cursor.execute("""
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
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS parseriteration (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                parseriterationfile TEXT,
                timestamp TEXT,
                new_jobs_count INTEGER,
                response_status_code INTEGER
            )
        """)
        conn.commit()



# Функция для вызова Nominatim
def fetch_geolocation(job):
    url = job.get("mapaGoogleUrl", "")
    if not url:
        url = job.get("mapaOsmUrl", "")
        if not url:
            return None
    
    parsed_url = urlparse(url)
    query_params = parse_qs(parsed_url.query)
    if 'query' not in query_params and "q" not in query_params:
        #address = job("miejscePracy","Warsazawa, Polska")
        return None
        print(f"Адрес не извлечен из ссылки, но предустановлен")
    else:
        address_raw = unquote(query_params['q'][0])  # Декодируем адрес из URL
        print(f"Извлеченный адрес: {address_raw}")
        if address_raw:
            # Декодируем URL-кодирование

            # Удаляем запятые
            cleaned_string = address_raw.replace(",", "")

            # Разделяем на слова
            words = cleaned_string.split()

            # Оставляем только последние вхождения слов
            unique_words = {}
            for i, word in enumerate(words):
                unique_words[word] = i  # Сохраняем индекс последнего вхождения

            # Сортируем слова по их индексу появления и формируем результат
            address_unquote = " ".join(sorted(unique_words, key=unique_words.get))
            address_quote = quote(address_unquote, safe="")
        

    params = {"q": address_unquote, "format": "json", "addressdetails": 1}
    headers = {
        'User-Agent': 'NonameApp/1.0 (lavr2004@gmail.com)'  # Укажите свои данные
    }
    response = requests.get(NOMINATIM_URL, params=params, headers=headers)
    #urltorequest = f"{NOMINATIM_URL}?{parsed_url.query}&format=json"
    #response = requests.get(urltorequest, headers=headers)
    if response.status_code == 200:
        data = response.json()
        data2 = response.text
        if data:
            return {
                "job_latitude": data[0].get("lat"),
                "job_longitude": data[0].get("lon"),
                "job_country": data[0]["address"].get("country"),
                "job_locality": data[0]["address"].get("city", data[0]["address"].get("town", data[0]["address"].get("village"))),
                "job_street": data[0]["address"].get("road"),
                "job_building": data[0]["address"].get("house_number"),
            }
    return None


# Функция для сохранения информации о запуске парсера
def save_parser_iteration(file_name, timestamp, response_status_code, new_jobs_count):
    with sqlite3.connect(DATABASE_FILE) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO parseriteration (parseriterationfile, timestamp, response_status_code, new_jobs_count)
            VALUES (?, ?, ?, ?)
        """, (file_name, timestamp, response_status_code, new_jobs_count))
        conn.commit()
        return cursor.lastrowid

def save_jobs_to_database(jobs, parseriteration_id):
    with sqlite3.connect(DATABASE_FILE) as conn:
        cursor = conn.cursor()
        new_jobs = 0
        for job in jobs:
            try:
                cursor.execute("""
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

                # Получаем геолокационные данные
                geo_data = fetch_geolocation(job)
                if geo_data:
                    print(geo_data)
                    cursor.execute("""
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
                    #input("Next...")
            except sqlite3.IntegrityError:
                continue
        conn.commit()
    return new_jobs



# Функция для сохранения вакансий в базу данных
# def save_jobs_to_database(jobs, parseriteration_id):
#     with sqlite3.connect(DATABASE_FILE) as conn:
#         cursor = conn.cursor()
#         new_jobs = 0
#         for job in jobs:
#             try:
#                 # Сохраняем основную информацию о вакансии
#                 cursor.execute("""
#                     INSERT INTO jobs (id, stanowisko, miejscePracy, pracodawca, dataDodaniaCbop, 
#                                       dataWaznOd, dataWaznDo, wynagrodzenie, zakresObowiazkow, parseriteration_id)
#                     VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
#                 """, (
#                     job["id"],
#                     job["stanowisko"],
#                     job["miejscePracy"],
#                     job["pracodawca"],
#                     job["dataDodaniaCbop"],
#                     job["dataWaznOd"],
#                     job["dataWaznDo"],
#                     job["wynagrodzenie"],
#                     job.get("zakresObowiazkow", ""),
#                     parseriteration_id
#                 ))
#                 new_jobs += 1

#                 # Получаем геолокационные данные
#                 address = job.get("miejscePracy", "")
#                 geo_data = fetch_geolocation(address)
#                 if geo_data:
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
#             except sqlite3.IntegrityError:
#                 continue
#         conn.commit()
#     return new_jobs


# Основная функция
def main():
    create_database()

    response = requests.post(API_URL, headers=HEADERS, json=DATA)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    file_name = f"jobs_{timestamp}.json"

    if response.status_code == 200:
        data = response.json()
        jobs = data.get("payload", {}).get("ofertyPracyPage", {}).get("content", [])
        
        # Сохраняем JSON-файл
        os.makedirs("job_data", exist_ok=True)
        with open(f"job_data/{file_name}", "w", encoding="utf-8") as fw:
            json.dump(jobs, fw, ensure_ascii=False, indent=4)

        # Сохраняем информацию о запуске парсера
        parseriteration_id = save_parser_iteration(file_name, timestamp, response.status_code, 0)
        
        # Сохраняем вакансии
        new_jobs_count = save_jobs_to_database(jobs, parseriteration_id)

        # Обновляем количество новых вакансий в таблице parseriteration
        with sqlite3.connect(DATABASE_FILE) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE parseriteration
                SET new_jobs_count = ?
                WHERE id = ?
            """, (new_jobs_count, parseriteration_id))
            conn.commit()

        print(f"Данные успешно обработаны. Добавлено новых вакансий: {new_jobs_count}")
    else:
        print(f"Ошибка запроса: {response.status_code}")
        save_parser_iteration(file_name, timestamp, response.status_code, 0)


if __name__ == "__main__":
    main()
