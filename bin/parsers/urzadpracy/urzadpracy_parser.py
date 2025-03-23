import time

import bin.logic.web
from bin.settings import NOMINATIM_PAUSE_IF_PUBLIC_API_SECONDS, NOMINATIM_URL

from urllib.parse import unquote, urlparse, parse_qs, quote

def parse_additionally_from_offer_page(jobid, nominatim_pause_if_public_api_seconds: int = 0):
    i = nominatim_pause_if_public_api_seconds
    while i > 0:
        print(f"OK - technical pause before request to public API {i} seconds...")
        time.sleep(1)
        i -= 1

    # Выполнение GET-запроса
    headers = {
        'Accept': '*/*',
        'Accept-Language': 'en-US,en;q=0.9,ru-BY;q=0.8,ru-RU;q=0.7,ru;q=0.6',
        'Connection': 'keep-alive',
        # 'Cookie': 'JSESSIONID=29D988089D078A84A8388D50070C4614.worker15; _ga=GA1.3.876714283.1734011519; _ga_HGXEGXBYEQ=GS1.3.1737155787.23.1.1737155794.53.0.0; cookieConsent=accepted; TS00000000076=0860e70c7dab280023fd2a44e98d5ff798513ff58c90ad87d87511669828a715a87eee304392eca6881a40db5c3fe5b508bc4e125f09d00019c4797ad6e1319444a6975157abb61c81cee8a9eea446618c98f5597f065697f25db19ca6cafa2b85448e435427aad0f9147b365d431b3bb6e271e8cd8b6274ae8fc290e6fbda0d680b32290a91a1abdbd5880d5cf00bdf63425ef730ebd0df9f40248f3029794851ee311110d296be3dcedb71e7aed81868b7c13445d0ffac1562f4c4574d74c3ec0281975793d8f10bb8914a7e09016ff4cbd0d410b68f586d56f80fc28d0ef9c6719574e1bddde760d2f0074eef232668d04c47f246e36e775e7fa429f756d5571b2b46470e0ad7; TSPD_101_DID=0860e70c7dab2800681eee8673f7a69544dda0be38e93686884dd9088efe7c621fadb898b4d2b1a4095baf6b6f4b873a08c0238c39063800ffefa35b0672ee8b3b9105209ab702f5a2065bc81b64875999fa025db83b71fb4f62c07c24abe3b6e86ae78936e20fcacf05f32361e97a13; TS0155ea11=01a1834bee2ed8fdd86250018355bd6a7a55f9beae96fffadc7543e9c07fe67e45c1b57064e4bf439ef273fa0b9481746b21611a63; TS0bfea4fd027=0860e70c7dab2000d07f605c5a524696f9ceb81071b962bb3ec890c5660c46e05b26babca779b3fc089b7eb5761130004c118c710ef36d70419dadf7ac6e845f1ec66d1069692cb46a6f9bd847dbf67e5f4d5e2fce9ee250fe1d2163801a2ca5',
        'Referer': f'https://oferty.praca.gov.pl/portal/lista-ofert/szczegoly-oferty/{jobid}',
        'Sec-Fetch-Dest': 'empty',
        'Sec-Fetch-Mode': 'cors',
        'Sec-Fetch-Site': 'same-origin',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36',
        'sec-ch-ua': '"Google Chrome";v="131", "Chromium";v="131", "Not_A Brand";v="24"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
    }

    params = {
        'alreadyVisited': 'true',
        'hashJap': '',
    }


    # Получение JSON-данных
    data_json, status_code = bin.logic.web.get_json_response_from_url(f'https://oferty.praca.gov.pl/portal-api/v3/oferta/szczegoly/{jobid}', params_dc=params, headers_dc=headers)

    # Парсинг значения адреса
    # address = data["payload"]["pracodawca"]["adres"]
    url = data_json.get("payload", "").get("pracodawca", "").get("mapaGoogleUrl", "")
    if not url:
        url = data_json.get("payload", "").get("pracodawca", "").get("mapaOsmUrl", "")

    if "Warszawa%2C%20Warszawa" in url:
        v = data_json.get("payload", "").get("warunki", "").get("miejscePracy", "")
        url = f"https://maps.google.pl/maps?q={quote(v)}"

    return url



