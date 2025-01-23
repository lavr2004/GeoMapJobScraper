# Получение вакансий ужонда працы 20250121

LICZNIKI: https://oferty.praca.gov.pl/portal-api/v3/oferta/licznik?jezyk=PL



==================== CURL BASH: 20250120

curl 'https://oferty.praca.gov.pl/portal-api/v3/oferta/wyszukiwanie?page=0&size=100&sort=stanowisko,asc' \
  -H 'Accept: */*' \
  -H 'Accept-Language: en-US,en;q=0.9,ru-BY;q=0.8,ru-RU;q=0.7,ru;q=0.6' \
  -H 'Connection: keep-alive' \
  -H 'Content-Type: application/json' \
  -H 'Cookie: JSESSIONID=29D988089D078A84A8388D50070C4614.worker15; _ga=GA1.3.876714283.1734011519; _ga_HGXEGXBYEQ=GS1.3.1737155787.23.1.1737155794.53.0.0; cookieConsent=accepted; TS00000000076=0860e70c7dab2800150d5d34dc1e1a31b67d5668c96bb23c7c46004f03a0eabcec8bf3770904a9b6aaab1d061ab9a80308c3fc9cb609d0005927788074b4bbd4bd67e96291b66d43472e60be7a53d00c62c8470eb9bd1b099b3be99f40d5bbd0fb4d9c56cf3976193b84185b20879e50f4febe91960056c38e6e872a7a8ef1bc95ab7cf82a3d8ef15792624805de5815f4929090ef03b41fe73d80ff43a6f31bbac4239442f46a518b6a8b2a3aa8010b6c29119665f647ba3927cd9c8692c754c504d1ab402854317eb9b056714b46c75a419b035d28dd63dbd1540c7a70c748feb00dcd9da623d66622ffefcb90e97b7dbd23a05f0667a506ed00ae52c0175f81b0b1975e2e9a0a; TSPD_101_DID=0860e70c7dab2800150d5d34dc1e1a31b67d5668c96bb23c7c46004f03a0eabcec8bf3770904a9b6aaab1d061ab9a80308c3fc9cb60638009c346b81d0c560d376d32bf0b54dab380095bf1d28a25b7e84b7c0b8b67fdf4e43445a23942e749a84aa916b16ebdd9e1766155980b04326; TS0155ea11=01a1834bee4d44315592fe20efbc6beec614e281a2048181ead5561356dfe4edf0a1a2a8ba593929366bc05e660b1e8892793c46bc; TS0bfea4fd027=0860e70c7dab20004a4941d198989c354623c2f12bee6323e2e06d5e0c46f4820bf44bec0f3e7f64085ea05d0711300063e7b338cc0068944b28fe9751d600b7d3c1a5637a4d4d2cf9f035a0c5eddd3adfa1d85f2265614b8bae480af31aaa9f' \
  -H 'Origin: https://oferty.praca.gov.pl' \
  -H 'Referer: https://oferty.praca.gov.pl/portal/lista-ofert' \
  -H 'Sec-Fetch-Dest: empty' \
  -H 'Sec-Fetch-Mode: cors' \
  -H 'Sec-Fetch-Site: same-origin' \
  -H 'User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36' \
  -H 'sec-ch-ua: "Google Chrome";v="131", "Chromium";v="131", "Not_A Brand";v="24"' \
  -H 'sec-ch-ua-mobile: ?0' \
  -H 'sec-ch-ua-platform: "Windows"' \
  --data-raw '{"miejscowosci":[{"miejscowoscId":"0918123","zasieg":5}],"kodJezyka":"PL","kodyPocztoweId":["01-107"]}'

==================== CURL BASH: 20250121

