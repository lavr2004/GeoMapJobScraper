import logging

import bin.logic.parser
import bin.logic.web
import bin.logic.filesystem
import bin.logic.nominatim
import bin.settings as settings

from bin.parsers.baseparser import BaseParser
from bin.parsers.pracujpl.pracujpl_parser import parse_address_in_warsaw_from_url_fc
from bin.parsers.pracujpl.pracujpl_database import Database_pracujpl

import random
import time

# URL_START_str = 'https://www.pracuj.pl/praca/warszawa;wp?rd=30&sc=0&pn=1' - 1st page
# URL_START_str = 'https://www.pracuj.pl/praca/warszawa;wp?rd=30&sc=0&pn=2' - 2nd page

"""
cookies = {
    'gp__cfXfiDZP': '26',
    '__cf_bm': 'yPRVnI5gB7sSVCAojje2PEEdsus8oS0tL08yjCc6JMI-1742652380-1.0.1.1-da5ZrkXV.rukcNER7K92UsmojLNL1UZ7R4fpC8gHsYWj7_hZaf1ZF8ZZDlx2sWpA28uIJSV4yMBeJ3Xos2728hqa2Bz1lGCvz2pQqq0HFHA',
    '__cfruid': 'e555d584e42f97443c0cac8874bd9bc1262c7793-1742652380',
    '_cfuvid': 'bU_6HROCUQz7NYocA4t57cpUwAW7xIYOy2zKyMnbcfk-1742652380088-0.0.1.1-604800000',
    'gp_tr_gptrackCookie': '4a92b28c-8e26-4346-8e0a-40708c8775c7',
    'gp_lang': 'pl',
    '_gpantiforgery': 'CfDJ8BnsG4UujmlAhMc6W89smJb3KSAOkweGLy8VZdBRIbE6WVe3EzCMk29JWyJyPi0IkcvJN3ZfdY9tE733E4GSbSYSsHYidjuzZx57Kwzq0tVRsFRvQNenI6bybeIDKGctdd5biSsAUl40jf64Ho_jOaY',
    'gp_tr_gptrackPVID': '913e0e3f-2a7f-44bf-9eee-29bf134c1029',
    'gptrackCookie': '5b44a81b-d742-4172-y422-29ef47e6ba35',
    'cf_clearance': 'tcIHPu3SB6RwSL18JkXz.TxrFBdAPwKm8JaonlPhcFY-1742652500-1.2.1.1-blMBLODQVETO8SAy7nARVEb8e878jSC8skHkvqJ95eqITUpWQNRcAFjfXyXJjQVslnydxoJlYHGX0Xgtsb20iMeJvEJG2hFLhbRTwyvdGMK1I6sCYL8IIBWYhIg1GLVFuikypL2OelzjyTVJZ0dp7o_Yf8Gg_6pHm01FIZt.bFSbcv8Rf7f2FpFKUg7GxCghckOOxNcfZSWzRBOy0CYxa.QaWzPJ0NxT.mtZ08WDxFwjz2WWWIuC9rpAc2pV0O0WW_Dm0EEtYE7wJO2eAclrnQG2yFqVuFC2mu32fByOFyGWAImytw8xm8C5a2.ku_xwxb6tMcxAM7GOZBg8xB49D8SAclbmlrBQd4OhpF328YE',
    'XSRF-TOKEN': 'CfDJ8BnsG4UujmlAhMc6W89smJZ-Bp_PoGORPYyN86JkbB-zsH2J0WuRB2hOFKiNGwDWXgT-FldNlQMdO3tc5X4Y8-t3bW_GwQlHqxAsZ_ZdxNsTpJzC4FvXnBUUwk-40Uy_z9fnFMuyJ8UQFUnoJsA_igY',
    'gptrackPVID': '75bfb6de-0aa2-4d83-y86a-386b36d45221',
    'gpc_v': '1',
    'gpc_analytic': '1',
    'gpc_func': '1',
    'gpc_ad': '1',
    'gpc_audience': '1',
    'gpc_social': '1',
    '_gcl_au': '1.1.776758616.1742652569',
    '_ga': 'GA1.2.962952641.1742652502',
    '_gid': 'GA1.2.1751474166.1742652569',
    '_ga_GD4CKCV28E': 'GS1.1.1742652501.1.0.1742652569.0.0.0',
    '_ga_DD6PPTKNH1': 'GS1.1.1742652501.1.0.1742652569.60.0.0',
    '_ga_WDELMMFCBH': 'GS1.1.1742652501.1.0.1742652569.60.0.0',
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
    # 'cookie': 'gp__cfXfiDZP=26; __cf_bm=yPRVnI5gB7sSVCAojje2PEEdsus8oS0tL08yjCc6JMI-1742652380-1.0.1.1-da5ZrkXV.rukcNER7K92UsmojLNL1UZ7R4fpC8gHsYWj7_hZaf1ZF8ZZDlx2sWpA28uIJSV4yMBeJ3Xos2728hqa2Bz1lGCvz2pQqq0HFHA; __cfruid=e555d584e42f97443c0cac8874bd9bc1262c7793-1742652380; _cfuvid=bU_6HROCUQz7NYocA4t57cpUwAW7xIYOy2zKyMnbcfk-1742652380088-0.0.1.1-604800000; gp_tr_gptrackCookie=4a92b28c-8e26-4346-8e0a-40708c8775c7; gp_lang=pl; _gpantiforgery=CfDJ8BnsG4UujmlAhMc6W89smJb3KSAOkweGLy8VZdBRIbE6WVe3EzCMk29JWyJyPi0IkcvJN3ZfdY9tE733E4GSbSYSsHYidjuzZx57Kwzq0tVRsFRvQNenI6bybeIDKGctdd5biSsAUl40jf64Ho_jOaY; gp_tr_gptrackPVID=913e0e3f-2a7f-44bf-9eee-29bf134c1029; gptrackCookie=5b44a81b-d742-4172-y422-29ef47e6ba35; cf_clearance=tcIHPu3SB6RwSL18JkXz.TxrFBdAPwKm8JaonlPhcFY-1742652500-1.2.1.1-blMBLODQVETO8SAy7nARVEb8e878jSC8skHkvqJ95eqITUpWQNRcAFjfXyXJjQVslnydxoJlYHGX0Xgtsb20iMeJvEJG2hFLhbRTwyvdGMK1I6sCYL8IIBWYhIg1GLVFuikypL2OelzjyTVJZ0dp7o_Yf8Gg_6pHm01FIZt.bFSbcv8Rf7f2FpFKUg7GxCghckOOxNcfZSWzRBOy0CYxa.QaWzPJ0NxT.mtZ08WDxFwjz2WWWIuC9rpAc2pV0O0WW_Dm0EEtYE7wJO2eAclrnQG2yFqVuFC2mu32fByOFyGWAImytw8xm8C5a2.ku_xwxb6tMcxAM7GOZBg8xB49D8SAclbmlrBQd4OhpF328YE; XSRF-TOKEN=CfDJ8BnsG4UujmlAhMc6W89smJZ-Bp_PoGORPYyN86JkbB-zsH2J0WuRB2hOFKiNGwDWXgT-FldNlQMdO3tc5X4Y8-t3bW_GwQlHqxAsZ_ZdxNsTpJzC4FvXnBUUwk-40Uy_z9fnFMuyJ8UQFUnoJsA_igY; gptrackPVID=75bfb6de-0aa2-4d83-y86a-386b36d45221; gpc_v=1; gpc_analytic=1; gpc_func=1; gpc_ad=1; gpc_audience=1; gpc_social=1; _gcl_au=1.1.776758616.1742652569; _ga=GA1.2.962952641.1742652502; _gid=GA1.2.1751474166.1742652569; _ga_GD4CKCV28E=GS1.1.1742652501.1.0.1742652569.0.0.0; _ga_DD6PPTKNH1=GS1.1.1742652501.1.0.1742652569.60.0.0; _ga_WDELMMFCBH=GS1.1.1742652501.1.0.1742652569.60.0.0',
}

params = {
    'rd': '30',
    'sc': '0',
    'pn': '3',
}

response = requests.get('https://www.pracuj.pl/praca/warszawa;wp', params=params, cookies=cookies, headers=headers)
"""


class PracujPLAllWarszawaParser(BaseParser):
    def __init__(self, mylogger: logging.Logger):
        super().__init__(platformname_str="pracujpl_all", url_start_str='https://www.pracuj.pl/praca/warszawa;wp', logger_obj=mylogger)
        self.oDatabase = Database_pracujpl(self.database_filepath_str)

    def _fetch_html(self, pagenumber_int=1):

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
            # 'cookie': 'gp__cfXfiDZP=26; __cf_bm=yPRVnI5gB7sSVCAojje2PEEdsus8oS0tL08yjCc6JMI-1742652380-1.0.1.1-da5ZrkXV.rukcNER7K92UsmojLNL1UZ7R4fpC8gHsYWj7_hZaf1ZF8ZZDlx2sWpA28uIJSV4yMBeJ3Xos2728hqa2Bz1lGCvz2pQqq0HFHA; __cfruid=e555d584e42f97443c0cac8874bd9bc1262c7793-1742652380; _cfuvid=bU_6HROCUQz7NYocA4t57cpUwAW7xIYOy2zKyMnbcfk-1742652380088-0.0.1.1-604800000; gp_tr_gptrackCookie=4a92b28c-8e26-4346-8e0a-40708c8775c7; gp_lang=pl; _gpantiforgery=CfDJ8BnsG4UujmlAhMc6W89smJb3KSAOkweGLy8VZdBRIbE6WVe3EzCMk29JWyJyPi0IkcvJN3ZfdY9tE733E4GSbSYSsHYidjuzZx57Kwzq0tVRsFRvQNenI6bybeIDKGctdd5biSsAUl40jf64Ho_jOaY; gp_tr_gptrackPVID=913e0e3f-2a7f-44bf-9eee-29bf134c1029; gptrackCookie=5b44a81b-d742-4172-y422-29ef47e6ba35; cf_clearance=tcIHPu3SB6RwSL18JkXz.TxrFBdAPwKm8JaonlPhcFY-1742652500-1.2.1.1-blMBLODQVETO8SAy7nARVEb8e878jSC8skHkvqJ95eqITUpWQNRcAFjfXyXJjQVslnydxoJlYHGX0Xgtsb20iMeJvEJG2hFLhbRTwyvdGMK1I6sCYL8IIBWYhIg1GLVFuikypL2OelzjyTVJZ0dp7o_Yf8Gg_6pHm01FIZt.bFSbcv8Rf7f2FpFKUg7GxCghckOOxNcfZSWzRBOy0CYxa.QaWzPJ0NxT.mtZ08WDxFwjz2WWWIuC9rpAc2pV0O0WW_Dm0EEtYE7wJO2eAclrnQG2yFqVuFC2mu32fByOFyGWAImytw8xm8C5a2.ku_xwxb6tMcxAM7GOZBg8xB49D8SAclbmlrBQd4OhpF328YE; XSRF-TOKEN=CfDJ8BnsG4UujmlAhMc6W89smJZ-Bp_PoGORPYyN86JkbB-zsH2J0WuRB2hOFKiNGwDWXgT-FldNlQMdO3tc5X4Y8-t3bW_GwQlHqxAsZ_ZdxNsTpJzC4FvXnBUUwk-40Uy_z9fnFMuyJ8UQFUnoJsA_igY; gptrackPVID=75bfb6de-0aa2-4d83-y86a-386b36d45221; gpc_v=1; gpc_analytic=1; gpc_func=1; gpc_ad=1; gpc_audience=1; gpc_social=1; _gcl_au=1.1.776758616.1742652569; _ga=GA1.2.962952641.1742652502; _gid=GA1.2.1751474166.1742652569; _ga_GD4CKCV28E=GS1.1.1742652501.1.0.1742652569.0.0.0; _ga_DD6PPTKNH1=GS1.1.1742652501.1.0.1742652569.60.0.0; _ga_WDELMMFCBH=GS1.1.1742652501.1.0.1742652569.60.0.0',
        }

        cookies = {
            'gp__cfXfiDZP': '26',
            '__cf_bm': 'yPRVnI5gB7sSVCAojje2PEEdsus8oS0tL08yjCc6JMI-1742652380-1.0.1.1-da5ZrkXV.rukcNER7K92UsmojLNL1UZ7R4fpC8gHsYWj7_hZaf1ZF8ZZDlx2sWpA28uIJSV4yMBeJ3Xos2728hqa2Bz1lGCvz2pQqq0HFHA',
            '__cfruid': 'e555d584e42f97443c0cac8874bd9bc1262c7793-1742652380',
            '_cfuvid': 'bU_6HROCUQz7NYocA4t57cpUwAW7xIYOy2zKyMnbcfk-1742652380088-0.0.1.1-604800000',
            'gp_tr_gptrackCookie': '4a92b28c-8e26-4346-8e0a-40708c8775c7',
            'gp_lang': 'pl',
            '_gpantiforgery': 'CfDJ8BnsG4UujmlAhMc6W89smJb3KSAOkweGLy8VZdBRIbE6WVe3EzCMk29JWyJyPi0IkcvJN3ZfdY9tE733E4GSbSYSsHYidjuzZx57Kwzq0tVRsFRvQNenI6bybeIDKGctdd5biSsAUl40jf64Ho_jOaY',
            'gp_tr_gptrackPVID': '913e0e3f-2a7f-44bf-9eee-29bf134c1029',
            'gptrackCookie': '5b44a81b-d742-4172-y422-29ef47e6ba35',
            'cf_clearance': 'tcIHPu3SB6RwSL18JkXz.TxrFBdAPwKm8JaonlPhcFY-1742652500-1.2.1.1-blMBLODQVETO8SAy7nARVEb8e878jSC8skHkvqJ95eqITUpWQNRcAFjfXyXJjQVslnydxoJlYHGX0Xgtsb20iMeJvEJG2hFLhbRTwyvdGMK1I6sCYL8IIBWYhIg1GLVFuikypL2OelzjyTVJZ0dp7o_Yf8Gg_6pHm01FIZt.bFSbcv8Rf7f2FpFKUg7GxCghckOOxNcfZSWzRBOy0CYxa.QaWzPJ0NxT.mtZ08WDxFwjz2WWWIuC9rpAc2pV0O0WW_Dm0EEtYE7wJO2eAclrnQG2yFqVuFC2mu32fByOFyGWAImytw8xm8C5a2.ku_xwxb6tMcxAM7GOZBg8xB49D8SAclbmlrBQd4OhpF328YE',
            'XSRF-TOKEN': 'CfDJ8BnsG4UujmlAhMc6W89smJZ-Bp_PoGORPYyN86JkbB-zsH2J0WuRB2hOFKiNGwDWXgT-FldNlQMdO3tc5X4Y8-t3bW_GwQlHqxAsZ_ZdxNsTpJzC4FvXnBUUwk-40Uy_z9fnFMuyJ8UQFUnoJsA_igY',
            'gptrackPVID': '75bfb6de-0aa2-4d83-y86a-386b36d45221',
            'gpc_v': '1',
            'gpc_analytic': '1',
            'gpc_func': '1',
            'gpc_ad': '1',
            'gpc_audience': '1',
            'gpc_social': '1',
            '_gcl_au': '1.1.776758616.1742652569',
            '_ga': 'GA1.2.962952641.1742652502',
            '_gid': 'GA1.2.1751474166.1742652569',
            '_ga_GD4CKCV28E': 'GS1.1.1742652501.1.0.1742652569.0.0.0',
            '_ga_DD6PPTKNH1': 'GS1.1.1742652501.1.0.1742652569.60.0.0',
            '_ga_WDELMMFCBH': 'GS1.1.1742652501.1.0.1742652569.60.0.0',
        }

        # if not pagenumber_int:
        #     params = {
        #         'rd': '30',
        #         'sc': '0',
        #         'pn': '1',
        #     }
        #
        #     return bin.logic.web.get_html_response_from_url(self.URL_START_STR, headers_dc=headers)

        params = {
            'rd': '30',
            'sc': '0',
            'pn': f'{pagenumber_int}',
        }
        # params.update({"sc": sortoptions}) if sortoptions else None
        # params.update({"rd": radiuskm}) if radiuskm else None
        pause_seconds_int = random.randint(3, 7)
        self.logger_obj.info(f"OK: Technical pause between requests to pracuj.pl - {pause_seconds_int} seconds")
        time.sleep(pause_seconds_int)
        return bin.logic.web.get_html_response_from_url(self.URL_START_STR, headers_dc=headers, params_dc=params, cookies_dc=cookies)

    def parse(self, start_pagenumber_int=1) -> None:

        max_page_count = 10
        j = 0
        jobs_collected_count = 0
        for i in range(start_pagenumber_int, max_page_count + 1):
            j = i
            html_content, response_status_code = self._fetch_html(pagenumber_int=i)

            json_data = bin.parsers.pracujpl.pracujpl_parser.recognition_JSON_in_HTML_area_fc(html_content)
            jobs_dc = bin.logic.parser.recursive_json_search_fc(json_data, "groupedOffers")
            if not jobs_dc:
                self.logger_obj.error(f"ER - not parsed jobs from page: {i}. Breaking requests to pracuj.pl Warszawa")
                break

            parsed_jobs_count = len(jobs_dc)
            jobs_collected_count += parsed_jobs_count
            j = i
            self.logger_obj.info(f"OK - parsed {parsed_jobs_count} jobs from page {i}")

            # Save JSON copy
            self.update_results_filepath_fc(pagenumber_int=i)
            bin.logic.filesystem.save_jobs_copy_into_json_file_fc(self.results_filepath_str, jobs_dc)
            #jobs_to_save_int_json_dc.update(jobs_dc)

            # Save to database
            self.oDatabase.step01_save_parseiteration_fc(self.results_filename_str, self.current_timestamp_str, len(jobs_dc), response_status_code, self.URL_START_STR)
            self.oDatabase.step02_save_joboffers_fc(jobs_dc, parse_address_in_warsaw_from_url_fc)

            if i:
                self.logger_obj.info(f"OK: {response_status_code}: Data from page {i} successfully saved in database {self.database_filepath_str}")
            else:
                self.logger_obj.info(f"OK: {response_status_code}: Data successfully saved in database {self.database_filepath_str}")

        self.logger_obj.info(f"OK: Collected jobs count - {jobs_collected_count}. Parsing from {self.URL_START_STR} finished on page {j}")

    def update_coordinates(self) -> None:
        jobs = self.oDatabase.step03_get_lastaddedvacancies_from_database_fc()

        for job in jobs:
            job_id, job_locality, job_street, job_building, display_workplace = job

            address = ", ".join(filter(None, [job_locality, job_street, job_building])) if job_street else display_workplace

            if address:
                latitude, longitude = bin.logic.nominatim.get_coordinates_latlon_fc(address, settings.NOMINATIM_URL)
                self.oDatabase.step04_update_geocoordinatest_fc(latitude, longitude, job_id)

                if latitude and longitude:
                    self.logger_obj.info(f"Coordinates for job ID {job_id} updated: {latitude}, {longitude}")
                else:
                    self.logger_obj.warning(f"Failed to get coordinates for job ID {job_id} (address: {address})")
            else:
                self.logger_obj.warning(f"No address for job ID {job_id}")

        self.logger_obj.info("OK - getting coordinates process finished")

    def commit_changes(self):
        self.oDatabase.step05_commit_things()


