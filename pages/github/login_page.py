from selenium.webdriver.common.by import By

from core.base_page import BasePage
from core.logger import get_logger

logger = get_logger(__name__)

USERNAME_INPUT = (By.ID, "login_field")
PASSWORD_INPUT = (By.ID, "password")
SUBMIT_BUTTON = (By.NAME, "commit")
ERROR_MESSAGE = (By.CSS_SELECTOR, ".flash-error")

USER_AVATAR = (By.CSS_SELECTOR, "img.avatar-user, summary[aria-label='View profile and more']")

class LoginPage(BasePage):
    def login(self, username: str, password: str) -> None:
        logger.info("Dang thuc hien GitHub login.")
        self.input_text(USERNAME_INPUT, username)
        self.input_text(PASSWORD_INPUT, password)
        self.safe_click(SUBMIT_BUTTON)

    def is_logged_in(self, timeout: int = 10) -> bool:
        logged_in = self.is_element_present(USER_AVATAR, timeout=timeout)
        if logged_in:
            logger.info("Login thanh cong.")
        else:
            logger.debug("Chua xac nhan duoc trang thai login.")
        return logged_in

    def has_login_error(self, timeout: int = 1) -> bool:
        login_form_visible = (
            self.is_element_present(USERNAME_INPUT, timeout=timeout)
            and self.is_element_present(PASSWORD_INPUT, timeout=timeout)
        )

        if not login_form_visible:
            return False

        return self.is_element_present(
            ERROR_MESSAGE,
            timeout=timeout,
        )

    def get_error_message(self) -> str:
        if self.is_element_present(ERROR_MESSAGE, timeout=3):
            return self.get_text(ERROR_MESSAGE)
        return ""