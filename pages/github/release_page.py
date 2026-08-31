import re
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC

from core.base_page import BasePage
from core.logger import get_logger

logger = get_logger(__name__)

REPO_BASE_URL_PATTERN = re.compile(r"^https?://github\.com/([^/?#]+)/([^/?#]+)")
VERSION_PATTERN = re.compile(r"/releases/tag/(?:v)?([^/?#]+)")

SIDEBAR_LATEST_RELEASE = (
    By.XPATH,
    "//a[contains(@href, '/releases/tag/') and (.//*[contains(text(), 'Latest')] or contains(@class, 'releaseLink'))]",
)

SOURCE_CODE_ZIP_LINK = (
    By.XPATH,
    "//a[contains(@href, '/archive/refs/tags/') and (contains(@href, '.zip') or contains(., 'Source code (zip)'))]",
)

RELEASE_CONTAINER = (
    By.CSS_SELECTOR,
    "[data-test-selector='release-card'], section[aria-label*='Release'], article.release, main",
)


class ReleasePage(BasePage):
    def open_latest_from_ui(self) -> None:
        logger.info("Dang tim va click link Latest release o sidebar...")
        element = self.wait_visible(SIDEBAR_LATEST_RELEASE)
        self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", element)
        element.click()
        self.wait.until(EC.url_contains("/releases/tag/"))
        self.wait_visible(RELEASE_CONTAINER)

    def open_latest_release_url(self) -> None:
        current_url = self.driver.current_url
        match = REPO_BASE_URL_PATTERN.match(current_url)

        if not match:
            logger.error("Khong nhan dien duoc URL repo tu: %s", current_url)
            raise ValueError(f"Dang khong o trang 1 repository GitHub hop le: {current_url}")

        owner, repo = match.group(1), match.group(2)
        target_url = f"https://github.com/{owner}/{repo}/releases/latest"

        logger.info("Dung fallback mo thang URL: %s", target_url)
        self.open(target_url)
        self.wait.until(EC.url_contains("/releases/tag/"))
        self.wait_visible(RELEASE_CONTAINER)

    def navigate_to_latest_release(self) -> None:
        try:
            self.open_latest_from_ui()
            logger.info("Mo release bang UI sidebar thanh cong.")
        except Exception as error:
            logger.warning("Khong click duoc bang UI sidebar (%s). Chuyen sang fallback mo URL.", error)
            self.open_latest_release_url()

    def get_latest_version(self) -> str:
        current_url = self.driver.current_url
        match = VERSION_PATTERN.search(current_url)

        if not match:
            logger.error("Khong tim thay version trong URL: %s", current_url)
            raise ValueError(f"Khong the xac dinh version tu URL: {current_url}")

        version = match.group(1)
        logger.info("Da xac dinh version moi nhat: %s", version)
        return version

    def download_source_zip(self) -> None:
        logger.info("Dang click de tai Source code (zip)")
        self.driver.execute_script("document.querySelectorAll('details').forEach(el => el.open = true);")
        self.scroll_to(SOURCE_CODE_ZIP_LINK)
        self.safe_click(SOURCE_CODE_ZIP_LINK)