if __name__ == "__main__":
    parser = PracujPLAllWarszawaParser()

    # Parsing multiple pages
    for page in range(0, 6):
        parser.parse(page)

    # Update job vacancies with coordinates
    parser.update_coordinates()

    # Commit changes to the database
    parser.commit_changes()





#
# import bin.logic.parser
# import bin.logic.web
# import bin.logic.filesystem
# import bin.logic.nominatim
# import bin.settings as settings
#
# from bin.parsers.pracujpl.pracujpl_parser import parse_address_in_warsaw_from_url_fc
# from bin.parsers.pracujpl.pracujpl_database import Database_pracujpl
#
# import time
# import random
#
#
# class Pracujpl:
#     PLATFORMNAME_STR = "pracujpl"
#     URL_START_STR = 'https://www.pracuj.pl/praca/warszawa;kw'
#
#     def __init__(self):
#         self.database_filepath = settings.get_databasefilepath_fc(self.PLATFORMNAME_STR)
#         self.oDatabasePracujpl = Database_pracujpl(self.database_filepath)
#         self.results_filepath = settings.get_dailyresultsfilepath_fc(self.PLATFORMNAME_STR)
#         self.results_filename = settings.get_filenamefrompath(self.results_filepath)
#         self.current_timestamp = settings.get_timestamp()
#
#     def _fetch_html(self, pagenumber_int=None):
#         if not pagenumber_int:
#             headers = {
#                 'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
#                 'accept-language': 'en-US,en;q=0.9,ru-BY;q=0.8,ru-RU;q=0.7,ru;q=0.6',
#                 # 'cookie': 'gp__cfXfiDZP=43; __cfruid=34c5ac7f7068c5a18c2c1720033cdc8bb818b495-1732121145; gptrackCookie=99bb3647-5c3f-4a50-y6ae-6a50428adf91; gp_lang=pl; gpc_v=1; gpc_analytic=1; gpc_func=1; gpc_ad=1; gpc_audience=1; gpc_social=1; _gcl_au=1.1.1526634893.1732121151; x-auth-csrf-token=ae26d655736547e565e84eaf999be25c9b15bcb67db4e952907477b878b2e75e; _gpauthclient=pracuj.pl_external; gpSearchType=Default; _gpauthrt=ZLZJuxlIZRD%2BuXoKIMOLbJLUMS%2FhVKP%2FqZoeyG6ET%2BeHWeiC%2F7DyTVx88xz7lQu1unplwre9Ectjchwac%2F9xLrsyWHs5UCPJnjYdBzVXEexeGybgJKtOQHSy7IbOuTdfMsIx4F7Be%2FFGAuXDEr%2Fy1Q%3D%3D; gp_ab__tech__227=A; _cfuvid=C7btfQNsTWLGZZyIvqjvf8Rm1D5LQTVxwlBHPUNG4jw-1737523183907-0.0.1.1-604800000; gp_tr_gptrackCookie=c1b88749-2665-4ad1-b82b-8e98c9e6b785; _gpantiforgery=CfDJ8BnsG4UujmlAhMc6W89smJZKuLovf73H9nLwDFytKfwJy4jZkis6Uh-OPSZRqxiz2pMtGEePLenbtqR5wumc-44uCpQIEn_qdtYbIE8jYKxwr-avzzJazkjMtCFBrzAjTaUul_Evdm7osgHFwb7Yz0s; _gpauth=eyJhbGciOiJSUzI1NiIsImtpZCI6IjI0QkVFNDg5MTIwRTE1ODdBMEYyOEE1ODYwRTY4QkM2OTQwODkxNDAiLCJ4NXQiOiJKTDdraVJJT0ZZZWc4b3BZWU9hTHhwUUlrVUEiLCJ0eXAiOiJKV1QifQ.eyJpc3MiOiJodHRwczovL2F1dGgucHJhY3VqLnBsIiwibmJmIjoxNzM3NjM3NzA1LCJpYXQiOjE3Mzc2Mzc3MDUsImV4cCI6MTczNzcyNDcwNSwiYXVkIjpbInByYWN1ai5wbCIsImh0dHBzOi8vYXV0aC5wcmFjdWoucGwvcmVzb3VyY2VzIl0sInNjb3BlIjpbInByYWN1ai5wbCIsIm9mZmxpbmVfYWNjZXNzIl0sImFtciI6WyJleHRlcm5hbCJdLCJjbGllbnRfaWQiOiJwcmFjdWoucGxfZXh0ZXJuYWwiLCJmaWxlc3RvcmVfYWNjZXNzIjoiYWxsb3ciLCJhcHBsaWNhdGlvbnNfYWNjZXNzIjoiYWxsb3ciLCJmaWxlX293bmVyIjoidHJ1ZSIsInVzZXJfYWdyZWVtZW50c19hY2Nlc3MiOiJhbGxvdyIsInNhdmVkX29mZmVyc19hY2Nlc3MiOiJhbGxvdyIsImpvYm9mZmVyc19hY2Nlc3MiOiJhbGxvdyIsImNyZWF0ZV9hY2NvdW50IjoiYWxsb3ciLCJnZXRfYWNjb3VudCI6ImFsbG93IiwiYWdyZWVtZW50X3Jldm9rZSI6ImFsbG93IiwibmVicmFza2FfYWNjZXNzIjoiYWxsb3ciLCJhcHBsaWNhdGlvbnNmb3JtX2FjY2VzcyI6ImFsbG93Iiwic2tpZGJsYW5kaXJfYWNjZXNzIjoiYWxsb3ciLCJjb25maXJtX25ld19lbWFpbCI6ImFsbG93IiwidHJhY2tpbmdfYWNjZXNzIjoiYWxsb3ciLCJha2lyYV9hY2Nlc3MiOiJhbGxvdyIsInBlcnNvbmFsaXp1amFjeXBhdHJ5a19hY2Nlc3MiOiJhbGxvdyIsInN1YiI6Im1vanByYWN1ajoyMzQ0Njg2OCIsImF1dGhfdGltZSI6MTczMjEyMTE2NSwiaWRwIjoiZ3J1cGFwcmFjdWoiLCJlbWFpbCI6ImxhdnIyMDA0QGdtYWlsLmNvbSIsIklzQ29uZmlybWVkIjoiVHJ1ZSIsImVtYWlsX3ZlcmlmaWVkIjoiVHJ1ZSIsImdpdmVuX25hbWUiOiJBbmRyZWkiLCJmYW1pbHlfbmFtZSI6IklobmF0b3ZpY3oiLCJDaXR5IjoiV2Fyc3phd2EiLCJFbXBsb3ltZW50TGV2ZWwiOiJzYW1vZHppZWxueSBzcGVjamFsaXN0YSIsInVzZXJmaWxlc19hY2Nlc3MiOiJhbGxvdyIsInJvbGUiOiJFeHRlcm5hbENsaWVudCIsInNpbHZlcnN0YXJfYWNjZXNzIjoiYWxsb3ciLCJoZWR3aWdhX2FjY2VzcyI6ImFsbG93IiwibWFpbmVfYWNjZXNzIjoiYWxsb3ciLCJtYWluZV9zdXJ2ZXlzX3dyaXRlIjoiYWxsb3ciLCJtYWluZV9zdXJ2ZXlzX3JlYWQiOiJteSIsIm1haW5lX2NvbXBhcmlzb25fcmVhZCI6Im15IiwiaGF3YWlpX2FjY2VzcyI6ImFsbG93Iiwib2tsYWhvbWFfYWNjZXNzIjoiYWxsb3ciLCJjb250ZW50b3d5Y3lwcmlhbl9hY2Nlc3MiOiJhbGxvdyIsInN6dWthamFjeXN6eW1vbl9hY2Nlc3MiOiJhbGxvdyIsInNhbmZyYW5jaXNjb19hY2Nlc3MiOiJhbGxvdyIsIm5pdHJ1amFjeW5lcG9tdWNlbl9hY2Nlc3MiOiJhbGxvdyIsInRleGFzX2FjY2VzcyI6ImFsbG93IiwidXNlckdyb3VwIjoiQ2FuZGlkYXRlcyIsInJlY29tbWVuZGF0aW9uX2FjY2VzcyI6ImFsbG93In0.V-WKFyV-FRb54lt7cskNQafc80R-yolQOJFD6OzQ0KsNgPZymkbobIYp6Ts8h1dOYOECmOAbpHPdI5Tcx-TbufJ1nPKU54ky_anpWHNy_P6MdemqKA4EeUovmHcMToPOtBc7sftE7zJqbHKRBIL3FdymtUaPkS4yNwcSk8G-LQQcCMjazaZ_yyxyodkbdsEuwqP8u-jyIStH41tXlkMRcxwoYE8GM6U3DVQPXNzDx6Wq4-xXyAUIQYqH8gQXQmeRwZb2w65OC4kxKtA748UeSTjRe4rZGBM8WM23f2vEHfNxxAyoycLKrnASok7KuGjKOTiSpNzHnNZOdQbXNTrDe5zptqOS8JRSh2SUE2wvE9KBvdbZlHOeyKmg7F8SeHxvUq_vbl5l6iOzpoTMkz36jHzgRJi9QmkNk9N_CHapUosrSqaQutQ53Xh5FHGUKVMJKZd8EaAeyI-BmlJMl_yWvWeyB9ILs5ifJrWmUjkNsywCU--ifUHKFHWNMLgtvVGdzxLqeBx-9mC4peY9lYTww9VRBCl2DoDE-t2SkJC58G_fD6TupHSQcw0_aOPprTakKlyBP1bRmKHzex7w_xIwzKp8SP_OS9_QyotP7xLRscrN1K5WVD9z-pFP9ZmMtnGOspAxbv1s6-N7m5nTwL4vfq0TLZj15qulYLDrIp3rOyA; __cf_bm=G9IzaHEIjw3YGSRPGAukweH0E2QZYLTz2UGapKYh9Mc-1737637706-1.0.1.1-qL9patuCBhGvgFxODRbkXFJd2yabaLLMRX5Pa3qYNVY4ADYveV8WfRS4V.UD.RSCoiBq.2pEkxaJFQ0sr.WNSQ; cf_clearance=p.EdYNtC9QXzYZoZdcs8GxgquhfbiLOaWqsGDYbYaZs-1737637708-1.2.1.1-imcTxWLEV5Eqb4STSAzGf6ykusdoAyU8WmJX1JjQp5S6sKn6FPo6J0_J.RcNCqm3gcXGo_WFbVGERM7771CUCNMQZbOb9Jn9ALc1Co9M7tEupsy9ePFPc.PanmFN8XDrqlzPLSzt3N7kunV3aNrKZ2Nq9f7XxDzlapCi7gMwXR3Pbyl1W7l.MDEyjweXqZDkfiqe1xHfd6bqzT5OF9njn1HAdj2szXpihr7G3iSqktpIX7dWXfHAtdS6q4RjBDTgWnsIAZCFPjA5yidD90rhLNvGZg587l874AofT0wvzYs; _gid=GA1.2.944345992.1737637710; __gfp_64b=JoMRE6QDzUfIZ.VhFWO00ReFGHNQG0SGzW7mvVJ1LwT.Y7|1732121151|2|||8:1:32; _clck=b27ccm%7C2%7Cfst%7C0%7C1785; gp_tr_gptrackPVID=c7943a68-f9e8-46eb-8d4e-db6f706862af; gptrackPVID=06993c8b-c261-43a0-y7c8-dca33cc17c6e; _ga_GD4CKCV28E=GS1.1.1737637709.6.1.1737637856.0.0.0; _ga_WDELMMFCBH=GS1.1.1737637709.7.1.1737637856.4.0.0; _ga_DD6PPTKNH1=GS1.1.1737637709.7.1.1737637856.4.0.0; _ga=GA1.2.430510135.1732121151; __rtbh.uid=%7B%22eventType%22%3A%22uid%22%2C%22id%22%3A%2223446868%22%2C%22expiryDate%22%3A%222026-01-23T13%3A10%3A57.799Z%22%7D; __rtbh.lid=%7B%22eventType%22%3A%22lid%22%2C%22id%22%3A%22wS03jY4zTOE06cPIxYsX%22%2C%22expiryDate%22%3A%222026-01-23T13%3A10%3A57.800Z%22%7D; _uetsid=24820510d98b11ef9d0cbf9e2df34c9f; _uetvid=e7bad5b0a75e11efae57936341321d2e; cto_bundle=YCf8rV9PM2hLMXZJU2djU3Q0QnZxUXpBMmxuT2NQZVhUWTNyMjg1eXZGaTZaN3JLJTJGMUNPNkE4MnB6MThzT3drZUJqWVJuVyUyQncyUWFRbG9VTVJMYzlDSHRqZmFUY29iYVNaNGZnOHJWVng4ZXppa2pUTUJIeFJGeGRmRjIzREFwWHR5U1p4QXBQZkJJQ0czUTV6Y1B4Z3pnaENnJTNEJTNE; XSRF-TOKEN=CfDJ8BnsG4UujmlAhMc6W89smJaPOUHFarirLTIWm0lGJFVMaz5fIzs2GdNpUnrqMTYFFr-mKuLCBsyJlvGZZvjeT6Dc4ZH6I4kKr4rwmP515BGNzFcFcXg1aqso51gMqIg3mlFusBMFGH3ox02J_bzqBQ0; _clsk=1fu0ix0%7C1737637859285%7C3%7C0%7Cl.clarity.ms%2Fcollect',
#                 'priority': 'u=0, i',
#                 'sec-ch-ua': '"Google Chrome";v="131", "Chromium";v="131", "Not_A Brand";v="24"',
#                 'sec-ch-ua-mobile': '?0',
#                 'sec-ch-ua-platform': '"Windows"',
#                 'sec-fetch-dest': 'document',
#                 'sec-fetch-mode': 'navigate',
#                 'sec-fetch-site': 'none',
#                 'sec-fetch-user': '?1',
#                 'upgrade-insecure-requests': '1',
#                 'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36',
#             }
#             return bin.logic.web.get_html_response_from_url(self.URL_START_STR, headers_dc=headers)
#
#         headers = {
#             'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
#             'accept-language': 'en-US,en;q=0.9,ru-BY;q=0.8,ru-RU;q=0.7,ru;q=0.6',
#             'priority': 'u=0, i',
#             'referer': 'https://www.pracuj.pl/praca/warszawa;kw',
#             'sec-ch-ua': '"Not(A:Brand";v="99", "Google Chrome";v="133", "Chromium";v="133"',
#             'sec-ch-ua-mobile': '?0',
#             'sec-ch-ua-platform': '"Windows"',
#             'sec-fetch-dest': 'document',
#             'sec-fetch-mode': 'navigate',
#             'sec-fetch-site': 'same-origin',
#             'sec-fetch-user': '?1',
#             'upgrade-insecure-requests': '1',
#             'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/133.0.0.0 Safari/537.36',
#             # 'cookie': 'gp__cfXfiDZP=43; gptrackCookie=99bb3647-5c3f-4a50-y6ae-6a50428adf91; gp_lang=pl; gpc_v=1; gpc_analytic=1; gpc_func=1; gpc_ad=1; gpc_audience=1; gpc_social=1; x-auth-csrf-token=ae26d655736547e565e84eaf999be25c9b15bcb67db4e952907477b878b2e75e; _gpauthclient=pracuj.pl_external; gpSearchType=Default; _gpauthrt=ZLZJuxlIZRD%2BuXoKIMOLbJLUMS%2FhVKP%2FqZoeyG6ET%2BeHWeiC%2F7DyTVx88xz7lQu1unplwre9Ectjchwac%2F9xLrsyWHs5UCPJnjYdBzVXEexeGybgJKtOQHSy7IbOuTdfMsIx4F7Be%2FFGAuXDEr%2Fy1Q%3D%3D; gp_tr_gptrackCookie=c1b88749-2665-4ad1-b82b-8e98c9e6b785; _gpantiforgery=CfDJ8BnsG4UujmlAhMc6W89smJZKuLovf73H9nLwDFytKfwJy4jZkis6Uh-OPSZRqxiz2pMtGEePLenbtqR5wumc-44uCpQIEn_qdtYbIE8jYKxwr-avzzJazkjMtCFBrzAjTaUul_Evdm7osgHFwb7Yz0s; _epantiforgery=CfDJ8HUifgaomuZGmjCc5nlQaanCCG7f6ToAIASOMWhelkl4NNACVgJVyfu8pDTdhTjYqb6afyjAPDY4JkQrTW1GkwKVPikAiutSgTCYRYep8Fn1sN-JTH_JNAXkU5AGBByj7Z25uyvDas1sx_TKAtk9wwI; Magpie-XSRF-Token=CfDJ8HUifgaomuZGmjCc5nlQaakGg3CzMCCqANlxOUGROTi3Sb9PKlalvEPqFJYdmgU3jlenEqfiBcJGAsGYRoOvzxUqU3C-VEEDMISRSZAyYdSZjvZl0wZTYrh2mYB_5bVM0t0FZ9G2jipZrYG6D0ko0j4; _ga_CJXS9Q5W6G=GS1.1.1737679478.2.0.1737679478.60.0.0; _ga_DD6PPTKNH1=deleted; x-account-csrf-token=9cbe863e1275f84c383733499d4fd4059d2db8e042c08cc3ed04d3dc64e902a8; gp_ab__notifications__230=B; gp_ab__HybridWebSearchV2__232=absent; __cfruid=bd2f483c899d681b49ce5c9fd685ef3430e5e26e-1740396977; _gcl_au=1.1.1729042314.1740396980; _gpauth=eyJhbGciOiJSUzI1NiIsImtpZCI6IjI0QkVFNDg5MTIwRTE1ODdBMEYyOEE1ODYwRTY4QkM2OTQwODkxNDAiLCJ4NXQiOiJKTDdraVJJT0ZZZWc4b3BZWU9hTHhwUUlrVUEiLCJ0eXAiOiJKV1QifQ.eyJpc3MiOiJodHRwczovL2F1dGgucHJhY3VqLnBsIiwibmJmIjoxNzQxMDUwNTc0LCJpYXQiOjE3NDEwNTA1NzQsImV4cCI6MTc0MTEzNzU3NCwiYXVkIjpbInByYWN1ai5wbCIsImh0dHBzOi8vYXV0aC5wcmFjdWoucGwvcmVzb3VyY2VzIl0sInNjb3BlIjpbInByYWN1ai5wbCIsIm9mZmxpbmVfYWNjZXNzIl0sImFtciI6WyJleHRlcm5hbCJdLCJjbGllbnRfaWQiOiJwcmFjdWoucGxfZXh0ZXJuYWwiLCJmaWxlc3RvcmVfYWNjZXNzIjoiYWxsb3ciLCJhcHBsaWNhdGlvbnNfYWNjZXNzIjoiYWxsb3ciLCJmaWxlX293bmVyIjoidHJ1ZSIsInVzZXJfYWdyZWVtZW50c19hY2Nlc3MiOiJhbGxvdyIsInNhdmVkX29mZmVyc19hY2Nlc3MiOiJhbGxvdyIsImpvYm9mZmVyc19hY2Nlc3MiOiJhbGxvdyIsImNyZWF0ZV9hY2NvdW50IjoiYWxsb3ciLCJnZXRfYWNjb3VudCI6ImFsbG93IiwiYWdyZWVtZW50X3Jldm9rZSI6ImFsbG93IiwibmVicmFza2FfYWNjZXNzIjoiYWxsb3ciLCJhcHBsaWNhdGlvbnNmb3JtX2FjY2VzcyI6ImFsbG93Iiwic2tpZGJsYW5kaXJfYWNjZXNzIjoiYWxsb3ciLCJjb25maXJtX25ld19lbWFpbCI6ImFsbG93IiwidHJhY2tpbmdfYWNjZXNzIjoiYWxsb3ciLCJha2lyYV9hY2Nlc3MiOiJhbGxvdyIsInBlcnNvbmFsaXp1amFjeXBhdHJ5a19hY2Nlc3MiOiJhbGxvdyIsInN1YiI6Im1vanByYWN1ajoyMzQ0Njg2OCIsImF1dGhfdGltZSI6MTczMjEyMTE2NSwiaWRwIjoiZ3J1cGFwcmFjdWoiLCJlbWFpbCI6ImxhdnIyMDA0QGdtYWlsLmNvbSIsIklzQ29uZmlybWVkIjoiVHJ1ZSIsImVtYWlsX3ZlcmlmaWVkIjoiVHJ1ZSIsImdpdmVuX25hbWUiOiJBbmRyZWkiLCJmYW1pbHlfbmFtZSI6IklobmF0b3ZpY3oiLCJDaXR5IjoiV2Fyc3phd2EiLCJFbXBsb3ltZW50TGV2ZWwiOiJzYW1vZHppZWxueSBzcGVjamFsaXN0YSIsInVzZXJmaWxlc19hY2Nlc3MiOiJhbGxvdyIsInJvbGUiOiJFeHRlcm5hbENsaWVudCIsInNpbHZlcnN0YXJfYWNjZXNzIjoiYWxsb3ciLCJoZWR3aWdhX2FjY2VzcyI6ImFsbG93IiwibWFpbmVfYWNjZXNzIjoiYWxsb3ciLCJtYWluZV9zdXJ2ZXlzX3dyaXRlIjoiYWxsb3ciLCJtYWluZV9zdXJ2ZXlzX3JlYWQiOiJteSIsIm1haW5lX2NvbXBhcmlzb25fcmVhZCI6Im15IiwiaGF3YWlpX2FjY2VzcyI6ImFsbG93Iiwib2tsYWhvbWFfYWNjZXNzIjoiYWxsb3ciLCJjb250ZW50b3d5Y3lwcmlhbl9hY2Nlc3MiOiJhbGxvdyIsInN6dWthamFjeXN6eW1vbl9hY2Nlc3MiOiJhbGxvdyIsInNhbmZyYW5jaXNjb19hY2Nlc3MiOiJhbGxvdyIsIm5pdHJ1amFjeW5lcG9tdWNlbl9hY2Nlc3MiOiJhbGxvdyIsInRleGFzX2FjY2VzcyI6ImFsbG93IiwiZ2VvZ2Vyd2F6eV9hY2Nlc3MiOiJhbGxvdyIsIndhc2hpbmd0b25fYWNjZXNzIjoiYWxsb3ciLCJ1c2VyR3JvdXAiOiJDYW5kaWRhdGVzIiwicmVjb21tZW5kYXRpb25fYWNjZXNzIjoiYWxsb3cifQ.n1BOs04Dw9jOj6S2ZeZc-gRPa0gqwYhOCTejHroEalSRAU8IlMaYk8CK-sDzjnuk7S1dXhaKQqqCjfRPkf4B01VGXENWti5CZ_XolAMwYJoB4h7OL0yX0SthamW9nlQxvx_lp9rQv7_LcxIQS7MNzRGo8oIuruZfNXG-6WjqxRrxPXDTjWwXieEUr8kW_QwiHcKDA3ME37mA1N8XV80BHzbCPxSZo7uWSWrSNFsT19M1ssje1CoV8fLotq9Or-QiSKacpJy31N1Cx6RcP5Abn4k6xfzd3hg2hEtgz1c_O_idq-EYKGritXzTeM-tYEKlOK9cMVTY-v4dcV_prtgnhueT5zaI2smN7EwhpLjW-6fgQLccP4d1vPCun2qA2lkDRY5l4MIm6q--kRc8i3RXHbd4pBZhJqTiVwzk4wNBBaYWhXxF7RdWRrz0g6OCFHtkfxacnyufdjbD4OxIwtHdkUVXrBmSUJswPXixOdcKDIkmZi6lMNxGfT4JR2FjsjlCySPJ8T5cIXz2FCfenznZ4QQ-5k-VYa6H34KDkYdHAV-UaVG4GJTf_Nreo9yIRN6XqXzqg0Oudg6q0xnTeyORxs8kbzQdfZhMrvx1toLxpVg-GjyXiyS4t3m_hQTQB-bwH4qZN8sKQ1xxSHVgluaXPH1G1-KK15b-gMrbPYOdccc; __cf_bm=.thNC6atKDV9R0oSwByfLuWR1ZllKYSk5JBD_sdjgLY-1741050574-1.0.1.1-FTB16Dij0CqXfT7N5GJPw9B09q42GFBQvJ7_Lwc_WeN1HhEeQPXOhQNCss_2TMG4CLPwLF7vjRY7jjrmD1xGsChXjCx2ileBu2zeSr7_oYI; _cfuvid=Bo15BBqfy8c4WvGnKdmrdtnSfEOrDKJNU3hMRL1oYLI-1741050574711-0.0.1.1-604800000; gp_tr_gptrackPVID=ad3470a8-6372-446a-b7bb-bebda8c2b5f0; gptrackPVID=4606e70e-2c28-455f-y5b2-3ca0d84791f8; cf_clearance=HWeIQ_Q_qz.FxYiemScYjAWAHXRa2zjQ7D2hrCcYsH4-1741050576-1.2.1.1-LSMS5fm_VD8j9K.5kP0PfgyjMXmajkrWJ6YD7KwW09QPuWKiwOBnqgAc7NT28ZWPIusSbrTFOgB2eGn9.dz1Dt.yj1kWO25CsQIUmYNONm46tHUAIiZV_0Bu.KSLImxARKw6UMaI.EXUZxo39vxrM8rsdEIdk9LnED9vuSfwlvEVoBkR30VOVZEg1vpL0VTQUHen2EY6CiooQE.wYubd5BUwUE9ySOFfCKgX2Fw8zlMHuBKFzYDHMq38Nr6fBrfsrCl2RIR8ZpEUit3ZiD8dVfdHONKlb4pCTClwfbT2LMOK.XW17qhggyaTRsGXP69MfLxdYr.ImfOGQ5A95RHaWokLXDqMKs2nyZWknwskKAD8FW4abtIci7X51GyuH4MwKthPGpOiraOhG6eXz2baxCRt_q8jOsxQinFaa0qizb4; _ga_WDELMMFCBH=GS1.1.1741050577.46.0.1741050577.60.0.0; _ga_DD6PPTKNH1=GS1.1.1741050577.46.0.1741050577.60.0.0; _ga_GD4CKCV28E=GS1.1.1741050577.12.0.1741050577.0.0.0; _ga=GA1.2.430510135.1732121151; _gid=GA1.2.2012319682.1741050578; XSRF-TOKEN=CfDJ8BnsG4UujmlAhMc6W89smJaYlxfkoEx0Qkeqpmz_R4qK6Msvqh1mGYH_j0fxO4XuAPYbXHycExhiIPU6yFt_oHCcBr3NpPOPvPKIqGnBbxldt-zbRPZt-hyMk3Yzw2PEZM3ETGMn7U4shvZ0FhGN9WE; _dc_gtm_UA-350045-57=1; _dc_gtm_UA-350045-7=1; _dc_gtm_UA-350045-80=1; _dc_gtm_UA-350045-59=1; __rtbh.uid=%7B%22eventType%22%3A%22uid%22%2C%22id%22%3A%2223446868%22%2C%22expiryDate%22%3A%222026-03-04T01%3A09%3A38.555Z%22%7D; __rtbh.lid=%7B%22eventType%22%3A%22lid%22%2C%22id%22%3A%22wS03jY4zTOE06cPIxYsX%22%2C%22expiryDate%22%3A%222026-03-04T01%3A09%3A38.557Z%22%7D; _uetsid=58578910f89511ef84a3c9f118f5785f; _uetvid=e7bad5b0a75e11efae57936341321d2e; __gfp_64b=vFsceqhKnYBMxDJ4gxd1WdIqNDVblEaehZc4B4S5dRj.w7|1732121151|2|||8:1:32; cto_bundle=nqKLVF9PM2hLMXZJU2djU3Q0QnZxUXpBMmxqSlJNYWs5ak1yVGpRMGdiOE9kOGhxSGlaZlZYbzhUZ3hIMTlrVmclMkZNbUJyTFVzWXhnalFpazZ4ZnJCbEN3Z1N3WmI0Q2UzTFBwY1doVkNYaWI3SXJiaGpmUWR2cjRBWXRxcEJvZlhqN3cyTEpHRmZjV3cyMDZKMGVDVFhQVUliZyUzRCUzRA; cto_bundle=nqKLVF9PM2hLMXZJU2djU3Q0QnZxUXpBMmxqSlJNYWs5ak1yVGpRMGdiOE9kOGhxSGlaZlZYbzhUZ3hIMTlrVmclMkZNbUJyTFVzWXhnalFpazZ4ZnJCbEN3Z1N3WmI0Q2UzTFBwY1doVkNYaWI3SXJiaGpmUWR2cjRBWXRxcEJvZlhqN3cyTEpHRmZjV3cyMDZKMGVDVFhQVUliZyUzRCUzRA; _clck=b27ccm%7C2%7Cftx%7C0%7C1785; _clsk=1k4uttu%7C1741050580033%7C1%7C0%7Cs.clarity.ms%2Fcollect',
#         }
#         cookies = {
#             'gp__cfXfiDZP': '43',
#             'gptrackCookie': '99bb3647-5c3f-4a50-y6ae-6a50428adf91',
#             'gp_lang': 'pl',
#             'gpc_v': '1',
#             'gpc_analytic': '1',
#             'gpc_func': '1',
#             'gpc_ad': '1',
#             'gpc_audience': '1',
#             'gpc_social': '1',
#             'x-auth-csrf-token': 'ae26d655736547e565e84eaf999be25c9b15bcb67db4e952907477b878b2e75e',
#             '_gpauthclient': 'pracuj.pl_external',
#             'gpSearchType': 'Default',
#             '_gpauthrt': 'ZLZJuxlIZRD%2BuXoKIMOLbJLUMS%2FhVKP%2FqZoeyG6ET%2BeHWeiC%2F7DyTVx88xz7lQu1unplwre9Ectjchwac%2F9xLrsyWHs5UCPJnjYdBzVXEexeGybgJKtOQHSy7IbOuTdfMsIx4F7Be%2FFGAuXDEr%2Fy1Q%3D%3D',
#             'gp_tr_gptrackCookie': 'c1b88749-2665-4ad1-b82b-8e98c9e6b785',
#             '_gpantiforgery': 'CfDJ8BnsG4UujmlAhMc6W89smJZKuLovf73H9nLwDFytKfwJy4jZkis6Uh-OPSZRqxiz2pMtGEePLenbtqR5wumc-44uCpQIEn_qdtYbIE8jYKxwr-avzzJazkjMtCFBrzAjTaUul_Evdm7osgHFwb7Yz0s',
#             '_epantiforgery': 'CfDJ8HUifgaomuZGmjCc5nlQaanCCG7f6ToAIASOMWhelkl4NNACVgJVyfu8pDTdhTjYqb6afyjAPDY4JkQrTW1GkwKVPikAiutSgTCYRYep8Fn1sN-JTH_JNAXkU5AGBByj7Z25uyvDas1sx_TKAtk9wwI',
#             'Magpie-XSRF-Token': 'CfDJ8HUifgaomuZGmjCc5nlQaakGg3CzMCCqANlxOUGROTi3Sb9PKlalvEPqFJYdmgU3jlenEqfiBcJGAsGYRoOvzxUqU3C-VEEDMISRSZAyYdSZjvZl0wZTYrh2mYB_5bVM0t0FZ9G2jipZrYG6D0ko0j4',
#             '_ga_CJXS9Q5W6G': 'GS1.1.1737679478.2.0.1737679478.60.0.0',
#             '_ga_DD6PPTKNH1': 'deleted',
#             'x-account-csrf-token': '9cbe863e1275f84c383733499d4fd4059d2db8e042c08cc3ed04d3dc64e902a8',
#             'gp_ab__notifications__230': 'B',
#             'gp_ab__HybridWebSearchV2__232': 'absent',
#             '__cfruid': 'bd2f483c899d681b49ce5c9fd685ef3430e5e26e-1740396977',
#             '_gcl_au': '1.1.1729042314.1740396980',
#             '_gpauth': 'eyJhbGciOiJSUzI1NiIsImtpZCI6IjI0QkVFNDg5MTIwRTE1ODdBMEYyOEE1ODYwRTY4QkM2OTQwODkxNDAiLCJ4NXQiOiJKTDdraVJJT0ZZZWc4b3BZWU9hTHhwUUlrVUEiLCJ0eXAiOiJKV1QifQ.eyJpc3MiOiJodHRwczovL2F1dGgucHJhY3VqLnBsIiwibmJmIjoxNzQxMDUwNTc0LCJpYXQiOjE3NDEwNTA1NzQsImV4cCI6MTc0MTEzNzU3NCwiYXVkIjpbInByYWN1ai5wbCIsImh0dHBzOi8vYXV0aC5wcmFjdWoucGwvcmVzb3VyY2VzIl0sInNjb3BlIjpbInByYWN1ai5wbCIsIm9mZmxpbmVfYWNjZXNzIl0sImFtciI6WyJleHRlcm5hbCJdLCJjbGllbnRfaWQiOiJwcmFjdWoucGxfZXh0ZXJuYWwiLCJmaWxlc3RvcmVfYWNjZXNzIjoiYWxsb3ciLCJhcHBsaWNhdGlvbnNfYWNjZXNzIjoiYWxsb3ciLCJmaWxlX293bmVyIjoidHJ1ZSIsInVzZXJfYWdyZWVtZW50c19hY2Nlc3MiOiJhbGxvdyIsInNhdmVkX29mZmVyc19hY2Nlc3MiOiJhbGxvdyIsImpvYm9mZmVyc19hY2Nlc3MiOiJhbGxvdyIsImNyZWF0ZV9hY2NvdW50IjoiYWxsb3ciLCJnZXRfYWNjb3VudCI6ImFsbG93IiwiYWdyZWVtZW50X3Jldm9rZSI6ImFsbG93IiwibmVicmFza2FfYWNjZXNzIjoiYWxsb3ciLCJhcHBsaWNhdGlvbnNmb3JtX2FjY2VzcyI6ImFsbG93Iiwic2tpZGJsYW5kaXJfYWNjZXNzIjoiYWxsb3ciLCJjb25maXJtX25ld19lbWFpbCI6ImFsbG93IiwidHJhY2tpbmdfYWNjZXNzIjoiYWxsb3ciLCJha2lyYV9hY2Nlc3MiOiJhbGxvdyIsInBlcnNvbmFsaXp1amFjeXBhdHJ5a19hY2Nlc3MiOiJhbGxvdyIsInN1YiI6Im1vanByYWN1ajoyMzQ0Njg2OCIsImF1dGhfdGltZSI6MTczMjEyMTE2NSwiaWRwIjoiZ3J1cGFwcmFjdWoiLCJlbWFpbCI6ImxhdnIyMDA0QGdtYWlsLmNvbSIsIklzQ29uZmlybWVkIjoiVHJ1ZSIsImVtYWlsX3ZlcmlmaWVkIjoiVHJ1ZSIsImdpdmVuX25hbWUiOiJBbmRyZWkiLCJmYW1pbHlfbmFtZSI6IklobmF0b3ZpY3oiLCJDaXR5IjoiV2Fyc3phd2EiLCJFbXBsb3ltZW50TGV2ZWwiOiJzYW1vZHppZWxueSBzcGVjamFsaXN0YSIsInVzZXJmaWxlc19hY2Nlc3MiOiJhbGxvdyIsInJvbGUiOiJFeHRlcm5hbENsaWVudCIsInNpbHZlcnN0YXJfYWNjZXNzIjoiYWxsb3ciLCJoZWR3aWdhX2FjY2VzcyI6ImFsbG93IiwibWFpbmVfYWNjZXNzIjoiYWxsb3ciLCJtYWluZV9zdXJ2ZXlzX3dyaXRlIjoiYWxsb3ciLCJtYWluZV9zdXJ2ZXlzX3JlYWQiOiJteSIsIm1haW5lX2NvbXBhcmlzb25fcmVhZCI6Im15IiwiaGF3YWlpX2FjY2VzcyI6ImFsbG93Iiwib2tsYWhvbWFfYWNjZXNzIjoiYWxsb3ciLCJjb250ZW50b3d5Y3lwcmlhbl9hY2Nlc3MiOiJhbGxvdyIsInN6dWthamFjeXN6eW1vbl9hY2Nlc3MiOiJhbGxvdyIsInNhbmZyYW5jaXNjb19hY2Nlc3MiOiJhbGxvdyIsIm5pdHJ1amFjeW5lcG9tdWNlbl9hY2Nlc3MiOiJhbGxvdyIsInRleGFzX2FjY2VzcyI6ImFsbG93IiwiZ2VvZ2Vyd2F6eV9hY2Nlc3MiOiJhbGxvdyIsIndhc2hpbmd0b25fYWNjZXNzIjoiYWxsb3ciLCJ1c2VyR3JvdXAiOiJDYW5kaWRhdGVzIiwicmVjb21tZW5kYXRpb25fYWNjZXNzIjoiYWxsb3cifQ.n1BOs04Dw9jOj6S2ZeZc-gRPa0gqwYhOCTejHroEalSRAU8IlMaYk8CK-sDzjnuk7S1dXhaKQqqCjfRPkf4B01VGXENWti5CZ_XolAMwYJoB4h7OL0yX0SthamW9nlQxvx_lp9rQv7_LcxIQS7MNzRGo8oIuruZfNXG-6WjqxRrxPXDTjWwXieEUr8kW_QwiHcKDA3ME37mA1N8XV80BHzbCPxSZo7uWSWrSNFsT19M1ssje1CoV8fLotq9Or-QiSKacpJy31N1Cx6RcP5Abn4k6xfzd3hg2hEtgz1c_O_idq-EYKGritXzTeM-tYEKlOK9cMVTY-v4dcV_prtgnhueT5zaI2smN7EwhpLjW-6fgQLccP4d1vPCun2qA2lkDRY5l4MIm6q--kRc8i3RXHbd4pBZhJqTiVwzk4wNBBaYWhXxF7RdWRrz0g6OCFHtkfxacnyufdjbD4OxIwtHdkUVXrBmSUJswPXixOdcKDIkmZi6lMNxGfT4JR2FjsjlCySPJ8T5cIXz2FCfenznZ4QQ-5k-VYa6H34KDkYdHAV-UaVG4GJTf_Nreo9yIRN6XqXzqg0Oudg6q0xnTeyORxs8kbzQdfZhMrvx1toLxpVg-GjyXiyS4t3m_hQTQB-bwH4qZN8sKQ1xxSHVgluaXPH1G1-KK15b-gMrbPYOdccc',
#             '__cf_bm': '.thNC6atKDV9R0oSwByfLuWR1ZllKYSk5JBD_sdjgLY-1741050574-1.0.1.1-FTB16Dij0CqXfT7N5GJPw9B09q42GFBQvJ7_Lwc_WeN1HhEeQPXOhQNCss_2TMG4CLPwLF7vjRY7jjrmD1xGsChXjCx2ileBu2zeSr7_oYI',
#             '_cfuvid': 'Bo15BBqfy8c4WvGnKdmrdtnSfEOrDKJNU3hMRL1oYLI-1741050574711-0.0.1.1-604800000',
#             'gp_tr_gptrackPVID': 'ad3470a8-6372-446a-b7bb-bebda8c2b5f0',
#             'gptrackPVID': '4606e70e-2c28-455f-y5b2-3ca0d84791f8',
#             'cf_clearance': 'HWeIQ_Q_qz.FxYiemScYjAWAHXRa2zjQ7D2hrCcYsH4-1741050576-1.2.1.1-LSMS5fm_VD8j9K.5kP0PfgyjMXmajkrWJ6YD7KwW09QPuWKiwOBnqgAc7NT28ZWPIusSbrTFOgB2eGn9.dz1Dt.yj1kWO25CsQIUmYNONm46tHUAIiZV_0Bu.KSLImxARKw6UMaI.EXUZxo39vxrM8rsdEIdk9LnED9vuSfwlvEVoBkR30VOVZEg1vpL0VTQUHen2EY6CiooQE.wYubd5BUwUE9ySOFfCKgX2Fw8zlMHuBKFzYDHMq38Nr6fBrfsrCl2RIR8ZpEUit3ZiD8dVfdHONKlb4pCTClwfbT2LMOK.XW17qhggyaTRsGXP69MfLxdYr.ImfOGQ5A95RHaWokLXDqMKs2nyZWknwskKAD8FW4abtIci7X51GyuH4MwKthPGpOiraOhG6eXz2baxCRt_q8jOsxQinFaa0qizb4',
#             '_ga_WDELMMFCBH': 'GS1.1.1741050577.46.0.1741050577.60.0.0',
#             '_ga_DD6PPTKNH1': 'GS1.1.1741050577.46.0.1741050577.60.0.0',
#             '_ga_GD4CKCV28E': 'GS1.1.1741050577.12.0.1741050577.0.0.0',
#             '_ga': 'GA1.2.430510135.1732121151',
#             '_gid': 'GA1.2.2012319682.1741050578',
#             'XSRF-TOKEN': 'CfDJ8BnsG4UujmlAhMc6W89smJaYlxfkoEx0Qkeqpmz_R4qK6Msvqh1mGYH_j0fxO4XuAPYbXHycExhiIPU6yFt_oHCcBr3NpPOPvPKIqGnBbxldt-zbRPZt-hyMk3Yzw2PEZM3ETGMn7U4shvZ0FhGN9WE',
#             '_dc_gtm_UA-350045-57': '1',
#             '_dc_gtm_UA-350045-7': '1',
#             '_dc_gtm_UA-350045-80': '1',
#             '_dc_gtm_UA-350045-59': '1',
#             '__rtbh.uid': '%7B%22eventType%22%3A%22uid%22%2C%22id%22%3A%2223446868%22%2C%22expiryDate%22%3A%222026-03-04T01%3A09%3A38.555Z%22%7D',
#             '__rtbh.lid': '%7B%22eventType%22%3A%22lid%22%2C%22id%22%3A%22wS03jY4zTOE06cPIxYsX%22%2C%22expiryDate%22%3A%222026-03-04T01%3A09%3A38.557Z%22%7D',
#             '_uetsid': '58578910f89511ef84a3c9f118f5785f',
#             '_uetvid': 'e7bad5b0a75e11efae57936341321d2e',
#             '__gfp_64b': 'vFsceqhKnYBMxDJ4gxd1WdIqNDVblEaehZc4B4S5dRj.w7|1732121151|2|||8:1:32',
#             'cto_bundle': 'nqKLVF9PM2hLMXZJU2djU3Q0QnZxUXpBMmxqSlJNYWs5ak1yVGpRMGdiOE9kOGhxSGlaZlZYbzhUZ3hIMTlrVmclMkZNbUJyTFVzWXhnalFpazZ4ZnJCbEN3Z1N3WmI0Q2UzTFBwY1doVkNYaWI3SXJiaGpmUWR2cjRBWXRxcEJvZlhqN3cyTEpHRmZjV3cyMDZKMGVDVFhQVUliZyUzRCUzRA',
#             'cto_bundle': 'nqKLVF9PM2hLMXZJU2djU3Q0QnZxUXpBMmxqSlJNYWs5ak1yVGpRMGdiOE9kOGhxSGlaZlZYbzhUZ3hIMTlrVmclMkZNbUJyTFVzWXhnalFpazZ4ZnJCbEN3Z1N3WmI0Q2UzTFBwY1doVkNYaWI3SXJiaGpmUWR2cjRBWXRxcEJvZlhqN3cyTEpHRmZjV3cyMDZKMGVDVFhQVUliZyUzRCUzRA',
#             '_clck': 'b27ccm%7C2%7Cftx%7C0%7C1785',
#             '_clsk': '1k4uttu%7C1741050580033%7C1%7C0%7Cs.clarity.ms%2Fcollect',
#         }
#         params = {
#             'pn': f'{pagenumber_int}',
#         }
#         # params.update({"sc": sortoptions}) if sortoptions else None
#         # params.update({"rd": radiuskm}) if radiuskm else None
#         pause_seconds_int = random.randint(3, 7)
#         print(f"OK: Technical pause between requests to pracuj.pl - {pause_seconds_int} seconds")
#         time.sleep(pause_seconds_int)
#         return bin.logic.web.get_html_response_from_url(self.URL_START_STR, headers_dc=headers, params_dc=params, cookies_dc=cookies)
#
#     def parse(self, pagenumber_int=0):
#         html_content, response_status_code = self._fetch_html(pagenumber_int)
#
#         json_data = bin.parsers.pracujpl.pracujpl_parser.recognition_JSON_in_HTML_area_fc(html_content)
#         jobs = bin.logic.parser.recursive_json_search_fc(json_data, "groupedOffers")
#
#         # Save JSON copy
#         bin.logic.filesystem.save_jobs_copy_into_json_file_fc(self.results_filepath, jobs)
#
#         # Save to database
#         self.oDatabasePracujpl.step01_save_parseiteration_fc(
#             self.results_filename, self.current_timestamp, len(jobs), response_status_code, self.URL_START_STR
#         )
#         self.oDatabasePracujpl.step02_save_joboffers_fc(jobs, parse_address_in_warsaw_from_url_fc)
#
#         if pagenumber_int:
#             print(f"OK: Data from page {pagenumber_int} successfully saved in database {self.database_filepath}")
#         else:
#             print(f"OK: Data successfully saved in database {self.database_filepath}")
#
#         print(response_status_code)
#
#     def update_jobvacancies_lat_lon(self):
#         jobs = self.oDatabasePracujpl.step03_get_lastaddedvacancies_from_database_fc()
#
#         for job in jobs:
#             job_id, job_locality, job_street, job_building, display_workplace = job
#
#             address = ", ".join(filter(None, [job_locality, job_street, job_building])) if job_street else display_workplace
#
#             if address:
#                 latitude, longitude = bin.logic.nominatim.get_coordinates_latlon_fc(address, settings.NOMINATIM_URL)
#                 self.oDatabasePracujpl.step04_update_geocoordinatest_fc(latitude, longitude, job_id)
#
#                 if latitude and longitude:
#                     print(f"Coordinates for job ID {job_id} updated: {latitude}, {longitude}")
#                 else:
#                     print(f"Failed to get coordinates for job ID {job_id} (address: {address})")
#             else:
#                 print(f"No address for job ID {job_id}")
#
#     def commit_changes(self):
#         self.oDatabasePracujpl.step05_commit_things()
#
#
# if __name__ == "__main__":
#     parser = Pracujpl()
#
#     # Parsing multiple pages
#     for page in range(0, 6):
#         parser.parse(page)
#
#     # Update job vacancies with coordinates
#     parser.update_jobvacancies_lat_lon()
#
#     # Commit changes to the database
#     parser.commit_changes()
#     print("OK: Coordinate update completed.")




