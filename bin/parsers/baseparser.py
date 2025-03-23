import bin.logic.parser
import bin.logic.web
import bin.logic.filesystem
import bin.logic.nominatim
import bin.settings as settings

import time
import random


class BaseParser:
    PLATFORMNAME_STR = None
    URL_START_STR = None
    HEADERS = {
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36',
    }

    backuped_original_results_filename_str = ""

    def __init__(self, platformname_str, url_start_str):
        self.PLATFORMNAME_STR = platformname_str
        self.URL_START_STR = url_start_str
        self.database_filepath_str = settings.get_databasefilepath_fc(self.PLATFORMNAME_STR)
        self.results_filepath_str = settings.get_dailyresultsfilepath_fc(self.PLATFORMNAME_STR)
        self.results_filename_str = settings.get_filenamefrompath(self.results_filepath_str)
        self.backuped_original_results_filename_str = self.results_filename_str
        self.current_timestamp_str = settings.get_timestamp()

    def update_results_filepath_fc(self, pagenumber_int = None, filterslist_lst = None):
        suffix_str = ""
        if pagenumber_int:
            suffix_str += f"_{pagenumber_int}"
        if filterslist_lst:
            for i in filterslist_lst:
                if i:
                    suffix_str += f"_{i}"

        self.results_filename_str = settings.update_filename_with_suffix(self.backuped_original_results_filename_str, suffix_str)
        self.results_filepath_str = settings.update_filepath_with_suffix(self.results_filepath_str, suffix_str, self.backuped_original_results_filename_str)

    def _fetch_html(self, pagenumber_int = None) -> (str ,int):
        '''
        return: html_str, status_code_int
        '''
        if not pagenumber_int:
            return bin.logic.web.get_html_response_from_url(self.URL_START_STR, headers_dc=self.HEADERS)

        cookies = {

        }
        params = {
            'pn': f'{pagenumber_int}',
        }
        pause_seconds_int = random.randint(3, 7)
        print(f"OK: Technical pause between requests - {pause_seconds_int} seconds")
        time.sleep(pause_seconds_int)
        return bin.logic.web.get_html_response_from_url(self.URL_START_STR, headers_dc=self.HEADERS, params_dc=params, cookies_dc=cookies)

    def parse(self, pagenumber_int=0) -> None:
        '''dont return nothing, just write collected data into the database'''
        raise NotImplementedError("Subclasses must implement the 'parse' method")

    def update_coordinates(self) -> None:
        raise NotImplementedError("Subclasses must implement the 'update_coordinates' method")

    # def commit_changes(self) -> None:
    #     self.oDatabase.step05_commit_things()