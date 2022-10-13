import json


default_locale = "en-us"
cached_strings = {}


def refresh():
    print("Refreshing..")
    global cached_strings
    with open(f"strings/{default_locale}.json") as s:
        cached_strings = json.load(s)

def gettext(name):
    return cached_strings[name]


refresh()
