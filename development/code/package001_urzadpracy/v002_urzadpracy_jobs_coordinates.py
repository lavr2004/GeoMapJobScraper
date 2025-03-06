import requests
from urllib.parse import unquote, urlparse, parse_qs

def get_coordinates_from_url(url):
    # Извлечь адрес из параметра query
    parsed_url = urlparse(url)
    query_params = parse_qs(parsed_url.query)
    if 'query' not in query_params:
        return "Параметр 'query' отсутствует в ссылке."
    
    address = unquote(query_params['query'][0])  # Декодируем адрес из URL
    print(f"Извлеченный адрес: {address}")
    
    # Используем API Nominatim для получения координат
    nominatim_url = "https://nominatim.openstreetmap.org/search"
    headers = {
        'User-Agent': 'NonameApp/1.0 (lavr2004@gmail.com)'  # Укажите свои данные
    }
    response = requests.get(nominatim_url, params={
        'q': address,
        'format': 'json',
        'addressdetails': 1,
    }, headers=headers)
    
    if response.status_code != 200:
        return f"Ошибка при запросе к Nominatim: {response.status_code}"
    
    data = response.json()
    if not data:
        return "Координаты для данного адреса не найдены."
    
    # Извлекаем первую найденную запись
    coordinates = {
        'latitude': data[0]['lat'],
        'longitude': data[0]['lon']
    }
    return coordinates

# Пример использования
# url = "https://www.openstreetmap.org/search?query=Zofii%20Na%C5%82kowskiej%2C%20%2011%2C%20Warszawa%2C%20mazowieckie%2C%20Polska"
url = "http://localhost:8080/search?query=Zofii%20Na%C5%82kowskiej%2C%20%2011%2C%20Warszawa%2C%20mazowieckie%2C%20Polska"
coordinates = get_coordinates_from_url(url)
print("Координаты:", coordinates)
