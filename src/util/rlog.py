"""
RilowBot
-----------------------------
File: rlog.py
Date: 2022-11-07
Updated: 2022-11-08

Helper logging module to help with logging,
does NOT replace the builtin logging python module.
"""
from datetime import datetime
import logging
import os
import platform
import sys
import traceback
from typing import Callable, Optional

LOG_DIR = os.path.join(os.getcwd(), "logs")
CURRENT_LOG = os.path.join(LOG_DIR, "current.log")
LOGGING_LEVEL = logging.DEBUG
LOGGING_FORMAT_STR = "[%(asctime)s] [%(levelname)s] [%(filename)s:%(lineno)d] %(message)s"

# This string is used to format the filename of logs.
_day_time_format = "%Y-%m-%d"

# For except hook.
_orig_sys_excepthook = sys.excepthook

def _get_file_creation_date(path: str) -> datetime:
    """
    Attempts to get the creation date of a file,
    Falls back to last modified date if not available.
    See http://stackoverflow.com/a/39501288/1709587
    """
    if platform.system() == "Windows":
        return datetime.fromtimestamp(os.path.getctime(path))
    else:
        stat = os.stat(path)
        try:
            return datetime.fromtimestamp(stat.st_birthtime)
        except AttributeError:
            # We're probably on Linux. No easy way to get creation dates here,
            # so we'll settle for when its content was last modified.
            return datetime.fromtimestamp(stat.st_mtime)

_logging_initialized = False
def init_logging(*, create_log_dir: bool=True, create_log_file: bool=True) -> None:
    """
    Initialize logging module.
    This should only be called once.
    """
    global _logging_initialized
    
    if _logging_initialized: return

    _logging_initialized = True

    if not os.path.exists(LOG_DIR) and create_log_dir:
        os.mkdir(LOG_DIR)

    if os.path.exists(CURRENT_LOG) and create_log_file:
        # A current log was already in progress, save it using the last
        # modified date.
        created = _get_file_creation_date(CURRENT_LOG)
        format = created.strftime(_day_time_format)
        path = os.path.join(LOG_DIR, f"{format}.log")

        # Loop through and add a number onto the log, this means that each run of the current day will contain its own
        # log file and we will not overwrite any logs, but with all loops there needs to be an exit case so that
        # it does not loop forever so thats why we check for i_max.
        i = 0
        i_max = 9999
        while os.path.exists(path):
            i += 1
            if i >= i_max:
                raise RuntimeError(f"Max index reached when looking for log file name. Please delete/rename the file '{CURRENT_LOG}'")
            path = os.path.join(LOG_DIR, f"{format} ({i}).log")
        
        # Rename the current log to the new log.
        os.rename(CURRENT_LOG, path)

    # Setup file logging.
    filename = None
    if os.path.exists(LOG_DIR) and create_log_file:
        assert not os.path.exists(CURRENT_LOG)

        with open(CURRENT_LOG, "w+"):
            pass
    
        filename = CURRENT_LOG

    # Setup basic config.
    logging.basicConfig(
        format=LOGGING_FORMAT_STR,
        filename=filename,
        level=LOGGING_LEVEL
    )
    
    # Setup excepthook
    sys.excepthook = _rlog_excepthook

    # Done initializing.
    return

def finalize_logging() -> None:
    """
    This simply removes the exception hook, doesn't really finalize lol. 
    Maybe needs a better name (should it even be a function?)
    """
    sys.excepthook = _orig_sys_excepthook

def _rlog_excepthook(type_, exc, tb) -> None:
    """
    Internal system hook which gets called in the event of
    an unhandled exception. This does not work if `finalize_logging()` is called.
    """
    return _log_exception("Unhandled exception!!", exc, level=logging.CRITICAL)

def _get_source_name(source: Callable) -> str:
    if hasattr(source, "__qualname__") and source.__qualname__ is not None:
        source = source.__qualname__
    else:
        source = str(source)
    
    return source.replace("<locals>.", "")

def _log(msg: str, level: int) -> None:
    """
    Internal helper function to log a message.
    """
    logging.log(level, msg)

def _log_exception(msg: str, exc: Exception, *, level=logging.ERROR) -> None:
    """
    Log an exception.
    """
    # TODO: FORMAT EXC
    tb = "\n".join(traceback.format_exception(exc))
    msg += f"\n{tb}"

    _log(msg, level=level)

def log(msg: str, *, source: Optional[Callable]=None, level: int=logging.INFO, exc: Optional[Exception]=None) -> None:
    """
    Logs a message with an optional source.
    """
    if source:
        source = _get_source_name(source)
        msg = f"[{source}] {msg}"
    
    if exc is not None:
        _log_exception(msg, exc, level=level)
    else:
        _log(msg, level)

def debug(msg: str, *, source: Optional[Callable]=None) -> None:
    """
    Log a message at the debug level.
    """
    log(msg, level=logging.DEBUG, source=source)

def info(msg: str, *, source: Optional[Callable]=None) -> None:
    """
    Log a message at the info level.
    """
    log(msg, level=logging.INFO, source=source)

def warn(msg: str, *, source: Optional[Callable]=None) -> None:
    """
    Log a message at the warn level.
    """
    log(msg, level=logging.WARN, source=source)

def error(msg: str, *, source: Optional[Callable]=None) -> None:
    """
    Log a message at the error level.
    """
    log(msg, level=logging.ERROR, source=source)

def critical(msg: str, *, source: Optional[Callable]=None) -> None:
    """
    Log a message at the critical level.
    """
    log(msg, level=logging.CRITICAL, source=source)

def exception(msg: str, exc: Optional[Exception]=None, *, level=logging.ERROR, source: Optional[Callable]=None) -> None:
    """
    Log an exception with a message to the error level.
    """
    if exc is None:
        exc = sys.exc_info()[1]
    
    _log_exception(msg, exc, level=level, source=source)

if __name__ == "__main__":
    d = _get_file_creation_date(os.path.join(os.getcwd(), __file__)).strftime(_day_time_format)
    print(d)

    init_logging(create_log_dir=False, create_log_file=False)

    log("THIS IS A TEST 123", source=__name__)