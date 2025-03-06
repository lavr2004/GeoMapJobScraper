from bs4 import BeautifulSoup
import json
from jsonpath_ng import parser
import requests

cookies = {
    'gp__cfXfiDZP': '43',
    'gptrackCookie': '99bb3647-5c3f-4a50-y6ae-6a50428adf91',
    'gp_lang': 'pl',
    'gpc_v': '1',
    'gpc_analytic': '1',
    'gpc_func': '1',
    'gpc_ad': '1',
    'gpc_audience': '1',
    'gpc_social': '1',
    '_gcl_au': '1.1.1526634893.1732121151',
    'x-auth-csrf-token': 'ae26d655736547e565e84eaf999be25c9b15bcb67db4e952907477b878b2e75e',
    '_gpauthclient': 'pracuj.pl_external',
    'gpSearchType': 'Default',
    '_gpauthrt': 'ZLZJuxlIZRD%2BuXoKIMOLbJLUMS%2FhVKP%2FqZoeyG6ET%2BeHWeiC%2F7DyTVx88xz7lQu1unplwre9Ectjchwac%2F9xLrsyWHs5UCPJnjYdBzVXEexeGybgJKtOQHSy7IbOuTdfMsIx4F7Be%2FFGAuXDEr%2Fy1Q%3D%3D',
    'gp_tr_gptrackCookie': 'c1b88749-2665-4ad1-b82b-8e98c9e6b785',
    '_gpantiforgery': 'CfDJ8BnsG4UujmlAhMc6W89smJZKuLovf73H9nLwDFytKfwJy4jZkis6Uh-OPSZRqxiz2pMtGEePLenbtqR5wumc-44uCpQIEn_qdtYbIE8jYKxwr-avzzJazkjMtGEePLenbtqR5wumc-44uCpQIEn_qdtYbIE8jYKxwr-avzzJazkjMtCFBrzAjTaUul_Evdm7osgHFwb7Yz0s; _epantiforgery=CfDJ8HUifgaomuZGmjCc5nlQaanCCG7f6ToAIASOMWhelkl4NNACVgJVyfu8pDTdhTjYqb6afyjAPDY4JkQrTW1GkwKVPikAiutSgTCYRYep8Fn1sN-JTH_JNAXkU5AGBByj7Z25uyvDas1sx_TKAtk9wwI',
    'Magpie-XSRF-Token': 'CfDJ8HUifgaomuZGmjCc5nlQaakGg3CzMCCqANlxOUGROTi3Sb9PKlalvEPqFJYdmgU3jlenEqfiBcJGAsGYRoOvzxUqU3C-VEEDMISRSZAyYdSZjvZl0wZTYrh2mYB_5bVM0t0FZ9G2jipZrYG6D0ko0j4',
    '_ga_CJXS9Q5W6G': 'GS1.1.1737679478.2.0.1737679478.60.0.0',
    '_ga_DD6PPTKNH1': 'deleted',
    'x-account-csrf-token': '9cbe863e1275f84c383733499d4fd4059d2db8e042c08cc3ed04d3dc64e902a8',
    '__utmz': 'other',
    '__cfruid': '3a4dab20230f776bac930191548733bb87a460d1-1738018859',
    'gp_ab__spellCheck__231': 'B',
    '_cfuvid': 'SdrhQJMqZRJahjKHizoHMrNXWS6rleiJncecVbW4ovw-1739292576850-0.0.1.1-604800000',
    '_gpauth': 'eyJhbGciOiJSUzI1NiIsImtpZCI6IjI0QkVFNDg5MTIwRTE1ODdBMEYyOEE1ODYwRTY4QkM2OTQwODkxNDAiLCJ4NXQiOiJKTDdraVJJT0ZZZWc4b3BZWU9hTHhwUUlrVUEiLCJ0eXAiOiJKV1QifQ.eyJpc3MiOiJodHRwczovL2F1dGgucHJhY3VqLnBsIiwibmJmIjoxNzM5NTU0MjI2LCJpYXQiOjE3Mzk1NTQyMjYsImV4cCI6MTczOTY0MTIyNiwiYXVkIjpbInByYWN1ai5wbCIsImh0dHBzOi8vYXV0aC5wcmFjdWoucGwvcmVzb3VyY2VzIl0sInNjb3BlIjpbInByYWN1ai5wbCIsIm9mZmxpbmVfYWNjZXNzIl0sImFtciI6WyJleHRlcm5hbCJdLCJjbGllbnRfaWQiOiJwcmFjdWoucGxfZXh0ZXJuYWwiLCJmaWxlc3RvcmVfYWNjZXNzIjoiYWxsbG93Iiwic2tpZGJsYW5kaXJfYWNjZXNzIjoiYWxsbG93Iiwic2tpZGJsYW5kaXJfYWNjZXNzIjoiYWxsbG93In0.X3L2fi1JPegqcPRiKQkqOzQzJpP8IAGZ2HAucrsmYyedTT6USNCLxLk0Nnl2QikmOtekO3pDtL8xz-cGIWLmQQ0TnVIvln_uJMNUV5X9pGLgKfUeD1x9wMadflProXEQJOKRV6s90SScdn-6WwIS8T03RpR8xF3r9IcUlbe59yHg0JmnaTg3fcYT9CRbjTTmO5REdQZ0NWT3bDEybRDNk7FGq22Ey6uATt4OMNLwpYZ4Iod3c0g2Pn7ck9H_JMWFbK1mzWP2_wlBuOWww_h2o_H76j0kpFMM7KcrFg1neAfRst17mw-np8mCI9dYkJ2APRwb6wJbcWH9EsqwDV2cbeRGAt8FAMVClipIaGgSmgklblfV_PBHKplxvtu_NnEz3j9m9IrVeZGI5lcQ3js2b925I22tCM9IzV3IupgZlMTJL5hq0YQ-HyXbb67Y3Sqm1dpK0DtvJzvmr4eT5DMhtFZHptVJoereSy3AjdYwk6OMVmFzOBl-Lv8S8hkpWd4elti1BXyUUDn9Zn1XdDf_Uj7NNIUWcgsdjlhFG6BP_ju90PSyGpXemBVmPh2oawqDcF6cSaFeXtFeKs-28V1GTBz21smlMoevnC57nh-vBPAiYLzY6uF9fnyxBagNkra6boMo9wanuF-FJqWXhqhoK-Tz2w98-RoMhK_zHmRqn9I',
    'priority': 'u=0, i',
    'sec-ch-ua': '"Not A(Brand";v="8", "Chromium";v="132", "Google Chrome";v="132"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"Windows"',
    'sec-fetch-dest': 'document',
    'sec-fetch-mode': 'navigate',
    'sec-fetch-site': 'same-origin',
    'sec-fetch-user': '?1',
    'upgrade-insecure-requests': '1',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/132.0.0.0 Safari/537.36',
}

