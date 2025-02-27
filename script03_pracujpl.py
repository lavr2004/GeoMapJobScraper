import settings

from bin_code.pracujpl.module001_crawler_pracujpl import get_html_response_from_url
from bin_code.pracujpl.module002_parser_pracujpl import recognition_JSON_in_HTML_area_fc, recursive_json_search_fc, parse_address_in_warsaw_from_url_fc
from bin_code.pracujpl.module003_database_pracujpl import Database_pracujpl
from bin_code.pracujpl.module004_filesystem_pracujpl import save_jobs_copy_into_json_file_fc
from bin_code.nominatim.module001_nominatim import get_coordinates_latlon_fc

PLATFORMNAME_str = "pracujpl"
DATABASE_FILEPATH_str = settings.get_databasefilepath_fc(PLATFORMNAME_str)
URL_START_str = 'https://www.pracuj.pl/praca/warszawa;kw'

# HTML-код (можно заменить на чтение из файла или другой источник)
oDatabasePracujpl = Database_pracujpl(DATABASE_FILEPATH_str)
html_content, response_status_code = get_html_response_from_url(URL_START_str)
json_data = recognition_JSON_in_HTML_area_fc(html_content)
jobs = recursive_json_search_fc(json_data, "groupedOffers")


# Данные для записи в таблицу parseiteration
parseiteraion_results_filepath = settings.get_dailyresultsfilepath_fc(PLATFORMNAME_str)
parseiteraion_results_filename = settings.get_filenamefrompath(parseiteraion_results_filepath)
current_timestamp = settings.get_timestamp()
url = URL_START_str

# Сохраняем JSON-файл
save_jobs_copy_into_json_file_fc(parseiteraion_results_filepath, jobs)
# with open(parseiteraion_results_filepath, "w", encoding="utf-8") as fw:
#     json.dump(jobs, fw, ensure_ascii=False, indent=4)


oDatabasePracujpl.step01_save_parseiteration_fc(parseiteraion_results_filename, current_timestamp, len(jobs), response_status_code, url)




def update_jobvacancies_lat_lon_fc(Database_pracujpl):
    jobs = Database_pracujpl.step03_get_lastaddedvacancies_from_database_fc()
    # Обновление координат в базе данных
    for job in jobs:
        job_id, job_locality, job_street, job_building, display_workplace = job
        
        # Формирование адреса
        if job_street:  # Если указан job_street, формируем адрес из деталей
            address = ", ".join(filter(None, [job_locality, job_street, job_building]))
        else:  # Если job_street отсутствует, используем display_workplace
            address = display_workplace
        
        if address:  # Если есть адрес для поиска
            latitude, longitude = get_coordinates_latlon_fc(address, settings.NOMINATIM_URL)#latitude, longitude = 0, 0
            # if not latitude or not longitude:
            #     latitude, longitude = get_coordinates(job_locality)
            #cursor.execute(
            #        "UPDATE jobs SET job_latitude = ?, job_longitude = ? WHERE id = ?",
            #        (latitude, longitude, job_id),
            #    )
            Database_pracujpl.step04_update_geocoordinatest_fc(latitude, longitude, job_id)

            if latitude and longitude:  # Если координаты получены успешно
                print(f"Координаты для вакансии ID {job_id} обновлены: {latitude}, {longitude}")
            else:
                print(f"Не удалось получить координаты для вакансии ID {job_id} (адрес: {address})")
        else:
            print(f"Адрес отсутствует для вакансии ID {job_id}")

# Сохранение изменений и закрытие соединения
oDatabasePracujpl.step02_save_joboffers_fc(jobs, parse_address_in_warsaw_from_url_fc)

print(f"OK: Данные успешно сохранены в базе данных {DATABASE_FILEPATH_str}")
print(response_status_code)

update_jobvacancies_lat_lon_fc(Database_pracujpl=oDatabasePracujpl)
oDatabasePracujpl.step05_commit_things()
#conn.commit()
#conn.close()
print("OK: Обновление координат завершено.")