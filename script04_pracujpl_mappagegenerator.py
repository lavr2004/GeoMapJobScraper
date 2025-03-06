import sqlite3 
import os
from geopy.distance import geodesic
import settings

PLATFORMNAME_str = "pracujpl"

#FOLDERNAME_RESULTS_ALL = "data_results"
#FILEPATH_DATABASE = os.path.join(FOLDERNAME_RESULTS_ALL, "pracujpl_jobs.sqlite")
FILEPATH_DATABASE = settings.get_databasefilepath_fc(PLATFORMNAME_str)

MAX_DISTANCE_AROUND_AREA_KM = 20
MAX_ALL_JOBS_COUNT_NOT_FILTERED = 1000
MAX_COUNT_OF_JOBS_FILTERED = 1000

CENTRALPOINT_COORDINATES_LAT = 52.2321841
CENTRALPOINT_COORDINATES_LON = 20.935230422848832

# DEFAULT_COORDINATES_LAT = 52.2319581
# DEFAULT_COORDINATES_LON = 21.0067249
DEFAULT_COORDINATES_LAT = CENTRALPOINT_COORDINATES_LAT
DEFAULT_COORDINATES_LON = CENTRALPOINT_COORDINATES_LON

ALL_VACANCIES_COUNT_GOT = 0

# Координаты, от которых нужно фильтровать (например, Варшава)
reference_point = (CENTRALPOINT_COORDINATES_LAT, CENTRALPOINT_COORDINATES_LON)

import random

# Функция для смещения координат
# def add_offset(latitude, longitude, index):
#     offset = 0.0001 * index  # Индекс увеличивает смещение
#     latitude += random.choice([-1, 1]) * offset
#     longitude += random.choice([-1, 1]) * offset
#     return latitude, longitude

import math
def generate_pin_offsets(vacancies_list, radius=0.00015):
    """
    Смещает пины в пределах окружности радиусом `radius` вокруг точки (center_lat, center_lng).
    Углы распределяются равномерно по окружности.

    :param center_lat: Широта центрального пина.
    :param center_lng: Долгота центрального пина.
    :param num_pins: Количество пинов для размещения.
    :param radius: Радиус смещения в градусах (примерно в километрах зависит от географии).
    :return: Список координат (lat, lng) для пинов.
    """
    new_vacancies_list = []
    angle_step = 360 / len(vacancies_list)  # Угловой шаг между пинами в градусах по кругу

    for i in range(len(vacancies_list)):

        vacancy_list = vacancies_list[i]

        if i == 0:
            center_lat = vacancy_list[3]
            center_lng = vacancy_list[4]
            new_vacancies_list = [tuple(vacancies_list[i])]
            continue

        angle_deg = i * angle_step
        angle_rad = math.radians(angle_deg)

        # Вычисляем смещение по широте и долготе
        offset_lat = radius * math.sin(angle_rad)
        offset_lng = radius * math.cos(angle_rad)

        # Генерируем новые координаты пина
        new_lat = center_lat + offset_lat
        new_lng = center_lng + offset_lng

        vacancy_list[3] = new_lat
        vacancy_list[4] = new_lng

        new_vacancies_list.append(tuple(vacancy_list))

    return new_vacancies_list

# Adding offset for vacancies that have same coordinates on map
def add_offset_for_same_vacancies_coordinates(vacancies):
    seen_coords = {}  # Хранение количества повторений координат
    processed_pins = []

    for vacancy_tuple in vacancies:
        lat, lon = vacancy_tuple[3], vacancy_tuple[4]

        #todo: do not use that script with other sources
        #set Warsaw default coordinates if not set
        if not lat or not lon:
            lat = DEFAULT_COORDINATES_LAT
            lon = DEFAULT_COORDINATES_LON

        # Проверяем, есть ли такие координаты
        if (lat, lon) in seen_coords:
            seen_coords[(lat, lon)].append(list(vacancy_tuple))
        else:
            # Если координаты новые, добавляем их в словарь
            seen_coords[(lat, lon)] = [list(vacancy_tuple)]
        
    # вычисляем субкоординаты для повторяющихся координат
    for k, v in seen_coords.items():
        vacancy_list_list = v
        new_vacancies_lst_lst = []

        if len(vacancy_list_list) > 1:
            new_vacancies_lst_lst = generate_pin_offsets(vacancy_list_list)
        else:
            new_vacancies_lst_lst = [vacancy_list_list[0]]
        
        # Добавляем пин с обновленными координатами
        for i in new_vacancies_lst_lst:
            processed_pins.append(i)

    return processed_pins

