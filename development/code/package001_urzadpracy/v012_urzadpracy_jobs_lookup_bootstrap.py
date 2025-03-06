import sqlite3 
import os
from geopy.distance import geodesic

FOLDERNAME_RESULTS_ALL = "data_results"
FILEPATH_DATABASE = os.path.join(FOLDERNAME_RESULTS_ALL, "urzadpracy_jobs.sqlite")

MAX_DISTANCE_AROUND_AREA_KM = 20
MAX_ALL_JOBS_COUNT_NOT_FILTERED = 1000
MAX_COUNT_OF_JOBS_FILTERED = 1000

CENTRALPOINT_COORDINATES_LAT = 52.2321841
CENTRALPOINT_COORDINATES_LON = 20.935230422848832

ALL_VACANCIES_COUNT_GOT = 0

# Координаты, от которых нужно фильтровать (например, Варшава)
reference_point = (CENTRALPOINT_COORDINATES_LAT, CENTRALPOINT_COORDINATES_LON)

# Функция для фильтрации вакансий
def filter_vacancies(vacancies, reference_point, max_distance_km=3):
    filtered_vacancies = []
    for vacancy in vacancies:
        if not vacancy[3] or not vacancy[4]:
            continue
        vacancy_coords = (vacancy[3], vacancy[4])  # (latitude, longitude)
        distance = geodesic(reference_point, vacancy_coords).km
        if distance <= max_distance_km:
            filtered_vacancies.append(vacancy)
    return filtered_vacancies


# Подключаемся к базе данных
conn = sqlite3.connect(FILEPATH_DATABASE)
cursor = conn.cursor()

# Извлекаем вакансии из базы данных
cursor.execute(f'SELECT id, stanowisko, wynagrodzenie, job_latitude, job_longitude, pracodawca, parseriteration_id, job_street, job_building, job_locality FROM jobs ORDER BY parseriteration_id DESC LIMIT {MAX_ALL_JOBS_COUNT_NOT_FILTERED}')
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

    <h1>VacMap:) ''' + str(len(vacancies)) + f" jobs from {ALL_VACANCIES_COUNT_GOT} job offers in radius of {MAX_DISTANCE_AROUND_AREA_KM} kilometers around" +'''</h1>

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
        <input id="radius-slider" class="slider" type="range" min="1" max="''' + str(MAX_DISTANCE_AROUND_AREA_KM) + '''" step="1" value="10">
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
                    '<b><h4 style="color:green">' + vacancy.title + '</h4></b><br><b>' + vacancy.employee + '</b><br><br>' + vacancy.job_address_to_show + '<br><br>' +
                    '<b>Salary: </b>' + vacancy.salary_to_show + '<br>' +
                    '<a href="https://oferty.praca.gov.pl/portal/lista-ofert/szczegoly-oferty/' + vacancy.id + '" target="_blank">Details...</a>'
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

    country_beginningaddress_lambda = lambda vacancy: f"{str(vacancy[9]) if str(vacancy[9]) or str(vacancy[9]) != "None" else ""}"
    middlepartaddress_lambda = lambda vacancy, index: f", {str(vacancy[index]) if str(vacancy[index]) or str(vacancy[index]) != "None" else ""}"
    street_middleaddress_lambda = lambda vacancy: middlepartaddress_lambda(vacancy, 7)
    building_middleaddress_lambda = lambda vacancy: middlepartaddress_lambda(vacancy, 8)
    
    fulladdress_lambda = lambda vacancy: f"{country_beginningaddress_lambda(vacancy)}{street_middleaddress_lambda(vacancy)}{building_middleaddress_lambda(vacancy)}" if street_middleaddress_lambda(vacancy) else ""

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
            'job_address_to_show': fulladdress_lambda(vacancy)
        }
        for vacancy in vacancies
    ]
    return json.dumps(vacancies_data, ensure_ascii=False)

#html_content = getcode_map_full(vacancies)
html_content = getcode_map_full2(vacancies)

# Сохраняем HTML в файл
html_file_path = os.path.join(FOLDERNAME_RESULTS_ALL, 'vacancies_map.html')
with open(html_file_path, 'w', encoding='utf-8') as file:
    file.write(html_content)

# Открываем файл в браузере
# os.system(f'xdg-open {html_file_path}')  # Для Linux, для Windows используйте os.startfile(html_file_path)
os.startfile(html_file_path)
