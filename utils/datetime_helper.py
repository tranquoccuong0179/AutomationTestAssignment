"""
datetime_helper.py: Cac ham xu ly ngay gio - dung cho 2 muc dich chinh:
1. Format ngay hien tai theo yyyyMMdd (dat ten file zip)
2. Tinh execution time (thoi gian chay test) de dua vao noi dung email

Cach dung o noi khac:
    from utils.datetime_helper import get_today_str, format_duration

    today = get_today_str()  # "20260827"
    filename = f"{today}_ThuVien_Bootstrap_v5.3.8.zip"

    duration = format_duration(start_time, end_time)  # "00:05:32"
"""

from datetime import datetime


def get_today_str(fmt: str = "%Y%m%d") -> str:
    """
    Tra ve ngay hien tai dang string, mac dinh format yyyyMMdd.
    Dung de dat ten file: 20260827_ThuVien_Bootstrap_v5.3.8.zip
    """
    return datetime.now().strftime(fmt)


def get_timestamp_str(fmt: str = "%Y%m%d_%H%M%S") -> str:
    """
    Tra ve timestamp day du (ca gio phut giay), dung de dat ten
    file khong bi trung khi tao nhieu file lien tiep (vd: screenshot).
    """
    return datetime.now().strftime(fmt)


def format_duration(start_time: float, end_time: float) -> str:
    """
    Tinh khoang thoi gian giua 2 moc thoi gian (tinh bang giay, lay tu time.time()),
    tra ve dang chuoi HH:MM:SS de dua vao noi dung email/report.

    Vi du:
        start = time.time()
        ... chay test ...
        end = time.time()
        format_duration(start, end)  # "00:05:32"
    """
    total_seconds = int(end_time - start_time)
    hours, remainder = divmod(total_seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    return f"{hours:02d}:{minutes:02d}:{seconds:02d}"


def now_readable(fmt: str = "%Y-%m-%d %H:%M:%S") -> str:
    """
    Tra ve thoi gian hien tai dang de doc, dung de hien thi trong
    noi dung email (vd: "Thoi gian chay: 2026-08-27 05:42:00").
    """
    return datetime.now().strftime(fmt)