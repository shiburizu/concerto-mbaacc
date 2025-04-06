import logging, json, sys, os

if hasattr(sys, '_MEIPASS'):
    LOC_STRINGS = json.load(open(os.path.join(sys._MEIPASS,'ui\\strings.json'),encoding='utf-8'))
else:
    LOC_STRINGS = json.load(open('ui\\strings.json',encoding='utf-8'))

#TODO LOC_STRINGS
#Map Option combo boxes to localized choices, including online menu
#Concerto.kv ResourceScreen Button Labels
#CCCaster Error LOC_STRINGS in mbaacc.py
#discord presences - maybe dont?
current_lang = "EN"

def localize(s,v=None):
    s = s.upper()
    if s in LOC_STRINGS:
        if current_lang in LOC_STRINGS[s]:
            if v:
                return LOC_STRINGS[s][current_lang] % v
            else:
                return LOC_STRINGS[s][current_lang]
    logging.warning('ConcertoLang: MISSING "%s" (%s)' % (s,current_lang)) 
    return 'MISSING "%s" (%s)' % (s,current_lang)