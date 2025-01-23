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

def getcode_stylepage():
    return "#map { height: 600px; }"

def getcode_map():
    s = '''
    // Инициализируем карту
    var map = L.map('map').setView([%s, %s], 10); //Варшава
    ''' % (str(CENTRALPOINT_COORDINATES_LAT), str(CENTRALPOINT_COORDINATES_LON))
    return s

def getcode_layer_round():
    s = '''
        // Создаем круг радиусом 5 км вокруг указанной точки
        var circle = L.circle([%s, %s], {
            color: 'blue',             // Цвет контура
            fillColor: 'blue',         // Цвет заливки
            fillOpacity: 0.1,          // Прозрачность заливки (0.2 = 20 percents)
            radius: %s000               // Радиус круга в метрах (5 км)
        }).addTo(map);
    ''' % (str(CENTRALPOINT_COORDINATES_LAT), str(CENTRALPOINT_COORDINATES_LON), str(MAX_DISTANCE_AROUND_AREA_KM))
    return s

def getcode_osmlayer():
    s = '''
        L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
        }).addTo(map);
        '''
    return s

import json
def getcode_vacanciesdata(vacancies):
    max_parseriteration_id = max(vacancies, key=lambda x: x[6])[6] if vacancies else 0
    vacancies_data = [
        {
            'id': vacancy[0],
            'title': str(vacancy[1]),
            'salary': str(vacancy[2])[:50],
            'latitude': vacancy[3],
            'longitude': vacancy[4],
            'pracodawca': str(vacancy[5])[:50],
            'is_new': vacancy[6] == max_parseriteration_id  # True для новых вакансий
            
        }
        for vacancy in vacancies
    ]
    return json.dumps(vacancies_data, ensure_ascii=False)

# def getcode_addcallouttopinsonmap():
#     s = '''
#     // Добавляем Callout для каждого пина на карте
#     vacancies.forEach(function(vacancy) {
#         var marker = L.marker([vacancy.latitude, vacancy.longitude]).addTo(map);
#         var link = 'https://oferty.praca.gov.pl/portal/lista-ofert/szczegoly-oferty/' + vacancy.id;

#         marker.bindPopup('<b><h4 style="color:green">' + vacancy.title + '</h1></b><br><b>' + vacancy.pracodawca + '</b><br>' + 
#                             '<b>Зарплата: </b>' + vacancy.salary + '<br>' +
#                             '<a href="' + link + '" target="_blank">Подробнее</a>');
#     });
#     '''
#     return s

def getcode_addcallouttopinsonmap():
    s = '''
    var markers = [];
    function addMarkers() {
        vacancies.forEach(function(vacancy) {
            var markerColor = vacancy.is_new ? 'red' : 'blue';
            var marker = L.marker([vacancy.latitude, vacancy.longitude], {
                icon: L.icon({
                    iconUrl: `https://raw.githubusercontent.com/pointhi/leaflet-color-markers/master/img/marker-icon-${markerColor}.png`,
                    shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-shadow.png',
                    iconSize: [25, 41],
                    iconAnchor: [12, 41],
                    popupAnchor: [1, -34],
                    shadowSize: [41, 41]
                })
            }).addTo(map);

            marker.bindPopup('<b><h4 style="color:green">' + vacancy.title + '</h4></b><br><b>' + vacancy.pracodawca + '</b><br>' +
                            '<b>Зарплата: </b>' + vacancy.salary + '<br>' +
                            '<a href="https://oferty.praca.gov.pl/portal/lista-ofert/szczegoly-oferty/' + vacancy.id + '" target="_blank">Подробнее</a>');
            markers.push({ marker, is_new: vacancy.is_new });
        });
    }

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

    addMarkers();
    '''
    return s


html_content = f'''
<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Vacancies on map</title>
    <link rel="stylesheet" href="https://unpkg.com/leaflet/dist/leaflet.css" />
    <style>
        {getcode_stylepage()}
    </style>
</head>
<body>
    <h1>Vacancies on map: {len(vacancies)}</h1>

    <!-- Легенда -->
    <div>
        <h2>Legend:</h2>
        <p><span style="color:red;">●</span> New Vacancies</p>
        <p><span style="color:blue;">●</span> Old Vacancies</p>
        <button onclick="filterMarkers('new')"> Filter New Vacancies</button>
        <button onclick="filterMarkers('old')"> Filter Old Vacancies</button>
        <button onclick="filterMarkers('all')"> No Filter </button>
    </div>


    <div id="map"></div>
    <script src="https://unpkg.com/leaflet/dist/leaflet.js"></script>
    <script>
        // Инициализируем карту
        {getcode_map()} //Варшава

        // Создаем круг радиусом 5 км вокруг указанной точки
        {getcode_layer_round()}

        // Добавляем слой OpenStreetMap
        {getcode_osmlayer()}

        // Добавляем пины для каждой вакансии
        var vacancies = {getcode_vacanciesdata(vacancies=vacancies)};  // Это данные вакансий из Python

        // Добавляем Callout для каждого пина на карте
        {getcode_addcallouttopinsonmap()}
    </script>
</body>
</html>
'''

# Сохраняем HTML в файл
html_file_path = 'vacancies_map.html'
with open(html_file_path, 'w', encoding='utf-8') as file:
    file.write(html_content)

# Открываем файл в браузере
# os.system(f'xdg-open {html_file_path}')  # Для Linux, для Windows используйте os.startfile(html_file_path)
os.startfile(html_file_path)
