
import logging
from typing import Optional

class Logger:

    def __init__(self, name: str, level: int = logging.INFO):

        self._logger = logging.getLogger(name)
        self._logger.setLevel(level)

        if not self._logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            self._logger.addHandler(handler)

    def info(self, message: str) -> None:

        self._logger.info(message)

    def warning(self, message: str) -> None:

        self._logger.warning(message)

    def error(self, message: str, exc_info: bool = False) -> None:

        self._logger.error(message, exc_info=exc_info)

    def debug(self, message: str) -> None:

        self._logger.debug(message)