# import bin.logic.parser
# import bin.logic.web
# import bin.logic.filesystem
# import bin.logic.nominatim
# import bin.settings as settings
#
# from bin.parsers.pracujpl.pracujpl_parser import parse_address_in_warsaw_from_url_fc
# from bin.parsers.pracujpl.pracujpl_database import Database_pracujpl
#
# import time
# import random
#
# PLATFORMNAME_str = "pracujpl"
# DATABASE_FILEPATH_str = settings.get_databasefilepath_fc(PLATFORMNAME_str)
# URL_START_str = 'https://www.pracuj.pl/praca/warszawa;kw'
#
# # HTML-код (можно заменить на чтение из файла или другой источник)
# oDatabasePracujpl = Database_pracujpl(DATABASE_FILEPATH_str)
#
# def parse_from_pracuj_pl(oDatabasePracujpl, parseiteraion_results_filepath, parseiteraion_results_filename, current_timestamp, pagenumber_int = 0):
#     if not pagenumber_int:
#         headers = {
#             'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
#             'accept-language': 'en-US,en;q=0.9,ru-BY;q=0.8,ru-RU;q=0.7,ru;q=0.6',
#             # 'cookie': 'gp__cfXfiDZP=43; __cfruid=34c5ac7f7068c5a18c2c1720033cdc8bb818b495-1732121145; gptrackCookie=99bb3647-5c3f-4a50-y6ae-6a50428adf91; gp_lang=pl; gpc_v=1; gpc_analytic=1; gpc_func=1; gpc_ad=1; gpc_audience=1; gpc_social=1; _gcl_au=1.1.1526634893.1732121151; x-auth-csrf-token=ae26d655736547e565e84eaf999be25c9b15bcb67db4e952907477b878b2e75e; _gpauthclient=pracuj.pl_external; gpSearchType=Default; _gpauthrt=ZLZJuxlIZRD%2BuXoKIMOLbJLUMS%2FhVKP%2FqZoeyG6ET%2BeHWeiC%2F7DyTVx88xz7lQu1unplwre9Ectjchwac%2F9xLrsyWHs5UCPJnjYdBzVXEexeGybgJKtOQHSy7IbOuTdfMsIx4F7Be%2FFGAuXDEr%2Fy1Q%3D%3D; gp_ab__tech__227=A; _cfuvid=C7btfQNsTWLGZZyIvqjvf8Rm1D5LQTVxwlBHPUNG4jw-1737523183907-0.0.1.1-604800000; gp_tr_gptrackCookie=c1b88749-2665-4ad1-b82b-8e98c9e6b785; _gpantiforgery=CfDJ8BnsG4UujmlAhMc6W89smJZKuLovf73H9nLwDFytKfwJy4jZkis6Uh-OPSZRqxiz2pMtGEePLenbtqR5wumc-44uCpQIEn_qdtYbIE8jYKxwr-avzzJazkjMtCFBrzAjTaUul_Evdm7osgHFwb7Yz0s; _gpauth=eyJhbGciOiJSUzI1NiIsImtpZCI6IjI0QkVFNDg5MTIwRTE1ODdBMEYyOEE1ODYwRTY4QkM2OTQwODkxNDAiLCJ4NXQiOiJKTDdraVJJT0ZZZWc4b3BZWU9hTHhwUUlrVUEiLCJ0eXAiOiJKV1QifQ.eyJpc3MiOiJodHRwczovL2F1dGgucHJhY3VqLnBsIiwibmJmIjoxNzM3NjM3NzA1LCJpYXQiOjE3Mzc2Mzc3MDUsImV4cCI6MTczNzcyNDcwNSwiYXVkIjpbInByYWN1ai5wbCIsImh0dHBzOi8vYXV0aC5wcmFjdWoucGwvcmVzb3VyY2VzIl0sInNjb3BlIjpbInByYWN1ai5wbCIsIm9mZmxpbmVfYWNjZXNzIl0sImFtciI6WyJleHRlcm5hbCJdLCJjbGllbnRfaWQiOiJwcmFjdWoucGxfZXh0ZXJuYWwiLCJmaWxlc3RvcmVfYWNjZXNzIjoiYWxsb3ciLCJhcHBsaWNhdGlvbnNfYWNjZXNzIjoiYWxsb3ciLCJmaWxlX293bmVyIjoidHJ1ZSIsInVzZXJfYWdyZWVtZW50c19hY2Nlc3MiOiJhbGxvdyIsInNhdmVkX29mZmVyc19hY2Nlc3MiOiJhbGxvdyIsImpvYm9mZmVyc19hY2Nlc3MiOiJhbGxvdyIsImNyZWF0ZV9hY2NvdW50IjoiYWxsb3ciLCJnZXRfYWNjb3VudCI6ImFsbG93IiwiYWdyZWVtZW50X3Jldm9rZSI6ImFsbG93IiwibmVicmFza2FfYWNjZXNzIjoiYWxsb3ciLCJhcHBsaWNhdGlvbnNmb3JtX2FjY2VzcyI6ImFsbG93Iiwic2tpZGJsYW5kaXJfYWNjZXNzIjoiYWxsb3ciLCJjb25maXJtX25ld19lbWFpbCI6ImFsbG93IiwidHJhY2tpbmdfYWNjZXNzIjoiYWxsb3ciLCJha2lyYV9hY2Nlc3MiOiJhbGxvdyIsInBlcnNvbmFsaXp1amFjeXBhdHJ5a19hY2Nlc3MiOiJhbGxvdyIsInN1YiI6Im1vanByYWN1ajoyMzQ0Njg2OCIsImF1dGhfdGltZSI6MTczMjEyMTE2NSwiaWRwIjoiZ3J1cGFwcmFjdWoiLCJlbWFpbCI6ImxhdnIyMDA0QGdtYWlsLmNvbSIsIklzQ29uZmlybWVkIjoiVHJ1ZSIsImVtYWlsX3ZlcmlmaWVkIjoiVHJ1ZSIsImdpdmVuX25hbWUiOiJBbmRyZWkiLCJmYW1pbHlfbmFtZSI6IklobmF0b3ZpY3oiLCJDaXR5IjoiV2Fyc3phd2EiLCJFbXBsb3ltZW50TGV2ZWwiOiJzYW1vZHppZWxueSBzcGVjamFsaXN0YSIsInVzZXJmaWxlc19hY2Nlc3MiOiJhbGxvdyIsInJvbGUiOiJFeHRlcm5hbENsaWVudCIsInNpbHZlcnN0YXJfYWNjZXNzIjoiYWxsb3ciLCJoZWR3aWdhX2FjY2VzcyI6ImFsbG93IiwibWFpbmVfYWNjZXNzIjoiYWxsb3ciLCJtYWluZV9zdXJ2ZXlzX3dyaXRlIjoiYWxsb3ciLCJtYWluZV9zdXJ2ZXlzX3JlYWQiOiJteSIsIm1haW5lX2NvbXBhcmlzb25fcmVhZCI6Im15IiwiaGF3YWlpX2FjY2VzcyI6ImFsbG93Iiwib2tsYWhvbWFfYWNjZXNzIjoiYWxsb3ciLCJjb250ZW50b3d5Y3lwcmlhbl9hY2Nlc3MiOiJhbGxvdyIsInN6dWthamFjeXN6eW1vbl9hY2Nlc3MiOiJhbGxvdyIsInNhbmZyYW5jaXNjb19hY2Nlc3MiOiJhbGxvdyIsIm5pdHJ1amFjeW5lcG9tdWNlbl9hY2Nlc3MiOiJhbGxvdyIsInRleGFzX2FjY2VzcyI6ImFsbG93IiwidXNlckdyb3VwIjoiQ2FuZGlkYXRlcyIsInJlY29tbWVuZGF0aW9uX2FjY2VzcyI6ImFsbG93In0.V-WKFyV-FRb54lt7cskNQafc80R-yolQOJFD6OzQ0KsNgPZymkbobIYp6Ts8h1dOYOECmOAbpHPdI5Tcx-TbufJ1nPKU54ky_anpWHNy_P6MdemqKA4EeUovmHcMToPOtBc7sftE7zJqbHKRBIL3FdymtUaPkS4yNwcSk8G-LQQcCMjazaZ_yyxyodkbdsEuwqP8u-jyIStH41tXlkMRcxwoYE8GM6U3DVQPXNzDx6Wq4-xXyAUIQYqH8gQXQmeRwZb2w65OC4kxKtA748UeSTjRe4rZGBM8WM23f2vEHfNxxAyoycLKrnASok7KuGjKOTiSpNzHnNZOdQbXNTrDe5zptqOS8JRSh2SUE2wvE9KBvdbZlHOeyKmg7F8SeHxvUq_vbl5l6iOzpoTMkz36jHzgRJi9QmkNk9N_CHapUosrSqaQutQ53Xh5FHGUKVMJKZd8EaAeyI-BmlJMl_yWvWeyB9ILs5ifJrWmUjkNsywCU--ifUHKFHWNMLgtvVGdzxLqeBx-9mC4peY9lYTww9VRBCl2DoDE-t2SkJC58G_fD6TupHSQcw0_aOPprTakKlyBP1bRmKHzex7w_xIwzKp8SP_OS9_QyotP7xLRscrN1K5WVD9z-pFP9ZmMtnGOspAxbv1s6-N7m5nTwL4vfq0TLZj15qulYLDrIp3rOyA; __cf_bm=G9IzaHEIjw3YGSRPGAukweH0E2QZYLTz2UGapKYh9Mc-1737637706-1.0.1.1-qL9patuCBhGvgFxODRbkXFJd2yabaLLMRX5Pa3qYNVY4ADYveV8WfRS4V.UD.RSCoiBq.2pEkxaJFQ0sr.WNSQ; cf_clearance=p.EdYNtC9QXzYZoZdcs8GxgquhfbiLOaWqsGDYbYaZs-1737637708-1.2.1.1-imcTxWLEV5Eqb4STSAzGf6ykusdoAyU8WmJX1JjQp5S6sKn6FPo6J0_J.RcNCqm3gcXGo_WFbVGERM7771CUCNMQZbOb9Jn9ALc1Co9M7tEupsy9ePFPc.PanmFN8XDrqlzPLSzt3N7kunV3aNrKZ2Nq9f7XxDzlapCi7gMwXR3Pbyl1W7l.MDEyjweXqZDkfiqe1xHfd6bqzT5OF9njn1HAdj2szXpihr7G3iSqktpIX7dWXfHAtdS6q4RjBDTgWnsIAZCFPjA5yidD90rhLNvGZg587l874AofT0wvzYs; _gid=GA1.2.944345992.1737637710; __gfp_64b=JoMRE6QDzUfIZ.VhFWO00ReFGHNQG0SGzW7mvVJ1LwT.Y7|1732121151|2|||8:1:32; _clck=b27ccm%7C2%7Cfst%7C0%7C1785; gp_tr_gptrackPVID=c7943a68-f9e8-46eb-8d4e-db6f706862af; gptrackPVID=06993c8b-c261-43a0-y7c8-dca33cc17c6e; _ga_GD4CKCV28E=GS1.1.1737637709.6.1.1737637856.0.0.0; _ga_WDELMMFCBH=GS1.1.1737637709.7.1.1737637856.4.0.0; _ga_DD6PPTKNH1=GS1.1.1737637709.7.1.1737637856.4.0.0; _ga=GA1.2.430510135.1732121151; __rtbh.uid=%7B%22eventType%22%3A%22uid%22%2C%22id%22%3A%2223446868%22%2C%22expiryDate%22%3A%222026-01-23T13%3A10%3A57.799Z%22%7D; __rtbh.lid=%7B%22eventType%22%3A%22lid%22%2C%22id%22%3A%22wS03jY4zTOE06cPIxYsX%22%2C%22expiryDate%22%3A%222026-01-23T13%3A10%3A57.800Z%22%7D; _uetsid=24820510d98b11ef9d0cbf9e2df34c9f; _uetvid=e7bad5b0a75e11efae57936341321d2e; cto_bundle=YCf8rV9PM2hLMXZJU2djU3Q0QnZxUXpBMmxuT2NQZVhUWTNyMjg1eXZGaTZaN3JLJTJGMUNPNkE4MnB6MThzT3drZUJqWVJuVyUyQncyUWFRbG9VTVJMYzlDSHRqZmFUY29iYVNaNGZnOHJWVng4ZXppa2pUTUJIeFJGeGRmRjIzREFwWHR5U1p4QXBQZkJJQ0czUTV6Y1B4Z3pnaENnJTNEJTNE; XSRF-TOKEN=CfDJ8BnsG4UujmlAhMc6W89smJaPOUHFarirLTIWm0lGJFVMaz5fIzs2GdNpUnrqMTYFFr-mKuLCBsyJlvGZZvjeT6Dc4ZH6I4kKr4rwmP515BGNzFcFcXg1aqso51gMqIg3mlFusBMFGH3ox02J_bzqBQ0; _clsk=1fu0ix0%7C1737637859285%7C3%7C0%7Cl.clarity.ms%2Fcollect',
#             'priority': 'u=0, i',
#             'sec-ch-ua': '"Google Chrome";v="131", "Chromium";v="131", "Not_A Brand";v="24"',
#             'sec-ch-ua-mobile': '?0',
#             'sec-ch-ua-platform': '"Windows"',
#             'sec-fetch-dest': 'document',
#             'sec-fetch-mode': 'navigate',
#             'sec-fetch-site': 'none',
#             'sec-fetch-user': '?1',
#             'upgrade-insecure-requests': '1',
#             'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36',
#         }
#         html_content, response_status_code = bin.logic.web.get_html_response_from_url(url_str=URL_START_str, headers_dc=headers)
#     else:
#         headers = {
#             'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
#             'accept-language': 'en-US,en;q=0.9,ru-BY;q=0.8,ru-RU;q=0.7,ru;q=0.6',
#             'priority': 'u=0, i',
#             'referer': 'https://www.pracuj.pl/praca/warszawa;kw',
#             'sec-ch-ua': '"Not(A:Brand";v="99", "Google Chrome";v="133", "Chromium";v="133"',
#             'sec-ch-ua-mobile': '?0',
#             'sec-ch-ua-platform': '"Windows"',
#             'sec-fetch-dest': 'document',
#             'sec-fetch-mode': 'navigate',
#             'sec-fetch-site': 'same-origin',
#             'sec-fetch-user': '?1',
#             'upgrade-insecure-requests': '1',
#             'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/133.0.0.0 Safari/537.36',
#             # 'cookie': 'gp__cfXfiDZP=43; gptrackCookie=99bb3647-5c3f-4a50-y6ae-6a50428adf91; gp_lang=pl; gpc_v=1; gpc_analytic=1; gpc_func=1; gpc_ad=1; gpc_audience=1; gpc_social=1; x-auth-csrf-token=ae26d655736547e565e84eaf999be25c9b15bcb67db4e952907477b878b2e75e; _gpauthclient=pracuj.pl_external; gpSearchType=Default; _gpauthrt=ZLZJuxlIZRD%2BuXoKIMOLbJLUMS%2FhVKP%2FqZoeyG6ET%2BeHWeiC%2F7DyTVx88xz7lQu1unplwre9Ectjchwac%2F9xLrsyWHs5UCPJnjYdBzVXEexeGybgJKtOQHSy7IbOuTdfMsIx4F7Be%2FFGAuXDEr%2Fy1Q%3D%3D; gp_tr_gptrackCookie=c1b88749-2665-4ad1-b82b-8e98c9e6b785; _gpantiforgery=CfDJ8BnsG4UujmlAhMc6W89smJZKuLovf73H9nLwDFytKfwJy4jZkis6Uh-OPSZRqxiz2pMtGEePLenbtqR5wumc-44uCpQIEn_qdtYbIE8jYKxwr-avzzJazkjMtCFBrzAjTaUul_Evdm7osgHFwb7Yz0s; _epantiforgery=CfDJ8HUifgaomuZGmjCc5nlQaanCCG7f6ToAIASOMWhelkl4NNACVgJVyfu8pDTdhTjYqb6afyjAPDY4JkQrTW1GkwKVPikAiutSgTCYRYep8Fn1sN-JTH_JNAXkU5AGBByj7Z25uyvDas1sx_TKAtk9wwI; Magpie-XSRF-Token=CfDJ8HUifgaomuZGmjCc5nlQaakGg3CzMCCqANlxOUGROTi3Sb9PKlalvEPqFJYdmgU3jlenEqfiBcJGAsGYRoOvzxUqU3C-VEEDMISRSZAyYdSZjvZl0wZTYrh2mYB_5bVM0t0FZ9G2jipZrYG6D0ko0j4; _ga_CJXS9Q5W6G=GS1.1.1737679478.2.0.1737679478.60.0.0; _ga_DD6PPTKNH1=deleted; x-account-csrf-token=9cbe863e1275f84c383733499d4fd4059d2db8e042c08cc3ed04d3dc64e902a8; gp_ab__notifications__230=B; gp_ab__HybridWebSearchV2__232=absent; __cfruid=bd2f483c899d681b49ce5c9fd685ef3430e5e26e-1740396977; _gcl_au=1.1.1729042314.1740396980; _gpauth=eyJhbGciOiJSUzI1NiIsImtpZCI6IjI0QkVFNDg5MTIwRTE1ODdBMEYyOEE1ODYwRTY4QkM2OTQwODkxNDAiLCJ4NXQiOiJKTDdraVJJT0ZZZWc4b3BZWU9hTHhwUUlrVUEiLCJ0eXAiOiJKV1QifQ.eyJpc3MiOiJodHRwczovL2F1dGgucHJhY3VqLnBsIiwibmJmIjoxNzQxMDUwNTc0LCJpYXQiOjE3NDEwNTA1NzQsImV4cCI6MTc0MTEzNzU3NCwiYXVkIjpbInByYWN1ai5wbCIsImh0dHBzOi8vYXV0aC5wcmFjdWoucGwvcmVzb3VyY2VzIl0sInNjb3BlIjpbInByYWN1ai5wbCIsIm9mZmxpbmVfYWNjZXNzIl0sImFtciI6WyJleHRlcm5hbCJdLCJjbGllbnRfaWQiOiJwcmFjdWoucGxfZXh0ZXJuYWwiLCJmaWxlc3RvcmVfYWNjZXNzIjoiYWxsb3ciLCJhcHBsaWNhdGlvbnNfYWNjZXNzIjoiYWxsb3ciLCJmaWxlX293bmVyIjoidHJ1ZSIsInVzZXJfYWdyZWVtZW50c19hY2Nlc3MiOiJhbGxvdyIsInNhdmVkX29mZmVyc19hY2Nlc3MiOiJhbGxvdyIsImpvYm9mZmVyc19hY2Nlc3MiOiJhbGxvdyIsImNyZWF0ZV9hY2NvdW50IjoiYWxsb3ciLCJnZXRfYWNjb3VudCI6ImFsbG93IiwiYWdyZWVtZW50X3Jldm9rZSI6ImFsbG93IiwibmVicmFza2FfYWNjZXNzIjoiYWxsb3ciLCJhcHBsaWNhdGlvbnNmb3JtX2FjY2VzcyI6ImFsbG93Iiwic2tpZGJsYW5kaXJfYWNjZXNzIjoiYWxsb3ciLCJjb25maXJtX25ld19lbWFpbCI6ImFsbG93IiwidHJhY2tpbmdfYWNjZXNzIjoiYWxsb3ciLCJha2lyYV9hY2Nlc3MiOiJhbGxvdyIsInBlcnNvbmFsaXp1amFjeXBhdHJ5a19hY2Nlc3MiOiJhbGxvdyIsInN1YiI6Im1vanByYWN1ajoyMzQ0Njg2OCIsImF1dGhfdGltZSI6MTczMjEyMTE2NSwiaWRwIjoiZ3J1cGFwcmFjdWoiLCJlbWFpbCI6ImxhdnIyMDA0QGdtYWlsLmNvbSIsIklzQ29uZmlybWVkIjoiVHJ1ZSIsImVtYWlsX3ZlcmlmaWVkIjoiVHJ1ZSIsImdpdmVuX25hbWUiOiJBbmRyZWkiLCJmYW1pbHlfbmFtZSI6IklobmF0b3ZpY3oiLCJDaXR5IjoiV2Fyc3phd2EiLCJFbXBsb3ltZW50TGV2ZWwiOiJzYW1vZHppZWxueSBzcGVjamFsaXN0YSIsInVzZXJmaWxlc19hY2Nlc3MiOiJhbGxvdyIsInJvbGUiOiJFeHRlcm5hbENsaWVudCIsInNpbHZlcnN0YXJfYWNjZXNzIjoiYWxsb3ciLCJoZWR3aWdhX2FjY2VzcyI6ImFsbG93IiwibWFpbmVfYWNjZXNzIjoiYWxsb3ciLCJtYWluZV9zdXJ2ZXlzX3dyaXRlIjoiYWxsb3ciLCJtYWluZV9zdXJ2ZXlzX3JlYWQiOiJteSIsIm1haW5lX2NvbXBhcmlzb25fcmVhZCI6Im15IiwiaGF3YWlpX2FjY2VzcyI6ImFsbG93Iiwib2tsYWhvbWFfYWNjZXNzIjoiYWxsb3ciLCJjb250ZW50b3d5Y3lwcmlhbl9hY2Nlc3MiOiJhbGxvdyIsInN6dWthamFjeXN6eW1vbl9hY2Nlc3MiOiJhbGxvdyIsInNhbmZyYW5jaXNjb19hY2Nlc3MiOiJhbGxvdyIsIm5pdHJ1amFjeW5lcG9tdWNlbl9hY2Nlc3MiOiJhbGxvdyIsInRleGFzX2FjY2VzcyI6ImFsbG93IiwiZ2VvZ2Vyd2F6eV9hY2Nlc3MiOiJhbGxvdyIsIndhc2hpbmd0b25fYWNjZXNzIjoiYWxsb3ciLCJ1c2VyR3JvdXAiOiJDYW5kaWRhdGVzIiwicmVjb21tZW5kYXRpb25fYWNjZXNzIjoiYWxsb3cifQ.n1BOs04Dw9jOj6S2ZeZc-gRPa0gqwYhOCTejHroEalSRAU8IlMaYk8CK-sDzjnuk7S1dXhaKQqqCjfRPkf4B01VGXENWti5CZ_XolAMwYJoB4h7OL0yX0SthamW9nlQxvx_lp9rQv7_LcxIQS7MNzRGo8oIuruZfNXG-6WjqxRrxPXDTjWwXieEUr8kW_QwiHcKDA3ME37mA1N8XV80BHzbCPxSZo7uWSWrSNFsT19M1ssje1CoV8fLotq9Or-QiSKacpJy31N1Cx6RcP5Abn4k6xfzd3hg2hEtgz1c_O_idq-EYKGritXzTeM-tYEKlOK9cMVTY-v4dcV_prtgnhueT5zaI2smN7EwhpLjW-6fgQLccP4d1vPCun2qA2lkDRY5l4MIm6q--kRc8i3RXHbd4pBZhJqTiVwzk4wNBBaYWhXxF7RdWRrz0g6OCFHtkfxacnyufdjbD4OxIwtHdkUVXrBmSUJswPXixOdcKDIkmZi6lMNxGfT4JR2FjsjlCySPJ8T5cIXz2FCfenznZ4QQ-5k-VYa6H34KDkYdHAV-UaVG4GJTf_Nreo9yIRN6XqXzqg0Oudg6q0xnTeyORxs8kbzQdfZhMrvx1toLxpVg-GjyXiyS4t3m_hQTQB-bwH4qZN8sKQ1xxSHVgluaXPH1G1-KK15b-gMrbPYOdccc; __cf_bm=.thNC6atKDV9R0oSwByfLuWR1ZllKYSk5JBD_sdjgLY-1741050574-1.0.1.1-FTB16Dij0CqXfT7N5GJPw9B09q42GFBQvJ7_Lwc_WeN1HhEeQPXOhQNCss_2TMG4CLPwLF7vjRY7jjrmD1xGsChXjCx2ileBu2zeSr7_oYI; _cfuvid=Bo15BBqfy8c4WvGnKdmrdtnSfEOrDKJNU3hMRL1oYLI-1741050574711-0.0.1.1-604800000; gp_tr_gptrackPVID=ad3470a8-6372-446a-b7bb-bebda8c2b5f0; gptrackPVID=4606e70e-2c28-455f-y5b2-3ca0d84791f8; cf_clearance=HWeIQ_Q_qz.FxYiemScYjAWAHXRa2zjQ7D2hrCcYsH4-1741050576-1.2.1.1-LSMS5fm_VD8j9K.5kP0PfgyjMXmajkrWJ6YD7KwW09QPuWKiwOBnqgAc7NT28ZWPIusSbrTFOgB2eGn9.dz1Dt.yj1kWO25CsQIUmYNONm46tHUAIiZV_0Bu.KSLImxARKw6UMaI.EXUZxo39vxrM8rsdEIdk9LnED9vuSfwlvEVoBkR30VOVZEg1vpL0VTQUHen2EY6CiooQE.wYubd5BUwUE9ySOFfCKgX2Fw8zlMHuBKFzYDHMq38Nr6fBrfsrCl2RIR8ZpEUit3ZiD8dVfdHONKlb4pCTClwfbT2LMOK.XW17qhggyaTRsGXP69MfLxdYr.ImfOGQ5A95RHaWokLXDqMKs2nyZWknwskKAD8FW4abtIci7X51GyuH4MwKthPGpOiraOhG6eXz2baxCRt_q8jOsxQinFaa0qizb4; _ga_WDELMMFCBH=GS1.1.1741050577.46.0.1741050577.60.0.0; _ga_DD6PPTKNH1=GS1.1.1741050577.46.0.1741050577.60.0.0; _ga_GD4CKCV28E=GS1.1.1741050577.12.0.1741050577.0.0.0; _ga=GA1.2.430510135.1732121151; _gid=GA1.2.2012319682.1741050578; XSRF-TOKEN=CfDJ8BnsG4UujmlAhMc6W89smJaYlxfkoEx0Qkeqpmz_R4qK6Msvqh1mGYH_j0fxO4XuAPYbXHycExhiIPU6yFt_oHCcBr3NpPOPvPKIqGnBbxldt-zbRPZt-hyMk3Yzw2PEZM3ETGMn7U4shvZ0FhGN9WE; _dc_gtm_UA-350045-57=1; _dc_gtm_UA-350045-7=1; _dc_gtm_UA-350045-80=1; _dc_gtm_UA-350045-59=1; __rtbh.uid=%7B%22eventType%22%3A%22uid%22%2C%22id%22%3A%2223446868%22%2C%22expiryDate%22%3A%222026-03-04T01%3A09%3A38.555Z%22%7D; __rtbh.lid=%7B%22eventType%22%3A%22lid%22%2C%22id%22%3A%22wS03jY4zTOE06cPIxYsX%22%2C%22expiryDate%22%3A%222026-03-04T01%3A09%3A38.557Z%22%7D; _uetsid=58578910f89511ef84a3c9f118f5785f; _uetvid=e7bad5b0a75e11efae57936341321d2e; __gfp_64b=vFsceqhKnYBMxDJ4gxd1WdIqNDVblEaehZc4B4S5dRj.w7|1732121151|2|||8:1:32; cto_bundle=nqKLVF9PM2hLMXZJU2djU3Q0QnZxUXpBMmxqSlJNYWs5ak1yVGpRMGdiOE9kOGhxSGlaZlZYbzhUZ3hIMTlrVmclMkZNbUJyTFVzWXhnalFpazZ4ZnJCbEN3Z1N3WmI0Q2UzTFBwY1doVkNYaWI3SXJiaGpmUWR2cjRBWXRxcEJvZlhqN3cyTEpHRmZjV3cyMDZKMGVDVFhQVUliZyUzRCUzRA; cto_bundle=nqKLVF9PM2hLMXZJU2djU3Q0QnZxUXpBMmxqSlJNYWs5ak1yVGpRMGdiOE9kOGhxSGlaZlZYbzhUZ3hIMTlrVmclMkZNbUJyTFVzWXhnalFpazZ4ZnJCbEN3Z1N3WmI0Q2UzTFBwY1doVkNYaWI3SXJiaGpmUWR2cjRBWXRxcEJvZlhqN3cyTEpHRmZjV3cyMDZKMGVDVFhQVUliZyUzRCUzRA; _clck=b27ccm%7C2%7Cftx%7C0%7C1785; _clsk=1k4uttu%7C1741050580033%7C1%7C0%7Cs.clarity.ms%2Fcollect',
#         }
#         cookies = {
#             'gp__cfXfiDZP': '43',
#             'gptrackCookie': '99bb3647-5c3f-4a50-y6ae-6a50428adf91',
#             'gp_lang': 'pl',
#             'gpc_v': '1',
#             'gpc_analytic': '1',
#             'gpc_func': '1',
#             'gpc_ad': '1',
#             'gpc_audience': '1',
#             'gpc_social': '1',
#             'x-auth-csrf-token': 'ae26d655736547e565e84eaf999be25c9b15bcb67db4e952907477b878b2e75e',
#             '_gpauthclient': 'pracuj.pl_external',
#             'gpSearchType': 'Default',
#             '_gpauthrt': 'ZLZJuxlIZRD%2BuXoKIMOLbJLUMS%2FhVKP%2FqZoeyG6ET%2BeHWeiC%2F7DyTVx88xz7lQu1unplwre9Ectjchwac%2F9xLrsyWHs5UCPJnjYdBzVXEexeGybgJKtOQHSy7IbOuTdfMsIx4F7Be%2FFGAuXDEr%2Fy1Q%3D%3D',
#             'gp_tr_gptrackCookie': 'c1b88749-2665-4ad1-b82b-8e98c9e6b785',
#             '_gpantiforgery': 'CfDJ8BnsG4UujmlAhMc6W89smJZKuLovf73H9nLwDFytKfwJy4jZkis6Uh-OPSZRqxiz2pMtGEePLenbtqR5wumc-44uCpQIEn_qdtYbIE8jYKxwr-avzzJazkjMtCFBrzAjTaUul_Evdm7osgHFwb7Yz0s',
#             '_epantiforgery': 'CfDJ8HUifgaomuZGmjCc5nlQaanCCG7f6ToAIASOMWhelkl4NNACVgJVyfu8pDTdhTjYqb6afyjAPDY4JkQrTW1GkwKVPikAiutSgTCYRYep8Fn1sN-JTH_JNAXkU5AGBByj7Z25uyvDas1sx_TKAtk9wwI',
#             'Magpie-XSRF-Token': 'CfDJ8HUifgaomuZGmjCc5nlQaakGg3CzMCCqANlxOUGROTi3Sb9PKlalvEPqFJYdmgU3jlenEqfiBcJGAsGYRoOvzxUqU3C-VEEDMISRSZAyYdSZjvZl0wZTYrh2mYB_5bVM0t0FZ9G2jipZrYG6D0ko0j4',
#             '_ga_CJXS9Q5W6G': 'GS1.1.1737679478.2.0.1737679478.60.0.0',
#             '_ga_DD6PPTKNH1': 'deleted',
#             'x-account-csrf-token': '9cbe863e1275f84c383733499d4fd4059d2db8e042c08cc3ed04d3dc64e902a8',
#             'gp_ab__notifications__230': 'B',
#             'gp_ab__HybridWebSearchV2__232': 'absent',
#             '__cfruid': 'bd2f483c899d681b49ce5c9fd685ef3430e5e26e-1740396977',
#             '_gcl_au': '1.1.1729042314.1740396980',
#             '_gpauth': 'eyJhbGciOiJSUzI1NiIsImtpZCI6IjI0QkVFNDg5MTIwRTE1ODdBMEYyOEE1ODYwRTY4QkM2OTQwODkxNDAiLCJ4NXQiOiJKTDdraVJJT0ZZZWc4b3BZWU9hTHhwUUlrVUEiLCJ0eXAiOiJKV1QifQ.eyJpc3MiOiJodHRwczovL2F1dGgucHJhY3VqLnBsIiwibmJmIjoxNzQxMDUwNTc0LCJpYXQiOjE3NDEwNTA1NzQsImV4cCI6MTc0MTEzNzU3NCwiYXVkIjpbInByYWN1ai5wbCIsImh0dHBzOi8vYXV0aC5wcmFjdWoucGwvcmVzb3VyY2VzIl0sInNjb3BlIjpbInByYWN1ai5wbCIsIm9mZmxpbmVfYWNjZXNzIl0sImFtciI6WyJleHRlcm5hbCJdLCJjbGllbnRfaWQiOiJwcmFjdWoucGxfZXh0ZXJuYWwiLCJmaWxlc3RvcmVfYWNjZXNzIjoiYWxsb3ciLCJhcHBsaWNhdGlvbnNfYWNjZXNzIjoiYWxsb3ciLCJmaWxlX293bmVyIjoidHJ1ZSIsInVzZXJfYWdyZWVtZW50c19hY2Nlc3MiOiJhbGxvdyIsInNhdmVkX29mZmVyc19hY2Nlc3MiOiJhbGxvdyIsImpvYm9mZmVyc19hY2Nlc3MiOiJhbGxvdyIsImNyZWF0ZV9hY2NvdW50IjoiYWxsb3ciLCJnZXRfYWNjb3VudCI6ImFsbG93IiwiYWdyZWVtZW50X3Jldm9rZSI6ImFsbG93IiwibmVicmFza2FfYWNjZXNzIjoiYWxsb3ciLCJhcHBsaWNhdGlvbnNmb3JtX2FjY2VzcyI6ImFsbG93Iiwic2tpZGJsYW5kaXJfYWNjZXNzIjoiYWxsb3ciLCJjb25maXJtX25ld19lbWFpbCI6ImFsbG93IiwidHJhY2tpbmdfYWNjZXNzIjoiYWxsb3ciLCJha2lyYV9hY2Nlc3MiOiJhbGxvdyIsInBlcnNvbmFsaXp1amFjeXBhdHJ5a19hY2Nlc3MiOiJhbGxvdyIsInN1YiI6Im1vanByYWN1ajoyMzQ0Njg2OCIsImF1dGhfdGltZSI6MTczMjEyMTE2NSwiaWRwIjoiZ3J1cGFwcmFjdWoiLCJlbWFpbCI6ImxhdnIyMDA0QGdtYWlsLmNvbSIsIklzQ29uZmlybWVkIjoiVHJ1ZSIsImVtYWlsX3ZlcmlmaWVkIjoiVHJ1ZSIsImdpdmVuX25hbWUiOiJBbmRyZWkiLCJmYW1pbHlfbmFtZSI6IklobmF0b3ZpY3oiLCJDaXR5IjoiV2Fyc3phd2EiLCJFbXBsb3ltZW50TGV2ZWwiOiJzYW1vZHppZWxueSBzcGVjamFsaXN0YSIsInVzZXJmaWxlc19hY2Nlc3MiOiJhbGxvdyIsInJvbGUiOiJFeHRlcm5hbENsaWVudCIsInNpbHZlcnN0YXJfYWNjZXNzIjoiYWxsb3ciLCJoZWR3aWdhX2FjY2VzcyI6ImFsbG93IiwibWFpbmVfYWNjZXNzIjoiYWxsb3ciLCJtYWluZV9zdXJ2ZXlzX3dyaXRlIjoiYWxsb3ciLCJtYWluZV9zdXJ2ZXlzX3JlYWQiOiJteSIsIm1haW5lX2NvbXBhcmlzb25fcmVhZCI6Im15IiwiaGF3YWlpX2FjY2VzcyI6ImFsbG93Iiwib2tsYWhvbWFfYWNjZXNzIjoiYWxsb3ciLCJjb250ZW50b3d5Y3lwcmlhbl9hY2Nlc3MiOiJhbGxvdyIsInN6dWthamFjeXN6eW1vbl9hY2Nlc3MiOiJhbGxvdyIsInNhbmZyYW5jaXNjb19hY2Nlc3MiOiJhbGxvdyIsIm5pdHJ1amFjeW5lcG9tdWNlbl9hY2Nlc3MiOiJhbGxvdyIsInRleGFzX2FjY2VzcyI6ImFsbG93IiwiZ2VvZ2Vyd2F6eV9hY2Nlc3MiOiJhbGxvdyIsIndhc2hpbmd0b25fYWNjZXNzIjoiYWxsb3ciLCJ1c2VyR3JvdXAiOiJDYW5kaWRhdGVzIiwicmVjb21tZW5kYXRpb25fYWNjZXNzIjoiYWxsb3cifQ.n1BOs04Dw9jOj6S2ZeZc-gRPa0gqwYhOCTejHroEalSRAU8IlMaYk8CK-sDzjnuk7S1dXhaKQqqCjfRPkf4B01VGXENWti5CZ_XolAMwYJoB4h7OL0yX0SthamW9nlQxvx_lp9rQv7_LcxIQS7MNzRGo8oIuruZfNXG-6WjqxRrxPXDTjWwXieEUr8kW_QwiHcKDA3ME37mA1N8XV80BHzbCPxSZo7uWSWrSNFsT19M1ssje1CoV8fLotq9Or-QiSKacpJy31N1Cx6RcP5Abn4k6xfzd3hg2hEtgz1c_O_idq-EYKGritXzTeM-tYEKlOK9cMVTY-v4dcV_prtgnhueT5zaI2smN7EwhpLjW-6fgQLccP4d1vPCun2qA2lkDRY5l4MIm6q--kRc8i3RXHbd4pBZhJqTiVwzk4wNBBaYWhXxF7RdWRrz0g6OCFHtkfxacnyufdjbD4OxIwtHdkUVXrBmSUJswPXixOdcKDIkmZi6lMNxGfT4JR2FjsjlCySPJ8T5cIXz2FCfenznZ4QQ-5k-VYa6H34KDkYdHAV-UaVG4GJTf_Nreo9yIRN6XqXzqg0Oudg6q0xnTeyORxs8kbzQdfZhMrvx1toLxpVg-GjyXiyS4t3m_hQTQB-bwH4qZN8sKQ1xxSHVgluaXPH1G1-KK15b-gMrbPYOdccc',
#             '__cf_bm': '.thNC6atKDV9R0oSwByfLuWR1ZllKYSk5JBD_sdjgLY-1741050574-1.0.1.1-FTB16Dij0CqXfT7N5GJPw9B09q42GFBQvJ7_Lwc_WeN1HhEeQPXOhQNCss_2TMG4CLPwLF7vjRY7jjrmD1xGsChXjCx2ileBu2zeSr7_oYI',
#             '_cfuvid': 'Bo15BBqfy8c4WvGnKdmrdtnSfEOrDKJNU3hMRL1oYLI-1741050574711-0.0.1.1-604800000',
#             'gp_tr_gptrackPVID': 'ad3470a8-6372-446a-b7bb-bebda8c2b5f0',
#             'gptrackPVID': '4606e70e-2c28-455f-y5b2-3ca0d84791f8',
#             'cf_clearance': 'HWeIQ_Q_qz.FxYiemScYjAWAHXRa2zjQ7D2hrCcYsH4-1741050576-1.2.1.1-LSMS5fm_VD8j9K.5kP0PfgyjMXmajkrWJ6YD7KwW09QPuWKiwOBnqgAc7NT28ZWPIusSbrTFOgB2eGn9.dz1Dt.yj1kWO25CsQIUmYNONm46tHUAIiZV_0Bu.KSLImxARKw6UMaI.EXUZxo39vxrM8rsdEIdk9LnED9vuSfwlvEVoBkR30VOVZEg1vpL0VTQUHen2EY6CiooQE.wYubd5BUwUE9ySOFfCKgX2Fw8zlMHuBKFzYDHMq38Nr6fBrfsrCl2RIR8ZpEUit3ZiD8dVfdHONKlb4pCTClwfbT2LMOK.XW17qhggyaTRsGXP69MfLxdYr.ImfOGQ5A95RHaWokLXDqMKs2nyZWknwskKAD8FW4abtIci7X51GyuH4MwKthPGpOiraOhG6eXz2baxCRt_q8jOsxQinFaa0qizb4',
#             '_ga_WDELMMFCBH': 'GS1.1.1741050577.46.0.1741050577.60.0.0',
#             '_ga_DD6PPTKNH1': 'GS1.1.1741050577.46.0.1741050577.60.0.0',
#             '_ga_GD4CKCV28E': 'GS1.1.1741050577.12.0.1741050577.0.0.0',
#             '_ga': 'GA1.2.430510135.1732121151',
#             '_gid': 'GA1.2.2012319682.1741050578',
#             'XSRF-TOKEN': 'CfDJ8BnsG4UujmlAhMc6W89smJaYlxfkoEx0Qkeqpmz_R4qK6Msvqh1mGYH_j0fxO4XuAPYbXHycExhiIPU6yFt_oHCcBr3NpPOPvPKIqGnBbxldt-zbRPZt-hyMk3Yzw2PEZM3ETGMn7U4shvZ0FhGN9WE',
#             '_dc_gtm_UA-350045-57': '1',
#             '_dc_gtm_UA-350045-7': '1',
#             '_dc_gtm_UA-350045-80': '1',
#             '_dc_gtm_UA-350045-59': '1',
#             '__rtbh.uid': '%7B%22eventType%22%3A%22uid%22%2C%22id%22%3A%2223446868%22%2C%22expiryDate%22%3A%222026-03-04T01%3A09%3A38.555Z%22%7D',
#             '__rtbh.lid': '%7B%22eventType%22%3A%22lid%22%2C%22id%22%3A%22wS03jY4zTOE06cPIxYsX%22%2C%22expiryDate%22%3A%222026-03-04T01%3A09%3A38.557Z%22%7D',
#             '_uetsid': '58578910f89511ef84a3c9f118f5785f',
#             '_uetvid': 'e7bad5b0a75e11efae57936341321d2e',
#             '__gfp_64b': 'vFsceqhKnYBMxDJ4gxd1WdIqNDVblEaehZc4B4S5dRj.w7|1732121151|2|||8:1:32',
#             'cto_bundle': 'nqKLVF9PM2hLMXZJU2djU3Q0QnZxUXpBMmxqSlJNYWs5ak1yVGpRMGdiOE9kOGhxSGlaZlZYbzhUZ3hIMTlrVmclMkZNbUJyTFVzWXhnalFpazZ4ZnJCbEN3Z1N3WmI0Q2UzTFBwY1doVkNYaWI3SXJiaGpmUWR2cjRBWXRxcEJvZlhqN3cyTEpHRmZjV3cyMDZKMGVDVFhQVUliZyUzRCUzRA',
#             'cto_bundle': 'nqKLVF9PM2hLMXZJU2djU3Q0QnZxUXpBMmxqSlJNYWs5ak1yVGpRMGdiOE9kOGhxSGlaZlZYbzhUZ3hIMTlrVmclMkZNbUJyTFVzWXhnalFpazZ4ZnJCbEN3Z1N3WmI0Q2UzTFBwY1doVkNYaWI3SXJiaGpmUWR2cjRBWXRxcEJvZlhqN3cyTEpHRmZjV3cyMDZKMGVDVFhQVUliZyUzRCUzRA',
#             '_clck': 'b27ccm%7C2%7Cftx%7C0%7C1785',
#             '_clsk': '1k4uttu%7C1741050580033%7C1%7C0%7Cs.clarity.ms%2Fcollect',
#         }
#         params = {
#             'pn': f'{pagenumber_int}',
#         }
#         # params.update({"sc": sortoptions}) if sortoptions else None
#         # params.update({"rd": radiuskm}) if radiuskm else None
#         pause_seconds_int = random.randint(3, 7)
#         print(f"OK: technical pause between requests to pracuj.pl - {pause_seconds_int} seconds")
#         time.sleep(pause_seconds_int)
#         #getting next page setting up in params
#         html_content, response_status_code = bin.logic.web.get_html_response_from_url(URL_START_str, headers_dc=headers, params_dc=params, cookies_dc=cookies)
#
#
#     json_data = bin.parsers.pracujpl.pracujpl_parser.recognition_JSON_in_HTML_area_fc(html_content)
#     jobs = bin.logic.parser.recursive_json_search_fc(json_data, "groupedOffers")
#
#     # Сохраняем JSON-файл
#     bin.logic.filesystem.save_jobs_copy_into_json_file_fc(parseiteraion_results_filepath, jobs)
#
#     oDatabasePracujpl.step01_save_parseiteration_fc(parseiteraion_results_filename, current_timestamp, len(jobs), response_status_code, URL_START_str)
#
#     # Сохранение изменений и закрытие соединения
#     oDatabasePracujpl.step02_save_joboffers_fc(jobs, parse_address_in_warsaw_from_url_fc)
#
#     if pagenumber_int:
#         print(f"OK: Данные со страницы {pagenumber_int} успешно сохранены в базе данных {DATABASE_FILEPATH_str}")
#     else:
#         print(f"OK: Данные успешно сохранены в базе данных {DATABASE_FILEPATH_str}")
#
#     print(response_status_code)
#
#
# # Данные для записи в таблицу parseiteration
# parseiteraion_results_filepath = settings.get_dailyresultsfilepath_fc(PLATFORMNAME_str)
# parseiteraion_results_filename = settings.get_filenamefrompath(parseiteraion_results_filepath)
# current_timestamp = settings.get_timestamp()
# url = URL_START_str
#
# def update_jobvacancies_lat_lon_fc(Database_pracujpl):
#     jobs = Database_pracujpl.step03_get_lastaddedvacancies_from_database_fc()
#     # Обновление координат в базе данных
#     for job in jobs:
#         job_id, job_locality, job_street, job_building, display_workplace = job
#
#         # Формирование адреса
#         if job_street:  # Если указан job_street, формируем адрес из деталей
#             address = ", ".join(filter(None, [job_locality, job_street, job_building]))
#         else:  # Если job_street отсутствует, используем display_workplace
#             address = display_workplace
#
#         if address:  # Если есть адрес для поиска
#             latitude, longitude = bin.logic.nominatim.get_coordinates_latlon_fc(address, settings.NOMINATIM_URL)#latitude, longitude = 0, 0
#             # if not latitude or not longitude:
#             #     latitude, longitude = get_coordinates(job_locality)
#             #cursor.execute(
#             #        "UPDATE jobs SET job_latitude = ?, job_longitude = ? WHERE id = ?",
#             #        (latitude, longitude, job_id),
#             #    )
#             Database_pracujpl.step04_update_geocoordinatest_fc(latitude, longitude, job_id)
#
#             if latitude and longitude:  # Если координаты получены успешно
#                 print(f"Координаты для вакансии ID {job_id} обновлены: {latitude}, {longitude}")
#             else:
#                 print(f"Не удалось получить координаты для вакансии ID {job_id} (адрес: {address})")
#         else:
#             print(f"Адрес отсутствует для вакансии ID {job_id}")
#
# parse_from_pracuj_pl(oDatabasePracujpl, parseiteraion_results_filepath, parseiteraion_results_filename, current_timestamp)
# parse_from_pracuj_pl(oDatabasePracujpl, parseiteraion_results_filepath, parseiteraion_results_filename, current_timestamp, 2)
# parse_from_pracuj_pl(oDatabasePracujpl, parseiteraion_results_filepath, parseiteraion_results_filename, current_timestamp, 3)
# parse_from_pracuj_pl(oDatabasePracujpl, parseiteraion_results_filepath, parseiteraion_results_filename, current_timestamp, 4)
# parse_from_pracuj_pl(oDatabasePracujpl, parseiteraion_results_filepath, parseiteraion_results_filename, current_timestamp, 5)
#
# update_jobvacancies_lat_lon_fc(Database_pracujpl=oDatabasePracujpl)
# oDatabasePracujpl.step05_commit_things()
# print("OK: Обновление координат завершено.")