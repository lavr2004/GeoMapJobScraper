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

def parse_additionally_from_offer_page(jobid):
    i = NOMINATIM_PAUSE_IF_PUBLIC_API_SECONDS
    while i > 0:
        print(f"OK - technical pause before request to public API {i} seconds...")
        time.sleep(1)
        i -= 1
    
    # url = f"https://oferty.praca.gov.pl/portal-api/v3/oferta/szczegoly/{jobid}?alreadyVisited=true&hashJap="
    # url = None
    
    try:
        # Выполнение GET-запроса
        headers = {
            'Accept': '*/*',
            'Accept-Language': 'en-US,en;q=0.9,ru-BY;q=0.8,ru-RU;q=0.7,ru;q=0.6',
            'Connection': 'keep-alive',
            # 'Cookie': 'JSESSIONID=29D988089D078A84A8388D50070C4614.worker15; _ga=GA1.3.876714283.1734011519; _ga_HGXEGXBYEQ=GS1.3.1737155787.23.1.1737155794.53.0.0; cookieConsent=accepted; TS00000000076=0860e70c7dab280023fd2a44e98d5ff798513ff58c90ad87d87511669828a715a87eee304392eca6881a40db5c3fe5b508bc4e125f09d00019c4797ad6e1319444a6975157abb61c81cee8a9eea446618c98f5597f065697f25db19ca6cafa2b85448e435427aad0f9147b365d431b3bb6e271e8cd8b6274ae8fc290e6fbda0d680b32290a91a1abdbd5880d5cf00bdf63425ef730ebd0df9f40248f3029794851ee311110d296be3dcedb71e7aed81868b7c13445d0ffac1562f4c4574d74c3ec0281975793d8f10bb8914a7e09016ff4cbd0d410b68f586d56f80fc28d0ef9c6719574e1bddde760d2f0074eef232668d04c47f246e36e775e7fa429f756d5571b2b46470e0ad7; TSPD_101_DID=0860e70c7dab2800681eee8673f7a69544dda0be38e93686884dd9088efe7c621fadb898b4d2b1a4095baf6b6f4b873a08c0238c39063800ffefa35b0672ee8b3b9105209ab702f5a2065bc81b64875999fa025db83b71fb4f62c07c24abe3b6e86ae78936e20fcacf05f32361e97a13; TS0155ea11=01a1834bee2ed8fdd86250018355bd6a7a55f9beae96fffadc7543e9c07fe67e45c1b57064e4bf439ef273fa0b9481746b21611a63; TS0bfea4fd027=0860e70c7dab2000d07f605c5a524696f9ceb81071b962bb3ec890c5660c46e05b26babca779b3fc089b7eb5761130004c118c710ef36d70419dadf7ac6e845f1ec66d1069692cb46a6f9bd847dbf67e5f4d5e2fce9ee250fe1d2163801a2ca5',
            'Referer': f'https://oferty.praca.gov.pl/portal/lista-ofert/szczegoly-oferty/{jobid}',
            'Sec-Fetch-Dest': 'empty',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Site': 'same-origin',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36',
            'sec-ch-ua': '"Google Chrome";v="131", "Chromium";v="131", "Not_A Brand";v="24"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
        }

        params = {
            'alreadyVisited': 'true',
            'hashJap': '',
        }

        response = requests.get(
            f'https://oferty.praca.gov.pl/portal-api/v3/oferta/szczegoly/{jobid}',
            params=params,
            headers=headers,
        )
        response.raise_for_status()  # Проверка на ошибки HTTP
        
        # Получение JSON-данных
        data = response.json()
        
        # Парсинг значения адреса
        # address = data["payload"]["pracodawca"]["adres"]
        url = data.get("payload", "").get("pracodawca", "").get("mapaGoogleUrl", "")
        if not url:
            url = data.get("payload", "").get("pracodawca", "").get("mapaOsmUrl", "")
        
        if "Warszawa%2C%20Warszawa" in url:
            v = data.get("payload", "").get("warunki", "").get("miejscePracy", "")
            url = f"https://maps.google.pl/maps?q={quote(v)}"


    except requests.RequestException as e:
        return f"ER - Ошибка запроса: {e}"
    except ValueError:
        return "Не удалось декодировать JSON."
    
    return url


# Функция для вызова Nominatim
def fetch_geolocation(job):
    def get_value_torequestfromnominatim(job):
        address_unquote = None

        url = job.get("mapaGoogleUrl", "")
        if not url:
            url = job.get("mapaOsmUrl", "")
        
        if "Warszawa%2C%20Warszawa" in url:
            url = parse_additionally_from_offer_page(job.get("id"))

        
        
        parsed_url = urlparse(url)
        query_params = parse_qs(parsed_url.query)
        if 'query' not in query_params and "q" not in query_params:
            #address = job("miejscePracy","Warsazawa, Polska")
            # return None
            print(f"ER: адрес не извлечен из ссылки, но предустановлен")
        else:
            address_raw = unquote(query_params['q'][0])  # Декодируем адрес из URL
            if not address_raw:
                address_raw = unquote(query_params['query'][0])
            
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
    # if not addresstorequest_unquote:
    #     return None
    
    params = {"q": addresstorequest_unquote, "format": "json", "addressdetails": 1}
    headers = {
        'User-Agent': 'NonameApp/1.0 (lavr2004@gmail.com)'  # Укажите свои данные
    }

    if NOMINATIM_PUBLIC_API_URL == NOMINATIM_URL:
        print(f"OK - pause before request public API: {NOMINATIM_PAUSE_IF_PUBLIC_API_SECONDS} seconds...")
        time.sleep(NOMINATIM_PAUSE_IF_PUBLIC_API_SECONDS)
    
    try:
        response = requests.get(NOMINATIM_URL, params=params, headers=headers)

        #tolookupindebug_urltorequest = f"{NOMINATIM_URL}?q={quote(addresstorequest_unquote, safe="")}&format=json"
        #response = requests.get(urltorequest, headers=headers)
        if response.status_code == 200:
            data = response.json()
            #tolookupindebug_data2 = response.text
            if data:
                return {
                    "job_latitude": data[0].get("lat") if addresstorequest_unquote else 0,
                    "job_longitude": data[0].get("lon") if addresstorequest_unquote else 0,
                    "job_country": data[0]["address"].get("country"),
                    "job_locality": data[0]["address"].get("city", data[0]["address"].get("town", data[0]["address"].get("village"))),
                    "job_street": data[0]["address"].get("road"),
                    "job_building": data[0]["address"].get("house_number"),
                }
    except Exception as e:
        print(f"ER: {e}")
    
    return None


# Функция для сохранения информации о запуске парсера
def save_parser_iteration(file_name, timestamp, response_status_code, new_jobs_count):
    with sqlite3.connect(DATABASE_FILEPATH) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO parseriteration (parseriterationfile, timestamp, response_status_code, new_jobs_count)
            VALUES (?, ?, ?, ?)
        """, (file_name, timestamp, response_status_code, new_jobs_count))
        conn.commit()
        return cursor.lastrowid

def save_jobs_to_database(jobs, parseriteration_id):
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
        parseriteration_id = save_parser_iteration(file_name, timestamp, response.status_code, 0)
        
        # Сохраняем вакансии
        new_jobs_count = save_jobs_to_database(jobs, parseriteration_id)

        # Обновляем количество новых вакансий в таблице parseriteration
        with sqlite3.connect(DATABASE_FILEPATH) as conn:
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
