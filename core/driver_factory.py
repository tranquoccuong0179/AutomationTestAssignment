"""
Khoi tao WebDriver (Chrome) voi cau hinh phu hop cho automation:
- Tu dong tai file ve DOWNLOAD_DIR, khong hien popup "Save As"
- Ho tro bat/tat headless
- Ap dung implicit wait mac dinh tu settings

Cach dung o noi khac:
    from core.driver_factory import create_driver
    driver = create_driver()
    ...
    driver.quit()
"""

from selenium import webdriver
from selenium.webdriver.chrome.options import Options

from configs.settings import HEADLESS, DOWNLOAD_DIR, IMPLICIT_WAIT
from core.logger import get_logger

logger = get_logger(__name__)


def _build_chrome_options() -> Options:
    """Dung rieng 1 ham de gom het logic cau hinh Options, de doc va de test."""
    options = Options()

    if HEADLESS:
        options.add_argument("--headless=new")
        logger.info("Chay Chrome o che do headless")

    # Cac flag on dinh khi chay trong moi truong CI/Docker (khong co GUI thuc)
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--window-size=1920,1080")

    # Cau hinh de Chrome tu dong tai file .zip ve DOWNLOAD_DIR,
    # khong hien popup hoi "Save As" (bat buoc cho automation khong nguoi truc)
    prefs = {
        "download.default_directory": DOWNLOAD_DIR,
        "download.prompt_for_download": False,
        "download.directory_upgrade": True,
        "safebrowsing.enabled": True,
    }
    options.add_experimental_option("prefs", prefs)

    return options


def create_driver() -> webdriver.Chrome:
    """
    Tao va tra ve 1 instance Chrome WebDriver da cau hinh san.
    Selenium 4.6+ tu dong tai va quan ly ChromeDriver (Selenium Manager),
    khong can cai them webdriver-manager.
    """
    logger.info("Dang khoi tao Chrome WebDriver...")
    options = _build_chrome_options()

    driver = webdriver.Chrome(options=options)
    driver.implicitly_wait(IMPLICIT_WAIT)

    logger.info("Chrome WebDriver da san sang (download_dir=%s)", DOWNLOAD_DIR)
    return driver