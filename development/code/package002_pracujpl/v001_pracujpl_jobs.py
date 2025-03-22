from bin import settings
import requests
import re

PLATFORMNAME_str = "pracujpl"
DATABASE_FILENAME_str = settings.get_databasefilename_fc(PLATFORMNAME_str)
URL_START_str = 'https://www.pracuj.pl/praca/warszawa;kw'

headers = {
    'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
    'accept-language': 'en-US,en;q=0.9,ru-BY;q=0.8,ru-RU;q=0.7,ru;q=0.6',
    # 'cookie': 'gp__cfXfiDZP=43; __cfruid=34c5ac7f7068c5a18c2c1720033cdc8bb818b495-1732121145; gptrackCookie=99bb3647-5c3f-4a50-y6ae-6a50428adf91; gp_lang=pl; gpc_v=1; gpc_analytic=1; gpc_func=1; gpc_ad=1; gpc_audience=1; gpc_social=1; _gcl_au=1.1.1526634893.1732121151; x-auth-csrf-token=ae26d655736547e565e84eaf999be25c9b15bcb67db4e952907477b878b2e75e; _gpauthclient=pracuj.pl_external; gpSearchType=Default; _gpauthrt=ZLZJuxlIZRD%2BuXoKIMOLbJLUMS%2FhVKP%2FqZoeyG6ET%2BeHWeiC%2F7DyTVx88xz7lQu1unplwre9Ectjchwac%2F9xLrsyWHs5UCPJnjYdBzVXEexeGybgJKtOQHSy7IbOuTdfMsIx4F7Be%2FFGAuXDEr%2Fy1Q%3D%3D; gp_ab__tech__227=A; _cfuvid=C7btfQNsTWLGZZyIvqjvf8Rm1D5LQTVxwlBHPUNG4jw-1737523183907-0.0.1.1-604800000; gp_tr_gptrackCookie=c1b88749-2665-4ad1-b82b-8e98c9e6b785; _gpantiforgery=CfDJ8BnsG4UujmlAhMc6W89smJZKuLovf73H9nLwDFytKfwJy4jZkis6Uh-OPSZRqxiz2pMtGEePLenbtqR5wumc-44uCpQIEn_qdtYbIE8jYKxwr-avzzJazkjMtCFBrzAjTaUul_Evdm7osgHFwb7Yz0s; _gpauth=eyJhbGciOiJSUzI1NiIsImtpZCI6IjI0QkVFNDg5MTIwRTE1ODdBMEYyOEE1ODYwRTY4QkM2OTQwODkxNDAiLCJ4NXQiOiJKTDdraVJJT0ZZZWc4b3BZWU9hTHhwUUlrVUEiLCJ0eXAiOiJKV1QifQ.eyJpc3MiOiJodHRwczovL2F1dGgucHJhY3VqLnBsIiwibmJmIjoxNzM3NjM3NzA1LCJpYXQiOjE3Mzc2Mzc3MDUsImV4cCI6MTczNzcyNDcwNSwiYXVkIjpbInByYWN1ai5wbCIsImh0dHBzOi8vYXV0aC5wcmFjdWoucGwvcmVzb3VyY2VzIl0sInNjb3BlIjpbInByYWN1ai5wbCIsIm9mZmxpbmVfYWNjZXNzIl0sImFtciI6WyJleHRlcm5hbCJdLCJjbGllbnRfaWQiOiJwcmFjdWoucGxfZXh0ZXJuYWwiLCJmaWxlc3RvcmVfYWNjZXNzIjoiYWxsb3ciLCJhcHBsaWNhdGlvbnNfYWNjZXNzIjoiYWxsb3ciLCJmaWxlX293bmVyIjoidHJ1ZSIsInVzZXJfYWdyZWVtZW50c19hY2Nlc3MiOiJhbGxvdyIsInNhdmVkX29mZmVyc19hY2Nlc3MiOiJhbGxvdyIsImpvYm9mZmVyc19hY2Nlc3MiOiJhbGxvdyIsImNyZWF0ZV9hY2NvdW50IjoiYWxsb3ciLCJnZXRfYWNjb3VudCI6ImFsbG93IiwiYWdyZWVtZW50X3Jldm9rZSI6ImFsbG93IiwibmVicmFza2FfYWNjZXNzIjoiYWxsb3ciLCJhcHBsaWNhdGlvbnNmb3JtX2FjY2VzcyI6ImFsbG93Iiwic2tpZGJsYW5kaXJfYWNjZXNzIjoiYWxsb3ciLCJjb25maXJtX25ld19lbWFpbCI6ImFsbG93IiwidHJhY2tpbmdfYWNjZXNzIjoiYWxsb3ciLCJha2lyYV9hY2Nlc3MiOiJhbGxvdyIsInBlcnNvbmFsaXp1amFjeXBhdHJ5a19hY2Nlc3MiOiJhbGxvdyIsInN1YiI6Im1vanByYWN1ajoyMzQ0Njg2OCIsImF1dGhfdGltZSI6MTczMjEyMTE2NSwiaWRwIjoiZ3J1cGFwcmFjdWoiLCJlbWFpbCI6ImxhdnIyMDA0QGdtYWlsLmNvbSIsIklzQ29uZmlybWVkIjoiVHJ1ZSIsImVtYWlsX3ZlcmlmaWVkIjoiVHJ1ZSIsImdpdmVuX25hbWUiOiJBbmRyZWkiLCJmYW1pbHlfbmFtZSI6IklobmF0b3ZpY3oiLCJDaXR5IjoiV2Fyc3phd2EiLCJFbXBsb3ltZW50TGV2ZWwiOiJzYW1vZHppZWxueSBzcGVjamFsaXN0YSIsInVzZXJmaWxlc19hY2Nlc3MiOiJhbGxvdyIsInJvbGUiOiJFeHRlcm5hbENsaWVudCIsInNpbHZlcnN0YXJfYWNjZXNzIjoiYWxsb3ciLCJoZWR3aWdhX2FjY2VzcyI6ImFsbG93IiwibWFpbmVfYWNjZXNzIjoiYWxsb3ciLCJtYWluZV9zdXJ2ZXlzX3dyaXRlIjoiYWxsb3ciLCJtYWluZV9zdXJ2ZXlzX3JlYWQiOiJteSIsIm1haW5lX2NvbXBhcmlzb25fcmVhZCI6Im15IiwiaGF3YWlpX2FjY2VzcyI6ImFsbG93Iiwib2tsYWhvbWFfYWNjZXNzIjoiYWxsb3ciLCJjb250ZW50b3d5Y3lwcmlhbl9hY2Nlc3MiOiJhbGxvdyIsInN6dWthamFjeXN6eW1vbl9hY2Nlc3MiOiJhbGxvdyIsInNhbmZyYW5jaXNjb19hY2Nlc3MiOiJhbGxvdyIsIm5pdHJ1amFjeW5lcG9tdWNlbl9hY2Nlc3MiOiJhbGxvdyIsInRleGFzX2FjY2VzcyI6ImFsbG93IiwidXNlckdyb3VwIjoiQ2FuZGlkYXRlcyIsInJlY29tbWVuZGF0aW9uX2FjY2VzcyI6ImFsbG93In0.V-WKFyV-FRb54lt7cskNQafc80R-yolQOJFD6OzQ0KsNgPZymkbobIYp6Ts8h1dOYOECmOAbpHPdI5Tcx-TbufJ1nPKU54ky_anpWHNy_P6MdemqKA4EeUovmHcMToPOtBc7sftE7zJqbHKRBIL3FdymtUaPkS4yNwcSk8G-LQQcCMjazaZ_yyxyodkbdsEuwqP8u-jyIStH41tXlkMRcxwoYE8GM6U3DVQPXNzDx6Wq4-xXyAUIQYqH8gQXQmeRwZb2w65OC4kxKtA748UeSTjRe4rZGBM8WM23f2vEHfNxxAyoycLKrnASok7KuGjKOTiSpNzHnNZOdQbXNTrDe5zptqOS8JRSh2SUE2wvE9KBvdbZlHOeyKmg7F8SeHxvUq_vbl5l6iOzpoTMkz36jHzgRJi9QmkNk9N_CHapUosrSqaQutQ53Xh5FHGUKVMJKZd8EaAeyI-BmlJMl_yWvWeyB9ILs5ifJrWmUjkNsywCU--ifUHKFHWNMLgtvVGdzxLqeBx-9mC4peY9lYTww9VRBCl2DoDE-t2SkJC58G_fD6TupHSQcw0_aOPprTakKlyBP1bRmKHzex7w_xIwzKp8SP_OS9_QyotP7xLRscrN1K5WVD9z-pFP9ZmMtnGOspAxbv1s6-N7m5nTwL4vfq0TLZj15qulYLDrIp3rOyA; __cf_bm=G9IzaHEIjw3YGSRPGAukweH0E2QZYLTz2UGapKYh9Mc-1737637706-1.0.1.1-qL9patuCBhGvgFxODRbkXFJd2yabaLLMRX5Pa3qYNVY4ADYveV8WfRS4V.UD.RSCoiBq.2pEkxaJFQ0sr.WNSQ; cf_clearance=p.EdYNtC9QXzYZoZdcs8GxgquhfbiLOaWqsGDYbYaZs-1737637708-1.2.1.1-imcTxWLEV5Eqb4STSAzGf6ykusdoAyU8WmJX1JjQp5S6sKn6FPo6J0_J.RcNCqm3gcXGo_WFbVGERM7771CUCNMQZbOb9Jn9ALc1Co9M7tEupsy9ePFPc.PanmFN8XDrqlzPLSzt3N7kunV3aNrKZ2Nq9f7XxDzlapCi7gMwXR3Pbyl1W7l.MDEyjweXqZDkfiqe1xHfd6bqzT5OF9njn1HAdj2szXpihr7G3iSqktpIX7dWXfHAtdS6q4RjBDTgWnsIAZCFPjA5yidD90rhLNvGZg587l874AofT0wvzYs; _gid=GA1.2.944345992.1737637710; __gfp_64b=JoMRE6QDzUfIZ.VhFWO00ReFGHNQG0SGzW7mvVJ1LwT.Y7|1732121151|2|||8:1:32; _clck=b27ccm%7C2%7Cfst%7C0%7C1785; gp_tr_gptrackPVID=c7943a68-f9e8-46eb-8d4e-db6f706862af; gptrackPVID=06993c8b-c261-43a0-y7c8-dca33cc17c6e; _ga_GD4CKCV28E=GS1.1.1737637709.6.1.1737637856.0.0.0; _ga_WDELMMFCBH=GS1.1.1737637709.7.1.1737637856.4.0.0; _ga_DD6PPTKNH1=GS1.1.1737637709.7.1.1737637856.4.0.0; _ga=GA1.2.430510135.1732121151; __rtbh.uid=%7B%22eventType%22%3A%22uid%22%2C%22id%22%3A%2223446868%22%2C%22expiryDate%22%3A%222026-01-23T13%3A10%3A57.799Z%22%7D; __rtbh.lid=%7B%22eventType%22%3A%22lid%22%2C%22id%22%3A%22wS03jY4zTOE06cPIxYsX%22%2C%22expiryDate%22%3A%222026-01-23T13%3A10%3A57.800Z%22%7D; _uetsid=24820510d98b11ef9d0cbf9e2df34c9f; _uetvid=e7bad5b0a75e11efae57936341321d2e; cto_bundle=YCf8rV9PM2hLMXZJU2djU3Q0QnZxUXpBMmxuT2NQZVhUWTNyMjg1eXZGaTZaN3JLJTJGMUNPNkE4MnB6MThzT3drZUJqWVJuVyUyQncyUWFRbG9VTVJMYzlDSHRqZmFUY29iYVNaNGZnOHJWVng4ZXppa2pUTUJIeFJGeGRmRjIzREFwWHR5U1p4QXBQZkJJQ0czUTV6Y1B4Z3pnaENnJTNEJTNE; XSRF-TOKEN=CfDJ8BnsG4UujmlAhMc6W89smJaPOUHFarirLTIWm0lGJFVMaz5fIzs2GdNpUnrqMTYFFr-mKuLCBsyJlvGZZvjeT6Dc4ZH6I4kKr4rwmP515BGNzFcFcXg1aqso51gMqIg3mlFusBMFGH3ox02J_bzqBQ0; _clsk=1fu0ix0%7C1737637859285%7C3%7C0%7Cl.clarity.ms%2Fcollect',
    'priority': 'u=0, i',
    'sec-ch-ua': '"Google Chrome";v="131", "Chromium";v="131", "Not_A Brand";v="24"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"Windows"',
    'sec-fetch-dest': 'document',
    'sec-fetch-mode': 'navigate',
    'sec-fetch-site': 'none',
    'sec-fetch-user': '?1',
    'upgrade-insecure-requests': '1',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36',
}

