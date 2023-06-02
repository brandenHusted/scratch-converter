import logging

# DEBUG, INFO, WARNING, ERROR, CRITICAL
logging.basicConfig(level=logging.INFO)


logger = logging.getLogger("my")
logger.setLevel(logging.DEBUG)

# get flask built-in logger
werkzeug_logger = logging.getLogger('werkzeug')
# only log higher than warning level
werkzeug_logger.setLevel(logging.WARNING)