# Функция для фильтрации вакансий
def filter_vacancies(vacancies, reference_point, max_distance_km=3):
    filtered_vacancies = []
    for vacancy in vacancies:
        temp = list(vacancy)
        lat = temp[3]
        lon = temp[4]
        
        if not lat or not lon:
            lat = DEFAULT_COORDINATES_LAT
            lon = DEFAULT_COORDINATES_LON

        #todo: set default coordinates for parsing script later
        if lat == 52.2053382 and lon == 21.0745384:
            lat = CENTRALPOINT_COORDINATES_LAT#52.2321841
            lon = CENTRALPOINT_COORDINATES_LON
        
        vacancy_coords = (lat, lon)  # (latitude, longitude)
        distance = geodesic(reference_point, vacancy_coords).km
        if distance <= max_distance_km:
            temp[3] = lat
            temp[4] = lon
            vacancy = tuple(temp)
            filtered_vacancies.append(vacancy)

    print(f"OK - fetched {len(filtered_vacancies)} vacancies from database")
    filtered_vacancies = add_offset_for_same_vacancies_coordinates(filtered_vacancies)
    print(f"OK - {len(filtered_vacancies)} vacancies stay after processing")

    return filtered_vacancies


# Подключаемся к базе данных
conn = sqlite3.connect(FILEPATH_DATABASE)
cursor = conn.cursor()

# Извлекаем вакансии из базы данных
from datetime import datetime
current_date = datetime.utcnow().isoformat()  # Получаем текущую дату в формате "YYYY-MM-DDTHH:MM:SS"
#cursor.execute(f'SELECT id, job_title, salary, job_latitude, job_longitude, company_name, parseiteration_id, job_street, job_building, job_locality, last_publicated FROM jobs ORDER BY parseiteration_id DESC LIMIT {MAX_ALL_JOBS_COUNT_NOT_FILTERED}')
cursor.execute("""SELECT id, job_title, salary, job_latitude, job_longitude, company_name, parseiteration_id, job_street, job_building, job_locality, last_publicated
    FROM jobs 
    WHERE expiration_date >= ? 
    ORDER BY parseiteration_id DESC 
    LIMIT ?""", (current_date, MAX_ALL_JOBS_COUNT_NOT_FILTERED)
)
vacancies = cursor.fetchall()

# Применяем фильтрацию к списку вакансий
vacancies = filter_vacancies(vacancies, reference_point, max_distance_km=MAX_DISTANCE_AROUND_AREA_KM)
ALL_VACANCIES_COUNT_GOT = len(vacancies)
if len(vacancies) > MAX_COUNT_OF_JOBS_FILTERED:
    vacancies = vacancies[:MAX_COUNT_OF_JOBS_FILTERED]

# Закрываем соединение с базой данных
conn.close()






