import os
import datetime

TIMESTAMP_FORCURRENTITERATION_str = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")

FOLDERNAME_RESULTS_ALL = "data_results"
FOLDERNAME_DAILYDATA = "daily_results"

FOLDERPATH_RESULTS_ALL = os.path.join(os.getcwd(), FOLDERNAME_RESULTS_ALL)
FOLDERPATH_DAILYDATA = os.path.join(FOLDERPATH_RESULTS_ALL, FOLDERNAME_DAILYDATA)

os.makedirs(FOLDERPATH_RESULTS_ALL, exist_ok=True)
os.makedirs(FOLDERPATH_DAILYDATA, exist_ok=True)

ALPHABET_POLISH_str = "AĄBCĆDEĘFGHIJKLMNOÓPRSŚTUWYZŹŻaąbcćdeęfghijklmnoóprsśtuwyzźż0123456789"
MATHNUMBERS_str = "0123456789"

# SETTINGS NOMINATIM
NOMINATIM_IS_USE_PUBLIC_API = False
NOMINATIM_PRIVATE_API_URL = "http://localhost:8080/search"
NOMINATIM_PUBLIC_API_URL = "https://nominatim.openstreetmap.org/search"
NOMINATIM_URL = NOMINATIM_PUBLIC_API_URL if NOMINATIM_IS_USE_PUBLIC_API else NOMINATIM_PRIVATE_API_URL# Nominatim api server address
NOMINATIM_PAUSE_IF_PUBLIC_API_SECONDS = 3

# GET FILENAMES OUTPUT
def get_databasefilename_fc(platformname_str = "pracujpl"):
    return f"jobs_{platformname_str}.sqlite"#"pracujpl_jobs.sqlite"

def get_htmlmapfilename_fc(platformname_str = "pracujpl"):
    return f"mapvacancies_{platformname_str}.html"#"mapvacancies_pracujpl.html"

def get_dailyresultsfilename_fc(platformname_str = "pracujpl"):
    return f"dailyjobs_{platformname_str}_{get_timestamp()}.json"


# GET FILEPATHS OUTPUT
def get_databasefilepath_fc(platformname_str):
    return os.path.join(FOLDERPATH_RESULTS_ALL, get_databasefilename_fc(platformname_str))

def get_htmlmapfilepath_fc(platformname_str):
    return os.path.join(FOLDERNAME_RESULTS_ALL, get_htmlmapfilename_fc(platformname_str))

def get_dailyresultsfilepath_fc(platformname_str):
    return os.path.join(FOLDERPATH_DAILYDATA, get_dailyresultsfilename_fc(platformname_str))

# OTHER

def get_timestamp():
    return TIMESTAMP_FORCURRENTITERATION_str
    #return datetime.datetime.now().strftime("%Y%m%d_%H%M%S")

def get_jsonfilename():
    return f"jobs_{get_timestamp()}.json"

# def get_dailyresultsfilename_fc(portalname_str):
#     return os.path.join(FOLDERPATH_DAILYDATA, f"{portalname_str}_{get_jsonfilename()}")

def get_filenamefrompath(path_str):
    return os.path.basename(path_str)