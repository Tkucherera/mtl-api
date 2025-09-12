"""
author: Tinashe Kucherera
date: 2024-06-20
description: Logger configuration for the application.
"""

import logging
import sys
import os
from logging.handlers import RotatingFileHandler


# Ensure the logs directory exists
if not os.path.exists('logs'):
    os.makedirs('logs')

# Configure logging
# we need a an activity log for the application
# we also need to log errors and exceptions

# we will log to a file and to the console

# Activity logger for successful CRUD actions
activity_logger = logging.getLogger('activity')
activity_logger.setLevel(logging.INFO)
activity_handler = RotatingFileHandler(
    'logs/activity.log', maxBytes=5*1024*1024, backupCount=5
)
activity_formatter = logging.Formatter(
    '%(asctime)s - %(levelname)s - %(message)s'
)
activity_handler.setFormatter(activity_formatter)
activity_logger.addHandler(activity_handler)

# Stdout logger for general info/debug
stdout_logger = logging.getLogger('stdout')
stdout_logger.setLevel(logging.INFO)
stdout_handler = logging.StreamHandler(sys.stdout)
stdout_formatter = logging.Formatter(
    '%(asctime)s - %(levelname)s - %(message)s'
)
stdout_handler.setFormatter(stdout_formatter)
stdout_logger.addHandler(stdout_handler)

# Stderr logger for errors and exceptions
error_logger = logging.getLogger('error')
error_logger.setLevel(logging.ERROR)
error_handler = RotatingFileHandler(
    'logs/error.log', maxBytes=5*1024*1024, backupCount=5
)
error_formatter = logging.Formatter(
    '%(asctime)s - %(levelname)s - %(message)s'
)
error_handler.setFormatter(error_formatter)
error_logger.addHandler(error_handler)

stderr_handler = logging.StreamHandler(sys.stderr)
stderr_handler.setFormatter(error_formatter)
error_logger.addHandler(stderr_handler)

# Make sure to log uncaught exceptions
def handle_exception(exc_type, exc_value, exc_traceback):
    if issubclass(exc_type, KeyboardInterrupt):
        sys.__excepthook__(exc_type, exc_value, exc_traceback)
        return
    error_logger.error("Uncaught exception", exc_info=(exc_type, exc_value, exc_traceback))
sys.excepthook = handle_exception

# initialize the loggers to create log files if they don't exist
activity_logger.info("Activity logger initialized.")
stdout_logger.info("Stdout logger initialized.")
error_logger.error("Error logger initialized.")

# Set up a root logger to capture all logs
root_logger = logging.getLogger()
root_logger.setLevel(logging.DEBUG)

# Add handlers to root logger to log everything to a separate file
all_handler = RotatingFileHandler(
    'logs/all.log', maxBytes=10*1024*1024, backupCount=5
)
all_formatter = logging.Formatter(
    '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
all_handler.setFormatter(all_formatter)
root_logger.addHandler(all_handler)

# Example usage:
# activity_logger.info("This is an activity log message.")
# stdout_logger.info("This is a standard output log message.")
# error_logger.error("This is an error log message.")
