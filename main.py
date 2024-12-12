import asyncio
import logging
from datetime import datetime

import daemon
from pytz import timezone as tz

from app import bot
from app.config import EVENT_LEVEL, LOG_FILE, LOG_LEVEL, TIME_FORMAT, TIMEZONE

with daemon.DaemonContext():
    logging.Formatter.converter = lambda *args: datetime.now(tz(TIMEZONE)).strftime(TIME_FORMAT)
    levels = {
        "DEBUG": logging.DEBUG,
        "INFO": logging.INFO,
        "WARNING": logging.WARN,
        "ERROR": logging.ERROR,
        "CRITICAL": logging.CRITICAL,
        "FATAL": logging.FATAL,
        "EXCEPTION": logging.ERROR,
    }

    logger = logging.getLogger()
    logger.setLevel(levels[LOG_LEVEL])

    for handler in logger.handlers[:]:
        logger.removeHandler(handler)

    formatter = logging.Formatter(
        fmt="%(asctime)s %(levelname)s  %(message)s",
        datefmt="%H:%M:%S %d-%m-%Y",
    )
    file_handler = logging.FileHandler(LOG_FILE, encoding="utf-8")
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
    logging.getLogger("aiogram.event").setLevel(levels[EVENT_LEVEL])
    asyncio.run(bot.main())
