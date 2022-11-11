"""
RilowBot
-----------------------------
File: config.py
Date: 2022-11-08
Updated: 2022-11-08

Helper module which allows for easy config management using json.
"""
import json
import logging
import os
from typing import Any, Optional

class AttrDict(dict):
    def __getattr__(self, attr):
        return self.__getitem__(attr)
    
    def __setattr__(self, attr, val):
        return self.__setitem__(attr, val)
    
    def __delattr__(self, attr):
        return self.__delitem__(attr)

CONFIG_RESERVED_ATTRIBUTES = {"filepath", "_data", "_savecount", "_logger"}
SAVEABLE_CONFIG_MAX_SAVECOUNT = 1

class Config:
    @classmethod
    def fromData(cls, filepath: str, data: dict) -> None:
        c = cls(filepath, load=False)
        c._data = data
        return c

    def __init__(self, filepath: str, *, load: bool=True):
        self._logger = logging.getLogger(__name__)
        self._data = {}

        self.filepath = filepath

        if load:
            self._load()
    
    def __repr__(self):
        return f"<Config({repr(self._data)})>"

    def _load(self) -> None:
        """
        Internal method that loads the config data from disk.
        """
        if not os.path.exists(self.filepath):
            return self._logger.warn(f"File '{self.filepath}' does not exist")
        
        with open(self.filepath) as f:
            data = json.load(f)
        
        self._data = data

    def _save(self) -> None:
        """
        Internal method to save the config file to disk.
        """
        with open(self.filepath, "w+") as f:
            json.dump(self._data, f, indent=4, sort_keys=True)

    def __getattr__(self, attr):
        return self._data[attr]

    def __setattr__(self, attr, val):
        if attr in CONFIG_RESERVED_ATTRIBUTES:
            self.__dict__[attr] = val
        else:
            self._data[attr] = val

    def __getitem__(self, item):
        return self._data[item]

    def __setitem__(self, item, val):
        self._data[item] = val
    
    def __delitem__(self, item):
        del self._data[item]

    def get(self, key: str, default: Optional[Any]=None) -> Any:
        """
        Attempts to get the key from the config,
        if it doesn't exist returns default instead.
        """
        return self._data.get(key, default)

if __name__ == "__main__":
    data = {
        "hello": "world",
        "test": True,
    }

    c = Config.fromData("config.json", data)
    print(c)
    print(c.hello)
    print(c["test"])

    
    c.test2 = False
    print(c)
    print(c.test2)