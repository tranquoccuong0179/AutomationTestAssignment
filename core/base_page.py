"""
BasePage: lop cha chua cac ham Selenium co ban, dung chung cho MOI Page Object
(login_page, search_page, repo_detail_page...) ke thua lai.

Muc dich: neu sau nay Selenium doi API, hoac can them logic
retry/wait, chi can sua 1 cho o day, khong phai sua tung page rieng le.

Cach dung o pages/:
    from core.base_page import BasePage

    class LoginPage(BasePage):
        def __init__(self, driver):
            super().__init__(driver)

        def login(self, username, password):
            self.input_text(USERNAME_LOCATOR, username)
            self.input_text(PASSWORD_LOCATOR, password)
            self.safe_click(SUBMIT_BUTTON_LOCATOR)
"""

from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, ElementClickInterceptedException

from configs.settings import IMPLICIT_WAIT
from core.logger import get_logger

logger = get_logger(__name__)


class BasePage:
    """Lop cha cho moi Page Object, chua cac hanh dong Selenium dung chung."""

    def __init__(self, driver, timeout: int = None):
        self.driver = driver
        self.timeout = timeout or IMPLICIT_WAIT
        self.wait = WebDriverWait(self.driver, self.timeout)

    def open(self, url: str) -> None:
        """Dieu huong den 1 URL."""
        logger.info("Mo trang: %s", url)
        self.driver.get(url)

    def wait_visible(self, locator: tuple):
        """
        Doi den khi element XUAT HIEN va HIEN THI tren man hinh.
        locator: tuple dang (By.ID, "value") hoac (By.XPATH, "//...")
        """
        try:
            element = self.wait.until(EC.visibility_of_element_located(locator))
            return element
        except TimeoutException:
            logger.error("Timeout: khong thay element %s sau %ss", locator, self.timeout)
            raise

    def wait_clickable(self, locator: tuple):
        """Doi den khi element co the click duoc (hien thi + khong bi che + enabled)."""
        try:
            element = self.wait.until(EC.element_to_be_clickable(locator))
            return element
        except TimeoutException:
            logger.error("Timeout: element %s khong the click sau %ss", locator, self.timeout)
            raise

    def safe_click(self, locator: tuple) -> None:
        """
        Click an toan: doi element clickable truoc, neu bi element khac che
        (ElementClickInterceptedException) thi thu lai bang JavaScript click.
        """
        element = self.wait_clickable(locator)
        try:
            element.click()
            logger.debug("Da click: %s", locator)
        except ElementClickInterceptedException:
            logger.warning("Click thuong bi chan, thu lai bang JavaScript: %s", locator)
            self.driver.execute_script("arguments[0].click();", element)

    def input_text(self, locator: tuple, text: str, clear_first: bool = True) -> None:
        """Nhap text vao 1 o input, mac dinh xoa noi dung cu truoc khi go."""
        element = self.wait_visible(locator)
        if clear_first:
            element.clear()
        element.send_keys(text)
        logger.debug("Da nhap text vao %s", locator)

    def get_text(self, locator: tuple) -> str:
        """Lay noi dung text hien thi cua 1 element."""
        element = self.wait_visible(locator)
        return element.text.strip()

    def is_element_present(self, locator: tuple, timeout: int = 3) -> bool:
        """
        Kiem tra nhanh 1 element co ton tai khong, KHONG raise exception.
        Dung khi can if/else thay vi try/except (vd: kiem tra da login thanh cong chua).
        """
        try:
            WebDriverWait(self.driver, timeout).until(
                EC.visibility_of_element_located(locator)
            )
            #  Hoặc nhưng không khuyên dùng
            # self.wait._timeout = timeout
            # self.wait.until(EC.visibility_of_element_located(locator))
            return True
        except TimeoutException:
            return False

    def scroll_to(self, locator: tuple) -> None:
        """Cuon trang den vi tri cua 1 element (huu ich khi element nam ngoai vung nhin thay)."""
        element = self.wait_visible(locator)
        self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", element)