def getcode_map_full2(vacancies):
    centerpoint_coords_list_str = f"[{CENTRALPOINT_COORDINATES_LAT}, {CENTRALPOINT_COORDINATES_LON}]"

    s = '''
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Vacancy Map</title>
        <link rel="stylesheet" href="https://unpkg.com/leaflet@1.7.1/dist/leaflet.css" />
        <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0-alpha3/dist/css/bootstrap.min.css" rel="stylesheet">
        <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0-alpha3/dist/js/bootstrap.bundle.min.js"></script>
        <link href="https://fonts.googleapis.com/css2?family=Roboto:wght@400;700&display=swap" rel="stylesheet">
        <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/animate.css/4.1.1/animate.min.css" />
        <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
        <style>
            #map { height: 600px; }
            .filter-container {
                margin: 10px;
            }
            .slider-label {
                margin-right: 10px;
            }
            .slider {
                width: 300px;
            }

            body {
                background-color: #f8f9fa; /* Светло-серый цвет */
                font-family: 'Roboto', sans-serif; /* Современный шрифт */
                color: #212529; /* Основной цвет текста */
            }

            h1 {
                text-align: center;
                color: #007bff;
                margin-top: 20px;
            }

            .legend {
                padding: 10px;
                background: white;
                border-radius: 10px;
                box-shadow: 0 2px 5px rgba(0, 0, 0, 0.1);
            }

            .legend h2 {
                color: #343a40;
                margin-bottom: 10px;
            }

            .form-range {
                appearance: none;
                width: 100%;
                height: 8px;
                background: #ddd;
                border-radius: 5px;
                outline: none;
                opacity: 0.9;
                transition: opacity 0.2s ease-in-out;
            }

            .form-range:hover {
                opacity: 1;
            }

            .form-range::-webkit-slider-thumb {
                appearance: none;
                width: 20px;
                height: 20px;
                background: #007bff;
                border-radius: 50%;
                cursor: pointer;
                box-shadow: 0 0 4px rgba(0, 0, 0, 0.2);
            }

            .form-range::-moz-range-thumb {
                width: 20px;
                height: 20px;
                background: #007bff;
                border-radius: 50%;
                cursor: pointer;
            }

            input.form-range {
                background: #555 !important;
            }
        </style>
    </head>
    <body>

    <h1>VacMap:) ''' + str(len(vacancies)) + f" job offers in radius of {MAX_DISTANCE_AROUND_AREA_KM} kilometers around" +'''</h1>

    <!-- Легенда -->
    <div>
        <h2>Legend:</h2>
        <p><span style="color:red;">●</span> New Vacancies</p>
        <p><span style="color:blue;">●</span> Old Vacancies</p>
        <button class="btn btn-primary me-2" onclick="filterMarkers('new')">Filter New Vacancies</button>
        <button class="btn btn-secondary me-2" onclick="filterMarkers('old')">Filter Old Vacancies</button>
        <button class="btn btn-success" onclick="filterMarkers('all')">No Filter</button>
    </div>

    <!-- Filter -->
    <div class="filter-container">
        <label class="slider-label" for="salary-slider">Minimum Salary:</label>
        <input id="salary-slider" class="slider" type="range" min="0" max="20000" step="500" value="0">
        <span id="salary-value">0 PLN</span>
        <br>
        <label class="slider-label" for="radius-slider">Search Radius (km):</label>
        <input id="radius-slider" class="slider" type="range" min="1" max="''' + str(MAX_DISTANCE_AROUND_AREA_KM) + '''" step="1" value="''' + str(MAX_DISTANCE_AROUND_AREA_KM) + '''">
        <span id="radius-value">''' + str(MAX_DISTANCE_AROUND_AREA_KM) + ''' km</span>
    </div>

    <div id="map"></div>

    <script src="https://unpkg.com/leaflet@1.7.1/dist/leaflet.js"></script>
    <script>
    // Sample data
    const vacancies = ''' + getcode_vacanciesdata(vacancies) + ''';

    const map = L.map('map').setView(''' + centerpoint_coords_list_str + ''', 13);

    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        maxZoom: 19
    }).addTo(map);

    // L.tileLayer('https://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}{r}.png', {
    //     attribution: '© OpenStreetMap contributors &copy; CartoDB',
    //     subdomains: 'abcd',
    //     maxZoom: 19}).addTo(map);

    // Создаем пользовательскую иконку
    const binocularIcon = L.icon({
        iconUrl: 'https://icons.iconarchive.com/icons/papirus-team/papirus-apps/256/pingus-icon-icon.png', // Путь к изображению иконки
        iconSize: [32, 32], // Размеры иконки
        iconAnchor: [16, 32], // Точка привязки (основание иконки)
        popupAnchor: [0, -32] // Точка всплывающего окна
    });

    let markers = [];
    const radiusCircle = L.circle(''' + centerpoint_coords_list_str + ''', {
        radius: ''' + str(MAX_DISTANCE_AROUND_AREA_KM) + '''000,
        color: 'blue',
        fillColor: 'blue',
        fillOpacity: 0.1
    }).addTo(map);

    function addMarkers(minSalary, maxDistance) {
        // Удаляем старые маркеры
        markers.forEach(({ marker }) => map.removeLayer(marker));
        markers = [];

        vacancies.forEach(vacancy => {
            const markerColor = vacancy.is_new ? 'red' : 'blue';
            const salary = vacancy.salary; // Числовое значение зарплаты
            const distance = map.distance([vacancy.latitude, vacancy.longitude], ''' + centerpoint_coords_list_str + ''');

            if (salary >= minSalary && distance <= maxDistance) {
                const marker = L.marker([vacancy.latitude, vacancy.longitude], {
                    icon: L.icon({
                        iconUrl: `https://raw.githubusercontent.com/pointhi/leaflet-color-markers/master/img/marker-icon-${markerColor}.png`,
                        shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-shadow.png',
                        iconSize: [25, 41],
                        iconAnchor: [12, 41],
                        popupAnchor: [1, -34],
                        shadowSize: [41, 41]
                    })
                }).addTo(map);

                marker.bindPopup(
                    '<b><h5>Published: </b>' + vacancy.last_publicated + '</h5><br>' +
                    '<b><h4 style="color:green">' + vacancy.title + '</h4></b><br><b>' + vacancy.employee + '</b><br><br>' + vacancy.job_address_to_show + '<br><br>' +
                    '<b>Salary: </b>' + vacancy.salary_to_show + '<br>' +
                    '<a href="https://www.pracuj.pl/praca/,oferta,' + vacancy.id + '" target="_blank">Details...</a>'
                );

                markers.push({ marker, is_new: vacancy.is_new });
            }
        });

        // Добавляем маркер в центральную точку
        L.marker(''' + centerpoint_coords_list_str + ''', { icon: binocularIcon })
            .addTo(map)
            .bindPopup('<div class="animate__animated animate__bounce"><b>Here we start! :)</b><br>from here we start to search vacancies in area around</div>')
            .openPopup();
    }

    function filterMarkers(type) {
        markers.forEach(({ marker, is_new }) => {
            if (type === 'new' && !is_new) {
                map.removeLayer(marker);
            } else if (type === 'old' && is_new) {
                map.removeLayer(marker);
            } else {
                if (!map.hasLayer(marker)) {
                    map.addLayer(marker);
                }
            }
        });
    }

    function updateCircleRadius(radius) {
        radiusCircle.setRadius(radius);
    }

    // Event listeners for sliders
    document.getElementById('salary-slider').addEventListener('input', event => {
        const minSalary = parseInt(event.target.value, 10);
        document.getElementById('salary-value').textContent = `${minSalary} PLN`;
        const radius = parseInt(document.getElementById('radius-slider').value, 10) * 1000;
        addMarkers(minSalary, radius);
    });

    document.getElementById('radius-slider').addEventListener('input', event => {
        const radius = parseInt(event.target.value, 10) * 1000;
        document.getElementById('radius-value').textContent = `${event.target.value} km`;
        updateCircleRadius(radius);
        const minSalary = parseInt(document.getElementById('salary-slider').value, 10);
        addMarkers(minSalary, radius);
    });

    // Initial rendering
    addMarkers(0, 10000);


    </script>
    </body>
    </html>
    '''
    return s






