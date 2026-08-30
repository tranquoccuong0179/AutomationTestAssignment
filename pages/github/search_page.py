"""
SearchPage: Page Object cho chuc nang tim kiem tren GitHub.

QUAN TRONG - locator KHONG duoc gan cung theo 1 tu khoa/repo cu the (xem
release_page.py cung ap dung nguyen tac tuong tu).

QUAN TRONG - loc ket qua theo HINH DANG URL, khong doan ten CSS class:
    Container ket qua tim kiem GitHub chua NHIEU loai <a> khac nhau (link
    repo THAT, link owner/avatar, link topic/badge...). Neu chi dua vao
    1 CSS selector chung chung nhu "[data-testid='results-list'] a", co
    the vo tinh bat trung link OWNER (vd: github.com/twbs) thay vi link
    REPO THAT (vd: github.com/twbs/bootstrap) - vi ca 2 deu la <a> hop le
    trong cung container.
    De tranh phu thuoc vao doan CSS class chinh xac (de doi, kho xac nhan
    khi GitHub chan bot fetch), click_first_result() LOC theo HINH DANG
    URL: chi chap nhan link dung dang "github.com/{owner}/{repo}" (dung
    2 doan duong dan, khong nhieu hon/it hon) - day la dac diem BAT BIEN
    cua link repo that, bat ke GitHub doi CSS/class nhu the nao.

**CANH BAO**: locator SEARCH_TRIGGER/SEARCH_INPUT van can tu kiem tra lai
bang DevTools truoc khi chay chinh thuc.
"""

import re

from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys

from core.base_page import BasePage
from core.logger import get_logger

logger = get_logger(__name__)

GITHUB_HOME_URL = "https://github.com"

# Chi chinh xac 2 doan duong dan sau domain (owner/repo), khong hon khong kem
# -> tu dong loai owner-only link (/twbs) va sub-page link (/twbs/bootstrap/stargazers)
REPO_LINK_PATTERN = re.compile(r"^https?://github\.com/([^/]+)/([^/]+)/?$")

# Cac tu khoa duong dan GitHub danh rieng cho tinh nang he thong, KHONG PHAI
# ten user/to chuc that - can loai tru vi topic badge (vd: /topics/css) cung
# co dung 2 doan duong dan giong het link repo, de bi loc nham neu chi dua
# vao so luong doan duong dan.
RESERVED_PATH_PREFIXES = {
    "topics", "marketplace", "sponsors", "settings", "notifications",
    "issues", "pulls", "orgs", "features", "pricing", "about",
    "contact", "support", "login", "join", "session", "search", "collections",
}

SEARCH_TRIGGER = (By.CSS_SELECTOR, "button[aria-label*='quick search dialog']," " button.Search-module__searchButton__aiE0a")
SEARCH_INPUT = (By.CSS_SELECTOR, "input[aria-label='Search or jump to'], input[placeholder='Search or jump to...']")

# Lay TAT CA link trong container ket qua - se LOC lai theo URL o click_first_result()
RESULT_LINKS = (By.CSS_SELECTOR, "[data-testid='results-list'] a, .search-title a")
RESULTS_CONTAINER = (By.CSS_SELECTOR, "[data-testid='results-list'], .repo-list")


class SearchPage(BasePage):
    """Page Object cho chuc nang tim kiem repository tren GitHub."""

    def open_home(self) -> None:
        """Dieu huong den trang chu GitHub, noi co o tim kiem."""
        self.open(GITHUB_HOME_URL)

    def search(self, keyword: str) -> None:
        """Nhap tu khoa BAT KY vao o tim kiem va nhan Enter."""
        logger.info("Dang tim kiem tu khoa: %s", keyword)

        if self.is_element_present(SEARCH_TRIGGER, timeout=2):
            try:
                self.safe_click(SEARCH_TRIGGER)
                self.input_text(SEARCH_INPUT, f"{keyword}{Keys.ENTER}")
                return
            except Exception:
                logger.warning("Header search loi, chuyen sang fallback URL truc tiep")

        logger.info("Header search chua san sang, mo truc tiep link query: %s", keyword)
        self.open(f"{GITHUB_HOME_URL}/search?q={keyword}&type=repositories")

    def click_first_result(self) -> None:
        """
        Cho ket qua load xong, LOC trong tat ca cac link tim thay, chi lay
        link dung dinh dang "github.com/{owner}/{repo}" (link REPO THAT),
        bo qua link owner/topic/badge du chung cung nam trong container ket qua.
        """
        self.wait_visible(RESULTS_CONTAINER)
        candidates = self.driver.find_elements(*RESULT_LINKS)

        for candidate in candidates:
            href = candidate.get_attribute("href") or ""
            match = REPO_LINK_PATTERN.match(href)

            if match and match.group(1).lower() not in RESERVED_PATH_PREFIXES:
                logger.info("Da tim thay link repo hop le, dang click: %s", href)
                self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", candidate)
                candidate.click()
                return

        logger.error("Khong tim thay link repo hop le nao trong ket qua tim kiem")
        raise Exception("Khong tim thay link repository hop le (dang github.com/owner/repo) trong ket qua tim kiem")

    def search_and_open_first_result(self, keyword: str) -> None:
        """Ham tien loi: gop search() + click_first_result() thanh 1 buoc."""
        self.search(keyword)
        self.click_first_result()