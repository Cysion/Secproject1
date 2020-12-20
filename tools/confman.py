import json
import os
import logging
DEFAULT_PATH = "/home/kevin/Projekt/env/Secproject1/conf/"


def get_lang(path=DEFAULT_PATH + "lang.json", sections = []) -> dict:
    """Returns language file as dict, returns dict if successful, returns Exception is failed
    Keyword arguments:
    path = path to lang.json file, defaults to "conf/lang.json", useful for using multiple language files
    sections = list of sections in the json file to return, ex ["universal", "home"]
               which can somewhat mimize memory usage for large language files,
               defaults to all sections"""
    langdict = {}
    try:
        with open(path) as langfile:
            loaddict = json.load(langfile)
            assert type(sections) == type([])
            if sections:
                for section in sections:
                    langdict[section] = loaddict[section]
            else:
                langdict = loaddict
    except AssertionError as e:
        return e

    except KeyError as e:
        return e

    except FileNotFoundError as e:
        return e

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
            loaddict = json.load(conffile)
            assert type(sections) == type([])
            if sections:
                for section in sections:
                    confdict[section] = loaddict[section]
            else:
                confdict = loaddict

    except AssertionError as e:
        return e

    except KeyError as e:
        return e

    except FileNotFoundError as e:
        return e

    return confdict
