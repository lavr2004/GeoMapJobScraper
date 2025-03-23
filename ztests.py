import requests

cookies = {
    'gp__cfXfiDZP': '26',
    '__cfruid': 'e555d584e42f97443c0cac8874bd9bc1262c7793-1742652380',
    '_cfuvid': 'bU_6HROCUQz7NYocA4t57cpUwAW7xIYOy2zKyMnbcfk-1742652380088-0.0.1.1-604800000',
    'gp_tr_gptrackCookie': '4a92b28c-8e26-4346-8e0a-40708c8775c7',
    'gp_lang': 'pl',
    '_gpantiforgery': 'CfDJ8BnsG4UujmlAhMc6W89smJb3KSAOkweGLy8VZdBRIbE6WVe3EzCMk29JWyJyPi0IkcvJN3ZfdY9tE733E4GSbSYSsHYidjuzZx57Kwzq0tVRsFRvQNenI6bybeIDKGctdd5biSsAUl40jf64Ho_jOaY',
    'gptrackCookie': '5b44a81b-d742-4172-y422-29ef47e6ba35',
    'gpc_v': '1',
    'gpc_analytic': '1',
    'gpc_func': '1',
    'gpc_ad': '1',
    'gpc_audience': '1',
    'gpc_social': '1',
    '_gcl_au': '1.1.776758616.1742652569',
    '_gid': 'GA1.2.1751474166.1742652569',
    'gp_ab__LocalizationSelector__236': 'B',
    '_fbp': 'fb.1.1742652647327.612258847563636169',
    '__gfp_64b': '6fiFHXxl3yUXW0YUBUQvquaY1XNxVTBts5ov6zh7.FP.W7|1742652647|2|||8:1:32',
    '_clck': '9x47f1%7C2%7Cfuf%7C0%7C1907',
    'gp_tr_gptrackPVID': '41618b16-9450-4397-967f-99f4d409cc38',
    'gptrackPVID': '753f9e06-74bd-46b7-y15b-b89a589caa65',
    'cf_clearance': 'buumsRdkB3Awa.oboMIG8t7uXfruXYATSHl9dJZ_jHU-1742653325-1.2.1.1-n.M6UmMrX._2uElj35dkXbuGw__Yrr1g5M2E9LqOrpg4pf2PIbU6_iXPhStWb2s7dMSCG04ESCUEa6Wy44cEe1IY6FGGLs6.m6vknDSknKBVc86AEZAPH.aEWcmR2JpyYlyf0S1AcFJtmRFOuCQFIw3KsRy1zMczBzl6hi0cD5zYG3qCcosDpJtD3wq1OV7WCWdbUS4e3GPlhmJqiGg1cn7wtmnTuzfdZIEip8QL0QOTv5eN.mW.3BbKobRyfdz1WMWvuhhac_ijCsQHNdlc_TM1oU.yGi7ADBy02nABX6RwXpxXXFx0d_TAv399ijYSiHIXTs2C.UjPSMCRU8O3jRUOMTzEnaWoAnpuo5A1xnM',
    '_ga': 'GA1.2.962952641.1742652502',
    '__rtbh.uid': '%7B%22eventType%22%3A%22uid%22%2C%22id%22%3A%220%22%2C%22expiryDate%22%3A%222026-03-22T14%3A22%3A06.601Z%22%7D',
    '__rtbh.lid': '%7B%22eventType%22%3A%22lid%22%2C%22id%22%3A%22muWyPEFa4e4aUGxvM4pA%22%2C%22expiryDate%22%3A%222026-03-22T14%3A22%3A06.602Z%22%7D',
    '_uetsid': '73f9bda0072711f0b13c8ffdd26f3712',
    '_uetvid': '73fa1800072711f0aa2b139326c8f250',
    'cto_bundle': 'ryzCmV9rTnJpanFFJTJCNkpaQ1YxbWNlOWZMbDI0TjFDYWduQXVEenYlMkJ3VjhDR3NVMVBNTnVpd0UyQ2lqJTJCMjdaU253YUpXUGoyVUY4V2ZjYmJFS2FWMSUyRnR2QXhhQjRoUzFGS1UwREolMkZZVWl5T1N2NFhMS2tCS0FXVVBHJTJCdmRickQ3V05lMg',
    'XSRF-TOKEN': 'CfDJ8BnsG4UujmlAhMc6W89smJaIS0XZsdxrmKLVgx7RccQrl_iD8ikcFhYLfvLCyWmfKFROlePVqRRCO5j1VROQrD0A6P1TwfKnTX44RBSiSZ2WnR_L-J-JV8KyQH-3vM7oj0BFw01RZDF-AMVoFTncCVQ',
    '_ga_GD4CKCV28E': 'GS1.1.1742652501.1.1.1742653333.0.0.0',
    '_ga_WDELMMFCBH': 'GS1.1.1742652501.1.1.1742653333.50.0.0',
    '_ga_DD6PPTKNH1': 'GS1.1.1742652501.1.1.1742653333.50.0.0',
    '_clsk': '106i945%7C1742682100358%7C1%7C1%7Ck.clarity.ms%2Fcollect',
}

