import bin.logic.parser
import bin.logic.web
import bin.logic.filesystem
import bin.logic.nominatim
import bin.settings as settings

from bin.parsers.baseparser import BaseParser
from bin.parsers.urzadpracy.urzadpracy_database import Database_urzadpracy

import random
import time

COUNT_OF_JOBS_TO_REQUEST = 500
IS_USE_PUBLIC_NOMINATIM_API = False

# NOMINATIM_PRIVATE_API_URL = "http://localhost:8080/search"
# NOMINATIM_PUBLIC_API_URL = "https://nominatim.openstreetmap.org/search"
# NOMINATIM_URL = NOMINATIM_PUBLIC_API_URL if IS_USE_PUBLIC_NOMINATIM_API else NOMINATIM_PRIVATE_API_URL# Nominatim api server address
# NOMINATIM_PAUSE_IF_PUBLIC_API_SECONDS = 3
NOMINATIM_PRIVATE_API_URL = settings.NOMINATIM_PRIVATE_API_URL
NOMINATIM_PUBLIC_API_URL = settings.NOMINATIM_PUBLIC_API_URL
NOMINATIM_URL = NOMINATIM_PUBLIC_API_URL if IS_USE_PUBLIC_NOMINATIM_API else NOMINATIM_PRIVATE_API_URL
NOMINATIM_PAUSE_IF_PUBLIC_API_SECONDS = settings.NOMINATIM_PAUSE_IF_PUBLIC_API_SECONDS

import bin.parsers.urzadpracy.urzadpracy_database

class UrzadparcyParser(BaseParser):
    def __init__(self):
        super().__init__(platformname_str="urzadpracy", url_start_str=f"https://oferty.praca.gov.pl/portal-api/v3/oferta/wyszukiwanie?page=0&size={COUNT_OF_JOBS_TO_REQUEST}&sort=dataDodania,desc")
        self.oDatabase = Database_urzadpracy(self.database_filepath_str)
        self.oDatabase.create_database()

    def _fetch_html(self, pagenumber_int=None):
        headers = {
            "Accept": "*/*",
            "Content-Type": "application/json",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
        }
        json_post = {
            "miejscowosci": [{"miejscowoscId": "0918123", "zasieg": 0}],
            "kodJezyka": "PL",
            "kodyPocztoweId": ["01-107"],
        }
        pause_seconds_int = random.randint(3, 7)
        print(f"OK: Technical pause between requests to {self.PLATFORMNAME_STR} - {pause_seconds_int} seconds")
        time.sleep(pause_seconds_int)
        return bin.logic.web.get_json_response_from_url(self.URL_START_STR, json_dc=json_post, headers_dc=headers, request_type_str="POST")

    def parse(self, pagenumber_int=0) -> None:
        data, response_status_code = self._fetch_html(pagenumber_int)
        if response_status_code == 200:
            jobs = data.get("payload", {}).get("ofertyPracyPage", {}).get("content", [])

            # Сохраняем JSON-файл
            # os.makedirs(FOLDERPATH_DAILYDATA, exist_ok=True)
            #fp = os.path.join(FOLDERPATH_DAILYDATA, file_name)
            # fp = settings.get_dailyresultsfilepath_fc(PLATFORMNAME_str)
            # with open(fp, "w", encoding="utf-8") as fw:
            #     json.dump(jobs, fw, ensure_ascii=False, indent=4)

            fp = bin.logic.filesystem.write_daily_results_to_json_file(jobs, self.PLATFORMNAME_STR)

            # Сохраняем информацию о запуске парсера
            file_name = settings.get_filenamefrompath(fp)
            parseriteration_id = self.oDatabase.save_parser_iteration(file_name, self.current_timestamp_str, response_status_code, 0)

            # Сохраняем вакансии
            new_jobs_count = self.oDatabase.save_jobs_to_database(jobs, parseriteration_id)

            # Обновляем количество новых вакансий в таблице parseriteration
            self.oDatabase.update_count_of_new_vacancies_added(new_jobs_count, parseriteration_id)

            print(f"OK - Данные успешно обработаны. Добавлено новых вакансий: {new_jobs_count}")
        else:
            print(f"ER - Ошибка запроса: {response_status_code}")
            self.oDatabase.save_parser_iteration("", self.current_timestamp_str, response_status_code, 0)

    def update_coordinates(self) -> None:
        pass

    def commit_changes(self):
        self.oDatabase.commit_and_close()


if __name__ == "__main__":
    parser = UrzadparcyParser()

    # Parsing multiple pages
    # for page in range(0, 6):
    #     parser.parse(page)

    parser.parse()

    # Update job vacancies with coordinates
    # parser.update_coordinates()

    # Commit changes to the database
    parser.commit_changes()
    print("OK: Data parsed")