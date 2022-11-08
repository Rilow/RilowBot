"""
RilowBot
-----------------------------
File: lang.py
Date: 2022-11-07
Updated: 2022-11-07

Allows for language translations, instead of hard coding strings
instead use a string identifier (signified by #) with the 
translator and it will provide the translated string using the
currently active language.
"""
import ctypes
import locale
import os
from typing import Dict

import rlog

def _get_default_lang() -> str:
    """
    Returns the currently running machines default language code.
    """
    try:
        # Use `GetUserDefaultUILanguage()` when available because
        # it's more accurate.
        windll = ctypes.windll.kernel32
        return locale.windows_locale[windll.GetUserDefaultUILanguage()]
    except:
        # NOTE: This is sometimes not accurate as this will return the language of
        # the computers location and not the active UI Language being used
        # on the OS
        return locale.getdefaultlocale()[0]

def _parse(s: str) -> Dict[str, str]:
    """
    Internal function which parses a string and
    creates a dictionary map from its data using
    my own lang file parser.
    """
    lines = s.strip().splitlines()

    data = {}

    for line in lines:
        if line.startswith("//"): continue
        if "=" not in line: continue

        split = line.split("=")

        if len(split) > 2:
            key = split[0]
            val = "=".join(split[1:])
        else:
            key = split[0]
            val = split[1]
        
        key = key.strip().replace(" ", "_")
        val = val.strip()
        data[key] = val
    
    return data

class Lang:
    @classmethod
    def fromData(cls, data: Dict[str, str]) -> "Lang":
        """
        Create a lang object from data.
        """
        # Use data as the lang code.
        l = cls("data", load=False)
        l._data = data
        return l

    def __init__(self, lang: str=None, *, load: bool=True):
        self._data = {}
        
        self.setLang(lang)
    
    def setLang(self, lang: str, *, load: bool=True) -> None:
        """
        Set the language to use.
        """
        if lang is None:
            lang = _get_default_lang()

        if load:
            self._load(lang)
        
        self.lang = lang

    def _load(self, lang) -> None:
        """
        Internal function that loads the lang dictionary
        from file.
        """
        def _check_path(p):
            if not os.path.exists(p):
                rlog.warn(f"Path '{p}' does not exist.", source=_check_path)
                return False
            return True

        langDir = os.path.join(os.getcwd(), "lang")
        if not _check_path(langDir): return

        langDir = os.path.join(langDir, f"{lang}.lang")
        if not _check_path(langDir): return
        
        with open(langDir) as f:
            content = f.read()
        
        data = _parse(content)

        # Wait until after everything finishes (no errors) before
        # setting the lang dict, as setting it to an empty dict
        # or an unfinished dict could result in strings not being
        # displayed correctly.
        self._data = data

    def translateKey(self, key: str) -> str:
        """
        Translates a key using the current language and
        returns the translated key.
        """
        # Return back the key by default
        return self._data.get(key, key)
    
    def translateKeyFormat(self, key: str, *args, **kwargs) -> str:
        """
        Translates a key using the current language and formats it
        if the translation is found. Returns the translated key + format.
        """
        s = self.translateKey(key)

        # Could not translate, so don't format.
        if s == key:
            return key
        
        return s.format(*args, **kwargs)


if __name__ == "__main__":
    rlog.init_logging(create_log_dir=False, create_log_file=False)

    l = Lang()

    d = _parse("""
//comment
#test_key=3232
#test_key2 = 3232
#test key3 = this is a = test lol
""")

    print(d)