headers = {
    'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
    'accept-language': 'en-US,en;q=0.9',
    'priority': 'u=0, i',
    'sec-ch-ua': '"Chromium";v="134", "Not:A-Brand";v="24", "Google Chrome";v="134"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"Windows"',
    'sec-fetch-dest': 'document',
    'sec-fetch-mode': 'navigate',
    'sec-fetch-site': 'none',
    'sec-fetch-user': '?1',
    'upgrade-insecure-requests': '1',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.36',
    # 'cookie': 'gp__cfXfiDZP=26; __cfruid=e555d584e42f97443c0cac8874bd9bc1262c7793-1742652380; _cfuvid=bU_6HROCUQz7NYocA4t57cpUwAW7xIYOy2zKyMnbcfk-1742652380088-0.0.1.1-604800000; gp_tr_gptrackCookie=4a92b28c-8e26-4346-8e0a-40708c8775c7; gp_lang=pl; _gpantiforgery=CfDJ8BnsG4UujmlAhMc6W89smJb3KSAOkweGLy8VZdBRIbE6WVe3EzCMk29JWyJyPi0IkcvJN3ZfdY9tE733E4GSbSYSsHYidjuzZx57Kwzq0tVRsFRvQNenI6bybeIDKGctdd5biSsAUl40jf64Ho_jOaY; gptrackCookie=5b44a81b-d742-4172-y422-29ef47e6ba35; gpc_v=1; gpc_analytic=1; gpc_func=1; gpc_ad=1; gpc_audience=1; gpc_social=1; _gcl_au=1.1.776758616.1742652569; _gid=GA1.2.1751474166.1742652569; gp_ab__LocalizationSelector__236=B; _fbp=fb.1.1742652647327.612258847563636169; __gfp_64b=6fiFHXxl3yUXW0YUBUQvquaY1XNxVTBts5ov6zh7.FP.W7|1742652647|2|||8:1:32; _clck=9x47f1%7C2%7Cfuf%7C0%7C1907; gp_tr_gptrackPVID=41618b16-9450-4397-967f-99f4d409cc38; gptrackPVID=753f9e06-74bd-46b7-y15b-b89a589caa65; cf_clearance=buumsRdkB3Awa.oboMIG8t7uXfruXYATSHl9dJZ_jHU-1742653325-1.2.1.1-n.M6UmMrX._2uElj35dkXbuGw__Yrr1g5M2E9LqOrpg4pf2PIbU6_iXPhStWb2s7dMSCG04ESCUEa6Wy44cEe1IY6FGGLs6.m6vknDSknKBVc86AEZAPH.aEWcmR2JpyYlyf0S1AcFJtmRFOuCQFIw3KsRy1zMczBzl6hi0cD5zYG3qCcosDpJtD3wq1OV7WCWdbUS4e3GPlhmJqiGg1cn7wtmnTuzfdZIEip8QL0QOTv5eN.mW.3BbKobRyfdz1WMWvuhhac_ijCsQHNdlc_TM1oU.yGi7ADBy02nABX6RwXpxXXFx0d_TAv399ijYSiHIXTs2C.UjPSMCRU8O3jRUOMTzEnaWoAnpuo5A1xnM; _ga=GA1.2.962952641.1742652502; __rtbh.uid=%7B%22eventType%22%3A%22uid%22%2C%22id%22%3A%220%22%2C%22expiryDate%22%3A%222026-03-22T14%3A22%3A06.601Z%22%7D; __rtbh.lid=%7B%22eventType%22%3A%22lid%22%2C%22id%22%3A%22muWyPEFa4e4aUGxvM4pA%22%2C%22expiryDate%22%3A%222026-03-22T14%3A22%3A06.602Z%22%7D; _uetsid=73f9bda0072711f0b13c8ffdd26f3712; _uetvid=73fa1800072711f0aa2b139326c8f250; cto_bundle=ryzCmV9rTnJpanFFJTJCNkpaQ1YxbWNlOWZMbDI0TjFDYWduQXVEenYlMkJ3VjhDR3NVMVBNTnVpd0UyQ2lqJTJCMjdaU253YUpXUGoyVUY4V2ZjYmJFS2FWMSUyRnR2QXhhQjRoUzFGS1UwREolMkZZVWl5T1N2NFhMS2tCS0FXVVBHJTJCdmRickQ3V05lMg; XSRF-TOKEN=CfDJ8BnsG4UujmlAhMc6W89smJaIS0XZsdxrmKLVgx7RccQrl_iD8ikcFhYLfvLCyWmfKFROlePVqRRCO5j1VROQrD0A6P1TwfKnTX44RBSiSZ2WnR_L-J-JV8KyQH-3vM7oj0BFw01RZDF-AMVoFTncCVQ; _ga_GD4CKCV28E=GS1.1.1742652501.1.1.1742653333.0.0.0; _ga_WDELMMFCBH=GS1.1.1742652501.1.1.1742653333.50.0.0; _ga_DD6PPTKNH1=GS1.1.1742652501.1.1.1742653333.50.0.0; _clsk=106i945%7C1742682100358%7C1%7C1%7Ck.clarity.ms%2Fcollect',
}

params = {
    'rd': '30',
    'sc': '0',
    'pn': '1',
}

response = requests.get('https://www.pracuj.pl/praca/warszawa;wp', params=params, cookies=cookies, headers=headers)

import bin.parsers.pracujpl.pracujpl_parser
json_data = bin.parsers.pracujpl.pracujpl_parser.recognition_JSON_in_HTML_area_fc(response.text)

import bin.logic.parser
jobs_dc = bin.logic.parser.recursive_json_search_fc(json_data, "groupedOffers")

import json
print(json.dumps(jobs_dc, indent=4, ensure_ascii=False))
print(response.status_code)
print(len(jobs_dc))