from bs4 import BeautifulSoup
import json
#import jsonpath_ng#pip install  jsonpath-ng
#from jsonpath_ng.jsonpath import parse

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
    '_gpantiforgery': 'CfDJ8BnsG4UujmlAhMc6W89smJZKuLovf73H9nLwDFytKfwJy4jZkis6Uh-OPSZRqxiz2pMtGEePLenbtqR5wumc-44uCpQIEn_qdtYbIE8jYKxwr-avzzJazkjMtCFBrzAjTaUul_Evdm7osgHFwb7Yz0s',
    '_epantiforgery': 'CfDJ8HUifgaomuZGmjCc5nlQaanCCG7f6ToAIASOMWhelkl4NNACVgJVyfu8pDTdhTjYqb6afyjAPDY4JkQrTW1GkwKVPikAiutSgTCYRYep8Fn1sN-JTH_JNAXkU5AGBByj7Z25uyvDas1sx_TKAtk9wwI',
    'Magpie-XSRF-Token': 'CfDJ8HUifgaomuZGmjCc5nlQaakGg3CzMCCqANlxOUGROTi3Sb9PKlalvEPqFJYdmgU3jlenEqfiBcJGAsGYRoOvzxUqU3C-VEEDMISRSZAyYdSZjvZl0wZTYrh2mYB_5bVM0t0FZ9G2jipZrYG6D0ko0j4',
    '_ga_CJXS9Q5W6G': 'GS1.1.1737679478.2.0.1737679478.60.0.0',
    '_ga_DD6PPTKNH1': 'deleted',
    'x-account-csrf-token': '9cbe863e1275f84c383733499d4fd4059d2db8e042c08cc3ed04d3dc64e902a8',
    '__utmz': 'other',
    '__cfruid': '3a4dab20230f776bac930191548733bb87a460d1-1738018859',
    'gp_ab__spellCheck__231': 'B',
    '_cfuvid': 'SdrhQJMqZRJahjKHizoHMrNXWS6rleiJncecVbW4ovw-1739292576850-0.0.1.1-604800000',
    '_gpauth': 'eyJhbGciOiJSUzI1NiIsImtpZCI6IjI0QkVFNDg5MTIwRTE1ODdBMEYyOEE1ODYwRTY4QkM2OTQwODkxNDAiLCJ4NXQiOiJKTDdraVJJT0ZZZWc4b3BZWU9hTHhwUUlrVUEiLCJ0eXAiOiJKV1QifQ.eyJpc3MiOiJodHRwczovL2F1dGgucHJhY3VqLnBsIiwibmJmIjoxNzM5NTU0MjI2LCJpYXQiOjE3Mzk1NTQyMjYsImV4cCI6MTczOTY0MTIyNiwiYXVkIjpbInByYWN1ai5wbCIsImh0dHBzOi8vYXV0aC5wcmFjdWoucGwvcmVzb3VyY2VzIl0sInNjb3BlIjpbInByYWN1ai5wbCIsIm9mZmxpbmVfYWNjZXNzIl0sImFtciI6WyJleHRlcm5hbCJdLCJjbGllbnRfaWQiOiJwcmFjdWoucGxfZXh0ZXJuYWwiLCJmaWxlc3RvcmVfYWNjZXNzIjoiYWxsb3ciLCJhcHBsaWNhdGlvbnNfYWNjZXNzIjoiYWxsb3ciLCJmaWxlX293bmVyIjoidHJ1ZSIsInVzZXJfYWdyZWVtZW50c19hY2Nlc3MiOiJhbGxvdyIsInNhdmVkX29mZmVyc19hY2Nlc3MiOiJhbGxvdyIsImpvYm9mZmVyc19hY2Nlc3MiOiJhbGxvdyIsImNyZWF0ZV9hY2NvdW50IjoiYWxsb3ciLCJnZXRfYWNjb3VudCI6ImFsbG93IiwiYWdyZWVtZW50X3Jldm9rZSI6ImFsbG93IiwibmVicmFza2FfYWNjZXNzIjoiYWxsb3ciLCJhcHBsaWNhdGlvbnNmb3JtX2FjY2VzcyI6ImFsbG93Iiwic2tpZGJsYW5kaXJfYWNjZXNzIjoiYWxsb3ciLCJjb25maXJtX25ld19lbWFpbCI6ImFsbG93IiwidHJhY2tpbmdfYWNjZXNzIjoiYWxsb3ciLCJha2lyYV9hY2Nlc3MiOiJhbGxvdyIsInBlcnNvbmFsaXp1amFjeXBhdHJ5a19hY2Nlc3MiOiJhbGxvdyIsInN1YiI6Im1vanByYWN1ajoyMzQ0Njg2OCIsImF1dGhfdGltZSI6MTczMjEyMTE2NSwiaWRwIjoiZ3J1cGFwcmFjdWoiLCJlbWFpbCI6ImxhdnIyMDA0QGdtYWlsLmNvbSIsIklzQ29uZmlybWVkIjoiVHJ1ZSIsImVtYWlsX3ZlcmlmaWVkIjoiVHJ1ZSIsImdpdmVuX25hbWUiOiJBbmRyZWkiLCJmYW1pbHlfbmFtZSI6IklobmF0b3ZpY3oiLCJDaXR5IjoiV2Fyc3phd2EiLCJFbXBsb3ltZW50TGV2ZWwiOiJzYW1vZHppZWxueSBzcGVjamFsaXN0YSIsInVzZXJmaWxlc19hY2Nlc3MiOiJhbGxvdyIsInJvbGUiOiJFeHRlcm5hbENsaWVudCIsInNpbHZlcnN0YXJfYWNjZXNzIjoiYWxsb3ciLCJoZWR3aWdhX2FjY2VzcyI6ImFsbG93IiwibWFpbmVfYWNjZXNzIjoiYWxsb3ciLCJtYWluZV9zdXJ2ZXlzX3dyaXRlIjoiYWxsb3ciLCJtYWluZV9zdXJ2ZXlzX3JlYWQiOiJteSIsIm1haW5lX2NvbXBhcmlzb25fcmVhZCI6Im15IiwiaGF3YWlpX2FjY2VzcyI6ImFsbG93Iiwib2tsYWhvbWFfYWNjZXNzIjoiYWxsb3ciLCJjb250ZW50b3d5Y3lwcmlhbl9hY2Nlc3MiOiJhbGxvdyIsInN6dWthamFjeXN6eW1vbl9hY2Nlc3MiOiJhbGxvdyIsInNhbmZyYW5jaXNjb19hY2Nlc3MiOiJhbGxvdyIsIm5pdHJ1amFjeW5lcG9tdWNlbl9hY2Nlc3MiOiJhbGxvdyIsInRleGFzX2FjY2VzcyI6ImFsbG93IiwidXNlckdyb3VwIjoiQ2FuZGlkYXRlcyIsInJlY29tbWVuZGF0aW9uX2FjY2VzcyI6ImFsbG93In0.X3L2fi1JPegqcPRiKQkqOzQzJpP8IAGZ2HAucrsmYyedTT6USNCLxLk0Nnl2QikmOtekO3pDtL8xz-cGIWLmQQ0TnVIvln_uJMNUV5X9pGLgKfUeD1x9wMadflProXEQJOKRV6s90SScdn-6WwIS8T03RpR8xF3r9IcUlbe59yHg0JmnaTg3fcYT9CRbjTTmO5REdQZ0NWT3bDEybRDNk7FGq22Ey6uATt4OMNLwpYZ4Iod3c0g2Pn7ck9H_JMWFbK1mzWP2_wlBuOWww_h2o_H76j0kpFMM7KcrFg1neAfRst17mw-np8mCI9dYkJ2APRwb6wJbcWH9EsqwDV2cbeRGAt8FAMVClipIaGgSmgklblfV_PBHKplxvtu_NnEz3j9m9IrVeZGI5lcQ3js2b925I22tCM9IzV3IupgZlMTJL5hq0YQ-HyXbb67Y3Sqm1dpK0DtvJzvmr4eT5DMhtFZHptVJoereSy3AjdYwk6OMVmFzOBl-Lv8S8hkpWd4elti1BXyUUDn9Zn1XdDf_Uj7NNIUWcgsdjlhFG6BP_ju90PSyGpXemBVmPh2oawqDcF6cSaFeXtFeKs-28V1GTBz21smlMoevnC57nh-vBPAiYLzY6uF9fnyxBagNkra6boMo9wanuF-FJqWXhqhoK-Tz2w98-RoMhK_zHmRqn9I',
    '_gid': 'GA1.2.800044253.1739554231',
    '__gfp_64b': '0UC3qmczVRjS78rRVt7ef23jqxelq2FtjwpEJd8jaFL.P7|1732121151|2|||8:1:32',
    '_clck': 'b27ccm%7C2%7Cftf%7C0%7C1785',
    '__cf_bm': '_uz5U_vS9fTj06.VxrENJpU.1haq9VTWMuZOV0MvEkE-1739558875-1.0.1.1-3nBZNcWaGk_fsfMUbevb0ymVDP8AvuVgDZgEzs5XHtrR_bhyi4z_bSokPm1B.hiBzjXA9Dfw6JjFX9eeJHWOyQ',
    'gp_tr_gptrackPVID': '95937c97-7bad-498a-a8dc-3ab9bff74240',
    'gptrackPVID': 'e44f6df7-dab5-4a7d-y3ae-cf9fab908297',
    'XSRF-TOKEN': 'CfDJ8BnsG4UujmlAhMc6W89smJbZfdIOYjFFRPpTkSMCFJs_t6zuPnY3cbKU6NN4u6RUFUmJeEqWbgTDLsIAaOEhrJ0BqxuJjATnMW0TX978AsaqDGHeKfV-riv1PjLluwOdiXxPCTUtOmmvvNWumuxB9YQ',
    '_ga_GD4CKCV28E': 'GS1.1.1739558243.10.1.1739558879.0.0.0',
    '_ga_DD6PPTKNH1': 'GS1.1.1739558243.43.1.1739558879.60.0.0',
    '_ga_WDELMMFCBH': 'GS1.1.1739558243.43.1.1739558879.60.0.0',
    'cf_clearance': '7aOrtl7Liy27PV2lHtuEWwZhzciwY8ynD_LTNdUOYWI-1739558878-1.2.1.1-EOKnTdxywG7q46PLgSFmuAyCj4uOeSAOuWZLcBgB9D6NvGwGaiUzPhETW7ElKVSd_gFXEeK9KehzL9jU73PA_l_o1aJGOQ_I.6q9FahMirFVyqzTohO2PtnIuiPuvhA8U5jUMIfbOa4NT_O9KUurxtcvZdmcrbIeSYx2bsQ8E690OihK0_QKYer5lrozyfS.toA7ES6MM1LQBrmWyek54QTUSXHttQrQEX6nt5SnXIQCUVTE_yyDZUbB4ucg7ew2REUu68rdjZu8q3.u5.E5e0R5CoUc893z_LtXoeosZck',
    '_ga': 'GA1.2.430510135.1732121151',
    '__rtbh.uid': '%7B%22eventType%22%3A%22uid%22%2C%22id%22%3A%2223446868%22%2C%22expiryDate%22%3A%222026-02-14T18%3A48%3A02.239Z%22%7D',
    '__rtbh.lid': '%7B%22eventType%22%3A%22lid%22%2C%22id%22%3A%22wS03jY4zTOE06cPIxYsX%22%2C%22expiryDate%22%3A%222026-02-14T18%3A48%3A02.240Z%22%7D',
    '_uetsid': '64827bf0eaf911ef85f9d11556d64204',
    '_uetvid': 'e7bad5b0a75e11efae57936341321d2e',
    'cto_bundle': 'RXEldF9PM2hLMXZJU2djU3Q0QnZxUXpBMmxnWW1kckRZekluWHNra2xjNUg5RjQwJTJGcjNtc0kzN2JoamxhJTJCYVAyeml6YVFQJTJGMHozck9pVUF4VGpWODh3TGFrZXF4Ym43S3JVNTU1SnJwR2Q3NHVqQ0YlMkZLTjJna0h1eTVMUkdxbDhxR3ZFJTJGVWUwYlBPUzVMV01sZjE0TyUyRjNDSnclM0QlM0Q',
    'cto_bundle': 'RXEldF9PM2hLMXZJU2djU3Q0QnZxUXpBMmxnWW1kckRZekluWHNra2xjNUg5RjQwJTJGcjNtc0kzN2JoamxhJTJCYVAyeml6YVFQJTJGMHozck9pVUF4VGpWODh3TGFrZXF4Ym43S3JVNTU1SnJwR2Q3NHVqQ0YlMkZLTjJna0h1eTVMUkdxbDhxR3ZFJTJGVWUwYlBPUzVMV01sZjE0TyUyRjNDSnclM0QlM0Q',
    '_clsk': 'b43ifl%7C1739560220848%7C2%7C0%7Cx.clarity.ms%2Fcollect',
}

