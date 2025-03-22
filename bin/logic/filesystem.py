import json
import os
import bin.settings

def save_jobs_copy_into_json_file_fc(parseiteraion_results_filepath, jobs_dc):
    # Проверяем, существует ли файл
    if os.path.isfile(parseiteraion_results_filepath):
        # Открываем файл и загружаем существующие данные
        with open(parseiteraion_results_filepath, "r", encoding="utf-8") as fr:
            try:
                data = json.load(fr)  # Загружаем существующий JSON
                if not isinstance(data, list):
                    data = [data]  # Если там не список, преобразуем в список
            except json.JSONDecodeError:
                data = []  # Если файл пустой или битый, создаём новый список
    else:
        data = []

    # Добавляем новые данные в список
    data.append(jobs_dc)

    # Записываем обновлённый список обратно в файл
    with open(parseiteraion_results_filepath, "w", encoding="utf-8") as fw:
        json.dump(data, fw, ensure_ascii=False, indent=4)

def write_daily_results_to_json_file(data_dc, platformname_str) -> str:
    # Сохраняем JSON-файл
    os.makedirs(bin.settings.FOLDERPATH_DAILYDATA, exist_ok=True)
    #fp = os.path.join(FOLDERPATH_DAILYDATA, file_name)
    fp = bin.settings.get_dailyresultsfilepath_fc(platformname_str)
    with open(fp, "w", encoding="utf-8") as fw:
        json.dump(data_dc, fw, ensure_ascii=False, indent=4)

    return fp