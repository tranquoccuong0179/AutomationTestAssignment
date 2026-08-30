from pathlib import Path

from configs.settings import DOWNLOAD_DIR
from core.logger import get_logger
from utils.file_helper import wait_for_download_complete, rename_file, clean_old_downloads

logger = get_logger(__name__)


def prepare_download_folder(download_dir: str = DOWNLOAD_DIR) -> None:
    Path(download_dir).mkdir(parents=True, exist_ok=True)
    clean_old_downloads(download_dir)


def wait_and_rename(new_filename: str, timeout: int = 60, download_dir: str = DOWNLOAD_DIR) -> Path:
    logger.info("Chờ tải và chuẩn bị đổi tên thành: %s", new_filename)
    downloaded_file = wait_for_download_complete(download_dir, timeout=timeout)
    if downloaded_file is None:
        raise TimeoutError(f"Tai file that bai: khong tim thay file .zip sau khi cho {timeout}s")
    
    return rename_file(downloaded_file, new_filename)