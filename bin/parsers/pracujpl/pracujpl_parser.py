from bin import settings as settings_obj
from bs4 import BeautifulSoup
import json

def recognition_JSON_in_HTML_area_fc(html_content):
    soup = BeautifulSoup(html_content, 'html.parser')
    script_tag = soup.find('script', {'id': '__NEXT_DATA__'})
    if not script_tag:
        raise ValueError("ER: Тег <script id='__NEXT_DATA__'> не найден")
    json_data_dc = json.loads(script_tag.string)
    return json_data_dc

# MAIN ENTRY FUNCTION
def parse_address_in_warsaw_from_url_fc(url):
    #https://www.pracuj.pl/praca/menedzer-ds-merchandisingu-i-sprzedazy-odziez-sportowa-i-akcesoria-warszawa-konwiktorska-6,oferta,1003811905
    #match = re.search(r'/praca/.*?-(.+),oferta,\d+$', url)

    country = "Poland"
    locality = None
    street = None
    building = None

    needpart_str = parse_addressneedpart_from_url_fc(url)
    if not needpart_str:
        return locality, street, building

    building, restofstring = parse_building_from_url_fc(needpart_str)
    if building is None:
        return locality, street, building

    street, restofstring = parse_street_from_url_warszawa_fc(restofstring)

    if restofstring:
        locality, restofstring = parse_lastword_from_url_fc(restofstring)
    else:
        locality = "Warszawa"

    return locality, street, building


# SECONDARY FUNCTIONS
def parse_addressneedpart_from_url_fc(url):
    if not url:
        return None

    needpart_str = url.split(',')[0]
    if not needpart_str:
        return None

    needpart_str = needpart_str.split('/')[-1]
    if not needpart_str:
        return None

    address_parts = needpart_str.split('-')
    if len(address_parts) < 4:
        return None

    return needpart_str

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

        if l[i].lower() not in settings_obj.ALPHABET_POLISH_str:
            r += l[i]
            lastindex = i
            continue

        if not startofnumberfound:
            if l[i] in settings_obj.MATHNUMBERS_str:
                startofnumberfound = True
            r += l[i]
            lastindex = i
            continue
        else:
            if l[i] not in settings_obj.MATHNUMBERS_str:
                break
            lastindex = i
            r += l[i]

    restofstring = needpart_str[:lastindex]
    if r:
        r = r.strip()
        r = r[::-1]

    if r[0] not in settings_obj.MATHNUMBERS_str:
        r = None

    return r, restofstring


def parse_street_from_url_warszawa_fc(restofurl_str):
    if not restofurl_str:
        return None, None

    r = ""

    l = restofurl_str.split("-warszawa-")
    if len(l) > 1:
        r = " ".join(l[1:])
        r = r.replace("-"," ")
        r = r.title()
        return r, None
    else:
        #take one last word instead
        r, restofurl_str = parse_lastword_from_url_fc(restofurl_str)
        r = r.replace("-"," ")
        r = r.title()
        return r, restofurl_str

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