curl 'https://oferty.praca.gov.pl/portal-api/v3/oferta/wyszukiwanie?page=0&size=100&sort=dataDodania,asc' \
  -H 'Accept: */*' \
  -H 'Accept-Language: en-US,en;q=0.9,ru-BY;q=0.8,ru-RU;q=0.7,ru;q=0.6' \
  -H 'Connection: keep-alive' \
  -H 'Content-Type: application/json' \
  -H 'Cookie: JSESSIONID=29D988089D078A84A8388D50070C4614.worker15; _ga=GA1.3.876714283.1734011519; _ga_HGXEGXBYEQ=GS1.3.1737155787.23.1.1737155794.53.0.0; cookieConsent=accepted; TScdcb8370078=0860e70c7dab20004d808ee98515a9b8165a91635b7fede039a29c5c06b414da03eb2e6ffda668b508eb97dd1f18380134db9ae007f6da48d6e33f384bdb5d4f09ac47b6f2156920acea2b3ffd40f424c2e311a54e38eab51e86e1f57e289ed221520e32bb857c71b198795b41bd6423862d86eb7164800a49bcb60df14b2d0e62ef036832e0640f1af512d684bccde53e57bb573f05c09cd4bddf66555285ac30781cee0fc10c33a776f6c5e7cc29152e56524d679e31d0100534884c1d1d89ffe0251bec59c0bb81d9bd85bed347161804939eb468d2d3f8ae5921ef03db1ad4499bd2b0e6653c5c3d8127d29e672ddc0d71b1592883f50028646c1dcd25e0171abd93862d159e614cbe962f65a1b9342b86a9462147d565285de9d8feff376a3198bf9fd2bcdbe23d9ee5dcdc23eb21113307b266c825de0980e5a4e757aa2e7ed3bd4d7324cf5e80380d12d8dc89e7a0843996d61344328000caaddd4e4a290ef4a4ffa45041; TS00000000076=0860e70c7dab280051ced38b172ec75d10570b4ca0e5101cefb7d4bafa969a3889eb489fff95601502ec8ed68918e22a0860b471c209d000ac5c8e3df6dea278e70fd1b3b1e0613f38038807a1d80de36499cbb619ceaef622ae409476a938ebc207c33341041867cdd4b8a6dc71acfe5a196d77e27ad8c2b1fb90fea95d08dab0433f0d55776e7e011448a2efd61c7de0dadbcd787f572fa99963c00cc92f3c6bb11df6121644e584111de9cb7da9e7d4438b70a56fec7ede59fbb5311d0a30bc8a4cab62ad2fd40e892b3eb14302e15df11d90d3ab19adc0e6e6aff9ed312e538f3173108ddb72b143fedfe0a079cf04a76ad7ea200e41f459de462258e8a7f6f222e2d4751bb2; TSPD_101_DID=0860e70c7dab280051ced38b172ec75d10570b4ca0e5101cefb7d4bafa969a3889eb489fff95601502ec8ed68918e22a0860b471c2063800474d0bdfcaef9aeb86df787ee41921b7f8c2be1dc60bbc254124177b302f93dcfcdfa38fa8299798d58086237233d7a821c13bc15e29a95d; TS0155ea11=01a1834bee996f883b6173c1c60d5fd00dcc330d7ed4eac2ef275930dafd035764bd9f13227086cdcbe046ae1b1929ff794aae9998; TScdcb8370029=0860e70c7dab2800dff0ccd96b881f8158f568886e732ecd129aee73c9840d3ba00a271b49096e8bf34b31425c57b1c7; TS0bfea4fd027=0860e70c7dab20002f1f545a83024236cafeab4fc8020c56467d799816078c07bae748f606988072081e1ad88b1130004fce0710df490afadebd2ae19dd85d4fbb9666215ae3aa7ebd9deb2bc3d13add683ca1ede0450e77f0788001466c1e82' \
  -H 'Origin: https://oferty.praca.gov.pl' \
  -H 'Referer: https://oferty.praca.gov.pl/portal/lista-ofert' \
  -H 'Sec-Fetch-Dest: empty' \
  -H 'Sec-Fetch-Mode: cors' \
  -H 'Sec-Fetch-Site: same-origin' \
  -H 'User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36' \
  -H 'sec-ch-ua: "Google Chrome";v="131", "Chromium";v="131", "Not_A Brand";v="24"' \
  -H 'sec-ch-ua-mobile: ?0' \
  -H 'sec-ch-ua-platform: "Windows"' \
  --data-raw '{"miejscowosci":[{"miejscowoscId":"0918123","zasieg":0}],"kodJezyka":"PL","kodyPocztoweId":["01-107"]}'

=================== CURL TO PYTHON

import requests

cookies = {
    'JSESSIONID': '29D988089D078A84A8388D50070C4614.worker15',
    '_ga': 'GA1.3.876714283.1734011519',
    '_ga_HGXEGXBYEQ': 'GS1.3.1737155787.23.1.1737155794.53.0.0',
    'cookieConsent': 'accepted',
    'TS00000000076': '0860e70c7dab2800150d5d34dc1e1a31b67d5668c96bb23c7c46004f03a0eabcec8bf3770904a9b6aaab1d061ab9a80308c3fc9cb609d0005927788074b4bbd4bd67e96291b66d43472e60be7a53d00c62c8470eb9bd1b099b3be99f40d5bbd0fb4d9c56cf3976193b84185b20879e50f4febe91960056c38e6e872a7a8ef1bc95ab7cf82a3d8ef15792624805de5815f4929090ef03b41fe73d80ff43a6f31bbac4239442f46a518b6a8b2a3aa8010b6c29119665f647ba3927cd9c8692c754c504d1ab402854317eb9b056714b46c75a419b035d28dd63dbd1540c7a70c748feb00dcd9da623d66622ffefcb90e97b7dbd23a05f0667a506ed00ae52c0175f81b0b1975e2e9a0a',
    'TSPD_101_DID': '0860e70c7dab2800150d5d34dc1e1a31b67d5668c96bb23c7c46004f03a0eabcec8bf3770904a9b6aaab1d061ab9a80308c3fc9cb60638009c346b81d0c560d376d32bf0b54dab380095bf1d28a25b7e84b7c0b8b67fdf4e43445a23942e749a84aa916b16ebdd9e1766155980b04326',
    'TS0155ea11': '01a1834bee4d44315592fe20efbc6beec614e281a2048181ead5561356dfe4edf0a1a2a8ba593929366bc05e660b1e8892793c46bc',
    'TS0bfea4fd027': '0860e70c7dab20004a4941d198989c354623c2f12bee6323e2e06d5e0c46f4820bf44bec0f3e7f64085ea05d0711300063e7b338cc0068944b28fe9751d600b7d3c1a5637a4d4d2cf9f035a0c5eddd3adfa1d85f2265614b8bae480af31aaa9f',
}