def extract_salary(text):
    import re
    if not text:
        return 0
    text = text.split(",")[0]
    if not text:
        return 0
    match = re.search(r'\b\d.\d{2,}\b', text)
    s =  str(match.group()) if match else ""
    r = ""
    if s:
        if not s:
            return 0
        
        for c in s:
            if c not in "0123456789":
                continue
            r += c
    return int(r) if r else 0


import json
def getcode_vacanciesdata(vacancies):
    max_parseriteration_id = max(vacancies, key=lambda x: x[6])[6] if vacancies else 0

    country_beginningaddress_lambda = lambda vacancy: f"{str(vacancy[9]) if str(vacancy[9]) or str(vacancy[9]) != 'None' or str(vacancy[9]) != None else ''}"
    middlepartaddress_lambda = lambda vacancy, index: f", {str(vacancy[index]) if str(vacancy[index]) or str(vacancy[index]) != 'None' else ''}"
    street_middleaddress_lambda = lambda vacancy: middlepartaddress_lambda(vacancy, 7)
    building_middleaddress_lambda = lambda vacancy: middlepartaddress_lambda(vacancy, 8)
    
    fulladdress_lambda = lambda vacancy: f"{country_beginningaddress_lambda(vacancy)}{street_middleaddress_lambda(vacancy)}{building_middleaddress_lambda(vacancy)}" if street_middleaddress_lambda(vacancy)  else ""

    vacancies_data = [
        {
            'id': vacancy[0],
            'title': str(vacancy[1]),
            'salary': extract_salary(str(vacancy[2])),
            'latitude': vacancy[3],
            'longitude': vacancy[4],
            'employee': str(vacancy[5])[:50],
            'is_new': vacancy[6] == max_parseriteration_id,  # True для новых вакансий
            'salary_to_show': str(vacancy[2]).split('.')[0] if vacancy[2] else "0",
            'job_address_to_show': fulladdress_lambda(vacancy).replace(", None", ""),
            #'last_publicated': datetime.strptime(str(vacancy[10]), "%Y-%m-%dT%H:%M:%SZ").strftime("%d-%m-%Y") if vacancy[10] else "N/A"  # Форматируем дату
            'last_publicated': str(vacancy[10]).split("T")[0] if vacancy[10] else "N/A"  # Добавляем дату публикации
        }
        for vacancy in vacancies
    ]
    return json.dumps(vacancies_data, ensure_ascii=False)

#html_content = getcode_map_full(vacancies)
html_content = getcode_map_full2(vacancies)

# Сохраняем HTML в файл
#html_file_path = os.path.join(FOLDERNAME_RESULTS_ALL, 'vacancies_pracujpl_map.html')
html_file_path = settings.get_htmlmapfilepath_fc(PLATFORMNAME_str)
with open(html_file_path, 'w', encoding='utf-8') as file:
    file.write(html_content)

# Открываем файл в браузере
# os.system(f'xdg-open {html_file_path}')  # Для Linux, для Windows используйте os.startfile(html_file_path)
os.startfile(html_file_path)
