import json
import os

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