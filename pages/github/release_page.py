"""
ReleasePage: Page Object cho trang Release cua 1 repository GitHub BAT KY.

QUAN TRONG - KHONG hard-code owner/repo: xem chi tiet o open_latest_release().

DIEM QUAN TRONG (da xac nhan qua tai lieu chinh thuc GitHub):
    GitHub co san 1 URL CO DINH luon tro den ban release moi nhat:
        https://github.com/{owner}/{repo}/releases/latest
    Khi truy cap URL nay, GitHub redirect sang:
        https://github.com/{owner}/{repo}/releases/tag/{version}

PHONG THU RACE CONDITION khi doc URL sau redirect:
    driver.get() thuong da doi redirect server xong moi tra ve, nhung neu
    GitHub dung client-side routing (Turbo/SPA) thay vi redirect server that,
    URL co the doi CHAM HON so voi luc DOM da hien thi xong. De an toan,
    CHU DONG cho URL khop dung pattern "/releases/tag/" TRUOC KHI doc
    current_url, thay vi tin tuong get() da du.

**CANH BAO**: locator cho nut/link "Download" (Source code zip) VAN chua duoc
xac nhan qua fetch truc tiep (GitHub chan bot). Can tu kiem tra lai bang
DevTools truoc khi chay chinh thuc.
"""

import re

from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC

from core.base_page import BasePage
from core.logger import get_logger

logger = get_logger(__name__)

REPO_BASE_URL_PATTERN = re.compile(r"(https?://github\.com/[^/?#]+/[^/?#]+)")

# Bat MOI ky tu den dau "/" tiep theo (khong gioi han chi so+dau cham),
# de xu ly duoc ca semver co pre-release nhu "v5.3.8-alpha.1", "v1.0.0-rc2"
VERSION_PATTERN = re.compile(r"/releases/tag/v?([^/]+)")

SOURCE_CODE_ZIP_LINK = (
    By.XPATH,
    "//a[contains(@href, '/archive/refs/tags/') and contains(@href, '.zip')]",
)
RELEASE_TAG_HEADING = (By.CSS_SELECTOR, "h1, [data-testid='latest-release-tag'], .f1")


class ReleasePage(BasePage):
    """Page Object cho trang Release - hoat dong voi BAT KY repository nao."""

    def open_latest_release(self) -> None:
        """
        Tu dong xac dinh repo dang duoc mo (tu driver.current_url HIEN TAI),
        dieu huong den URL /releases/latest TUONG UNG, roi CHU DONG CHO URL
        THAT SU da chuyen sang dang "/releases/tag/..." (phong thu race
        condition neu GitHub dung client-side routing thay vi redirect server).
        """
        current_url = self.driver.current_url
        match = REPO_BASE_URL_PATTERN.match(current_url)

        if not match:
            logger.error("Khong nhan dien duoc URL repo tu: %s", current_url)
            raise ValueError(
                f"Dang khong o trang 1 repository GitHub hop le: {current_url}"
            )

        repo_base_url = match.group(1)
        target_url = f"{repo_base_url}/releases/latest"

        logger.info("Dang mo trang release moi nhat: %s", target_url)
        self.open(target_url)

        # Cho URL THAT SU da redirect xong (khong chi cho DOM hien thi)
        self.wait.until(EC.url_contains("/releases/tag/"))
        self.wait_visible(RELEASE_TAG_HEADING)

    def get_latest_version(self) -> str:
        """
        Lay version tu URL hien tai. Regex bat MOI dinh dang tag (bao gom
        semver co pre-release: v5.3.8-alpha.1, v1.0.0-rc2, hoac tag dang
        ngay thang), khong chi gioi han so+dau cham.
        """
        current_url = self.driver.current_url
        match = VERSION_PATTERN.search(current_url)

        if not match:
            logger.error("Khong tim thay version trong URL: %s", current_url)
            raise ValueError(f"Khong the xac dinh version tu URL: {current_url}")

        version = match.group(1)
        logger.info("Da xac dinh version moi nhat: %s", version)
        return version

    def download_source_zip(self) -> None:
        """
        Click vao link 'Source code (zip)' de bat dau tai file .zip.
        Dung LAI self.safe_click() (da co san trong BasePage: thu click
        THAT truoc, chi fallback sang JS click NEU bi chan) thay vi ep
        JS click ngay tu dau - vua nhat quan kien truc, vua giam rui ro
        bi trinh duyet coi la khong phai user gesture that.
        """
        logger.info("Dang click de tai Source code (zip)")

        self.driver.execute_script(
            "document.querySelectorAll('details').forEach(el => el.open = true);"
        )

        self.scroll_to(SOURCE_CODE_ZIP_LINK)
        self.safe_click(SOURCE_CODE_ZIP_LINK)