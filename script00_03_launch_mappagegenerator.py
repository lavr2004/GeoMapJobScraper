import sqlite3
import os
from geopy.distance import geodesic
from datetime import datetime, timedelta
import json
from bin import settings

PLATFORMNAME_str = "combined_jobs"
FILEPATH_DATABASE = os.path.join(settings.FOLDERPATH_RESULTS_ALL, "combined_jobs.sqlite")

MAX_DISTANCE_AROUND_AREA_KM = 30
MAX_ALL_JOBS_COUNT_NOT_FILTERED = 10000
MAX_COUNT_OF_JOBS_FILTERED = 10000
LAST_MAX_COUNT_OF_DAYS_PERIOD = 14

CENTRALPOINT_COORDINATES_LAT = 52.2297  # Центр Варшавы - 52.2053382
CENTRALPOINT_COORDINATES_LON = 21.0122  # Центр Варшавы - 21.0745384
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

#//UPDATED: 202508202311_defaultcoords: UPDATED - Обновлена функция для проверки дополнительных дефолтных координат и возврата флага
def assign_default_coordinates(lat, lon):
    """
    Присваивает дефолтные координаты для вакансий без координат или с координатами, равными общим координатам Варшавы.
    Возвращает кортеж (lat, lon, is_default), где is_default указывает, являются ли координаты дефолтными.
    """
    is_default = False
    if not lat or not lon:
        lat = DEFAULT_COORDINATES_LAT
        lon = DEFAULT_COORDINATES_LON
        is_default = True
    elif (lat == 52.2053382 and lon == 21.0745384) or \
            (lat == 52.22959935742319 and lon == 21.01208877468034) or \
            (lat == 52.23191417658431 and lon == 21.00686832501021):
        lat = DEFAULT_COORDINATES_LAT
        lon = DEFAULT_COORDINATES_LON
        is_default = True
    return lat, lon, is_default
#//UPDATED: 202508202311_defaultcoords: UPDATED

#//UPDATED: 202508202319_fixunpackerror: UPDATED - Исправлена ошибка распаковки из-за нового возвращаемого значения assign_default_coordinates
def add_offset_for_same_vacancies_coordinates(vacancies):
    seen_coords = {}
    processed_pins = []
    for vacancy_tuple in vacancies:
        lat, lon = vacancy_tuple[3], vacancy_tuple[4]
        lat, lon, _ = assign_default_coordinates(lat, lon)  #//UPDATED: 202508202319_fixunpackerror: REPLACED - Игнорируем флаг is_default
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
#//UPDATED: 202508202319_fixunpackerror: UPDATED

#//UPDATED: 202508202311_defaultcoords: UPDATED - Обновлена функция для обработки флага is_default
def filter_vacancies(vacancies, reference_point, max_distance_km=3):
    filtered_vacancies = []
    for vacancy in vacancies:
        temp = list(vacancy)
        lat = temp[3]
        lon = temp[4]

        lat, lon, is_default = assign_default_coordinates(lat, lon)  #//UPDATED: 202508202311_defaultcoords: REPLACED - Добавлен флаг is_default

        vacancy_coords = (lat, lon)
        distance = geodesic(reference_point, vacancy_coords).km
        if distance <= max_distance_km:
            temp[3] = lat
            temp[4] = lon
            temp.append(is_default)  #//UPDATED: 202508202311_defaultcoords: ADDED - Добавляем флаг is_default в данные вакансии
            vacancy = tuple(temp)
            filtered_vacancies.append(vacancy)
    print(f"OK - fetched {len(filtered_vacancies)} vacancies from database")
    filtered_vacancies = add_offset_for_same_vacancies_coordinates(filtered_vacancies)
    print(f"OK - {len(filtered_vacancies)} vacancies stay after processing")
    return filtered_vacancies
#//UPDATED: 202508202311_defaultcoords: UPDATED

# Подключаемся к базе данных
conn = sqlite3.connect(FILEPATH_DATABASE)
cursor = conn.cursor()