headers = {
    'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
    'accept-language': 'en-US,en;q=0.9,ru-BY;q=0.8,ru-RU;q=0.7,ru;q=0.6',
    'cache-control': 'max-age=0',
    # 'cookie': 'gp__cfXfiDZP=43; gptrackCookie=99bb3647-5c3f-4a50-y6ae-6a50428adf91; gp_lang=pl; gpc_v=1; gpc_analytic=1; gpc_func=1; gpc_ad=1; gpc_audience=1; gpc_social=1; _gcl_au=1.1.1526634893.1732121151; x-auth-csrf-token=ae26d655736547e565e84eaf999be25c9b15bcb67db4e952907477b878b2e75e; _gpauthclient=pracuj.pl_external; gpSearchType=Default; _gpauthrt=ZLZJuxlIZRD%2BuXoKIMOLbJLUMS%2FhVKP%2FqZoeyG6ET%2BeHWeiC%2F7DyTVx88xz7lQu1unplwre9Ectjchwac%2F9xLrsyWHs5UCPJnjYdBzVXEexeGybgJKtOQHSy7IbOuTdfMsIx4F7Be%2FFGAuXDEr%2Fy1Q%3D%3D; gp_tr_gptrackCookie=c1b88749-2665-4ad1-b82b-8e98c9e6b785; _gpantiforgery=CfDJ8BnsG4UujmlAhMc6W89smJZKuLovf73H9nLwDFytKfwJy4jZkis6Uh-OPSZRqxiz2pMtGEePLenbtqR5wumc-44uCpQIEn_qdtYbIE8jYKxwr-avzzJazkjMtCFBrzAjTaUul_Evdm7osgHFwb7Yz0s; _epantiforgery=CfDJ8HUifgaomuZGmjCc5nlQaanCCG7f6ToAIASOMWhelkl4NNACVgJVyfu8pDTdhTjYqb6afyjAPDY4JkQrTW1GkwKVPikAiutSgTCYRYep8Fn1sN-JTH_JNAXkU5AGBByj7Z25uyvDas1sx_TKAtk9wwI; Magpie-XSRF-Token=CfDJ8HUifgaomuZGmjCc5nlQaakGg3CzMCCqANlxOUGROTi3Sb9PKlalvEPqFJYdmgU3jlenEqfiBcJGAsGYRoOvzxUqU3C-VEEDMISRSZAyYdSZjvZl0wZTYrh2mYB_5bVM0t0FZ9G2jipZrYG6D0ko0j4; _ga_CJXS9Q5W6G=GS1.1.1737679478.2.0.1737679478.60.0.0; _ga_DD6PPTKNH1=deleted; x-account-csrf-token=9cbe863e1275f84c383733499d4fd4059d2db8e042c08cc3ed04d3dc64e902a8; __utmz=other; __cfruid=3a4dab20230f776bac930191548733bb87a460d1-1738018859; gp_ab__spellCheck__231=B; _cfuvid=SdrhQJMqZRJahjKHizoHMrNXWS6rleiJncecVbW4ovw-1739292576850-0.0.1.1-604800000; _gpauth=eyJhbGciOiJSUzI1NiIsImtpZCI6IjI0QkVFNDg5MTIwRTE1ODdBMEYyOEE1ODYwRTY4QkM2OTQwODkxNDAiLCJ4NXQiOiJKTDdraVJJT0ZZZWc4b3BZWU9hTHhwUUlrVUEiLCJ0eXAiOiJKV1QifQ.eyJpc3MiOiJodHRwczovL2F1dGgucHJhY3VqLnBsIiwibmJmIjoxNzM5NTU0MjI2LCJpYXQiOjE3Mzk1NTQyMjYsImV4cCI6MTczOTY0MTIyNiwiYXVkIjpbInByYWN1ai5wbCIsImh0dHBzOi8vYXV0aC5wcmFjdWoucGwvcmVzb3VyY2VzIl0sInNjb3BlIjpbInByYWN1ai5wbCIsIm9mZmxpbmVfYWNjZXNzIl0sImFtciI6WyJleHRlcm5hbCJdLCJjbGllbnRfaWQiOiJwcmFjdWoucGxfZXh0ZXJuYWwiLCJmaWxlc3RvcmVfYWNjZXNzIjoiYWxsb3ciLCJhcHBsaWNhdGlvbnNfYWNjZXNzIjoiYWxsb3ciLCJmaWxlX293bmVyIjoidHJ1ZSIsInVzZXJfYWdyZWVtZW50c19hY2Nlc3MiOiJhbGxvdyIsInNhdmVkX29mZmVyc19hY2Nlc3MiOiJhbGxvdyIsImpvYm9mZmVyc19hY2Nlc3MiOiJhbGxvdyIsImNyZWF0ZV9hY2NvdW50IjoiYWxsb3ciLCJnZXRfYWNjb3VudCI6ImFsbG93IiwiYWdyZWVtZW50X3Jldm9rZSI6ImFsbG93IiwibmVicmFza2FfYWNjZXNzIjoiYWxsb3ciLCJhcHBsaWNhdGlvbnNmb3JtX2FjY2VzcyI6ImFsbG93Iiwic2tpZGJsYW5kaXJfYWNjZXNzIjoiYWxsb3ciLCJjb25maXJtX25ld19lbWFpbCI6ImFsbG93IiwidHJhY2tpbmdfYWNjZXNzIjoiYWxsb3ciLCJha2lyYV9hY2Nlc3MiOiJhbGxvdyIsInBlcnNvbmFsaXp1amFjeXBhdHJ5a19hY2Nlc3MiOiJhbGxvdyIsInN1YiI6Im1vanByYWN1ajoyMzQ0Njg2OCIsImF1dGhfdGltZSI6MTczMjEyMTE2NSwiaWRwIjoiZ3J1cGFwcmFjdWoiLCJlbWFpbCI6ImxhdnIyMDA0QGdtYWlsLmNvbSIsIklzQ29uZmlybWVkIjoiVHJ1ZSIsImVtYWlsX3ZlcmlmaWVkIjoiVHJ1ZSIsImdpdmVuX25hbWUiOiJBbmRyZWkiLCJmYW1pbHlfbmFtZSI6IklobmF0b3ZpY3oiLCJDaXR5IjoiV2Fyc3phd2EiLCJFbXBsb3ltZW50TGV2ZWwiOiJzYW1vZHppZWxueSBzcGVjamFsaXN0YSIsInVzZXJmaWxlc19hY2Nlc3MiOiJhbGxvdyIsInJvbGUiOiJFeHRlcm5hbENsaWVudCIsInNpbHZlcnN0YXJfYWNjZXNzIjoiYWxsb3ciLCJoZWR3aWdhX2FjY2VzcyI6ImFsbG93IiwibWFpbmVfYWNjZXNzIjoiYWxsb3ciLCJtYWluZV9zdXJ2ZXlzX3dyaXRlIjoiYWxsb3ciLCJtYWluZV9zdXJ2ZXlzX3JlYWQiOiJteSIsIm1haW5lX2NvbXBhcmlzb25fcmVhZCI6Im15IiwiaGF3YWlpX2FjY2VzcyI6ImFsbG93Iiwib2tsYWhvbWFfYWNjZXNzIjoiYWxsb3ciLCJjb250ZW50b3d5Y3lwcmlhbl9hY2Nlc3MiOiJhbGxvdyIsInN6dWthamFjeXN6eW1vbl9hY2Nlc3MiOiJhbGxvdyIsInNhbmZyYW5jaXNjb19hY2Nlc3MiOiJhbGxvdyIsIm5pdHJ1amFjeW5lcG9tdWNlbl9hY2Nlc3MiOiJhbGxvdyIsInRleGFzX2FjY2VzcyI6ImFsbG93IiwidXNlckdyb3VwIjoiQ2FuZGlkYXRlcyIsInJlY29tbWVuZGF0aW9uX2FjY2VzcyI6ImFsbG93In0.X3L2fi1JPegqcPRiKQkqOzQzJpP8IAGZ2HAucrsmYyedTT6USNCLxLk0Nnl2QikmOtekO3pDtL8xz-cGIWLmQQ0TnVIvln_uJMNUV5X9pGLgKfUeD1x9wMadflProXEQJOKRV6s90SScdn-6WwIS8T03RpR8xF3r9IcUlbe59yHg0JmnaTg3fcYT9CRbjTTmO5REdQZ0NWT3bDEybRDNk7FGq22Ey6uATt4OMNLwpYZ4Iod3c0g2Pn7ck9H_JMWFbK1mzWP2_wlBuOWww_h2o_H76j0kpFMM7KcrFg1neAfRst17mw-np8mCI9dYkJ2APRwb6wJbcWH9EsqwDV2cbeRGAt8FAMVClipIaGgSmgklblfV_PBHKplxvtu_NnEz3j9m9IrVeZGI5lcQ3js2b925I22tCM9IzV3IupgZlMTJL5hq0YQ-HyXbb67Y3Sqm1dpK0DtvJzvmr4eT5DMhtFZHptVJoereSy3AjdYwk6OMVmFzOBl-Lv8S8hkpWd4elti1BXyUUDn9Zn1XdDf_Uj7NNIUWcgsdjlhFG6BP_ju90PSyGpXemBVmPh2oawqDcF6cSaFeXtFeKs-28V1GTBz21smlMoevnC57nh-vBPAiYLzY6uF9fnyxBagNkra6boMo9wanuF-FJqWXhqhoK-Tz2w98-RoMhK_zHmRqn9I; _gid=GA1.2.800044253.1739554231; __gfp_64b=0UC3qmczVRjS78rRVt7ef23jqxelq2FtjwpEJd8jaFL.P7|1732121151|2|||8:1:32; _clck=b27ccm%7C2%7Cftf%7C0%7C1785; __cf_bm=_uz5U_vS9fTj06.VxrENJpU.1haq9VTWMuZOV0MvEkE-1739558875-1.0.1.1-3nBZNcWaGk_fsfMUbevb0ymVDP8AvuVgDZgEzs5XHtrR_bhyi4z_bSokPm1B.hiBzjXA9Dfw6JjFX9eeJHWOyQ; gp_tr_gptrackPVID=95937c97-7bad-498a-a8dc-3ab9bff74240; gptrackPVID=e44f6df7-dab5-4a7d-y3ae-cf9fab908297; XSRF-TOKEN=CfDJ8BnsG4UujmlAhMc6W89smJbZfdIOYjFFRPpTkSMCFJs_t6zuPnY3cbKU6NN4u6RUFUmJeEqWbgTDLsIAaOEhrJ0BqxuJjATnMW0TX978AsaqDGHeKfV-riv1PjLluwOdiXxPCTUtOmmvvNWumuxB9YQ; _ga_GD4CKCV28E=GS1.1.1739558243.10.1.1739558879.0.0.0; _ga_DD6PPTKNH1=GS1.1.1739558243.43.1.1739558879.60.0.0; _ga_WDELMMFCBH=GS1.1.1739558243.43.1.1739558879.60.0.0; cf_clearance=7aOrtl7Liy27PV2lHtuEWwZhzciwY8ynD_LTNdUOYWI-1739558878-1.2.1.1-EOKnTdxywG7q46PLgSFmuAyCj4uOeSAOuWZLcBgB9D6NvGwGaiUzPhETW7ElKVSd_gFXEeK9KehzL9jU73PA_l_o1aJGOQ_I.6q9FahMirFVyqzTohO2PtnIuiPuvhA8U5jUMIfbOa4NT_O9KUurxtcvZdmcrbIeSYx2bsQ8E690OihK0_QKYer5lrozyfS.toA7ES6MM1LQBrmWyek54QTUSXHttQrQEX6nt5SnXIQCUVTE_yyDZUbB4ucg7ew2REUu68rdjZu8q3.u5.E5e0R5CoUc893z_LtXoeosZck; _ga=GA1.2.430510135.1732121151; __rtbh.uid=%7B%22eventType%22%3A%22uid%22%2C%22id%22%3A%2223446868%22%2C%22expiryDate%22%3A%222026-02-14T18%3A48%3A02.239Z%22%7D; __rtbh.lid=%7B%22eventType%22%3A%22lid%22%2C%22id%22%3A%22wS03jY4zTOE06cPIxYsX%22%2C%22expiryDate%22%3A%222026-02-14T18%3A48%3A02.240Z%22%7D; _uetsid=64827bf0eaf911ef85f9d11556d64204; _uetvid=e7bad5b0a75e11efae57936341321d2e; cto_bundle=RXEldF9PM2hLMXZJU2djU3Q0QnZxUXpBMmxnWW1kckRZekluWHNra2xjNUg5RjQwJTJGcjNtc0kzN2JoamxhJTJCYVAyeml6YVFQJTJGMHozck9pVUF4VGpWODh3TGFrZXF4Ym43S3JVNTU1SnJwR2Q3NHVqQ0YlMkZLTjJna0h1eTVMUkdxbDhxR3ZFJTJGVWUwYlBPUzVMV01sZjE0TyUyRjNDSnclM0QlM0Q; cto_bundle=RXEldF9PM2hLMXZJU2djU3Q0QnZxUXpBMmxnWW1kckRZekluWHNra2xjNUg5RjQwJTJGcjNtc0kzN2JoamxhJTJCYVAyeml6YVFQJTJGMHozck9pVUF4VGpWODh3TGFrZXF4Ym43S3JVNTU1SnJwR2Q3NHVqQ0YlMkZLTjJna0h1eTVMUkdxbDhxR3ZFJTJGVWUwYlBPUzVMV01sZjE0TyUyRjNDSnclM0QlM0Q; _clsk=b43ifl%7C1739560220848%7C2%7C0%7Cx.clarity.ms%2Fcollect',
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

response = requests.get('https://www.pracuj.pl/praca/warszawa;kw', cookies=cookies, headers=headers)
response.text

def parse_html_and_visualize(html_file = None, html_content = None):
    output_str = ""

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
    # def print_structure(obj, indent=0):
    #     if isinstance(obj, dict):
    #         for key, value in obj.items():
    #             print('  ' * indent, f"{key}:")
    #             print_structure(value, indent+1)
    #     elif isinstance(obj, list):
    #         for i, item in enumerate(obj):
    #             print('  ' * indent, f"[{i}]:")
    #             print_structure(item, indent+1)
    #     else:
    #         print('  ' * indent, f"{obj}")
    
    def print_structure(obj, indent=0, output_string=""): # Добавлен параметр output_string
        if isinstance(obj, dict):
            for key, value in obj.items():
                output_string += '  ' * indent + f"{key}:\n" # Добавляем в строку, а не печатаем
                output_string = print_structure(value, indent+1, output_string) # Рекурсивный вызов и обновление строки
        elif isinstance(obj, list):
            for i, item in enumerate(obj):
                output_string += '  ' * indent + f"[{i}]:\n" # Добавляем в строку, а не печатаем
                output_string = print_structure(item, indent+1, output_string) # Рекурсивный вызов и обновление строки
        else:
            output_string += '  ' * indent + f"{obj}\n" # Добавляем в строку, а не печатаем
        return output_string # Возвращаем накопленную строку
    
    # Визуализация структуры (рекурсивная функция)
    structure_string = print_structure(data) # Получаем строку структуры
    # Сохранение структуры в файл
    with open("structure-of-markup.json", 'w', encoding='utf-8') as file: # Открываем файл для записи
        file.write(structure_string) # Записываем строку в файл

    #print_structure(data)
    
    # Пример использования jsonpath
    # jsonpath_expr = parse("$.props.data.items[0].name")  # Создаем объект парсера и компилируем выражение
    # jsonpath_expr = parser.parse("$.props.data.items[0].name")

    # Пример использования jsonpath
    jsonpath_expr = parser.parse("$.props.data.items[0].name")  # Используем parser.parse
    match = jsonpath_expr.find(data)
    if match and len(match) > 0: # Улучшенная проверка наличия результатов
        print(match[0].value)
    else:
        print("Path not found in JSON data.")

    #match = jsonpath_expr.find(data)  # Используем скомпилированное выражение для поиска
    #print(match[0].value)

# Замените 'your_html_file.html' на путь к вашему HTML файлу
parse_html_and_visualize(html_content = response.text)
























s = """ import settings

def parse_building_from_url_fc(needpart_str):
        #menedzer-ds-merchandisingu-i-sprzedazy-odziez-sportowa-i-akcesoria-warszawa-konwiktorska-6
        r = ""
        l = list(needpart_str)
        startofnumberfound = False
        lastindex = len(l) - 1
        for i in range(len(l) - 1, -1, -1):#startindex, finishindex, step

            if l[i] == '-':
                r += " "
                lastindex = i
                continue

            if l[i].lower() not in settings.ALPHABET_POLISH_str:
                r += l[i]
                lastindex = i
                continue

            if not startofnumberfound:
                if l[i] in settings.MATHNUMBERS_str:
                    startofnumberfound = True
                r += l[i]
                lastindex = i
                continue
            else:
                if l[i] not in settings.MATHNUMBERS_str:
                    break
                lastindex = i
                r += l[i]
        
        restofstring = needpart_str[:lastindex]
        if r:
             r = r.strip()
             r = r[::-1]
        
        return r, restofstring

def parse_lastword_from_url_fc(restofurl_str):
    #take one last word instead
    r = ""
    lastindex = len(restofurl_str) - 1
    startofstringfound = False
    for i in range(len(restofurl_str) - 1, -1, -1):
        if startofstringfound:
            if restofurl_str[i] == "-":
                break
            else:
                r += restofurl_str[i]
                lastindex = i
        else:
            if restofurl_str[i] == "-":
                r += " "
            else:
                r += restofurl_str[i]
            lastindex = i
            startofstringfound = True
    
    restofurl_str = restofurl_str[:lastindex]
    if r:
        r = r.strip()
        r = r[::-1]

    return r, restofurl_str

r, restofstring = parse_building_from_url_fc("menedzer-ds-merchandisingu-i-sprzedazy-odziez-sportowa-i-akcesoria-warszawa-konwiktorska-667")
print(r)
print(restofstring)


r, restofstring = parse_lastword_from_url_fc(restofstring)
print(r)
print(restofstring)
r, restofstring = parse_lastword_from_url_fc(restofstring)
print(r)
print(restofstring)
r, restofstring = parse_lastword_from_url_fc(restofstring)
print(r)
print(restofstring)
r, restofstring = parse_lastword_from_url_fc(restofstring)
print(r)
print(restofstring) """