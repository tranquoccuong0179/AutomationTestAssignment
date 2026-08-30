from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, ElementClickInterceptedException

from configs.settings import IMPLICIT_WAIT
from core.logger import get_logger

logger = get_logger(__name__)


class BasePage:
    def __init__(self, driver, timeout: int = None):
        self.driver = driver
        self.timeout = timeout if timeout is not None else IMPLICIT_WAIT
        self.wait = WebDriverWait(self.driver, self.timeout)

    def open(self, url: str) -> None:
        logger.info("Mo trang: %s", url)
        self.driver.get(url)

    def wait_visible(self, locator: tuple):
        try:
            element = self.wait.until(EC.visibility_of_element_located(locator))
            return element
        except TimeoutException:
            logger.error("Timeout: khong thay element %s sau %ss", locator, self.timeout)
            raise

    def wait_clickable(self, locator: tuple):
        try:
            element = self.wait.until(EC.element_to_be_clickable(locator))
            return element
        except TimeoutException:
            logger.error("Timeout: element %s khong the click sau %ss", locator, self.timeout)
            raise

    def safe_click(self, locator: tuple) -> None:
        element = self.wait_clickable(locator)
        try:
            element.click()
            logger.debug("Da click: %s", locator)
        except ElementClickInterceptedException:
            logger.warning("Click thuong bi chan, thu lai bang JavaScript: %s", locator)
            self.driver.execute_script("arguments[0].click();", element)

    def input_text(self, locator: tuple, text: str, clear_first: bool = True) -> None:
        element = self.wait_visible(locator)
        if clear_first:
            element.clear()
        element.send_keys(text)
        logger.debug("Da nhap text vao %s", locator)

    def get_text(self, locator: tuple) -> str:
        element = self.wait_visible(locator)
        return element.text.strip()

    def is_element_present(self, locator: tuple, timeout: int = 3) -> bool:
        try:
            WebDriverWait(self.driver, timeout).until(
                EC.visibility_of_element_located(locator)
            )
            return True
        except TimeoutException:
            return False

    def scroll_to(self, locator: tuple) -> None:
        element = self.wait_visible(locator)
        self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", element)