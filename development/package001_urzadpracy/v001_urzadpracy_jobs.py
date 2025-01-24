import requests

url = "https://oferty.praca.gov.pl/portal-api/v3/oferta/wyszukiwanie?page=0&size=100&sort=dataDodania,desc"
headers = {
    "Accept": "*/*",
    "Content-Type": "application/json",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
}
data = {
    "miejscowosci": [{"miejscowoscId": "0918123", "zasieg": 0}],
    "kodJezyka": "PL",
    "kodyPocztoweId": ["01-107"],
}

response = requests.post(url, headers=headers, json=data)
print(response.json())


import json
import os
folp = os.path.join(os.getcwd(), "001_python_scripts-for-requesting-jobs")
if not os.path.exists(folp):
    os.mkdir(folp)
fp = os.path.join(folp, "response.json")

with open(fp, "w", encoding="utf-8-sig", errors="ignore") as fw:
    json.dump(response.json(), fw, ensure_ascii=False, indent=4)