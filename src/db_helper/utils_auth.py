# Imports
from .utils_firebase import *

# from .utils_email import *
from .utils_storage import *
import inspect
import coloredlogs, logging
import sys

# Main Vars
logger = logging.getLogger(__name__)
coloredlogs.install(level="DEBUG", logger=logger)

# Main Functions


def generate_error(err):
    caller_function = inspect.currentframe().f_back.f_code.co_name
    line_number = inspect.currentframe().f_back.f_lineno
    error_str = f"{caller_function}:at line {line_number}:"
    logger.error(error_str)
    print(str(err), "\n-------------------END---------------------")


# Driver Code
