import sqlite3
import os
from geopy.distance import geodesic
from datetime import datetime, timedelta
import json
from bin import settings

PLATFORMNAME_str = "combined_jobs"
FILEPATH_DATABASE = os.path.join(settings.FOLDERPATH_RESULTS_ALL, "combined_jobs.sqlite")

MAX_DISTANCE_AROUND_AREA_KM = 15
MAX_ALL_JOBS_COUNT_NOT_FILTERED = 1000
MAX_COUNT_OF_JOBS_FILTERED = 1000

CENTRALPOINT_COORDINATES_LAT = 52.2321841
CENTRALPOINT_COORDINATES_LON = 20.935230422848832
DEFAULT_COORDINATES_LAT = CENTRALPOINT_COORDINATES_LAT
DEFAULT_COORDINATES_LON = CENTRALPOINT_COORDINATES_LON

ALL_VACANCIES_COUNT_GOT = 0
reference_point = (CENTRALPOINT_COORDINATES_LAT, CENTRALPOINT_COORDINATES_LON)

# Функции generate_pin_offsets и add_offset_for_same_vacancies_coordinates остаются без изменений
import math
def generate_pin_offsets(vacancies_list, radius=0.00015):
    new_vacancies_list = []
    angle_step = 360 / len(vacancies_list)
    for i in range(len(vacancies_list)):
        vacancy_list = vacancies_list[i]
        if i == 0:
            center_lat = vacancy_list[3]
            center_lng = vacancy_list[4]
            new_vacancies_list = [tuple(vacancies_list[i])]
            continue
        angle_deg = i * angle_step
        angle_rad = math.radians(angle_deg)
        offset_lat = radius * math.sin(angle_rad)
        offset_lng = radius * math.cos(angle_rad)
        new_lat = center_lat + offset_lat
        new_lng = center_lng + offset_lng
        vacancy_list[3] = new_lat
        vacancy_list[4] = new_lng
        new_vacancies_list.append(tuple(vacancy_list))
    return new_vacancies_list

def add_offset_for_same_vacancies_coordinates(vacancies):
    seen_coords = {}
    processed_pins = []
    for vacancy_tuple in vacancies:
        lat, lon = vacancy_tuple[3], vacancy_tuple[4]
        if not lat or not lon:
            lat = DEFAULT_COORDINATES_LAT
            lon = DEFAULT_COORDINATES_LON
        if (lat, lon) in seen_coords:
            seen_coords[(lat, lon)].append(list(vacancy_tuple))
        else:
            seen_coords[(lat, lon)] = [list(vacancy_tuple)]
    for k, v in seen_coords.items():
        vacancy_list_list = v
        new_vacancies_lst_lst = generate_pin_offsets(vacancy_list_list) if len(vacancy_list_list) > 1 else [vacancy_list_list[0]]
        for i in new_vacancies_lst_lst:
            processed_pins.append(i)
    return processed_pins

def filter_vacancies(vacancies, reference_point, max_distance_km=3):
    filtered_vacancies = []
    for vacancy in vacancies:
        temp = list(vacancy)
        lat = temp[3]
        lon = temp[4]
        if not lat or not lon:
            lat = DEFAULT_COORDINATES_LAT
            lon = DEFAULT_COORDINATES_LON
        if lat == 52.2053382 and lon == 21.0745384:
            lat = CENTRALPOINT_COORDINATES_LAT
            lon = CENTRALPOINT_COORDINATES_LON
        vacancy_coords = (lat, lon)
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

# Извлекаем вакансии не старше 3 недель по date_parsing
three_weeks_ago = (datetime.utcnow() - timedelta(days=21)).strftime('%Y%m%d_%H%M%S')
cursor.execute("""
    SELECT id, title, salary, latitude, longitude, employer, parseiteration_id, address, date_added, source, date_parsing
    FROM jobs 
    WHERE date_parsing >= ? 
    ORDER BY parseiteration_id DESC 
    LIMIT ?
""", (three_weeks_ago, MAX_ALL_JOBS_COUNT_NOT_FILTERED))
vacancies = cursor.fetchall()

# Отладочный вывод
unique_sources_in_vacancies = set(vacancy[9] for vacancy in vacancies)
print("Уникальные источники в выборке vacancies:", unique_sources_in_vacancies)

# Применяем фильтрацию по расстоянию
vacancies = filter_vacancies(vacancies, reference_point, max_distance_km=MAX_DISTANCE_AROUND_AREA_KM)
ALL_VACANCIES_COUNT_GOT = len(vacancies)
if len(vacancies) > MAX_COUNT_OF_JOBS_FILTERED:
    vacancies = vacancies[:MAX_COUNT_OF_JOBS_FILTERED]

