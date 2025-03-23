import sqlite3
import re


class Database_pracujpl:
    parseiteration_id = None #cursor.lastrowid

    def __init__(self, database_filepath_str):
        self.conn = sqlite3.connect(database_filepath_str)
        self.cursor = self.conn.cursor()

        # Создаём таблицу job_offers
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS jobs (
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
                job_country TEXT,
                job_locality TEXT,
                job_street TEXT,
                job_building TEXT,
                job_latitude REAL,
                job_longitude REAL,
                parseiteration_id INTEGER,
                FOREIGN KEY(parseiteration_id) REFERENCES parseiteration(id)
            )
        ''')

        # Создаём таблицу parseiteration
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS parseiteration (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                parseiterationfile TEXT,
                timestamp TEXT,
                new_jobs_count INTEGER,
                response_status_code INTEGER,
                url TEXT
            )
        ''')

    def step01_save_parseiteration_fc(self, parseiteraion_results_filename, current_timestamp, jobs_count, response_status_code, url):
        # Вставляем данные в таблицу parseiteration
        self.cursor.execute('''
            INSERT INTO parseiteration (parseiterationfile, timestamp, new_jobs_count, response_status_code, url)
            VALUES (?, ?, ?, ?, ?)
        ''', (parseiteraion_results_filename, current_timestamp, jobs_count, response_status_code, url))

        self.parseiteration_id = self.cursor.lastrowid

    def step02_save_joboffers_fc(self, jobs, parse_address_in_warsaw_from_url_fc):
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

            # Извлекаем адрес из URL
            job_country = "Poland"
            job_locality, job_street, job_building = parse_address_in_warsaw_from_url_fc(offer_url)
            job_locality = display_workplace.split(',')[0] if display_workplace else job_locality
            job_locality = job_locality.split('(')[0]
            if job_street and job_locality:
                job_street = job_street.split(job_locality)[-1].strip() if job_locality in job_street else job_street
                job_street = job_street.replace("Victoria Krolewska", "Krolewska").replace("Reduta","")
                if "Pulawska" in job_street:
                    job_street = "Pulawska"

            if not job_street:
                job_building = None


            job_locality = job_locality.strip() if job_locality else job_locality
            job_street = job_street.strip() if job_street else job_street
            job_building = job_building.strip() if job_building else job_building

            # Вставляем данные в таблицу job_offers
            self.cursor.execute('''
                INSERT OR IGNORE INTO jobs (
                    id, group_id, job_title, company_name, company_profile_url, company_id,
                    company_logo_url, last_publicated, expiration_date, salary, job_description,
                    position_levels, types_of_contract, work_schedules, work_modes,
                    offer_url, display_workplace, job_country, job_locality, job_street,
                    job_building, job_latitude, job_longitude, parseiteration_id
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                unique_job_id, group_id, job_title, company_name, company_profile_url, company_id,
                company_logo_url, last_publicated, expiration_date, salary, job_description,
                position_levels, types_of_contract, work_schedules, work_modes,
                offer_url, display_workplace, job_country, job_locality, job_street,
                job_building, None, None, self.parseiteration_id))

            self.conn.commit()

    def step03_get_lastaddedvacancies_from_database_fc(self):
        self.cursor.execute("SELECT id, job_locality, job_street, job_building, display_workplace FROM jobs WHERE job_latitude is NULL")
        jobs = self.cursor.fetchall()
        return jobs

    def step04_update_geocoordinatest_fc(self, latitude, longitude, job_id):
        self.cursor.execute("UPDATE jobs SET job_latitude = ?, job_longitude = ? WHERE id = ?", (latitude, longitude, job_id),)

    def step05_commit_things(self):
        self.conn.commit()

    def __del__(self):
        self.conn.commit()
        self.conn.close()

