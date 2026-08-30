from pathlib import Path

from utils.datetime_helper import get_timestamp_str
from core.logger import get_logger

logger = get_logger(__name__)

BASE_DIR = Path(__file__).resolve().parent.parent
SCREENSHOT_DIR = BASE_DIR / "reports" / "screenshots"


def capture_screenshot(driver, test_name: str = "failure", screenshot_dir: str | Path = SCREENSHOT_DIR) -> str:
    screenshot_dir = Path(screenshot_dir)
    screenshot_dir.mkdir(parents=True, exist_ok=True)

    safe_name = "".join(c if c.isalnum() or c in ("_", "-") else "_" for c in test_name)
    filename = f"{safe_name}_{get_timestamp_str()}.png"
    screenshot_path = screenshot_dir / filename

    try:
        driver.save_screenshot(str(screenshot_path))
        logger.info("Da chup screenshot: %s", screenshot_path)
        return str(screenshot_path)
    except Exception as e:
        logger.error("Chup screenshot that bai: %s", e)
        return ""