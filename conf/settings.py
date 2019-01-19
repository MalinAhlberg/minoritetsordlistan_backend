""" Settings! """
import json
import os

import utils.errors as errors

path = os.path.dirname(os.path.abspath(__file__))
conf = json.load(open(os.path.join(path, 'settings.json'), encoding='utf-8'))
default_conf = json.load(open(os.path.join(path, 'settings_default.json'), encoding='utf-8'))


karp = 'https://ws.spraakbanken.gu.se/ws/karp/v5'
ok_status = 'granskat och klart'

def get_modes():
    modes = set(conf.keys())
    for mode in default_conf.keys():
        modes.add(mode)
    modes.discard('default')
    return modes


def lookup(key):
    return conf.get(key, default_conf[key])


def get(key, mode="default", default=None):
    if key in conf.get(mode, {}):
        return conf[mode][key]
    if key in conf.get('default'):
        return conf['default'][key]
    if key in default_conf.get(mode, {}):
        return default_conf[mode][key]
    if key in default_conf.get('default', {}):
        return default_conf['default'][key]
    if default is not None:
        return default
    raise errors.ConfigurationError(key, mode)


def get_first_letter(lang, mode):
    if lang in get('first_letter', mode, {}):
        return get('first_letter', mode)[lang]
    return get('standard_first_letter', default='a')