response = requests.get(URL_START_str, headers=headers)

response.raise_for_status()

import json
import sqlite3
from bs4 import BeautifulSoup

# HTML-код (можно заменить на чтение из файла или другой источник)
html_content = response.text  # Ваш HTML здесь

# Извлекаем JSON из HTML
soup = BeautifulSoup(html_content, 'html.parser')
script_tag = soup.find('script', {'id': '__NEXT_DATA__'})
if not script_tag:
    raise ValueError("Тег <script id='__NEXT_DATA__'> не найден")
json_data = json.loads(script_tag.string)

# Извлекаем вакансии из JSON
jobs = json_data["props"]["pageProps"]["data"]["jobOffers"]["groupedOffers"]

# Подключаемся к SQLite базе данных
conn = sqlite3.connect(settings.get_databasefilepath_fc(DATABASE_FILENAME_str))
cursor = conn.cursor()

# Создаём таблицу job_offers
cursor.execute('''
    CREATE TABLE IF NOT EXISTS job_offers (
        id INTEGER PRIMARY KEY,
        group_id TEXT,
        job_title TEXT,
        company_name TEXT,
        company_profile_url TEXT,
        company_id INTEGER,
        company_logo_url TEXT,
        last_publicated TEXT,
        expiration_date TEXT,
        salary TEXT,
        job_description TEXT,
        position_levels TEXT,
        types_of_contract TEXT,
        work_schedules TEXT,
        work_modes TEXT,
        offer_url TEXT,
        display_workplace TEXT,
        parseiteration_id INTEGER,
        FOREIGN KEY(parseiteration_id) REFERENCES parseiteration(id)
    )
''')

