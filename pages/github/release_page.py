import re

from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC

from core.base_page import BasePage
from core.logger import get_logger

logger = get_logger(__name__)

REPO_BASE_URL_PATTERN = re.compile(r"^https?://github\.com/([^/?#]+)/([^/?#]+)")

VERSION_PATTERN = re.compile(r"/releases/tag/v?([^/]+)")

SOURCE_CODE_ZIP_LINK = (
    By.XPATH,
    "//a[contains(@href, '/archive/refs/tags/') and contains(@href, '.zip')]",
)
RELEASE_TAG_HEADING = (By.CSS_SELECTOR, "h1, [data-testid='latest-release-tag'], .f1")


class ReleasePage(BasePage):
    def open_latest_release(self) -> None:
        current_url = self.driver.current_url
        match = REPO_BASE_URL_PATTERN.match(current_url)

        if not match:
            logger.error("Khong nhan dien duoc URL repo tu: %s", current_url)
            raise ValueError(
                f"Dang khong o trang 1 repository GitHub hop le: {current_url}"
            )

        owner = match.group(1)
        repo = match.group(2)       
        repo_base_url = f"https://github.com/{owner}/{repo}"
        target_url = f"{repo_base_url}/releases/latest"

        logger.info("Dang mo trang release moi nhat: %s", target_url)
        self.open(target_url)

        self.wait.until(EC.url_contains("/releases/tag/"))
        self.wait_visible(RELEASE_TAG_HEADING)

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