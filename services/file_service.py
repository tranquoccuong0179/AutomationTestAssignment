from pathlib import Path

from configs.settings import DOWNLOAD_DIR
from core.logger import get_logger
from utils.file_helper import wait_for_download_complete, rename_file, clean_old_downloads

logger = get_logger(__name__)


def prepare_download_folder() -> None:
    """Don dep file .zip cu trong DOWNLOAD_DIR truoc khi bat dau tai file moi."""
    clean_old_downloads(DOWNLOAD_DIR)


def wait_and_rename(new_filename: str, timeout: int = 60) -> Path:
    logger.info("Chờ tải và chuẩn bị đổi tên thành: %s", new_filename)
    downloaded_file = wait_for_download_complete(DOWNLOAD_DIR, timeout=timeout)
    if downloaded_file is None:
        raise TimeoutError(f"Tai file that bai: khong tim thay file .zip sau khi cho {timeout}s")
    
    return rename_file(downloaded_file, new_filename)