# Создаём таблицу parseiteration
cursor.execute('''
    CREATE TABLE IF NOT EXISTS parseiteration (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        parseriterationfile TEXT,
        timestamp TEXT,
        new_jobs_count INTEGER,
        response_status_code INTEGER,
        url TEXT
    )
''')

# Данные для записи в таблицу parseiteration
parseiteraion_results_filepath = settings.get_dailyresultsfilename_fc(PLATFORMNAME_str)
parseiteraion_results_filename = settings.get_filenamefrompath(parseiteraion_results_filepath)
current_timestamp = settings.get_timestamp()
response_status_code = response.status_code
url = URL_START_str

# Сохраняем JSON-файл
with open(parseiteraion_results_filepath, "w", encoding="utf-8") as fw:
    json.dump(jobs, fw, ensure_ascii=False, indent=4)

# Вставляем данные в таблицу parseiteration
cursor.execute('''
    INSERT INTO parseiteration (parseriterationfile, timestamp, new_jobs_count, response_status_code, url)
    VALUES (?, ?, ?, ?, ?)
''', (parseiteraion_results_filename, current_timestamp, len(jobs), response_status_code, url))

# Получаем id последней записи parseiteration
parseiteration_id = cursor.lastrowid


# Сохраняем данные вакансий в таблицу job_offers
for offer in jobs:
    group_id = offer.get('groupId')
    job_title = offer.get('jobTitle')
    company_name = offer.get('companyName')
    company_profile_url = offer.get('companyProfileAbsoluteUri')
    company_id = offer.get('companyId')
    company_logo_url = offer.get('companyLogoUri')
    last_publicated = offer.get('lastPublicated')
    expiration_date = offer.get('expirationDate')
    salary = offer.get('salaryDisplayText')
    job_description = offer.get('jobDescription')
    position_levels = ", ".join(offer.get('positionLevels', []))
    types_of_contract = ", ".join(offer.get('typesOfContract', []))
    work_schedules = ", ".join(offer.get('workSchedules', []))
    work_modes = ", ".join(offer.get('workModes', []))

    # Берём первый элемент из списка 'offers', чтобы получить URL и адрес
    offer_details = offer['offers'][0] if offer.get('offers') else {}
    offer_url = offer_details.get('offerAbsoluteUri')
    display_workplace = offer_details.get('displayWorkplace')

    # Генерируем уникальный ID вакансии из ссылки
    unique_job_id = int(re.search(r'(\d+)$', offer_url).group(1)) if offer_url and re.search(r'(\d+)$', offer_url) else None

    # Пропускаем вакансию, если уникальный ID не найден
    if not unique_job_id:
        print(f"Пропуск вакансии: отсутствует уникальный ID в URL {offer_url}")
        continue

    # Вставляем данные в таблицу job_offers
    cursor.execute('''
        INSERT OR IGNORE INTO job_offers (
            id, group_id, job_title, company_name, company_profile_url, company_id,
            company_logo_url, last_publicated, expiration_date, salary, job_description,
            position_levels, types_of_contract, work_schedules, work_modes,
            offer_url, display_workplace, parseiteration_id
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        unique_job_id, group_id, job_title, company_name, company_profile_url, company_id,
        company_logo_url, last_publicated, expiration_date, salary, job_description,
        position_levels, types_of_contract, work_schedules, work_modes,
        offer_url, display_workplace, parseiteration_id
    ))

# Сохраняем изменения и закрываем соединение
conn.commit()
conn.close()

print(f"Данные успешно сохранены в базе данных {DATABASE_FILENAME_str}")
print(response.status_code)