headers = {
    'Accept': '*/*',
    'Accept-Language': 'en-US,en;q=0.9,ru-BY;q=0.8,ru-RU;q=0.7,ru;q=0.6',
    'Connection': 'keep-alive',
    'Content-Type': 'application/json',
    # 'Cookie': 'JSESSIONID=29D988089D078A84A8388D50070C4614.worker15; _ga=GA1.3.876714283.1734011519; _ga_HGXEGXBYEQ=GS1.3.1737155787.23.1.1737155794.53.0.0; cookieConsent=accepted; TS00000000076=0860e70c7dab2800150d5d34dc1e1a31b67d5668c96bb23c7c46004f03a0eabcec8bf3770904a9b6aaab1d061ab9a80308c3fc9cb609d0005927788074b4bbd4bd67e96291b66d43472e60be7a53d00c62c8470eb9bd1b099b3be99f40d5bbd0fb4d9c56cf3976193b84185b20879e50f4febe91960056c38e6e872a7a8ef1bc95ab7cf82a3d8ef15792624805de5815f4929090ef03b41fe73d80ff43a6f31bbac4239442f46a518b6a8b2a3aa8010b6c29119665f647ba3927cd9c8692c754c504d1ab402854317eb9b056714b46c75a419b035d28dd63dbd1540c7a70c748feb00dcd9da623d66622ffefcb90e97b7dbd23a05f0667a506ed00ae52c0175f81b0b1975e2e9a0a; TSPD_101_DID=0860e70c7dab2800150d5d34dc1e1a31b67d5668c96bb23c7c46004f03a0eabcec8bf3770904a9b6aaab1d061ab9a80308c3fc9cb60638009c346b81d0c560d376d32bf0b54dab380095bf1d28a25b7e84b7c0b8b67fdf4e43445a23942e749a84aa916b16ebdd9e1766155980b04326; TS0155ea11=01a1834bee4d44315592fe20efbc6beec614e281a2048181ead5561356dfe4edf0a1a2a8ba593929366bc05e660b1e8892793c46bc; TS0bfea4fd027=0860e70c7dab20004a4941d198989c354623c2f12bee6323e2e06d5e0c46f4820bf44bec0f3e7f64085ea05d0711300063e7b338cc0068944b28fe9751d600b7d3c1a5637a4d4d2cf9f035a0c5eddd3adfa1d85f2265614b8bae480af31aaa9f',
    'Origin': 'https://oferty.praca.gov.pl',
    'Referer': 'https://oferty.praca.gov.pl/portal/lista-ofert',
    'Sec-Fetch-Dest': 'empty',
    'Sec-Fetch-Mode': 'cors',
    'Sec-Fetch-Site': 'same-origin',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36',
    'sec-ch-ua': '"Google Chrome";v="131", "Chromium";v="131", "Not_A Brand";v="24"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"Windows"',
}

json_data = {
    'miejscowosci': [
        {
            'miejscowoscId': '0918123',
            'zasieg': 5,
        },
    ],
    'kodJezyka': 'PL',
    'kodyPocztoweId': [
        '01-107',
    ],
}

response = requests.post(
    'https://oferty.praca.gov.pl/portal-api/v3/oferta/wyszukiwanie?page=0&size=100&sort=stanowisko,asc',
    cookies=cookies,
    headers=headers,
    json=json_data,
)

# Note: json_data will not be serialized by requests
# exactly as it was in the original request.
#data = '{"miejscowosci":[{"miejscowoscId":"0918123","zasieg":5}],"kodJezyka":"PL","kodyPocztoweId":["01-107"]}'
#response = requests.post(
#    'https://oferty.praca.gov.pl/portal-api/v3/oferta/wyszukiwanie?page=0&size=100&sort=stanowisko,dsc',
#    cookies=cookies,
#    headers=headers,
#    data=data,
#)


================================================
JOB OFFER ID:
9589131ce4a00e8165d459164355523e

JOB OFFER WEBSITE URL:
https://oferty.praca.gov.pl/portal/lista-ofert/szczegoly-oferty/1055aa2f80340783108bd16356b7bdd37


API URL:
https://oferty.praca.gov.pl/portal-api/v3/oferta/szczegoly/9589131ce4a00e8165d459164355523e?alreadyVisited=true&hashJap=

JOB DESCRIPTION FIELDS:
dataDodaniaCbop - дата, когда добавлена
zakresObowiazkow - description
miejscePracy  - address - !!!!!!!!
miejscowoscNazwa - address locality
mapaOsmUrl - maplocation
wymagania - wymagania