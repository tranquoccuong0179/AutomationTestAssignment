"""
SearchPage: Page Object cho chuc nang tim kiem tren GitHub
(o tim kiem o dau moi trang -> Enter -> trang ket qua search?q=...&type=repositories).

**CANH BAO QUAN TRONG**: locator trong file nay duoc viet dua tren cau truc
GitHub pho bien, CHUA duoc xac nhan qua fetch truc tiep (GitHub chan bot fetch
qua robots.txt). BAT BUOC phai tu kiem tra lai bang DevTools (F12 -> Inspect)
truoc khi chay chinh thuc, vi GitHub co the doi cau truc HTML bat ky luc nao.

Cach lay locator that bang DevTools:
    1. Mo https://github.com trong Chrome that
    2. Nhan F12 -> chuyen sang tab "Elements"
    3. Nhan Ctrl+Shift+C (hoac click icon mui ten o goc tren trai DevTools)
    4. Click vao o tim kiem tren trang GitHub -> DevTools se highlight dung the HTML
    5. Doi chieu id/class/name trong the do voi locator duoi day, sua neu khac
"""

from selenium.webdriver.common.by import By

from core.base_page import BasePage
from core.logger import get_logger
from selenium.webdriver.common.keys import Keys


logger = get_logger(__name__)

GITHUB_HOME_URL = "https://github.com"

# ==== Locators (CAN TU KIEM TRA LAI BANG DEVTOOLS) ====
# O tim kiem o dau trang (header), thuong co dang <input type="text" placeholder="Search or jump to...">
SEARCH_BOX = (By.CSS_SELECTOR, "input[placeholder*='Search'], input[name='q']")

# Item dau tien trong danh sach ket qua repository (thuong la <a> chua ten repo, vd "twbs/bootstrap")
FIRST_RESULT_LINK = (By.CSS_SELECTOR, "a[href*='/twbs/bootstrap'], .search-title a, [data-testid='results-list'] a")

# Container bao quanh toan bo danh sach ket qua, dung de cho ket qua load xong
RESULTS_CONTAINER = (By.CSS_SELECTOR, "[data-testid='results-list'], .repo-list")


class SearchPage(BasePage):
    """Page Object cho chuc nang tim kiem repository tren GitHub."""

    def open_home(self) -> None:
        """Dieu huong den trang chu GitHub, noi co o tim kiem."""
        self.open(GITHUB_HOME_URL)

    def search(self, keyword: str) -> None:
        """
        Nhap tu khoa vao o tim kiem va nhan Enter de xem ket qua.
        Dung Keys.ENTER thay vi tim nut submit rieng, vi o search
        cua GitHub thuong submit bang Enter, khong co nut bam ro rang.
        """

        logger.info("Dang tim kiem tu khoa: %s", keyword)
        self.input_text(SEARCH_BOX, keyword)
        search_box = self.wait_visible(SEARCH_BOX)
        search_box.send_keys(Keys.ENTER)

    def click_first_result(self) -> None:
        """
        Cho ket qua load xong, roi click vao ket qua dau tien
        (ky vong la repo twbs/bootstrap khi tim tu khoa "Bootstrap").
        """
        self.wait_visible(RESULTS_CONTAINER)
        logger.info("Dang click vao ket qua tim kiem dau tien")
        self.safe_click(FIRST_RESULT_LINK)

    def search_and_open_first_result(self, keyword: str) -> None:
        """Ham tien loi: gop search() + click_first_result() thanh 1 buoc."""
        self.search(keyword)
        self.click_first_result()