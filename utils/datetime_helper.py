from datetime import datetime
from zoneinfo import ZoneInfo

VN_TIMEZONE = ZoneInfo("Asia/Ho_Chi_Minh")

def get_today_str(fmt: str = "%Y%m%d") -> str:
    return datetime.now(VN_TIMEZONE).strftime(fmt)

def get_timestamp_str(fmt: str = "%Y%m%d_%H%M%S") -> str:
    return datetime.now(VN_TIMEZONE).strftime(fmt)

def format_duration(start_time: float, end_time: float) -> str:
    total_seconds = int(end_time - start_time)
    hours, remainder = divmod(total_seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    return f"{hours:02d}:{minutes:02d}:{seconds:02d}"

def now_readable(fmt: str = "%Y-%m-%d %H:%M:%S") -> str:
    return datetime.now(VN_TIMEZONE).strftime(fmt)