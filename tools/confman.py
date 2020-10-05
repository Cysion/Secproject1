import json

DEFAULT_PATH = "conf"


def get_lang(path=DEFAULT_PATH + "lang.json", sections = []) -> dict:
    """Returns language file as dict
    Keyword arguments:
    path = path to lang.json file, defaults to "conf/lang.json", useful for using multiple language files
    sections = list of sections in the json file to return, ex ["universal", "home"] 
               which can somewhat mimize memory usage for large language files"""
    langdict = {}
    try:
        with open(path) as langfile:
            langdict = json.load(langfile)
            assert type(sections) == type([])
            for section in sections:

    except AssertionError:

        
    return langdict


def get_conf(path=DEFAULT_PATH + "conf.json", sections = []):
    """Returns config file as dict
    path = path to conf.json file, defaults to "conf/conf.json", useful for using multiple language files
    sections = list of sections in the json file to return, ex ["logs", "misc"] 
               which can somewhat mimize memory usage for large config files,
               but mostly to make it easier to only use one section of the config"""
    confdict = {}
    try:
        with open(path) as conffile:
            confdict = json.load(conffile)
            assert type(sections) == type([])
            for section in sections:

    except AssertionError:
        
    return confdict