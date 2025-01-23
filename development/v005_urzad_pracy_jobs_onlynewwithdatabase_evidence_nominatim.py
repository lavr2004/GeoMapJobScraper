import requests
import sqlite3
import json
import os
from datetime import datetime

# Константы
DATABASE_FILE = "jobs.db"
API_URL = "https://oferty.praca.gov.pl/portal-api/v3/oferta/wyszukiwanie?page=0&size=100&sort=dataDodania,desc"
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
        
        # Таблица для вакансий
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS jobs (
                id TEXT PRIMARY KEY,
                stanowisko TEXT,
                miejscePracy TEXT,
                pracodawca TEXT,
                dataDodaniaCbop TEXT,
                dataWaznOd TEXT,
                dataWaznDo TEXT,
                wynagrodzenie TEXT,
                zakresObowiazkow TEXT,
                parseriteration_id INTEGER,
                latitude REAL,
                longitude REAL,
                country TEXT,
                locality TEXT,
                street TEXT,
                building TEXT,
                FOREIGN KEY (parseriteration_id) REFERENCES parseriteration (id)
            )
        """)
        
        # Таблица для записей о запусках парсера
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
def fetch_geolocation(address):
    params = {"q": address, "format": "json", "addressdetails": 1}
    response = requests.get(NOMINATIM_URL, params=params)
    if response.status_code == 200:
        data = response.json()
        if data:
            return {
                "latitude": data[0].get("lat"),
                "longitude": data[0].get("lon"),
                "country": data[0]["address"].get("country"),
                "locality": data[0]["address"].get("city", data[0]["address"].get("town", data[0]["address"].get("village"))),
                "street": data[0]["address"].get("road"),
                "building": data[0]["address"].get("house_number"),
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


# Функция для сохранения вакансий в базу данных
def save_jobs_to_database(jobs, parseriteration_id):
    with sqlite3.connect(DATABASE_FILE) as conn:
        cursor = conn.cursor()
        new_jobs = 0
        for job in jobs:
            try:
                # Сохраняем основную информацию о вакансии
                cursor.execute("""
                    INSERT INTO jobs (id, stanowisko, miejscePracy, pracodawca, dataDodaniaCbop, 
                                      dataWaznOd, dataWaznDo, wynagrodzenie, zakresObowiazkow, parseriteration_id)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    job["id"],
                    job["stanowisko"],
                    job["miejscePracy"],
                    job["pracodawca"],
                    job["dataDodaniaCbop"],
                    job["dataWaznOd"],
                    job["dataWaznDo"],
                    job["wynagrodzenie"],
                    job.get("zakresObowiazkow", ""),
                    parseriteration_id
                ))
                new_jobs += 1

                # Получаем геолокационные данные
                address = job.get("miejscePracy", "")
                geo_data = fetch_geolocation(address)
                if geo_data:
                    cursor.execute("""
                        UPDATE jobs
                        SET latitude = ?, longitude = ?, country = ?, locality = ?, street = ?, building = ?
                        WHERE id = ?
                    """, (
                        geo_data["latitude"],
                        geo_data["longitude"],
                        geo_data["country"],
                        geo_data["locality"],
                        geo_data["street"],
                        geo_data["building"],
                        job["id"]
                    ))
            except sqlite3.IntegrityError:
                continue
        conn.commit()
    return new_jobs


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
