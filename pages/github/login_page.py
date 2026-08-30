from selenium.webdriver.common.by import By

from core.base_page import BasePage
from core.logger import get_logger

logger = get_logger(__name__)

LOGIN_URL = "https://github.com/login"

USERNAME_INPUT = (By.ID, "login_field")
PASSWORD_INPUT = (By.ID, "password")
SUBMIT_BUTTON = (By.NAME, "commit")
ERROR_MESSAGE = (By.CSS_SELECTOR, ".flash-error")

USER_AVATAR = (By.CSS_SELECTOR, "img.avatar-user, summary[aria-label='View profile and more']")

class LoginPage(BasePage):
    def open_login_page(self) -> None:
        self.open(LOGIN_URL)

    def login(self, username: str, password: str) -> None:
        logger.info("Dang thuc hien login voi username: %s", username)
        self.input_text(USERNAME_INPUT, username)
        self.input_text(PASSWORD_INPUT, password)
        self.safe_click(SUBMIT_BUTTON)

    def is_logged_in(self, timeout: int = 10) -> bool:
        logged_in = self.is_element_present(USER_AVATAR, timeout=timeout)
        if logged_in:
            logger.info("Login thanh cong.")
        else:
            logger.error("Login that bai hoac chua xac nhan duoc trang thai.")
        return logged_in

    def get_error_message(self) -> str:
        if self.is_element_present(ERROR_MESSAGE, timeout=3):
            return self.get_text(ERROR_MESSAGE)
        return ""