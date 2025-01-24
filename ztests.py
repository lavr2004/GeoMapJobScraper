import settings

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
print(restofstring)