headers = {
    'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
    'accept-language': 'en-US,en;q=0.9,ru-BY;q=0.8,ru-RU;q=0.7,ru;q=0.6',
    'cache-control': 'max-age=0',
    # 'cookie': 'gp__cfXfiDZP=43; gptrackCookie=99bb3647-5c3f-4a50-y6ae-6a50428adf91; gp_lang=pl; gpc_v=1; gpc_analytic=1; gpc_func=1; gpc_ad=1; gpc_audience=1; gpc_social=1; _gcl_au=1.1.1526634893.1732121151; x-auth-csrf-token=ae26d655736547e565e84eaf999be25c9b15bcb67db4e952907477b878b2e75e; _gpauthclient=pracuj.pl_external; gpSearchType=Default; _gpauthrt=ZLZJuxlIZRD%2BuXoKIMOLbJLUMS%2FhVKP%2FqZoeyG6ET%2BeHWeiC%2F7DyTVx88xz7lQu1unplwre9Ectjchwac%2F9xLrsyWHs5UCPJnjYdBzVXEexeGybgJKtOQHSy7IbOuTdfMsIx4F7Be%2FFGAuXDEr%2Fy1Q%3D%3D; gp_tr_gptrackCookie=c1b88749-2665-4ad1-b82b-8e98c9e6b785; _gpantiforgery=CfDJ8BnsG4UujmlAhMc6W89smJZKuLovf73H9nLwDFytKfwJy4jZkis6Uh-OPSZRqxiz2pMtGEePLenbtqR5wumc-44uCpQIEn_qdtYbIE8jYKxwr-avzzJazkjMtGEePLenbtqR5wumc-44uCpQIEn_qdtYbIE8jYKxwr-avzzJazkjMtCFBrzAjTaUul_Evdm7osgHFwb7Yz0s; _epantiforgery=CfDJ8HUifgaomuZGmjCc5nlQaanCCG7f6ToAIASOMWhelkl4NNACVgJVyfu8pDTdhTjYqb6afyjAPDY4JkQrTW1GkwKVPikAiutSgTCYRYep8Fn1sN-JTH_JNAXkU5AGBByj7Z25uyvDas1sx_TKAtk9wwI; Magpie-XSRF-Token=CfDJ8HUifgaomuZGmjCc5nlQaakGg3CzMCCqANlxOUGROTi3Sb9PKlalvEPqFJYdmgU3jlenEqfiBcJGAsGYRoOvzxUqU3C-VEEDMISRSZAyYdSZjvZl0wZTYrh2mYB_5bVM0t0FZ9G2jipZrYG6D0ko0j4; _ga_CJXS9Q5W6G=GS1.1.1737679478.2.0.1737679478.60.0.0; _ga_DD6PPTKNH1=deleted; x-account-csrf-token=9cbe863e1275f84c383733499d4fd4059d2db8e042c08cc3ed04d3dc64e902a8; __utmz=other; __cfruid=3a4dab20230f776bac930191548733bb87a460d1-1738018859; gp_ab__spellCheck__231=B; _cfuvid=SdrhQJMqZRJahjKHizoHMrNXWS6rleiJncecVbW4ovw-1739292576850-0.0.1.1-604800000; _gpauth=eyJhbGciOiJSUzI1NiIsImtpZCI6IjI0QkVFNDg5MTIwRTE1ODdBMEYyOEE1ODYwRTY4QkM2OTQwODkxNDAiLCJ4NXQiOiJKTDdraVJJT0ZZZWc4b3BZWU9hTHhwUUlrVUEiLCJ0eXAiOiJKV1QifQ.eyJpc3MiOiJodHRwczovL2F1dGgucHJhY3VqLnBsIiwibmJmIjoxNzM5NTU0MjI2LCJpYXQiOjE3Mzk1NTQyMjYsImV4cCI6MTczOTY0MTIyNiwiYXVkIjpbInByYWN1ai5wbCIsImh0dHBzOi8vYXV0aC5wcmFjdWoucGwvcmVzb3VyY2VzIl0sInNjb3BlIjpbInByYWN1ai5wbCIsIm9mZmxpbmVfYWNjZXNzIl0sImFtciI6WyJleHRlcm5hbCJdLCJjbGllbnRfaWQiOiJwcmFjdWoucGxfZXh0ZXJuYWwiLCJmaWxlc3RvcmVfYWNjZXNzIjoiYWxsbG93Iiwic2tpZGJsYW5kaXJfYWNjZXNzIjoiYWxsbG93Iiwic2tpZGJsYW5kaXJfYWNjZXNzIjoiYWxsbG93In0.X3L2fi1JPegqcPRiKQkqOzQzJpP8IAGZ2HAucrsmYyedTT6USNCLxLk0Nnl2QikmOtekO3pDtL8xz-cGIWLmQQ0TnVIvln_uJMNUV5X9pGLgKfUeD1x9wMadflProXEQJOKRV6s90SScdn-6WwIS8T03RpR8xF3r9IcUlbe59yHg0JmnaTg3fcYT9CRbjTTmO5REdQZ0NWT3bDEybRDNk7FGq22Ey6uATt4OMNLwpYZ4Iod3c0g2Pn7ck9H_JMWFbK1mzWP2_wlBuOWww_h2o_H76j0kpFMM7KcrFg1neAfRst17mw-np8mCI9dYkJ2APRwb6wJbcWH9EsqwDV2cbeRGAt8FAMVClipIaGgSmgklblfV_PBHKplxvtu_NnEz3j9m9IrVeZGI5lcQ3js2b925I22tCM9IzV3IupgZlMTJL5hq0YQ-HyXbb67Y3Sqm1dpK0DtvJzvmr4eT5DMhtFZHptVJoereSy3AjdYwk6OMVmFzOBl-Lv8S8hkpWd4elti1BXyUUDn9Zn1XdDf_Uj7NNIUWcgsdjlhFG6BP_ju90PSyGpXemBVmPh2oawqDcF6cSaFeXtFeKs-28V1GTBz21smlMoevnC57nh-vBPAiYLzY6uF9fnyxBagNkra6boMo9wanuF-FJqWXhqhoK-Tz2w98-RoMhK_zHmRqn9I',
}

