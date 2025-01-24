import sqlite3  # или используйте другой драйвер для вашей базы данных
import os
from geopy.distance import geodesic

MAX_DISTANCE_AROUND_AREA_KM = 3
MAX_ALL_JOBS_COUNT_NOT_FILTERED = 1000
MAX_COUNT_OF_JOBS_FILTERED = 300

CENTRALPOINT_COORDINATES_LAT = 52.2321841
CENTRALPOINT_COORDINATES_LON = 20.935230422848832

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
conn = sqlite3.connect('jobs.db')
cursor = conn.cursor()

# Извлекаем вакансии из базы данных
cursor.execute(f'SELECT id, stanowisko, wynagrodzenie, job_latitude, job_longitude, pracodawca, parseriteration_id FROM jobs ORDER BY parseriteration_id DESC LIMIT {MAX_ALL_JOBS_COUNT_NOT_FILTERED}')
vacancies = cursor.fetchall()

# Применяем фильтрацию к списку вакансий
vacancies = filter_vacancies(vacancies, reference_point, max_distance_km=MAX_DISTANCE_AROUND_AREA_KM)
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
        </style>
    </head>
    <body>

    <h1>Vacancies on map: ''' + str(len(vacancies)) + f" in radius of {MAX_DISTANCE_AROUND_AREA_KM} kilometers around" +'''</h1>

    <!-- Легенда -->
    <div>
        <h2>Legend:</h2>
        <p><span style="color:red;">●</span> New Vacancies</p>
        <p><span style="color:blue;">●</span> Old Vacancies</p>
        <button onclick="filterMarkers('new')"> Filter New Vacancies</button>
        <button onclick="filterMarkers('old')"> Filter Old Vacancies</button>
        <button onclick="filterMarkers('all')"> No Filter </button>
    </div>

    <!-- Filter -->
    <div class="filter-container">
        <label class="slider-label" for="salary-slider">Minimum Salary:</label>
        <input id="salary-slider" class="slider" type="range" min="0" max="10000" step="500" value="0">
        <span id="salary-value">0 PLN</span>
        <br>
        <label class="slider-label" for="radius-slider">Search Radius (km):</label>
        <input id="radius-slider" class="slider" type="range" min="1" max="50" step="1" value="10">
        <span id="radius-value">10 km</span>
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

    let markers = [];
    const radiusCircle = L.circle(''' + centerpoint_coords_list_str + ''', {
        radius: ''' + str(MAX_DISTANCE_AROUND_AREA_KM) + '''000,
        color: 'blue',
        fillColor: 'blue',
        fillOpacity: 0.1
    }).addTo(map);

    function addMarkers(minSalary, maxDistance) {
        markers.forEach(marker => map.removeLayer(marker));
        markers = [];

        vacancies.forEach(vacancy => {

            var markerColor = vacancy.is_new ? 'red' : 'blue';

            const salary = vacancy.salary; // Поле уже числовое
            const distance = map.distance(''' + centerpoint_coords_list_str + ''', [vacancy.latitude, vacancy.longitude]);

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
                    '<b><h4 style="color:green">' + vacancy.title + '</h4></b><br><b>' + vacancy.employee + '</b><br>' +
                    '<b>Зарплата: </b>' + vacancy.salary_to_show + '<br>' +
                    '<a href="https://oferty.praca.gov.pl/portal/lista-ofert/szczegoly-oferty/' + vacancy.id + '" target="_blank">Подробнее</a>'
                );
                markers.push({ marker, is_new: vacancy.is_new });
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

    // Фильтрация пинов
    function filterMarkers(type) {
        markers.forEach(({ marker, is_new }) => {
            if (type === 'new' && !is_new) {
                map.removeLayer(marker);
            } else if (type === 'old' && is_new) {
                map.removeLayer(marker);
            } else {
                map.addLayer(marker);
            }
        });
    }

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
    vacancies_data = [
        {
            'id': vacancy[0],
            'title': str(vacancy[1]),
            'salary': extract_salary(str(vacancy[2])),
            'latitude': vacancy[3],
            'longitude': vacancy[4],
            'employee': str(vacancy[5])[:50],
            'is_new': vacancy[6] == max_parseriteration_id,  # True для новых вакансий
            'salary_to_show': str(vacancy[2])[:50],
            
        }
        for vacancy in vacancies
    ]
    return json.dumps(vacancies_data, ensure_ascii=False)

#html_content = getcode_map_full(vacancies)
html_content = getcode_map_full2(vacancies)

# Сохраняем HTML в файл
html_file_path = 'vacancies_map.html'
with open(html_file_path, 'w', encoding='utf-8') as file:
    file.write(html_content)

# Открываем файл в браузере
# os.system(f'xdg-open {html_file_path}')  # Для Linux, для Windows используйте os.startfile(html_file_path)
os.startfile(html_file_path)
