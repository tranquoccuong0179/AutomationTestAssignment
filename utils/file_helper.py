import re

import time
from pathlib import Path
from typing import Optional

from core.logger import get_logger

logger = get_logger(__name__)

INVALID_FILENAME_CHARS = re.compile(r'[<>:"/\\|?*]')

def sanitize_filename(filename: str) -> str:
    return INVALID_FILENAME_CHARS.sub("_", filename)

def wait_for_download_complete(
    download_dir: str, timeout: int = 60, poll_interval: float = 1.0
) -> Optional[Path]:
    download_path = Path(download_dir)
    elapsed = 0.0

    logger.info("Dang cho file tai xong trong %s (timeout=%ss)...", download_dir, timeout)

    while elapsed < timeout:
        in_progress = list(download_path.glob("*.crdownload"))
        zip_files = list(download_path.glob("*.zip"))

        if zip_files and not in_progress:
            latest_zip = max(zip_files, key=lambda p: p.stat().st_mtime)
            logger.info("Tai file xong: %s", latest_zip.name)
            return latest_zip

        time.sleep(poll_interval)
        elapsed += poll_interval

    logger.error("Het thoi gian cho (%ss) nhung khong thay file .zip nao tai xong", timeout)
    return None

def rename_file(source_path: Path, new_name: str) -> Path:
    source = Path(source_path)
    safe_name = sanitize_filename(new_name)
    destination = source.parent / safe_name

    if destination.exists():
        logger.warning("File dich da ton tai, se bi ghi de: %s", destination)
        destination.unlink()

    source.rename(destination)
    logger.info("Da doi ten file: %s -> %s", source.name, destination.name)
    return destination

def clean_old_downloads(download_dir: str, pattern: str = "*.zip") -> int:
    download_path = Path(download_dir)
    if not download_path.exists():
        download_path.mkdir(parents=True, exist_ok=True)
        return 0

    deleted_count = 0
    for old_file in download_path.glob(pattern):
        old_file.unlink()
        deleted_count += 1
        logger.debug("Da xoa file cu: %s", old_file.name)

    if deleted_count:
        logger.info("Da don dep %s file cu trong %s", deleted_count, download_dir)
    return deleted_count


def file_exists(file_path: str) -> bool:
    return Path(file_path).is_file()