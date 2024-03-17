from sys import stderr

from loguru import logger

from config import LOG_TO_FILE


logger.remove()
logger.add(
    stderr, 
    format='<white>{time:HH:mm:ss}</white>'
        ' | <bold><level>{level: <7}</level></bold>'
        ' | <cyan>{line: <3}</cyan>'
        ' | <white>{message}</white>'
)

if LOG_TO_FILE:
    logger.add('logger.log')
