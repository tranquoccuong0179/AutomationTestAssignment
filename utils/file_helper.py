"""
file_helper.py: Cac ham I/O file thuan tuy - doi ten, kiem tra ton tai,
kiem tra file tai xong chua, xoa file cu.

KHONG biet gi ve Selenium hay GitHub - chi lam viec voi file tren disk.

Cach dung o noi khac:
    from utils.file_helper import wait_for_download_complete, rename_file

    zip_path = wait_for_download_complete(DOWNLOAD_DIR)
    new_path = rename_file(zip_path, "20260827_ThuVien_Bootstrap_v5.3.8.zip")
"""

import time
from pathlib import Path
from typing import Optional

from core.logger import get_logger

logger = get_logger(__name__)


def wait_for_download_complete(
    download_dir: str, timeout: int = 60, poll_interval: float = 1.0
) -> Optional[Path]:
    """
    Doi cho den khi co 1 file .zip moi xuat hien va tai xong hoan toan
    trong thu muc download_dir.

    Chrome dat file dang tai voi duoi tam thoi ".crdownload" - khi file do
    bien mat (doi ten thanh .zip that su), nghia la da tai xong.

    Tra ve Path cua file .zip neu tim thay trong thoi gian timeout,
    None neu het thoi gian ma khong thay.
    """
    download_path = Path(download_dir)
    elapsed = 0.0

    logger.info("Dang cho file tai xong trong %s (timeout=%ss)...", download_dir, timeout)

    while elapsed < timeout:
        # Neu con file .crdownload (dang tai do), tiep tuc cho
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
    """
    Doi ten 1 file, giu nguyen thu muc chua no.
    Tra ve Path moi sau khi doi ten.
    """
    source = Path(source_path)
    destination = source.parent / new_name

    if destination.exists():
        logger.warning("File dich da ton tai, se bi ghi de: %s", destination)
        destination.unlink()

    source.rename(destination)
    logger.info("Da doi ten file: %s -> %s", source.name, destination.name)
    return destination


def clean_old_downloads(download_dir: str, pattern: str = "*.zip") -> int:
    """
    Xoa cac file cu trong thu muc download truoc khi chay test moi,
    tranh nham lan giua file zip cu va file vua tai.

    Tra ve so luong file da xoa.
    """
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
    """Kiem tra 1 file co ton tai tren disk khong."""
    return Path(file_path).is_file()