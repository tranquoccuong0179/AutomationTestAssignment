from selenium.webdriver.common.by import By

from core.base_page import BasePage
from core.logger import get_logger

logger = get_logger(__name__)

GITHUB_HOME_URL = "https://github.com/"

SIGN_IN_LINK = (
    By.LINK_TEXT,
    "Sign in",
)


class HomePage(BasePage):
    def open_home_page(self) -> None:
        logger.info("Mo GitHub homepage.")
        self.open(GITHUB_HOME_URL)

    def click_sign_in(self) -> None:
        logger.info("Click Sign in.")
        self.safe_click(SIGN_IN_LINK)