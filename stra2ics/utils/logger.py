import logging  # Importing the standard Python logging module
import os  # Importing the standard Python os module for operating system interactions

from rich.logging import RichHandler

# Importing the RichHandler from rich, a library for rich text and beautiful formatting in the terminal
from stra2ics.utils.namespace import NAMESPACE

# Set up a logger with the name of the current module.
# This will allow us to track where logged messages are coming from.
logger = logging.getLogger(__name__)

# Create a handler for logging to the terminal, using the RichHandler from the rich library for nicer formatting.
shell_handler = RichHandler()

# If the log folder does not exist, create it.
if not os.path.exists(NAMESPACE.directory_log):
    os.makedirs(NAMESPACE.directory_log)

# Create a handler for logging to a file.
file_handler = logging.FileHandler(NAMESPACE.filename_debug_log)

# Set the log levels for the logger and the two handlers.
# These determine the lowest severity of messages that will be handled.
logger.setLevel(NAMESPACE.logger_level)
shell_handler.setLevel(NAMESPACE.logger_shell_level)
file_handler.setLevel(NAMESPACE.logger_file_level)

# Create formatters with the format strings from the NAMESPACE.
# These determine how the log messages will be formatted.
shell_formatter = logging.Formatter(NAMESPACE.logger_shell_fmt)
file_formatter = logging.Formatter(NAMESPACE.logger_file_fmt)

# Attach the formatters to the handlers.
shell_handler.setFormatter(shell_formatter)
file_handler.setFormatter(file_formatter)

# Attach the handlers to the logger.
# This means that whenever we use this logger, the log messages will be sent to both handlers.
logger.addHandler(shell_handler)
logger.addHandler(file_handler)