# Определяем минимальную и максимальную даты парсинга для календаря
min_date = min(vacancy[10].replace('_', '')[:8] for vacancy in vacancies if vacancy[10])
max_date = max(vacancy[10].replace('_', '')[:8] for vacancy in vacancies if vacancy[10])
min_date_formatted = f"{min_date[:4]}-{min_date[4:6]}-{min_date[6:8]}"
max_date_formatted = f"{max_date[:4]}-{max_date[4:6]}-{max_date[6:8]}"

conn.close()

def extract_salary(text):
    import re
    if not text:
        return 0
    text = text.split(",")[0]
    if not text:
        return 0
    match = re.search(r'\b\d.\d{2,}\b', text)
    s = str(match.group()) if match else ""
    r = "".join(c for c in s if c in "0123456789")
    return int(r) if r else 0

def getcode_vacanciesdata(vacancies):
    max_parseriteration_id = max(vacancies, key=lambda x: x[6])[6] if vacancies else 0

    def get_details_url(source, vacancy_id):
        if 'jobs_urzadpracy.sqlite' in source:
            return f"https://oferty.praca.gov.pl/portal/lista-ofert/szczegoly-oferty/{vacancy_id}"
        elif 'jobs_pracujpl' in source:  # Подходит для jobs_pracujpl.sqlite и jobs_pracujpl_all.sqlite
            return f"https://www.pracuj.pl/praca/,oferta,{vacancy_id}"
        return "#"  # По умолчанию, если источник неизвестен

    vacancies_data = [
        {
            'id': vacancy[0],
            'title': str(vacancy[1]),
            'salary': extract_salary(str(vacancy[2])),
            'latitude': vacancy[3],
            'longitude': vacancy[4],
            'employee': str(vacancy[5])[:50],
            'is_new': vacancy[6] == max_parseriteration_id,
            'salary_to_show': str(vacancy[2]).split('.')[0] if vacancy[2] else "0",
            'job_address_to_show': str(vacancy[7]) if vacancy[7] else "",
            'last_publicated': str(vacancy[8]).split("T")[0] if vacancy[8] else "N/A",
            'source': str(vacancy[9]),
            'date_parsing': str(vacancy[10]),
            'details_url': get_details_url(str(vacancy[9]), vacancy[0])  # Новое поле с динамической ссылкой
        }
        for vacancy in vacancies
    ]
    return json.dumps(vacancies_data, ensure_ascii=False)

