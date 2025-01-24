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

# Функция для создания базы данных
def create_database():
    with sqlite3.connect(DATABASE_FILE) as conn:
        cursor = conn.cursor()
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
                zakresObowiazkow TEXT
            )
        """)
        conn.commit()

# Функция для сохранения новых вакансий в базу данных
def save_jobs_to_database(jobs):
    with sqlite3.connect(DATABASE_FILE) as conn:
        cursor = conn.cursor()
        new_jobs = 0
        for job in jobs:
            try:
                cursor.execute("""
                    INSERT INTO jobs (id, stanowisko, miejscePracy, pracodawca, dataDodaniaCbop, 
                                      dataWaznOd, dataWaznDo, wynagrodzenie, zakresObowiazkow)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    job["id"],
                    job["stanowisko"],
                    job["miejscePracy"],
                    job["pracodawca"],
                    job["dataDodaniaCbop"],
                    job["dataWaznOd"],
                    job["dataWaznDo"],
                    job["wynagrodzenie"],
                    job.get("zakresObowiazkow", "")
                ))
                new_jobs += 1
            except sqlite3.IntegrityError:
                # Запись уже существует, пропускаем
                continue
        conn.commit()
    print(f"Добавлено новых вакансий: {new_jobs}")

# Основная функция
def main():
    create_database()

    response = requests.post(API_URL, headers=HEADERS, json=DATA)
    if response.status_code == 200:
        data = response.json()
        jobs = data.get("payload", {}).get("ofertyPracyPage", {}).get("content", [])
        save_jobs_to_database(jobs)

        # Сохраняем JSON-файл для эвиденции
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        os.makedirs("job_data", exist_ok=True)
        with open(f"job_data/jobs_{timestamp}.json", "w", encoding="utf-8") as fw:
            json.dump(jobs, fw, ensure_ascii=False, indent=4)
        print("Данные успешно обработаны и сохранены.")
    else:
        print(f"Ошибка запроса: {response.status_code}")

if __name__ == "__main__":
    main()