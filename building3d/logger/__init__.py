import logging
from pathlib import Path

from building3d.config import LOG_FILE, LOG_LEVEL


def init_logger(logfile: None | str = None):
    if isinstance(logfile, str) and not Path(logfile).parent.exists():
        Path(logfile).parent.mkdir(parents=True)

    if logfile is None:
        logfile = LOG_FILE

    logging.basicConfig(
        filename=logfile,
        encoding="utf-8",
        level=LOG_LEVEL,
        filemode="w",
        format="[%(levelname)s|%(name)s|%(funcName)s|%(asctime)s] %(message)s",
        force=True,
    )