response = requests.get('https://www.pracuj.pl/praca/warszawa;kw', cookies=cookies, headers=headers)


def print_structure(obj, path="", output_string_list=None): # Изменен параметр output_string на output_string_list
    if output_string_list is None:
        output_string_list = [] # Инициализируем список, если None

    if isinstance(obj, dict):
        for key, value in obj.items():
            current_path = path + f'["{key}"]'
            output_string_list.append(f"{current_path}:") # Добавляем путь в список
            print_structure(value, current_path, output_string_list) # Рекурсивный вызов, передаем список
    elif isinstance(obj, list):
        for i, item in enumerate(obj):
            current_path = path + f'[{i}]'
            output_string_list.append(f"{current_path}:") # Добавляем путь в список
            print_structure(item, current_path, output_string_list) # Рекурсивный вызов, передаем список
    else:
        output_string_list.append(f"{path}: {obj}") # Добавляем путь и значение в список

    return "\n".join(output_string_list) # Возвращаем список строк, соединенных переносом строки


def parse_html_and_visualize(html_file = None, html_content = None, output_filename="structure-of-json-markup.txt"):
    if not html_content:
        with open(html_file, 'r') as f:
            soup = BeautifulSoup(f, 'html.parser')
    else:
        soup = BeautifulSoup(html_content, 'html.parser')

    # Найти скрипт с JSON данными
    script_tag = soup.find('script', id='__NEXT_DATA__')
    json_string = script_tag.string

    # Парсинг JSON
    data = json.loads(json_string)

    # Визуализация структуры (рекурсивная функция)
    structure_string = print_structure(data) # Получаем строку структуры из функции

    # Сохранение структуры в файл
    with open(output_filename, 'w', encoding='utf-8') as file:
        file.write(structure_string) # Записываем полученную строку в файл

    # Пример использования jsonpath
    jsonpath_expr = parser.parse("$.props.data.items[0].name")
    match = jsonpath_expr.find(data)
    if match and len(match) > 0:
        print(match[0].value)
    else:
        print("Path not found in JSON data.")


# Замените 'your_html_file.html' на путь к вашему HTML файлу
parse_html_and_visualize(html_content = response.text)