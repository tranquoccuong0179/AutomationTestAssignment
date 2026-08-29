"""
Cau hinh logger dung chung cho toan bo framework.
Ghi log ra 2 noi cung luc: console (xem truc tiep) va file .log (xem lai sau).

Cach dung o module khac:
    from core.logger import get_logger
    logger = get_logger(__name__)
    logger.info("Bat dau login GitHub...")
    logger.error("Login that bai: %s", str(e))
"""

import logging
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
LOG_DIR = BASE_DIR / "reports" / "logs"
LOG_FILE = LOG_DIR / "automation.log"

LOG_FORMAT = "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s"
DATE_FORMAT = "%Y-%m-%d %H:%M:%S"

_configured = False


def _setup_root_logger() -> None:
    """Cau hinh 1 lan duy nhat cho toan bo ung dung (goi ngam trong get_logger)."""
    global _configured
    if _configured:
        return

    LOG_DIR.mkdir(parents=True, exist_ok=True)

    formatter = logging.Formatter(LOG_FORMAT, datefmt=DATE_FORMAT)

    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    console_handler.setLevel(logging.INFO)

    file_handler = logging.FileHandler(LOG_FILE, encoding="utf-8")
    file_handler.setFormatter(formatter)
    file_handler.setLevel(logging.DEBUG)

    root_logger = logging.getLogger()
    root_logger.setLevel(logging.DEBUG)
    root_logger.addHandler(console_handler)
    root_logger.addHandler(file_handler)

    _configured = True


def get_logger(name: str) -> logging.Logger:
    """
    Tra ve 1 logger da cau hinh san, dat ten theo module goi den
    (thuong truyen __name__ de biet log nay xuat phat tu file nao).
    """
    _setup_root_logger()
    return logging.getLogger(name)