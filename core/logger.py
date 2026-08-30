import logging
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
LOG_DIR = BASE_DIR / "reports" / "logs"
LOG_FILE = LOG_DIR / "automation.log"

APP_LOGGER_NAME = "automation"

LOG_FORMAT = "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s"
DATE_FORMAT = "%Y-%m-%d %H:%M:%S"

_configured = False


def _setup_logger() -> None:
    global _configured

    if _configured:
        return

    LOG_DIR.mkdir(parents=True, exist_ok=True)

    formatter = logging.Formatter(
        LOG_FORMAT,
        datefmt=DATE_FORMAT,
    )

    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(formatter)

    file_handler = logging.FileHandler(
        LOG_FILE,
        encoding="utf-8",
    )
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(formatter)

    app_logger = logging.getLogger(APP_LOGGER_NAME)
    app_logger.setLevel(logging.DEBUG)
    app_logger.propagate = False

    app_logger.addHandler(console_handler)
    app_logger.addHandler(file_handler)

    logging.getLogger("selenium").setLevel(logging.WARNING)
    logging.getLogger("urllib3").setLevel(logging.WARNING)

    _configured = True


def get_logger(name: str) -> logging.Logger:
    _setup_logger()
    return logging.getLogger(f"{APP_LOGGER_NAME}.{name}")