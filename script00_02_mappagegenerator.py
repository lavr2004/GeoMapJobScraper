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

CENTRALPOINT_COORDINATES_LAT = 52.2297  # Центр Варшавы
CENTRALPOINT_COORDINATES_LON = 21.0122  # Центр Варшавы
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

# Извлекаем вакансии не старше 2 недель по date_parsing
three_weeks_ago = (datetime.utcnow() - timedelta(days=LAST_MAX_COUNT_OF_DAYS_PERIOD)).strftime('%Y%m%d_%H%M%S')
cursor.execute("""
    SELECT id, title, salary, latitude, longitude, employer, parseiteration_id, address, date_published, source, date_parsing
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

    def get_details_url(source, vacancy_id):
        if 'jobs_urzadpracy.sqlite' in source:
            return f"https://oferty.praca.gov.pl/portal/lista-ofert/szczegoly-oferty/{vacancy_id}"
        elif 'jobs_pracujpl' in source:
            return f"https://www.pracuj.pl/praca/,oferta,{vacancy_id}"
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
            'details_url': get_details_url(str(vacancy[9]), vacancy[0])
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
        <link href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.10.5/font/bootstrap-icons.css" rel="stylesheet">
        <!-- UPDATED: 202508150056_dateFormatFlatpickr: ADDED -->
        <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/flatpickr@4.6.13/dist/flatpickr.min.css">
        <!-- UPDATED: 202508150056_dateFormatFlatpickr: ADDED -->
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
                padding: 10px 20px;
                font-size: 18px;
                border-radius: 6px;
                cursor: pointer;
                z-index: 1001;
                box-shadow: 0 2px 6px rgba(0, 0, 0, 0.3);
            }}
            .toggle-btn:hover {{
                background-color: #0056b3;
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
            #tag-container {{
                display: flex;
                flex-wrap: wrap;
                gap: 5px;
                margin-top: 10px;
            }}
            .tag-btn {{
                border: none;
                border-radius: 20px;
                padding: 5px 10px;
                cursor: pointer;
                display: flex;
                align-items: center;
                font-size: 14px;
                background-color: #e0e0e0;
                color: #212529;
            }}
            .tag-btn.active {{
                color: white;
            }}
            .tag-close {{
                margin-left: 5px;
                color: #999;
                cursor: pointer;
            }}
            .tag-close:hover {{
                color: #ff0000;
            }}
            .set-radius-cursor {{
                cursor: url('https://icons.iconarchive.com/icons/papirus-team/papirus-apps/32/pingus-icon-icon.png') 16 32, auto;
            }}
            /* UPDATED: 202508150056_dateFormatFlatpickr: ADDED */
            .flatpickr-input {{
                width: 100%;
                padding: 0.375rem 0.75rem;
                font-size: 1rem;
                line-height: 1.5;
                color: #212529;
                background-color: #fff;
                border: 1px solid #ced4da;
                border-radius: 0.25rem;
            }}
            /* UPDATED: 202508150056_dateFormatFlatpickr: ADDED */
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
                            <!-- UPDATED: 202508150056_dateFormatFlatpickr: REPLACED -->
                            <input type="text" id="date-from" class="form-control flatpickr-input" value="{min_date_formatted}" data-min-date="{min_date_formatted}" data-max-date="{max_date_formatted}">
                            <!-- UPDATED: 202508150056_dateFormatFlatpickr: REPLACED -->
                        </div>
                        <div class="mb-3">
                            <label for="date-to">Filter To:</label>
                            <!-- UPDATED: 202508150056_dateFormatFlatpickr: REPLACED -->
                            <input type="text" id="date-to" class="form-control flatpickr-input" value="{max_date_formatted}" data-min-date="{min_date_formatted}" data-max-date="{max_date_formatted}">
                            <!-- UPDATED: 202508150056_dateFormatFlatpickr: REPLACED -->
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
            <button class="toggle-btn" id="toggleBtn">▼</button>
        </div>
        <div id="map"></div>

        <script src="https://unpkg.com/leaflet@1.7.1/dist/leaflet.js"></script>
        <!-- UPDATED: 202508150056_dateFormatFlatpickr: ADDED -->
        <script src="https://cdn.jsdelivr.net/npm/flatpickr@4.6.13/dist/flatpickr.min.js"></script>
        <!-- UPDATED: 202508150056_dateFormatFlatpickr: ADDED -->
        <script>
        // UPDATED: 202508140300_dynamicheader: ADDED
        const minDate = '{min_date_formatted}';
        const maxDate = '{max_date_formatted}';
        // UPDATED: 202508140300_dynamicheader: ADDED
        let textFiltersActive = true;
        const vacancies = {getcode_vacanciesdata(vacancies)};
        const map = L.map('map').setView({centerpoint_coords_list_str}, 13);
        L.tileLayer('https://{{s}}.tile.openstreetmap.org/{{z}}/{{x}}/{{y}}.png', {{maxZoom: 19}}).addTo(map);

        const binocularIcon = L.icon({{
            iconUrl: 'https://icons.iconarchive.com/icons/iconka/business-finance/256/target-icon.png',
            iconSize: [32, 32],
            iconAnchor: [16, 32],
            popupAnchor: [0, -32]
        }});

        let markers = [];
        let centerCoords = {centerpoint_coords_list_str};
        let binocularMarker = null;
        const radiusCircle = L.circle({centerpoint_coords_list_str}, {{
            radius: {MAX_DISTANCE_AROUND_AREA_KM}000,
            color: 'blue',
            fillColor: 'blue',
            fillOpacity: 0.1
        }}).addTo(map);
        let setRadiusMode = false;

        let searchTags = [];
        let activeTags = new Set();
        let tagColors = {{}};
        // UPDATED: 202508140142_fixedcolors: ADDED
        const availableColors = ['blue', 'gold', 'green', 'orange', 'yellow', 'violet', 'grey', 'black', 'red'];
        // UPDATED: 202508140142_fixedcolors: ADDED
        const maxTags = 10;
        const storageKey = 'vacancyMapFilters';

        // UPDATED: 202508141200_appliedCheckbox: ADDED
        let appliedVacancies = JSON.parse(localStorage.getItem('appliedVacancies')) || [];
        // UPDATED: 202508141200_appliedCheckbox: ADDED
        // UPDATED: 202508141200_appliedErrorFix: ADDED
        if (!Array.isArray(appliedVacancies)) {{
            appliedVacancies = [];
        }}
        // UPDATED: 202508141200_appliedErrorFix: ADDED

        // UPDATED: 202508150056_dateFormatFlatpickr: ADDED
        flatpickr('#date-from', {{
            dateFormat: 'Y-m-d',
            defaultDate: '{min_date_formatted}',
            minDate: '{min_date_formatted}',
            maxDate: '{max_date_formatted}',
            onChange: function(selectedDates, dateStr, instance) {{
                updateFilters();
            }}
        }});
        flatpickr('#date-to', {{
            dateFormat: 'Y-m-d',
            defaultDate: '{max_date_formatted}',
            minDate: '{min_date_formatted}',
            maxDate: '{max_date_formatted}',
            onChange: function(selectedDates, dateStr, instance) {{
                updateFilters();
            }}
        }});
        // UPDATED: 202508150056_dateFormatFlatpickr: ADDED

        // UPDATED: 202508142342_dateFormat: DELETED
        // function formatDateInput(inputElement) {{ ... }}
        // document.getElementById('date-from').addEventListener('change', (e) => {{ ... }});
        // document.getElementById('date-to').addEventListener('change', (e) => {{ ... }});
        // formatDateInput(document.getElementById('date-from'));
        // formatDateInput(document.getElementById('date-to'));
        // UPDATED: 202508142342_dateFormat: DELETED

        function saveToLocalStorage() {{
            localStorage.setItem(storageKey, JSON.stringify({{
                searchTags: searchTags,
                activeTags: Array.from(activeTags),
                centerCoords: centerCoords,
                tagColors: tagColors,
                // UPDATED: 202508141600_textFilters: ADDED
                textFiltersActive: textFiltersActive
                // UPDATED: 202508141600_textFilters: ADDED
            }}));
        }}

        function loadFromLocalStorage() {{
            const savedData = localStorage.getItem(storageKey);
            if (savedData) {{
                const {{ searchTags: savedTags, activeTags: savedActive, centerCoords: savedCoords, tagColors: savedTagColors, textFiltersActive: savedTextFiltersActive }} = JSON.parse(savedData);
                searchTags = savedTags.slice(-maxTags);
                activeTags = new Set(savedActive);
                centerCoords = savedCoords || {centerpoint_coords_list_str};
                // UPDATED: 202508140142_fixedcolors: UPDATED
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
                // UPDATED: 202508140142_fixedcolors: UPDATED
                // UPDATED: 202508141600_textFilters: ADDED
                textFiltersActive = savedTextFiltersActive !== undefined ? savedTextFiltersActive : true;
                // UPDATED: 202508141600_textFilters: ADDED
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
                // UPDATED: 202508140142_fixedcolors: UPDATED
                if (!tagColors[text]) {{
                    const usedColors = Object.values(tagColors);
                    const nextColor = availableColors.find(color => !usedColors.includes(color)) || 'red';
                    tagColors[text] = nextColor;
                }}
                // UPDATED: 202508140142_fixedcolors: UPDATED
                if (searchTags.length > maxTags) {{
                    const removedTag = searchTags.shift();
                    activeTags.delete(removedTag);
                    delete tagColors[removedTag];
                }}
                activeTags.add(text);
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
            // UPDATED: 202508141600_textFilters: UPDATED
            textFiltersActive = true;
            // UPDATED: 202508141600_textFilters: UPDATED
            updateToggleTextFiltersBtn();
            renderTags();
            saveToLocalStorage();
            updateFilters();
        }}

        function removeTag(text) {{
            searchTags = searchTags.filter(tag => tag !== text);
            activeTags.delete(text);
            delete tagColors[text];
            // UPDATED: 202508141600_textFilters: UPDATED
            textFiltersActive = activeTags.size > 0;
            // UPDATED: 202508141600_textFilters: UPDATED
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
                // UPDATED: 202508141600_textFilters: UPDATED
                btn.className = 'tag-btn' + (activeTags.has(tag) && textFiltersActive ? ' active' : '');
                btn.style.backgroundColor = (activeTags.has(tag) && textFiltersActive) ? tagColors[tag] : '#e0e0e0';
                btn.style.color = (activeTags.has(tag) && textFiltersActive) ? '#ffffff' : '#212529';
                // UPDATED: 202508141600_textFilters: UPDATED
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

        // UPDATED: 202508141200_appliedCheckbox: ADDED
        function toggleApply(el) {{
            let url = el.dataset.url;
            if (appliedVacancies.includes(url)) {{
                appliedVacancies = appliedVacancies.filter(u => u !== url);
                el.innerHTML = '<i class="bi bi-square" style="font-size: 1.5rem; color: black;"></i><span style="font-weight: bold; margin-left: 0.5rem;">not applied</span>';
            }} else {{
                appliedVacancies.push(url);
                el.innerHTML = '<i class="bi bi-check-square-fill" style="font-size: 1.5rem; color: green;"></i><span style="font-weight: bold; margin-left: 0.5rem; color: green;">applied</span>';
            }}
            localStorage.setItem('appliedVacancies', JSON.stringify(appliedVacancies));
            // UPDATED: 202508141200_appliedIcon: ADDED
            const markerObj = markers.find(m => m.url === url);
            if (markerObj) {{
                const isApplied = appliedVacancies.includes(url);
                const newIcon = getMarkerIcon(markerObj.color, isApplied);
                markerObj.marker.setIcon(newIcon);
            }}
            // UPDATED: 202508141200_appliedIcon: ADDED
        }}
        // UPDATED: 202508141200_appliedCheckbox: ADDED

        // UPDATED: 202508141200_appliedIcon: ADDED
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
        // UPDATED: 202508141200_appliedIcon: ADDED

        function addMarkers(minSalary, maxDistance, searchText = '', excludeText = '', selectedSource = 'all', dateFrom = '', dateTo = '') {{
            markers.forEach(({{ marker }}) => map.removeLayer(marker));
            markers = [];

            vacancies.forEach(vacancy => {{
                // UPDATED: 202508140142_fixedcolors: UPDATED
                let markerColor = vacancy.is_new && (!textFiltersActive || activeTags.size === 0) ? 'red' : 'blue';
                if (textFiltersActive && activeTags.size > 0) {{
                    for (let tag of activeTags) {{
                        if (vacancy.title.toLowerCase().includes(tag.toLowerCase())) {{
                            markerColor = tagColors[tag];
                            break;
                        }}
                    }}
                }}
                // UPDATED: 202508140142_fixedcolors: UPDATED
                const salary = vacancy.salary;
                const distance = map.distance([vacancy.latitude, vacancy.longitude], centerCoords);
                const title = vacancy.title.toLowerCase();
                const search = searchText.toLowerCase();
                const exclude = excludeText.toLowerCase();
                const source = vacancy.source;
                const parseDate = vacancy.date_parsing.replace('_', '').slice(0, 8);

                const dateFromFormatted = dateFrom.replace(/-/g, '');
                const dateToFormatted = dateTo.replace(/-/g, '');

                // UPDATED: 202508141600_textFilters: UPDATED
                let matchesTag = !textFiltersActive || activeTags.size === 0;
                if (textFiltersActive && activeTags.size > 0) {{
                    for (let tag of activeTags) {{
                        if (title.includes(tag.toLowerCase())) {{
                            matchesTag = true;
                            break;
                        }}
                    }}
                }}
                // UPDATED: 202508141600_textFilters: UPDATED

                if (salary >= minSalary && 
                    distance <= maxDistance && 
                    (search === '' || title.includes(search)) && 
                    (exclude === '' || !title.includes(exclude)) && 
                    (selectedSource === 'all' || source === selectedSource) && 
                    (dateFrom === '' || parseDate >= dateFromFormatted) && 
                    (dateTo === '' || parseDate <= dateToFormatted) &&
                    matchesTag) {{
                    // UPDATED: 202508141200_appliedIcon: ADDED
                    const isApplied = appliedVacancies.includes(vacancy.details_url);
                    const icon = getMarkerIcon(markerColor, isApplied);
                    // UPDATED: 202508141200_appliedIcon: ADDED
                    const marker = L.marker([vacancy.latitude, vacancy.longitude], {{
                        // UPDATED: 202508141200_appliedIcon: UPDATED
                        icon: icon
                        // UPDATED: 202508141200_appliedIcon: UPDATED
                    }}).addTo(map);

                    // UPDATED: 202508141200_dynamicPopup: UPDATED
                    marker.bindPopup(() => {{
                        let applyHtml = appliedVacancies.includes(vacancy.details_url) ? 
                            '<div class="d-flex justify-content-center align-items-center mt-2"><div class="apply-status" data-url="' + vacancy.details_url + '" onclick="toggleApply(this)"><i class="bi bi-check-square-fill" style="font-size: 1.5rem; color: green;"></i><span style="font-weight: bold; margin-left: 0.5rem; color: green;">applied</span></div></div>' :
                            '<div class="d-flex justify-content-center align-items-center mt-2"><div class="apply-status" data-url="' + vacancy.details_url + '" onclick="toggleApply(this)"><i class="bi bi-square" style="font-size: 1.5rem; color: black;"></i><span style="font-weight: bold; margin-left: 0.5rem;">not applied</span></div></div>';

                        return (
                            '<b><h5>Published: </b>' + vacancy.last_publicated + '</h5><br>' +
                            '<b><h5>Parsed: </b>' + vacancy.date_parsing + '</h5><br>' +
                            '<b><h4 style="color:green">' + vacancy.title + '</h4></b><br><b>' + vacancy.employee + '</b><br><br>' + 
                            vacancy.job_address_to_show + '<br><br>' +
                            '<b>Salary: </b>' + vacancy.salary_to_show + '<br>' +
                            '<b>Source: </b>' + vacancy.source + '<br>' +
                            '<a href="' + vacancy.details_url + '" target="_blank">Details...</a>' +
                            applyHtml
                        );
                    }});
                    // UPDATED: 202508141200_dynamicPopup: UPDATED

                    // UPDATED: 202508141200_appliedIcon: UPDATED
                    markers.push({{ marker, is_new: vacancy.is_new, url: vacancy.details_url, color: markerColor }});
                    // UPDATED: 202508141200_appliedIcon: UPDATED
                }}
            }});

            updateCenterMarker();
            // UPDATED: 202508140300_dynamicheader: ADDED
            const effectiveDateFrom = dateFrom || minDate;
            const effectiveDateTo = dateTo || maxDate;
            const daysPeriod = Math.ceil((new Date(effectiveDateTo) - new Date(effectiveDateFrom)) / (1000 * 60 * 60 * 24)) + 1;
            const vacancyCount = markers.length;
            const radiusKm = parseInt(maxDistance / 1000);
            document.getElementById('vacancy-header').textContent = `${{vacancyCount}} job offers in radius of ${{radiusKm}} km for last ${{daysPeriod}} days`;
            // UPDATED: 202508140300_dynamicheader: ADDED
        }}

        // UPDATED: 202508141545_filterMarkersFix: UPDATED
        function filterMarkers(type) {{
            markers.forEach(({{ marker, is_new }}) => {{
                if (type === 'new' && !is_new) {{
                    map.removeLayer(marker);
                }} else if (type === 'old' && is_new) {{
                    map.removeLayer(marker);
                }} else if (!map.hasLayer(marker)) {{
                    map.addLayer(marker);
                }}
            }});
        }}
        // UPDATED: 202508141545_filterMarkersFix: UPDATED

        function updateCircleRadius(radius) {{
            radiusCircle.setRadius(radius);
            radiusCircle.setLatLng(centerCoords);
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
        document.getElementById('search-input').addEventListener('keyup', (e) => {{
            if (e.key === 'Enter') {{
                const text = e.target.value.trim();
                if (text) {{
                    addTag(text);
                    e.target.value = '';
                }}
            }}
        }});
        document.getElementById('save-filter-btn').addEventListener('click', () => {{
            const text = document.getElementById('search-input').value.trim();
            if (text) {{
                addTag(text);
                document.getElementById('search-input').value = '';
            }}
        }});
        document.getElementById('exclude-input').addEventListener('input', updateFilters);
        document.getElementById('source-select').addEventListener('change', updateFilters);
        // UPDATED: 202508150056_dateFormatFlatpickr: DELETED
        // document.getElementById('date-from').addEventListener('change', updateFilters);
        // document.getElementById('date-to').addEventListener('change', updateFilters);
        // UPDATED: 202508150056_dateFormatFlatpickr: DELETED
        document.getElementById('set-radius-btn').addEventListener('click', toggleSetRadiusMode);
        document.getElementById('toggle-text-filters-btn').addEventListener('click', () => {{
            // UPDATED: 202508141600_textFilters: UPDATED
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
            // UPDATED: 202508141600_textFilters: UPDATED
        }});

        // UPDATED: 202508141600_textFilters: UPDATED
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
        // UPDATED: 202508141600_textFilters: UPDATED

        // UPDATED: 202508141200_appliedCheckbox: ADDED
        const currentUrls = vacancies.map(v => v.details_url);
        appliedVacancies = appliedVacancies.filter(url => currentUrls.includes(url));
        localStorage.setItem('appliedVacancies', JSON.stringify(appliedVacancies));
        // UPDATED: 202508141200_appliedCheckbox: ADDED

        loadFromLocalStorage();
        addMarkers(0, {MAX_DISTANCE_AROUND_AREA_KM}000);
        
        // выдвигаем либо прячем контейнер с фильтрами
        document.getElementById('toggleBtn').addEventListener('click', () => {{
            const panel = document.getElementById('filterPanel');
            panel.classList.toggle('hidden');
    
            const btn = document.getElementById('toggleBtn');
            if (panel.classList.contains('hidden')) {{
                btn.textContent = '▲';
            }} else {{
                btn.textContent = '▼';
            }}
        }});
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