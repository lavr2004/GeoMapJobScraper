import os
import datetime

FOLDERNAME_RESULTS_ALL = "data_results"
FOLDERNAME_DAILYDATA = "daily_results"

FOLDERPATH_RESULTS_ALL = os.path.join(os.getcwd(), FOLDERNAME_RESULTS_ALL)
FOLDERPATH_DAILYDATA = os.path.join(FOLDERPATH_RESULTS_ALL, FOLDERNAME_DAILYDATA)

os.makedirs(FOLDERPATH_RESULTS_ALL, exist_ok=True)
os.makedirs(FOLDERPATH_DAILYDATA, exist_ok=True)

ALPHABET_POLISH_str = "AĄBCĆDEĘFGHIJKLMNOÓPRSŚTUWYZŹŻaąbcćdeęfghijklmnoóprsśtuwyzźż0123456789"
MATHNUMBERS_str = "0123456789"

def get_databasefilename_fc(platformname_str = "pracujpl"):
    return f"{platformname_str}_jobs.sqlite"#"pracujpl_jobs.sqlite"

def get_databasefilepath_fc(platformname_str):
    return os.path.join(FOLDERPATH_RESULTS_ALL, get_databasefilename_fc(platformname_str))

def get_timestamp():
    return datetime.datetime.now().strftime("%Y%m%d_%H%M%S")

def get_jsonfilename():
    return f"jobs_{get_timestamp()}.json"

def get_jsonresultsfilepath(portalname_str):
    return os.path.join(FOLDERPATH_DAILYDATA, f"{portalname_str}_{get_jsonfilename()}")

def get_filenamefrompath(path_str):
    return os.path.basename(path_str)