from selenium import webdriver
from selenium.webdriver.chrome.options import Options

from configs.settings import HEADLESS, DOWNLOAD_DIR
from core.logger import get_logger

logger = get_logger(__name__)


def _build_chrome_options() -> Options:
    options = Options()

    if HEADLESS:
        options.add_argument("--headless=new")
        logger.info("Chay Chrome o che do headless")

    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--window-size=1920,1080")

    prefs = {
        "download.default_directory": DOWNLOAD_DIR,
        "download.prompt_for_download": False,
        "download.directory_upgrade": True,
        "safebrowsing.enabled": True,
    }
    options.add_experimental_option("prefs", prefs)

    return options


def create_driver() -> webdriver.Chrome:
    logger.info("Dang khoi tao Chrome WebDriver...")
    options = _build_chrome_options()
    driver = webdriver.Chrome(options=options)

    logger.info("Chrome WebDriver da san sang (download_dir=%s)", DOWNLOAD_DIR)
    return driver