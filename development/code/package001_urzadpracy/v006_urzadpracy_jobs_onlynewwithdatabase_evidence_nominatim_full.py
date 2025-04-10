import requests
import sqlite3
import json
import os
import time
from datetime import datetime

from urllib.parse import unquote, urlparse, parse_qs, quote

#SETTINGS
COUNT_OF_JOBS_TO_REQUEST = 500
IS_USE_PUBLIC_NOMINATIM_API = False

# Константы FILESYSTEM
FOLDERNAME_RESULTS_ALL = "data_results"
FOLDERNAME_DAILYDATA = "daily_results"

FOLDERPATH_RESULTS_ALL = os.path.join(os.getcwd(), FOLDERNAME_RESULTS_ALL)
FOLDERPATH_DAILYDATA = os.path.join(FOLDERPATH_RESULTS_ALL, FOLDERNAME_DAILYDATA)

os.makedirs(FOLDERPATH_RESULTS_ALL, exist_ok=True)
os.makedirs(FOLDERPATH_DAILYDATA, exist_ok=True)

DATABASE_FILEPATH = os.path.join(FOLDERPATH_RESULTS_ALL, "urzadpracy_jobs.sqlite")
#DATABASE_FILEPATH = "test.sqlite"


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

NOMINATIM_PRIVATE_API_URL = "http://localhost:8080/search"
NOMINATIM_PUBLIC_API_URL = "https://nominatim.openstreetmap.org/search"
NOMINATIM_URL = NOMINATIM_PUBLIC_API_URL if IS_USE_PUBLIC_NOMINATIM_API else NOMINATIM_PRIVATE_API_URL# Nominatim api server address
NOMINATIM_PAUSE_IF_PUBLIC_API_SECONDS = 3


# Функция для создания базы данных
def create_database():
    with sqlite3.connect(DATABASE_FILEPATH) as conn:
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
                parseiteration_id INTEGER,
                job_latitude REAL,
                job_longitude REAL,
                job_country TEXT,
                job_locality TEXT,
                job_street TEXT,
                job_building TEXT,
                FOREIGN KEY (parseiteration_id) REFERENCES parseiteration (id)
            )
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS parseiteration (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                parseiterationfile TEXT,
                timestamp TEXT,
                new_jobs_count INTEGER,
                response_status_code INTEGER
            )
        """)
        conn.commit()



# Функция для вызова Nominatim
def fetch_geolocation(job):
    def get_value_torequestfromnominatim(job):
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
                # address_quote = quote(address_unquote, safe="")
                return address_unquote

    
    addresstorequest_unquote = get_value_torequestfromnominatim(job)
    if not addresstorequest_unquote:
        return None
    
    params = {"q": addresstorequest_unquote, "format": "json", "addressdetails": 1}
    headers = {
        'User-Agent': 'NonameApp/1.0 (lavr2004@gmail.com)'  # Укажите свои данные
    }

    if NOMINATIM_PUBLIC_API_URL == NOMINATIM_URL:
        print(f"OK - pause before request public API: {NOMINATIM_PAUSE_IF_PUBLIC_API_SECONDS} seconds...")
        time.sleep(NOMINATIM_PAUSE_IF_PUBLIC_API_SECONDS)
    
    response = requests.get(NOMINATIM_URL, params=params, headers=headers)

    #tolookupindebug_urltorequest = f"{NOMINATIM_URL}?q={quote(addresstorequest_unquote, safe="")}&format=json"
    #response = requests.get(urltorequest, headers=headers)
    if response.status_code == 200:
        data = response.json()
        #tolookupindebug_data2 = response.text
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
    with sqlite3.connect(DATABASE_FILEPATH) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO parseiteration (parseiterationfile, timestamp, response_status_code, new_jobs_count)
            VALUES (?, ?, ?, ?)
        """, (file_name, timestamp, response_status_code, new_jobs_count))
        conn.commit()
        return cursor.lastrowid

def save_jobs_to_database(jobs, parseiteration_id):
    with sqlite3.connect(DATABASE_FILEPATH) as conn:
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
                        popularnosc, parseiteration_id
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
                    parseiteration_id
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
        os.makedirs(FOLDERPATH_DAILYDATA, exist_ok=True)
        fp = os.path.join(FOLDERPATH_DAILYDATA, file_name)
        with open(fp, "w", encoding="utf-8") as fw:
            json.dump(jobs, fw, ensure_ascii=False, indent=4)

        # Сохраняем информацию о запуске парсера
        parseiteration_id = save_parser_iteration(file_name, timestamp, response.status_code, 0)
        
        # Сохраняем вакансии
        new_jobs_count = save_jobs_to_database(jobs, parseiteration_id)

        # Обновляем количество новых вакансий в таблице parseiteration
        with sqlite3.connect(DATABASE_FILEPATH) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE parseiteration
                SET new_jobs_count = ?
                WHERE id = ?
            """, (new_jobs_count, parseiteration_id))
            conn.commit()

        print(f"Данные успешно обработаны. Добавлено новых вакансий: {new_jobs_count}")
    else:
        print(f"Ошибка запроса: {response.status_code}")
        save_parser_iteration(file_name, timestamp, response.status_code, 0)


if __name__ == "__main__":
    main()