TRY_TO_CONNECT_NOMINATIM_COUNTER = 0
# Функция для вызова Nominatim
def fetch_geolocation(job):
    global TRY_TO_CONNECT_NOMINATIM_COUNTER

    def get_value_torequestfromnominatim(job):
        address_unquote = None

        url = job.get("mapaGoogleUrl", "")
        if not url:
            url = job.get("mapaOsmUrl", "")

        if "Warszawa%2C%20Warszawa" in url:
            url = parse_additionally_from_offer_page(job.get("id"))



        parsed_url = urlparse(url)
        query_params = parse_qs(parsed_url.query)
        if 'query' not in query_params and "q" not in query_params:
            #address = job("miejscePracy","Warsazawa, Polska")
            # return None
            print(f"ER: адрес не извлечен из ссылки, но предустановлен")
        else:
            address_raw = unquote(query_params['q'][0])  # Декодируем адрес из URL
            if not address_raw:
                address_raw = unquote(query_params['query'][0])

            print(f"Извлеченный адрес: {address_raw}")
            if address_raw:
                # Декодируем URL-кодирование

                # Удаляем запятые
                cleaned_string = address_raw.replace(",", "")

                # Разделяем на слова
                words = cleaned_string.split()

                # Оставляем только последние вхождения слов
                unique_words = {}
                for i, word in enumerate(words):
                    unique_words[word] = i  # Сохраняем индекс последнего вхождения

                # Сортируем слова по их индексу появления и формируем результат
                address_unquote = " ".join(sorted(unique_words, key=unique_words.get))
                # address_quote = quote(address_unquote, safe="")
        return address_unquote


    addresstorequest_unquote = get_value_torequestfromnominatim(job)
    # if not addresstorequest_unquote:
    #     return None

    params = {"q": addresstorequest_unquote, "format": "json", "addressdetails": 1}
    headers = {
        'User-Agent': 'NonameApp/1.0 (lavr2004@gmail.com)'  # Укажите свои данные
    }

    if not "localhost" in NOMINATIM_URL:
        print(f"OK - pause before request public API: {NOMINATIM_PAUSE_IF_PUBLIC_API_SECONDS} seconds...")
        time.sleep(NOMINATIM_PAUSE_IF_PUBLIC_API_SECONDS)

    try:
        data_json, status_code = bin.logic.web.get_json_response_from_url(NOMINATIM_URL, headers_dc=headers, params_dc=params)

        if status_code == 200 and data_json:
            return {
                "job_latitude": data_json[0].get("lat") if addresstorequest_unquote else 0,
                "job_longitude": data_json[0].get("lon") if addresstorequest_unquote else 0,
                "job_country": data_json[0]["address"].get("country"),
                "job_locality": data_json[0]["address"].get("city", data_json[0]["address"].get("town", data_json[0]["address"].get("village"))),
                "job_street": data_json[0]["address"].get("road"),
                "job_building": data_json[0]["address"].get("house_number"),
            }

        #response = requests.get(NOMINATIM_URL, params=params, headers=headers)

        #tolookupindebug_urltorequest = f"{NOMINATIM_URL}?q={quote(addresstorequest_unquote, safe="")}&format=json"
        #response = requests.get(urltorequest, headers=headers)
        # if response.status_code == 200:
        #     data = response.json()
        #     #tolookupindebug_data2 = response.text
        #     if data:
        #         return {
        #             "job_latitude": data[0].get("lat") if addresstorequest_unquote else 0,
        #             "job_longitude": data[0].get("lon") if addresstorequest_unquote else 0,
        #             "job_country": data[0]["address"].get("country"),
        #             "job_locality": data[0]["address"].get("city", data[0]["address"].get("town", data[0]["address"].get("village"))),
        #             "job_street": data[0]["address"].get("road"),
        #             "job_building": data[0]["address"].get("house_number"),
        #         }
    except Exception as e:
        if TRY_TO_CONNECT_NOMINATIM_COUNTER == 4:
            input(f"ER: problem to connect any NOMINATIM service - local or public - need to solve it... Uploaded jobs count == 0")
        else:
            print(f"ER: {e}")
            input(f"To switch API Nominatim from {NOMINATIM_URL} to another press enter...")
            #NOMINATIM_URL = NOMINATIM_PUBLIC_API_URL if NOMINATIM_URL == NOMINATIM_PRIVATE_API_URL else NOMINATIM_PRIVATE_API_URL
            TRY_TO_CONNECT_NOMINATIM_COUNTER += 1

    return None