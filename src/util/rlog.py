"""
RilowBot
-----------------------------
File: rlog.py
Date: 2022-11-10
Updated: 2022-11-10

Helper logging module to help with logging,
does NOT replace the builtin logging python module.
"""
from datetime import datetime
import logging
import os
import platform
import sys
import traceback

LOG_DIR = os.path.join(os.getcwd(), "logs")
CURRENT_LOG = os.path.join(LOG_DIR, "current.log")

LOGGING_LEVEL_STREAM = logging.INFO
LOGGING_LEVEL_FILE = logging.DEBUG

LOGGING_FORMAT = "[%(asctime)s] [%(levelname)s] [%(filename)s:%(lineno)d] %(message)s"
LOGGING_DT_FORMAT = "%H:%M:%S"
LOGGING_FILE_NAME_FORMAT = "%Y-%m-%d"

LOGGING_NON_DISCORD_FILTER = lambda r: not r.name.startswith("discord")

def _get_file_creation_date(path: str) -> datetime:
    """
    Attempts to get the creation date of a file,
    Falls back to the last modified date if not available.
    See http://stackoverflow.com/a/39501288/1709587
    """
    if platform.system() == "Windows":
        delta = os.path.getctime(path)
    else:
        stat = os.stat(path)
        try:
            delta = stat.st_birthtime
        except AttributeError:
            # We're probably on Linux. No easy way to get creation dates here,
            # so we'll settle for when its content was last modified.
            delta = stat.st_mtime
    
    return datetime.fromtimestamp(delta)

def _touch(filepath: str) -> None:
    """
    Touches a file, creating it.

    NOTE: This file does not check if a file
    exists or not before touching it, using this on
    an already existing file will clear all of 
    it's content.
    """
    with open(filepath, "w+"):
        pass

def _rename_file_if_exists(filepath: str, *, suffix: str="") -> None:
    """
    Renames a file if it exists to the current 
    date using `LOGGING_FILE_NAME_FORMAT`
    """
    

_logging_initialized = False

def init_logging() -> None:
    """
    Initialize logging.
    """
    global _logging_initialized

    if _logging_initialized: return
    _logging_initialized = True

    # Do initializing here.

    if not os.path.exists(LOG_DIR):
        os.mkdir(LOG_DIR)
    
    # If it doesn't exist then we don't need to
    # do any renaming.
    if not os.path.exists(CURRENT_LOG):
        _touch(CURRENT_LOG)

    else:
        # Rename the file.
        # Get data
        created = _get_file_creation_date(CURRENT_LOG).strftime(LOGGING_FILE_NAME_FORMAT)
        newpath = os.path.join(LOG_DIR, f"{created}.log")

        # If the new file path already exists, append to it.
        if os.path.exists(newpath):
            with open(CURRENT_LOG) as f:
                content = f.read()

            with open(newpath, 'a') as f:
                f.write(content)
            
        else:
            # Rename the file
            os.rename(CURRENT_LOG, newpath)

        # Touch the file, note that this also removes content
        # in the case of appending data.

        # Create a new file in it's place with the old name.
        _touch(CURRENT_LOG)
    

    formatter = logging.Formatter(LOGGING_FORMAT, LOGGING_DT_FORMAT)
    
    # Stream
    streamHandler = logging.StreamHandler(sys.stderr)
    streamHandler.setLevel(LOGGING_LEVEL_STREAM)
    streamHandler.addFilter(LOGGING_NON_DISCORD_FILTER)
    streamHandler.setFormatter(formatter)

    # current.log
    fileHandler = logging.FileHandler(CURRENT_LOG)
    fileHandler.setLevel(LOGGING_LEVEL_FILE)
    fileHandler.addFilter(LOGGING_NON_DISCORD_FILTER)
    fileHandler.setFormatter(formatter)

    logging.basicConfig(
        level=logging.DEBUG,
        handlers=[fileHandler, streamHandler],
    )

def format_exception(exc: Exception) -> str:
    """
    Formats an exceptions traceback for output.
    """
    return "\n".join(traceback.format_exception(exc))

if __name__ == "__main__":
    init_logging()

    import discord
    from discord.ext import commands

    logger = logging.getLogger(__name__)
    logging.info("test")