# Извлекаем вакансии не старше 2 недель по date_parsing
three_weeks_ago = (datetime.utcnow() - timedelta(days=LAST_MAX_COUNT_OF_DAYS_PERIOD)).strftime('%Y%m%d_%H%M%S')
cursor.execute("""
    SELECT id, title, salary, latitude, longitude, employer, parseiteration_id, address, date_published, source, date_parsing, source_id
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
    current_date = datetime.utcnow().strftime('%Y-%m-%d')

    def get_details_url(source, vacancy_source_id):
        if 'jobs_urzadpracy.sqlite' in source:
            return f"https://oferty.praca.gov.pl/portal/lista-ofert/szczegoly-oferty/{vacancy_source_id}"
        elif 'jobs_pracujpl' in source:
            return f"https://www.pracuj.pl/praca/,oferta,{vacancy_source_id}"
        return "#"

    vacancies_data = [
        {
            'id': vacancy[0],
            'title': str(vacancy[1]),
            'salary': extract_salary(str(vacancy[2])),
            'latitude': vacancy[3],
            'longitude': vacancy[4],
            'employee': str(vacancy[5])[:50],
            'is_new': str(vacancy[8]).split("T")[0] == current_date if vacancy[8] else False,
            'salary_to_show': str(vacancy[2]).split('.')[0] if vacancy[2] else "0",
            'job_address_to_show': str(vacancy[7]) if vacancy[7] else "",
            'last_publicated': str(vacancy[8]).split("T")[0] if vacancy[8] else "N/A",
            'source': str(vacancy[9]),
            'date_parsing': str(vacancy[10]),
            'details_url': get_details_url(str(vacancy[9]), vacancy[11]),
            #'has_address': bool(vacancy[7] and str(vacancy[7]).strip() and not vacancy[12])  #//UPDATED: 202508202311_defaultcoords: REPLACED - Учитываем is_default
            #'has_address': bool(not vacancy[12] or (vacancy[7] and str(vacancy[7]).strip()))  #//UPDATED: 202508210001_addresslogic: REPLACED - has_address True, если координаты не дефолтные или есть адрес
            'has_address': not vacancy[12]  #//UPDATED: 202508210007_addresslogic: REPLACED - has_address True, если координаты не дефолтные
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
    <html lang="ru">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Карта Вакансий</title>
        <link rel="stylesheet" href="https://unpkg.com/leaflet@1.7.1/dist/leaflet.css" />
        <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0-alpha3/dist/css/bootstrap.min.css" rel="stylesheet">
        <link href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.10.5/font/bootstrap-icons.css" rel="stylesheet">
        <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/flatpickr@4.6.13/dist/flatpickr.min.css">
        <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0-alpha3/dist/js/bootstrap.bundle.min.js"></script>
        <link href="https://fonts.googleapis.com/css2?family=Roboto:wght@400;700&display=swap" rel="stylesheet">
        <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/animate.css/4.1.1/animate.min.css" />
        <style>
            body {{
                background-color: #f8f9fa;
                font-family: 'Roboto', sans-serif;
                margin: 0;
                padding: 0;
                overflow: hidden;
            }}
            #map {{ height: 100vh; }}

            /* --- MODIFIED: Top Filter Panel (Original structure, modified behavior) --- */
            .filter-panel {{
                position: fixed; /* Use fixed for consistent positioning */
                top: 0;
                left:0; right:0; /* Ensure full width */
                background-color: #fff;
                z-index: 1000;
                padding: 20px;
                box-shadow: 0 2px 5px rgba(0,0,0,0.2);
                transition: transform 0.3s ease-in-out;
                transform: translateY(-100%); /* Start hidden */
            }}
            .filter-panel.visible {{
                transform: translateY(0);
            }}
            .toggle-btn-top {{
                position: absolute; /* Positioned relative to the panel */
                top: 100%;
                left: 50%;
                transform: translateX(-50%);
                background-color: #007bff;
                color: white;
                border: none;
                padding: 8px 25px;
                font-size: 22px;
                border-bottom-left-radius: 12px;
                border-bottom-right-radius: 12px;
                cursor: pointer;
                z-index: 1001;
                box-shadow: 0 2px 6px rgba(0, 0, 0, 0.3);
            }}
            .toggle-btn-top:hover {{ background-color: #0056b3; }}

            /* --- MODIFIED: Right Side Panel (Improved design, modified behavior) --- */
            .side-panel {{
                position: fixed;
                top: 0;
                right: 0;
                width: 380px;
                max-width: 90%;
                height: 100vh;
                background-color: #fff;
                z-index: 1002;
                box-shadow: -2px 0 8px rgba(0,0,0,0.2);
                transition: transform 0.4s ease-in-out;
                transform: translateX(100%);
            }}
            .side-panel.visible {{
                transform: translateX(0);
            }}
            .toggle-btn-right {{
                position: absolute; /* Positioned relative to the panel */
                top: 50%;
                right: 100%; /* Sticks to the left edge of the panel */
                transform: translateY(-50%);
                background-color: #6c757d;
                color: white;
                border: none;
                padding: 12px 10px;
                font-size: 20px;
                cursor: pointer;
                z-index: 1001;
                box-shadow: -2px 2px 6px rgba(0, 0, 0, 0.3);
                border-top-left-radius: 12px;
                border-bottom-left-radius: 12px;
                display: flex;
                flex-direction: column;
                align-items: center;
                gap: 5px;
            }}
            .toggle-btn-right:hover {{ background-color: #5a6268; }}
            .panel-content {{
                padding: 15px;
                height: 100%;
                display: flex;
                flex-direction: column;
            }}
            .panel-list {{
                overflow-y: auto;
                flex-grow: 1;
            }}
            .vacancy-item {{
                padding: 10px;
                border-bottom: 1px solid #eee;
                font-size: 0.9rem;
                display: flex;
                justify-content: space-between;
                align-items: center;
            }}
            .vacancy-item-details a {{
                text-decoration: none;
                color: #007bff;
                font-weight: bold;
            }}
            .vacancy-item-details p {{ margin: 4px 0 0; color: #6c757d; }}
            .apply-toggle-container {{ cursor: pointer; text-align: center; }}
            
            /* --- Original / Unchanged styles --- */
            .slider {{ width: 100%; }}
            #tag-container {{ display: flex; flex-wrap: wrap; gap: 5px; margin-top: 10px; }}
            .tag-btn {{ border: none; border-radius: 20px; padding: 5px 10px; cursor: pointer; display: flex; align-items: center; font-size: 14px; background-color: #e0e0e0; color: #212529; }}
            .tag-btn.active {{ color: white; }}
            .tag-close {{ margin-left: 5px; color: #999; cursor: pointer; }}
            .tag-close:hover {{ color: #ff0000; }}
            .set-radius-cursor {{ cursor: url('https://icons.iconarchive.com/icons/papirus-team/papirus-apps/32/pingus-icon-icon.png') 16 32, auto; }}
            .flatpickr-input {{ width: 100%; }}
        </style>
    </head>
    <body>
        <div class="filter-panel" id="filterPanel">
            <div class="container">
                <h1 id="vacancy-header">{len(vacancies)} job offers in radius of {MAX_DISTANCE_AROUND_AREA_KM} km for last {LAST_MAX_COUNT_OF_DAYS_PERIOD} days</h1>
                <div class="row">
                    <div class="col-md-4">
                        <div class="mb-3">
                            <label for="search-input">Search by Job Title: <span style="color: #007bff;">(Press Enter to save filter)</span></label>
                            <div class="input-group">
                                <button class="btn btn-primary" id="save-filter-btn">Save Filter</button>
                                <input type="text" id="search-input" class="form-control" placeholder="Enter text to filter">
                            </div>
                        </div>
                        <div class="mb-3">
                            <label for="exclude-input">Not in Job Title:</label>
                            <input type="text" id="exclude-input" class="form-control" placeholder="Exclude text from titles">
                        </div>
                        <div id="tag-container"></div>
                        <button id="toggle-text-filters-btn" class="btn btn-danger mt-2">Deactivate Text Filters</button>
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
                            <input type="text" id="date-from" class="form-control flatpickr-input" value="{min_date_formatted}" data-min-date="{min_date_formatted}" data-max-date="{max_date_formatted}">
                        </div>
                        <div class="mb-3">
                            <label for="date-to">Filter To:</label>
                            <input type="text" id="date-to" class="form-control flatpickr-input" value="{max_date_formatted}" data-min-date="{min_date_formatted}" data-max-date="{max_date_formatted}">
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
                            <div class="input-group">
                                <input id="radius-slider" class="slider" type="range" min="1" max="{MAX_DISTANCE_AROUND_AREA_KM}" step="1" value="{MAX_DISTANCE_AROUND_AREA_KM}">
                            </div>
                            <span id="radius-value">{MAX_DISTANCE_AROUND_AREA_KM} km</span>
                        </div>
                        <div>
                            <button class="btn btn-primary me-2" onclick="filterMarkers('new')">New</button>
                            <button class="btn btn-secondary me-2" onclick="filterMarkers('old')">Old</button>
                            <button class="btn btn-success" onclick="filterMarkers('all')">All</button>
                            <button class="btn btn-primary" id="set-radius-btn"><i class="bi bi-geo-alt-fill"></i> Set Radius Point</button>
                        </div>
                    </div>
                </div>
            </div>
            <button class="toggle-btn-top" id="toggleBtn" title="Show/Hide Filters"><i class="bi bi-sliders"></i></button>
        </div>

        <div class="side-panel right-panel" id="noAddressPanel">
            <button class="toggle-btn-right" id="toggleNoAddressBtn" title="Vacancies without specified address">
                <i class="bi bi-pin-map"></i>
                <span id="noAddressCountBadge" class="badge bg-light text-dark">0</span>
            </button>
            <div class="panel-content">
                <h5 class="border-bottom pb-2">Vacancies without Address</h5>
                <div class="input-group my-3">
                    <input type="text" id="noAddressSearch" class="form-control" placeholder="Search in this list...">
                    <span class="input-group-text"><span id="noAddressVisibleCount">0</span>/<span id="noAddressTotalCount">0</span></span>
                </div>
                <div class="panel-list" id="noAddressList">
                    <p class="text-muted">No vacancies found without a specific address.</p>
                </div>
            </div>
        </div>

        <div id="map"></div>

        <script src="https://unpkg.com/leaflet@1.7.1/dist/leaflet.js"></script>
        <script src="https://cdn.jsdelivr.net/npm/flatpickr@4.6.13/dist/flatpickr.min.js"></script>
        <script>
        // --- MODIFIED: Panel Toggle Logic ---
        document.getElementById('toggleBtn').addEventListener('click', () => 
            document.getElementById('filterPanel').classList.toggle('visible')
        );
        document.getElementById('toggleNoAddressBtn').addEventListener('click', () => 
            document.getElementById('noAddressPanel').classList.toggle('visible')
        );
        
        // ---UNCHANGED SCRIPT LOGIC (with new panel/sync logic)---
        const vacancies = {getcode_vacanciesdata(vacancies)};
        const vacanciesWithoutAddress = vacancies.filter(v => !v.has_address);
        
        let appliedVacancies = JSON.parse(localStorage.getItem('appliedVacancies')) || [];
        if (!Array.isArray(appliedVacancies)) {{ appliedVacancies = []; }}

        // --- MODIFIED: Unified 'applied' status logic for full sync ---
        function masterToggleApply(url) {{
            const index = appliedVacancies.indexOf(url);
            if (index > -1) {{
                appliedVacancies.splice(index, 1); // Remove if exists
            }} else {{
                appliedVacancies.push(url); // Add if not
            }}
            localStorage.setItem('appliedVacancies', JSON.stringify(appliedVacancies));
            updateUiForVacancy(url); // Update all UI parts for this vacancy
        }}

        function updateUiForVacancy(url) {{
            const isApplied = appliedVacancies.includes(url);
            
            // 1. Update Map Marker Icon
            const markerObj = markers.find(m => m.url === url);
            if (markerObj) {{
                markerObj.marker.setIcon(getMarkerIcon(markerObj.color, isApplied));
            }}

            // 2. Update all Checkboxes (in popups, in side panel)
            const appliedStatusHTML = isApplied
                ? '<i class="bi bi-check-square-fill" style="font-size: 1.5rem; color: green;"></i><span style="font-weight: bold; margin-left: 0.5rem; color: green;">applied</span>'
                : '<i class="bi bi-square" style="font-size: 1.5rem; color: black;"></i><span style="font-weight: bold; margin-left: 0.5rem;">not applied</span>';
            
            document.querySelectorAll(`[data-url="${{url}}"]`).forEach(el => {{
                el.innerHTML = appliedStatusHTML;
            }});
        }}
        
        // --- MODIFIED: Function to populate and manage the new panel ---
        function initNoAddressPanel() {{
            const listContainer = document.getElementById('noAddressList');
            const searchInput = document.getElementById('noAddressSearch');
            const totalCountEl = document.getElementById('noAddressTotalCount');
            const visibleCountEl = document.getElementById('noAddressVisibleCount');
            document.getElementById('noAddressCountBadge').textContent = vacanciesWithoutAddress.length;

            if (vacanciesWithoutAddress.length > 0) {{
                listContainer.innerHTML = '';
                vacanciesWithoutAddress.forEach(vacancy => {{
                    const isApplied = appliedVacancies.includes(vacancy.details_url);
                    const appliedStatusHTML = isApplied
                        ? '<i class="bi bi-check-square-fill" style="font-size: 1.5rem; color: green;"></i><span style="font-weight: bold; margin-left: 0.5rem; color: green;">applied</span>'
                        : '<i class="bi bi-square" style="font-size: 1.5rem; color: black;"></i><span style="font-weight: bold; margin-left: 0.5rem;">not applied</span>';
                    
                    const item = document.createElement('div');
                    item.className = 'vacancy-item';
                    item.innerHTML = `
                        <div class="vacancy-item-details">
                            <a href="${{vacancy.details_url}}" target="_blank">${{vacancy.title}}</a>
                            <p>${{vacancy.employee}} | ${{vacancy.salary_to_show}} PLN</p>
                        </div>
                        <div class="apply-toggle-container" data-url="${{vacancy.details_url}}" onclick="masterToggleApply(this.dataset.url)">
                           ${{appliedStatusHTML}}
                        </div>
                    `;
                    listContainer.appendChild(item);
                }});
            }}

            const updateCounts = () => {{
                const visibleItems = listContainer.querySelectorAll('.vacancy-item[style*="display: flex"], .vacancy-item:not([style])').length;
                totalCountEl.textContent = vacanciesWithoutAddress.length;
                visibleCountEl.textContent = visibleItems;
            }};

            searchInput.addEventListener('keyup', () => {{
                const filter = searchInput.value.toLowerCase();
                const items = listContainer.getElementsByClassName('vacancy-item');
                for (let i = 0; i < items.length; i++) {{
                    const title = items[i].querySelector('a').textContent.toLowerCase();
                    if (title.includes(filter)) {{
                        items[i].style.display = 'flex';
                    }} else {{
                        items[i].style.display = 'none';
                    }}
                }}
                updateCounts();
            }});
            updateCounts();
        }}
        
        // --- REST OF THE SCRIPT (Mostly unchanged from original) ---
        const minDate = '{min_date_formatted}';
        const maxDate = '{max_date_formatted}';

        const map = L.map('map').setView({centerpoint_coords_list_str}, 13);
        L.tileLayer('https://{{s}}.tile.openstreetmap.org/{{z}}/{{x}}/{{y}}.png', {{maxZoom: 19, attribution: '© OpenStreetMap contributors'}}).addTo(map);

        const binocularIcon = L.icon({{ iconUrl: 'https://icons.iconarchive.com/icons/iconka/business-finance/256/target-icon.png', iconSize: [32, 32], iconAnchor: [16, 32], popupAnchor: [0, -32] }});
        let markers = [];
        let centerCoords = {centerpoint_coords_list_str};
        let binocularMarker = null;
        const radiusCircle = L.circle({centerpoint_coords_list_str}, {{ radius: {MAX_DISTANCE_AROUND_AREA_KM}000, color: 'blue', fillOpacity: 0.1 }}).addTo(map);
        
        let searchTags = [];
        let activeTags = new Set();
        let tagColors = {{}};
        const availableColors = ['blue', 'gold', 'green', 'orange', 'yellow', 'violet', 'grey', 'black', 'red'];
        const maxTags = 10;
        const storageKey = 'vacancyMapFilters';
        let textFiltersActive = true;
        let setRadiusMode = false;

        function saveToLocalStorage() {{
            localStorage.setItem(storageKey, JSON.stringify({{
                searchTags: searchTags,
                activeTags: Array.from(activeTags),
                centerCoords: centerCoords,
                tagColors: tagColors,
                textFiltersActive: textFiltersActive
            }}));
        }}

        function loadFromLocalStorage() {{
            const savedData = localStorage.getItem(storageKey);
            if (savedData) {{
                const {{ searchTags: savedTags, activeTags: savedActive, centerCoords: savedCoords, tagColors: savedTagColors, textFiltersActive: savedTextFiltersActive }} = JSON.parse(savedData);
                searchTags = savedTags.slice(-maxTags);
                activeTags = new Set(savedActive);
                centerCoords = savedCoords || {centerpoint_coords_list_str};
                tagColors = {{}};
                savedTags.forEach(tag => {{
                    if (savedTagColors[tag] && availableColors.includes(savedTagColors[tag])) {{
                        tagColors[tag] = savedTagColors[tag];
                    }} else {{
                        const usedColors = Object.values(tagColors);
                        const nextColor = availableColors.find(color => !usedColors.includes(color)) || 'red';
                        tagColors[tag] = nextColor;
                    }}
                }});
                textFiltersActive = savedTextFiltersActive !== undefined ? savedTextFiltersActive : true;
                updateToggleTextFiltersBtn();
                updateCenterMarker();
                renderTags();
                updateFilters();
            }}
        }}

        function updateCenterMarker() {{
            if (binocularMarker) {{
                map.removeLayer(binocularMarker);
            }}
            binocularMarker = L.marker(centerCoords, {{ 
                icon: binocularIcon, 
                draggable: false,
                zIndexOffset: 1000
            }})
                .addTo(map)
                .bindPopup('<div class="animate__animated animate__bounce"><b>🎯 Radius point:)</b></div>')
                .openPopup();
            radiusCircle.setLatLng(centerCoords);
        }}

        function toggleSetRadiusMode() {{
            setRadiusMode = !setRadiusMode;
            const setRadiusBtn = document.getElementById('set-radius-btn');
            setRadiusBtn.classList.toggle('active', setRadiusMode);
            if (setRadiusMode) {{
                document.getElementById('map').classList.add('set-radius-cursor');
                map.on('click', onMapClick);
            }} else {{
                document.getElementById('map').classList.remove('set-radius-cursor');
                map.off('click', onMapClick);
            }}
        }}

        function onMapClick(e) {{
            centerCoords = [e.latlng.lat, e.latlng.lng];
            updateCenterMarker();
            saveToLocalStorage();
            updateFilters();
            toggleSetRadiusMode();
        }}

        function addTag(text) {{
            if (text && !searchTags.includes(text)) {{
                searchTags.push(text);
                if (!tagColors[text]) {{
                    const usedColors = Object.values(tagColors);
                    const nextColor = availableColors.find(color => !usedColors.includes(color)) || 'red';
                    tagColors[text] = nextColor;
                }}
                if (searchTags.length > maxTags) {{
                    const removedTag = searchTags.shift();
                    activeTags.delete(removedTag);
                    delete tagColors[removedTag];
                }}
                activeTags.add(text);
                textFiltersActive = true;
                activeTags = new Set(searchTags);
                renderTags();
                saveToLocalStorage();
                updateFilters();
            }}
        }}

        function toggleTag(text) {{
            if (activeTags.has(text)) {{
                activeTags.delete(text);
            }} else {{
                activeTags.add(text);
            }}
            textFiltersActive = true;
            updateToggleTextFiltersBtn();
            renderTags();
            saveToLocalStorage();
            updateFilters();
        }}

        function removeTag(text) {{
            searchTags = searchTags.filter(tag => tag !== text);
            activeTags.delete(text);
            delete tagColors[text];
            textFiltersActive = activeTags.size > 0;
            updateToggleTextFiltersBtn();
            renderTags();
            saveToLocalStorage();
            updateFilters();
        }}

        function renderTags() {{
            const container = document.getElementById('tag-container');
            container.innerHTML = '';
            searchTags.forEach(tag => {{
                const btn = document.createElement('button');
                btn.className = 'tag-btn' + (activeTags.has(tag) && textFiltersActive ? ' active' : '');
                btn.style.backgroundColor = (activeTags.has(tag) && textFiltersActive) ? tagColors[tag] : '#e0e0e0';
                btn.style.color = (activeTags.has(tag) && textFiltersActive) ? '#ffffff' : '#212529';
                btn.textContent = tag;
                btn.onclick = () => toggleTag(tag);

                const close = document.createElement('span');
                close.className = 'tag-close';
                close.textContent = '×';
                close.onclick = (e) => {{
                    e.stopPropagation();
                    removeTag(tag);
                }};

                btn.appendChild(close);
                container.appendChild(btn);
            }});
        }}

        function getMarkerIcon(color, isApplied) {{
            if (isApplied) {{
                return L.icon({{
                    iconUrl: 'https://icons.iconarchive.com/icons/fasticon/action-circles/72/Circle-apply-icon.png',
                    iconSize: [32, 32],
                    iconAnchor: [16, 32],
                    popupAnchor: [0, -32]
                }});
            }} else {{
                return L.icon({{
                    iconUrl: `https://raw.githubusercontent.com/pointhi/leaflet-color-markers/master/img/marker-icon-${{color}}.png`,
                    shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-shadow.png',
                    iconSize: [25, 41],
                    iconAnchor: [12, 41],
                    popupAnchor: [1, -34],
                    shadowSize: [41, 41]
                }});
            }}
        }}

        function addMarkers(minSalary, maxDistance, searchText = '', excludeText = '', selectedSource = 'all', dateFrom = '', dateTo = '') {{
            markers.forEach(({{ marker }}) => map.removeLayer(marker));
            markers = [];

            vacancies.forEach(vacancy => {{
                let markerColor = vacancy.is_new && (!textFiltersActive || activeTags.size === 0) ? 'red' : 'blue';
                if (textFiltersActive && activeTags.size > 0) {{
                    for (let tag of activeTags) {{
                        if (vacancy.title.toLowerCase().includes(tag.toLowerCase())) {{
                            markerColor = tagColors[tag];
                            break;
                        }}
                    }}
                }}
                const salary = vacancy.salary;
                const distance = map.distance([vacancy.latitude, vacancy.longitude], centerCoords);
                const title = vacancy.title.toLowerCase();
                const search = searchText.toLowerCase();
                const exclude = excludeText.toLowerCase();
                const source = vacancy.source;
                const parseDate = vacancy.date_parsing.replace('_', '').slice(0, 8);

                const dateFromFormatted = dateFrom.replace(/-/g, '');
                const dateToFormatted = dateTo.replace(/-/g, '');

                let matchesTag = !textFiltersActive || activeTags.size === 0;
                if (textFiltersActive && activeTags.size > 0) {{
                    for (let tag of activeTags) {{
                        if (title.includes(tag.toLowerCase())) {{
                            matchesTag = true;
                            break;
                        }}
                    }}
                }}

                if (vacancy.has_address &&
                    salary >= minSalary && 
                    distance <= maxDistance && 
                    (search === '' || title.includes(search)) && 
                    (exclude === '' || !title.includes(exclude)) && 
                    (selectedSource === 'all' || source === selectedSource) && 
                    (dateFrom === '' || parseDate >= dateFromFormatted) && 
                    (dateTo === '' || parseDate <= dateToFormatted) &&
                    matchesTag) {{
                    const isApplied = appliedVacancies.includes(vacancy.details_url);
                    const icon = getMarkerIcon(markerColor, isApplied);
                    const marker = L.marker([vacancy.latitude, vacancy.longitude], {{ icon: icon }}).addTo(map);

                    marker.bindPopup(() => {{
                        const isAppliedNow = appliedVacancies.includes(vacancy.details_url);
                        const appliedStatusHTML = isAppliedNow
                            ? '<i class="bi bi-check-square-fill" style="font-size: 1.5rem; color: green;"></i><span style="font-weight: bold; margin-left: 0.5rem; color: green;">applied</span>'
                            : '<i class="bi bi-square" style="font-size: 1.5rem; color: black;"></i><span style="font-weight: bold; margin-left: 0.5rem;">not applied</span>';
                        
                        return (
                            '<b><h5>ID: </b>' + vacancy.id + '</h5><br>' +
                            '<b><h5>latitude: </b>' + vacancy.latitude + '</h5><br>' +
                            '<b><h5>longitude: </b>' + vacancy.longitude + '</h5><br>' +
                            '<b><h5>Published: </b>' + vacancy.last_publicated + '</h5><br>' +
                            '<b><h5>Parsed: </b>' + vacancy.date_parsing + '</h5><br>' +
                            '<b><h4 style="color:green">' + vacancy.title + '</h4></b><br><b>' + vacancy.employee + '</b><br><br>' + 
                            vacancy.job_address_to_show + '<br><br>' +
                            '<b>Salary: </b>' + vacancy.salary_to_show + '<br>' +
                            '<b>Source: </b>' + vacancy.source + '<br>' +
                            '<a href="' + vacancy.details_url + '" target="_blank">Details...</a>' +
                            `<div class="d-flex justify-content-center align-items-center mt-2"><div class="apply-toggle-container" data-url="${{vacancy.details_url}}" onclick="masterToggleApply(this.dataset.url)">${{appliedStatusHTML}}</div></div>`
                        );
                    }});
                    markers.push({{ marker, is_new: vacancy.is_new, url: vacancy.details_url, color: markerColor }});
                }}
            }});

            updateCenterMarker();
            const effectiveDateFrom = dateFrom || minDate;
            const effectiveDateTo = dateTo || maxDate;
            const daysPeriod = Math.ceil((new Date(effectiveDateTo) - new Date(effectiveDateFrom)) / (1000 * 60 * 60 * 24)) + 1;
            const vacancyCount = markers.length;
            const radiusKm = parseInt(maxDistance / 1000);
            document.getElementById('vacancy-header').textContent = `${{vacancyCount}} job offers in radius of ${{radiusKm}} km for last ${{daysPeriod}} days`;
        }}
        
        function filterMarkers(type) {{
            markers.forEach(({{ marker, is_new }}) => {{
                if (type === 'new' && !is_new) {{
                    map.removeLayer(marker.marker);
                }} else if (type === 'old' && is_new) {{
                    map.removeLayer(marker.marker);
                }} else if (!map.hasLayer(marker.marker)) {{
                    map.addLayer(marker.marker);
                }}
            }});
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
            radiusCircle.setRadius(radius);
            addMarkers(minSalary, radius, searchText, excludeText, selectedSource, dateFrom, dateTo);
        }}

        document.getElementById('salary-slider').addEventListener('input', updateFilters);
        document.getElementById('radius-slider').addEventListener('input', updateFilters);
        //UPDATED: 202508161200_disableRealtimeSearch: DELETED - Удалён слушатель 'input' для поля id="search-input" чтобы предотвратить реал-тайм обновления пинов и заголовка при каждом вводе буквы
        // document.getElementById('search-input').addEventListener('input', updateFilters);
        //UPDATED: 202508161200_disableRealtimeSearch: DELETED
        document.getElementById('exclude-input').addEventListener('input', updateFilters);
        document.getElementById('source-select').addEventListener('change', updateFilters);
        
        flatpickr('#date-from', {{ dateFormat: 'Y-m-d', defaultDate: '{min_date_formatted}', onChange: updateFilters }});
        flatpickr('#date-to', {{ dateFormat: 'Y-m-d', defaultDate: '{max_date_formatted}', onChange: updateFilters }});

        function updateToggleTextFiltersBtn() {{
            const btn = document.getElementById('toggle-text-filters-btn');
            if (textFiltersActive) {{
                btn.textContent = 'Deactivate Text Filters';
                btn.classList.remove('btn-success');
                btn.classList.add('btn-danger');
            }} else {{
                btn.textContent = 'Activate Text Filters';
                btn.classList.remove('btn-danger');
                btn.classList.add('btn-success');
            }}
        }}

        document.getElementById('search-input').addEventListener('keyup', (e) => {{
            if (e.key === 'Enter') {{
                const text = e.target.value.trim();
                if (text) {{
                    e.target.value = '';
                    addTag(text);
                }}
            }}
        }});
        document.getElementById('save-filter-btn').addEventListener('click', () => {{
            const text = document.getElementById('search-input').value.trim();
            if (text) {{
                document.getElementById('search-input').value = '';
                addTag(text);
            }}
        }});
        document.getElementById('set-radius-btn').addEventListener('click', toggleSetRadiusMode);
        document.getElementById('toggle-text-filters-btn').addEventListener('click', () => {{
            textFiltersActive = !textFiltersActive;
            if (!textFiltersActive) {{
                activeTags.clear();
            }} else {{
                activeTags = new Set(searchTags);
            }}
            updateToggleTextFiltersBtn();
            renderTags();
            saveToLocalStorage();
            updateFilters();
        }});

        const currentUrls = vacancies.map(v => v.details_url);
        appliedVacancies = appliedVacancies.filter(url => currentUrls.includes(url));
        localStorage.setItem('appliedVacancies', JSON.stringify(appliedVacancies));

        // Initial setup
        window.onload = () => {{
            loadFromLocalStorage();
            initNoAddressPanel();
            updateFilters();
        }};
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


