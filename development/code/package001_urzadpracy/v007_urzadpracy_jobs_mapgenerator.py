import sqlite3  # или используйте другой драйвер для вашей базы данных
import os
from geopy.distance import geodesic

MAX_DISTANCE_AROUND_AREA_KM = 5
MAX_COUNT_OF_JOBS = 1000
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
cursor.execute(f'SELECT id, stanowisko, wynagrodzenie, job_latitude, job_longitude, pracodawca FROM jobs ORDER BY parseriteration_id DESC LIMIT {MAX_COUNT_OF_JOBS}')
vacancies = cursor.fetchall()

# Применяем фильтрацию к списку вакансий
vacancies = filter_vacancies(vacancies, reference_point, max_distance_km=MAX_DISTANCE_AROUND_AREA_KM)

# Закрываем соединение с базой данных
conn.close()

# Формируем HTML-контент
html_content = '''
<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Вакансii на мапе</title>
    <link rel="stylesheet" href="https://unpkg.com/leaflet/dist/leaflet.css" />
    <style>
        #map { height: 600px; }
    </style>
</head>
<body>
    <h1>Вакансiяу на мапе: %s</h1>
    <div id="map"></div>
    <script src="https://unpkg.com/leaflet/dist/leaflet.js"></script>
    <script>
        // Инициализируем карту
        var map = L.map('map').setView([%s, %s], 10); //Варшава

        // Создаем круг радиусом 5 км вокруг указанной точки
        var circle = L.circle([%s, %s], {
            color: 'blue',             // Цвет контура
            fillColor: 'blue',         // Цвет заливки
            fillOpacity: 0.1,          // Прозрачность заливки (0.2 = 20 percents)
            radius: %s000               // Радиус круга в метрах (5 км)
        }).addTo(map);

        // Добавляем слой OpenStreetMap
        L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
            attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
        }).addTo(map);

        // Добавляем пины для каждой вакансии
        var vacancies = %s;  // Это данные вакансий из Python

        vacancies.forEach(function(vacancy) {
            var marker = L.marker([vacancy.latitude, vacancy.longitude]).addTo(map);
            var link = 'https://oferty.praca.gov.pl/portal/lista-ofert/szczegoly-oferty/' + vacancy.id;

            marker.bindPopup('<b><h4 style="color:green">' + vacancy.title + '</h1></b><br>' +
                             '<b>Зарплата: </b>' + vacancy.salary + '<br>' +
                             '<a href="' + link + '" target="_blank">Подробнее</a>');
        });
    </script>
</body>
</html>
''' % (str(len(vacancies)),
       str(CENTRALPOINT_COORDINATES_LAT),
       str(CENTRALPOINT_COORDINATES_LON),
       str(CENTRALPOINT_COORDINATES_LAT),
       str(CENTRALPOINT_COORDINATES_LON),
    str(MAX_DISTANCE_AROUND_AREA_KM),
    str([
        {
            'id': vacancy[0],
            'title': str(vacancy[1])[:30],
            'salary': str(vacancy[2])[:20],
            'latitude': vacancy[3],
            'longitude': vacancy[4],
            #'pracodawca': str(vacancy[5])[:30]
        }
        for vacancy in vacancies
    ]).replace("'", '"')  # Преобразуем данные в формат, удобный для JavaScript
)

# Сохраняем HTML в файл
html_file_path = 'vacancies_map.html'
with open(html_file_path, 'w', encoding='utf-8') as file:
    file.write(html_content)

# Открываем файл в браузере
# os.system(f'xdg-open {html_file_path}')  # Для Linux, для Windows используйте os.startfile(html_file_path)
os.startfile(html_file_path)
