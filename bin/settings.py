import os
import datetime
import logging
import sys


TIMESTAMP_FORCURRENTITERATION_str = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")

FOLDERNAME_RESULTS_ALL = "results"
FOLDERNAME_DAILYDATA = "results_daily"

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

# =============================================================================
# SETTINGS LOGGING START
# =============================================================================
FOLDERNAME_LOGS = "logs"
LOGS_DIR = os.path.join(FOLDERPATH_RESULTS_ALL, FOLDERNAME_LOGS)
MAX_LOG_FILES = 10

os.makedirs(LOGS_DIR, exist_ok=True)

# Формируем имя лог-файла по текущей дате и времени
timestamp_str = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
log_filename = f"log_{timestamp_str}.txt"
LOG_FILEPATH = os.path.join(LOGS_DIR, log_filename)

# Удаляем старые логи, если файлов больше MAX_LOG_FILES
log_files = sorted(
    [f for f in os.listdir(LOGS_DIR) if f.startswith("log_") and f.endswith(".txt")],
    key=lambda f: os.path.getmtime(os.path.join(LOGS_DIR, f))
)
while len(log_files) >= MAX_LOG_FILES:
    oldest_file = log_files.pop(0)
    os.remove(os.path.join(LOGS_DIR, oldest_file))


# Настройка логгера
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] - %(message)s',
    handlers=[
        logging.FileHandler(LOG_FILEPATH, encoding='utf-8'),
        logging.StreamHandler(sys.stdout)
    ]
)

def get_logger_fc(name_str: str = None) -> logging.Logger:
    return logging.getLogger(name_str) if name_str else logging.getLogger()

# =============================================================================
# SETTINGS LOGGING FINISH
# =============================================================================


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

def update_filename_with_suffix(filename_str, suffix_str):
    '''
    file1.txt -> file1_suffix1.txt
    '''
    if not suffix_str:
        return filename_str
    filename_base, filename_ext = os.path.splitext(filename_str)
    new_filename_str = f"{filename_base}{suffix_str}{filename_ext}"
    return new_filename_str
def update_filepath_with_suffix(filepath_str, suffix_str, to_update_old_filename_str = None):
    '''
    C:\folder1\file1.txt -> C:\folder1\file1_suffix1.txt
    '''
    if not suffix_str:
        if to_update_old_filename_str:
            # C:\folder1\file1.txt -> C:\folder1\newfilename1.txt
            return os.path.join(os.path.dirname(filepath_str), to_update_old_filename_str)
        else:
            # C:\folder1\file1.txt -> C:\folder1\file1.txt
            return filepath_str

    if not to_update_old_filename_str:
        # file1.txt -> newfilename1_suffix1.txt
        filename_str = os.path.basename(filepath_str)
        new_filename_str = update_filename_with_suffix(filename_str, suffix_str)
    else:
        # file1.txt -> file1_suffix1.txt
        new_filename_str = update_filename_with_suffix(to_update_old_filename_str, suffix_str)
    return os.path.join(os.path.dirname(filepath_str), new_filename_str)


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