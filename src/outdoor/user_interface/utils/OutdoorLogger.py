# logger_setup.py
import logging
import colorlog

def outdoorLogger(name="my_logger", level=logging.DEBUG):
    """
    Create a logger with a colored console handler. This method can be called in other class files to create a logger
    make sure to use the same name for the logger to prevent adding multiple handlers to the logger in different files.

    :param name:
    :param level:
    :return:
    """

    # Create a logger
    logger = logging.getLogger(name)
    logger.setLevel(level)

    # Prevent adding multiple handlers if the logger already has handlers
    if not logger.hasHandlers():
        # Create a console handler
        console_handler = logging.StreamHandler()

        # Define a colored formatter using colorlog
        formatter = colorlog.ColoredFormatter(
            "%(log_color)s%(levelname)s: %(message)s",
            log_colors={
                "DEBUG": "cyan",
                "INFO": "green",
                "WARNING": "yellow",
                "ERROR": "red",
                "CRITICAL": "bold_red",
            },
        )
        console_handler.setFormatter(formatter)

        # Attach the handler to the logger
        logger.addHandler(console_handler)

    return logger
