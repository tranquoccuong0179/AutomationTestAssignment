"""
screenshot_helper.py: Chup anh man hinh tu Selenium driver khi test fail,
luu vao reports/screenshots/ voi ten file kem timestamp de khong bi ghi de.

Cach dung o noi khac (thuong goi trong conftest.py hook khi test fail):
    from utils.screenshot_helper import capture_screenshot

    screenshot_path = capture_screenshot(driver, test_name="test_02_search")
"""

from pathlib import Path

from utils.datetime_helper import get_timestamp_str
from core.logger import get_logger

logger = get_logger(__name__)

BASE_DIR = Path(__file__).resolve().parent.parent
SCREENSHOT_DIR = BASE_DIR / "reports" / "screenshots"


def capture_screenshot(driver, test_name: str = "failure") -> str:
    """
    Chup anh man hinh hien tai cua driver, luu vao reports/screenshots/
    voi ten dang: {test_name}_{timestamp}.png

    Tra ve duong dan tuyet doi (string) cua file anh da luu,
    hoac chuoi rong "" neu chup that bai (khong raise exception,
    tranh lam crash them qua trinh xu ly fail von da dang co loi).
    """
    SCREENSHOT_DIR.mkdir(parents=True, exist_ok=True)

    # Lam sach ten test de dung lam ten file an toan (bo ky tu dac biet)
    safe_name = "".join(c if c.isalnum() or c in ("_", "-") else "_" for c in test_name)
    filename = f"{safe_name}_{get_timestamp_str()}.png"
    screenshot_path = SCREENSHOT_DIR / filename

    try:
        driver.save_screenshot(str(screenshot_path))
        logger.info("Da chup screenshot: %s", screenshot_path)
        return str(screenshot_path)
    except Exception as e:
        logger.error("Chup screenshot that bai: %s", str(e))
        return ""