def getcode_map_full2(vacancies):
    centerpoint_coords_list_str = f"[{CENTRALPOINT_COORDINATES_LAT}, {CENTRALPOINT_COORDINATES_LON}]"
    unique_sources = sorted(set(vacancy[9] for vacancy in vacancies))
    source_options = ''.join(f'<option value="{source}">{source}</option>' for source in unique_sources)

    s = f'''
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
        <style>
            body {{
                background-color: #f8f9fa;
                font-family: 'Roboto', sans-serif;
                color: #212529;
                margin: 0;
                padding: 0;
            }}
            #map {{
                height: 100vh;
            }}
            .filter-panel {{
                position: absolute;
                top: 0;
                width: 100%;
                background-color: #fff;
                z-index: 1000;
                padding: 20px;
                box-shadow: 0 2px 5px rgba(0,0,0,0.2);
                transition: transform 0.3s ease-in-out;
            }}
            .filter-panel.hidden {{
                transform: translateY(-100%);
            }}
            .toggle-btn {{
                position: absolute;
                top: 100%;
                left: 50%;
                transform: translateX(-50%);
                background-color: #007bff;
                color: white;
                border: none;
                padding: 5px 10px;
                cursor: pointer;
                z-index: 1001;
            }}
            .slider-label {{
                margin-right: 10px;
            }}
            .slider {{
                width: 100%;
                height: 8px;
                background: #ddd;
                border-radius: 5px;
                outline: none;
                opacity: 0.9;
                transition: opacity 0.2s ease-in-out;
            }}
            .slider:hover {{
                opacity: 1;
            }}
            .slider::-webkit-slider-thumb {{
                appearance: none;
                width: 20px;
                height: 20px;
                background: #007bff;
                border-radius: 50%;
                cursor: pointer;
                box-shadow: 0 0 4px rgba(0, 0, 0, 0.2);
            }}
            .slider::-moz-range-thumb {{
                width: 20px;
                height: 20px;
                background: #007bff;
                border-radius: 50%;
                cursor: pointer;
            }}
        </style>
    </head>
    <body>
        <div class="filter-panel" id="filterPanel">
            <div class="container">
                <h1>VacMap:) {len(vacancies)} job offers in radius of {MAX_DISTANCE_AROUND_AREA_KM} km</h1>
                <div class="row">
                    <div class="col-md-4">
                        <div class="mb-3">
                            <label for="search-input">Search by Job Title:</label>
                            <input type="text" id="search-input" class="form-control" placeholder="Enter text to filter">
                        </div>
                        <div class="mb-3">
                            <label for="exclude-input">Not in Job Title:</label>
                            <input type="text" id="exclude-input" class="form-control" placeholder="Exclude text from titles">
                        </div>
                    </div>
                    <div class="col-md-4">
                        <div class="mb-3">
                            <label for="source-select">Filter by Source:</label>
                            <select id="source-select" class="form-select">
                                <option value="all">All Sources</option>
                                {source_options}
                            </select>
                        </div>
                        <div class="mb-3">
                            <label for="date-from">Filter From:</label>
                            <input type="date" id="date-from" class="form-control" value="{min_date_formatted}" min="{min_date_formatted}" max="{max_date_formatted}">
                        </div>
                        <div class="mb-3">
                            <label for="date-to">Filter To:</label>
                            <input type="date" id="date-to" class="form-control" value="{max_date_formatted}" min="{min_date_formatted}" max="{max_date_formatted}">
                        </div>
                    </div>
                    <div class="col-md-4">
                        <div class="mb-3">
                            <label class="slider-label" for="salary-slider">Minimum Salary:</label>
                            <input id="salary-slider" class="slider" type="range" min="0" max="20000" step="500" value="0">
                            <span id="salary-value">0 PLN</span>
                        </div>
                        <div class="mb-3">
                            <label class="slider-label" for="radius-slider">Search Radius (km):</label>
                            <input id="radius-slider" class="slider" type="range" min="1" max="{MAX_DISTANCE_AROUND_AREA_KM}" step="1" value="{MAX_DISTANCE_AROUND_AREA_KM}">
                            <span id="radius-value">{MAX_DISTANCE_AROUND_AREA_KM} km</span>
                        </div>
                        <div>
                            <h2>Legend:</h2>
                            <p><span style="color:red;">●</span> New Vacancies</p>
                            <p><span style="color:blue;">●</span> Old Vacancies</p>
                            <button class="btn btn-primary me-2" onclick="filterMarkers('new')">New</button>
                            <button class="btn btn-secondary me-2" onclick="filterMarkers('old')">Old</button>
                            <button class="btn btn-success" onclick="filterMarkers('all')">All</button>
                        </div>
                    </div>
                </div>
            </div>
            <button class="toggle-btn" id="toggleBtn">▼</button>
        </div>
        <div id="map"></div>

        <script src="https://unpkg.com/leaflet@1.7.1/dist/leaflet.js"></script>
        <script>
        const vacancies = {getcode_vacanciesdata(vacancies)};
        const map = L.map('map').setView({centerpoint_coords_list_str}, 13);
        L.tileLayer('https://{{s}}.tile.openstreetmap.org/{{z}}/{{x}}/{{y}}.png', {{maxZoom: 19}}).addTo(map);

        const binocularIcon = L.icon({{
            iconUrl: 'https://icons.iconarchive.com/icons/papirus-team/papirus-apps/256/pingus-icon-icon.png',
            iconSize: [32, 32],
            iconAnchor: [16, 32],
            popupAnchor: [0, -32]
        }});

        let markers = [];
        const radiusCircle = L.circle({centerpoint_coords_list_str}, {{
            radius: {MAX_DISTANCE_AROUND_AREA_KM}000,
            color: 'blue',
            fillColor: 'blue',
            fillOpacity: 0.1
        }}).addTo(map);

        function addMarkers(minSalary, maxDistance, searchText = '', excludeText = '', selectedSource = 'all', dateFrom = '', dateTo = '') {{
            markers.forEach(({{ marker }}) => map.removeLayer(marker));
            markers = [];

            vacancies.forEach(vacancy => {{
                const markerColor = vacancy.is_new ? 'red' : 'blue';
                const salary = vacancy.salary;
                const distance = map.distance([vacancy.latitude, vacancy.longitude], {centerpoint_coords_list_str});
                const title = vacancy.title.toLowerCase();
                const search = searchText.toLowerCase();
                const exclude = excludeText.toLowerCase();
                const source = vacancy.source;
                const parseDate = vacancy.date_parsing.replace('_', '').slice(0, 8);

                const dateFromFormatted = dateFrom.replace(/-/g, '');
                const dateToFormatted = dateTo.replace(/-/g, '');

                if (salary >= minSalary && 
                    distance <= maxDistance && 
                    (search === '' || title.includes(search)) && 
                    (exclude === '' || !title.includes(exclude)) && 
                    (selectedSource === 'all' || source === selectedSource) && 
                    (dateFrom === '' || parseDate >= dateFromFormatted) && 
                    (dateTo === '' || parseDate <= dateToFormatted)) {{
                    const marker = L.marker([vacancy.latitude, vacancy.longitude], {{
                        icon: L.icon({{
                            iconUrl: `https://raw.githubusercontent.com/pointhi/leaflet-color-markers/master/img/marker-icon-${{markerColor}}.png`,
                            shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-shadow.png',
                            iconSize: [25, 41],
                            iconAnchor: [12, 41],
                            popupAnchor: [1, -34],
                            shadowSize: [41, 41]
                        }})
                    }}).addTo(map);

                    marker.bindPopup(
                        '<b><h5>Published: </b>' + vacancy.last_publicated + '</h5><br>' +
                        '<b><h5>Parsed: </b>' + vacancy.date_parsing + '</h5><br>' +
                        '<b><h4 style="color:green">' + vacancy.title + '</h4></b><br><b>' + vacancy.employee + '</b><br><br>' + 
                        vacancy.job_address_to_show + '<br><br>' +
                        '<b>Salary: </b>' + vacancy.salary_to_show + '<br>' +
                        '<b>Source: </b>' + vacancy.source + '<br>' +
                        '<a href="' + vacancy.details_url + '" target="_blank">Details...</a>'
                    );

                    markers.push({{ marker, is_new: vacancy.is_new }});
                }}
            }});

            L.marker({centerpoint_coords_list_str}, {{ icon: binocularIcon }})
                .addTo(map)
                .bindPopup('<div class="animate__animated animate__bounce"><b>Here we start! :)</b><br>Search area center</div>')
                .openPopup();
        }}

        function filterMarkers(type) {{
            markers.forEach(({{ marker, is_new }}) => {{
                if (type === 'new' && !is_new) map.removeLayer(marker);
                else if (type === 'old' && is_new) map.removeLayer(marker);
                else if (!map.hasLayer(marker)) map.addLayer(marker);
            }});
        }}

        function updateCircleRadius(radius) {{
            radiusCircle.setRadius(radius);
        }}

        function updateFilters() {{
            const minSalary = parseInt(document.getElementById('salary-slider').value, 10);
            const radius = parseInt(document.getElementById('radius-slider').value, 10) * 1000;
            const searchText = document.getElementById('search-input').value;
            const excludeText = document.getElementById('exclude-input').value;
            const selectedSource = document.getElementById('source-select').value;
            const dateFrom = document.getElementById('date-from').value;
            const dateTo = document.getElementById('date-to').value;
            document.getElementById('salary-value').textContent = `${{minSalary}} PLN`;
            document.getElementById('radius-value').textContent = `${{parseInt(radius / 1000)}} km`;
            updateCircleRadius(radius);
            addMarkers(minSalary, radius, searchText, excludeText, selectedSource, dateFrom, dateTo);
        }}

        document.getElementById('salary-slider').addEventListener('input', updateFilters);
        document.getElementById('radius-slider').addEventListener('input', updateFilters);
        document.getElementById('search-input').addEventListener('input', updateFilters);
        document.getElementById('exclude-input').addEventListener('input', updateFilters);
        document.getElementById('source-select').addEventListener('change', updateFilters);
        document.getElementById('date-from').addEventListener('change', updateFilters);
        document.getElementById('date-to').addEventListener('change', updateFilters);

        const filterPanel = document.getElementById('filterPanel');
        const toggleBtn = document.getElementById('toggleBtn');
        toggleBtn.addEventListener('click', () => {{
            filterPanel.classList.toggle('hidden');
            toggleBtn.textContent = filterPanel.classList.contains('hidden') ? '▼' : '▲';
        }});

        addMarkers(0, {MAX_DISTANCE_AROUND_AREA_KM}000);
        </script>
    </body>
    </html>
    '''
    return s

html_content = getcode_map_full2(vacancies)
html_file_path = settings.get_htmlmapfilepath_fc(PLATFORMNAME_str)
with open(html_file_path, 'w', encoding='utf-8') as file:
    file.write(html_content)

os.startfile(html_file_path)