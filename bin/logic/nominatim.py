import requests
from bin.settings import DEFAULT_COORDINATES_LATITUDE, DEFAULT_COORDINATES_LONGITUDE

def get_coordinates_latlon_fc(address, nominatim_url):
    latitude, longitude = DEFAULT_COORDINATES_LATITUDE, DEFAULT_COORDINATES_LONGITUDE

    params = {"q": address, "format": "json", "addressdetails": 1}
    headers = {
        'User-Agent': 'NonameApp/1.0 (lavr2004@gmail.com)'  # Укажите свои данные
    }

    try:
        response = requests.get(nominatim_url, params=params, timeout=5)
        response.raise_for_status()
        data = response.json()
        if data:  # Если API вернул данные
            latitude = data[0].get("lat")
            longitude = data[0].get("lon")
    except (requests.RequestException, ValueError) as e:
        print(f"Ошибка при запросе координат для адреса '{address}': {e}")
    finally:
        return latitude, longitude