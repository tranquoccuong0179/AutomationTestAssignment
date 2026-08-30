"""
LoginPage: Page Object cho trang dang nhap GitHub (https://github.com/login).

Locator xac nhan tu HTML thuc te cua GitHub:
    - O username/email: id="login_field"
    - O password:        id="password"
    - Nut submit:         name="commit", value="Sign in"

CANH BAO QUAN TRONG: neu tai khoan GitHub dung de test co bat 2FA
(Two-Factor Authentication), Selenium se KHONG the vuot qua buoc xac thuc
2FA bang username/password thuan tuy. Can dung tai khoan test rieng
da tat 2FA, hoac xu ly them Personal Access Token / TOTP.
"""

from selenium.webdriver.common.by import By

from core.base_page import BasePage
from core.logger import get_logger

logger = get_logger(__name__)

LOGIN_URL = "https://github.com/login"

# ==== Locators ====
USERNAME_INPUT = (By.ID, "login_field")
PASSWORD_INPUT = (By.ID, "password")
SUBMIT_BUTTON = (By.NAME, "commit")
ERROR_MESSAGE = (By.CSS_SELECTOR, ".flash-error")

# Locator dung de xac nhan da login thanh cong (avatar user o goc tren phai)
USER_AVATAR = (By.CSS_SELECTOR, "img.avatar-user, summary[aria-label='View profile and more']")


class LoginPage(BasePage):
    """Page Object cho trang dang nhap GitHub."""

    def open_login_page(self) -> None:
        """Dieu huong den trang login GitHub."""
        self.open(LOGIN_URL)

    def login(self, username: str, password: str) -> None:
        """Thuc hien dang nhap: nhap username, password, roi click submit."""
        logger.info("Dang thuc hien login voi username: %s", username)
        self.input_text(USERNAME_INPUT, username)
        self.input_text(PASSWORD_INPUT, password)
        self.safe_click(SUBMIT_BUTTON)

    def is_logged_in(self, timeout: int = 10) -> bool:
        """
        Kiem tra da login thanh cong hay chua, bang cach tim avatar user
        o goc tren phai trang - element nay CHI xuat hien khi da dang nhap.
        """
        logged_in = self.is_element_present(USER_AVATAR, timeout=timeout)
        if logged_in:
            logger.info("Login thanh cong.")
        else:
            logger.error("Login that bai hoac chua xac nhan duoc trang thai.")
        return logged_in

    def get_error_message(self) -> str:
        """Lay noi dung thong bao loi (vd: sai username/password), neu co."""
        if self.is_element_present(ERROR_MESSAGE, timeout=3):
            return self.get_text(ERROR_MESSAGE)
        return ""