"""
ReleasePage: Page Object cho trang Release cua 1 repository GitHub.

DIEM QUAN TRONG (da xac nhan qua tai lieu chinh thuc GitHub, KHONG phai doan):
    GitHub co san 1 URL CO DINH luon tro den ban release moi nhat:
        https://github.com/{owner}/{repo}/releases/latest
    Khi truy cap URL nay, GitHub tu dong redirect sang:
        https://github.com/{owner}/{repo}/releases/tag/{version}
    Nho vay, ta co the LAY DUNG SO VERSION MOI NHAT bang cach doc
    driver.current_url SAU KHI redirect, KHONG can click do tren giao dien
    de tim "ban moi nhat" - on dinh hon nhieu so voi dua vao vi tri hien thi.

**CANH BAO**: locator cho nut/link "Download" (Source code zip) VAN chua duoc
xac nhan qua fetch truc tiep (GitHub chan bot). Can tu kiem tra lai bang
DevTools truoc khi chay chinh thuc. Xem huong dan trong search_page.py.
"""

import re

from selenium.webdriver.common.by import By

from core.base_page import BasePage
from core.logger import get_logger

logger = get_logger(__name__)

REPO_OWNER = "twbs"
REPO_NAME = "bootstrap"
RELEASES_LATEST_URL = f"https://github.com/{REPO_OWNER}/{REPO_NAME}/releases/latest"

# ==== Locators (CAN TU KIEM TRA LAI BANG DEVTOOLS) ====
# Link tai "Source code (zip)" trong phan Assets cua trang release
SOURCE_CODE_ZIP_LINK = (
        By.XPATH,
        "//a[contains(@href, '/archive/refs/tags/') and contains(@href, '.zip')]",
    )

# Phan tu de xac nhan trang release da load xong (vd: tieu de tag/version)
RELEASE_TAG_HEADING = (By.CSS_SELECTOR, "h1, [data-testid='latest-release-tag'], .f1")


class ReleasePage(BasePage):
    """Page Object cho trang Release cua repository (mac dinh: twbs/bootstrap)."""

    def open_latest_release(self) -> None:
        """
        Dieu huong den URL co dinh /releases/latest.
        GitHub se tu dong redirect sang URL co chua so version that su.
        """
        logger.info("Dang mo trang release moi nhat: %s", RELEASES_LATEST_URL)
        self.open(RELEASES_LATEST_URL)
        self.wait_visible(RELEASE_TAG_HEADING)

    def get_latest_version(self) -> str:
        """
        Lay so version moi nhat bang cach doc URL hien tai SAU KHI da redirect.
        URL co dang: https://github.com/twbs/bootstrap/releases/tag/v5.3.8
        -> tra ve "5.3.8" (da bo chu "v" o dau, khop voi format ten file yeu cau).
        """
        current_url = self.driver.current_url
        match = re.search(r"/releases/tag/v?([\d.]+)", current_url)

        if not match:
            logger.error("Khong tim thay version trong URL: %s", current_url)
            raise ValueError(f"Khong the xac dinh version tu URL: {current_url}")

        version = match.group(1)
        logger.info("Da xac dinh version moi nhat: %s", version)
        return version

    def download_source_zip(self) -> None:
        """Click vao link 'Source code (zip)' de bat dau tai file .zip."""
        logger.info("Dang click de tai Source code (zip)")
        self.driver.execute_script("""
              document.querySelectorAll("details").forEach(el => el.open = true);
          """)
        element = self.wait_visible(SOURCE_CODE_ZIP_LINK)
        self.driver.execute_script(
            "arguments[0].scrollIntoView({block: 'center'});", element
        )
        self.driver.execute_script("arguments[0].click();", element)