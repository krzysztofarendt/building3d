import logging

from building3d.config import LOG_FILE, LOG_LEVEL


logging.basicConfig(
    filename=LOG_FILE,
    encoding="utf-8",
    level=LOG_LEVEL,
    filemode="w",
    format="[%(levelname)s|%(name)s|%(funcName)s|%(asctime)s] %(message)s",
)
