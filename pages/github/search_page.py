import re

from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys

from core.base_page import BasePage
from core.logger import get_logger
from urllib.parse import quote_plus

from selenium.common.exceptions import (
    NoSuchElementException,
    TimeoutException,
)

logger = get_logger(__name__)

GITHUB_HOME_URL = "https://github.com"

REPO_LINK_PATTERN = re.compile(r"^https?://github\.com/([^/]+)/([^/]+)/?$")

RESERVED_PATH_PREFIXES = {
    "topics", "marketplace", "sponsors", "settings", "notifications",
    "issues", "pulls", "orgs", "features", "pricing", "about",
    "contact", "support", "login", "join", "session", "search", "collections",
}

SEARCH_TRIGGER = (By.CSS_SELECTOR, "button[aria-label*='quick search dialog']," " button.Search-module__searchButton__aiE0a")
SEARCH_INPUT = (By.CSS_SELECTOR, "input[aria-label='Search or jump to'], input[placeholder='Search or jump to...']")

RESULT_LINKS = (By.CSS_SELECTOR, "[data-testid='results-list'] a, .search-title a")
RESULTS_CONTAINER = (By.CSS_SELECTOR, "[data-testid='results-list'], .repo-list")


class SearchPage(BasePage):
    def search(self, keyword: str) -> None:
        logger.info("Dang tim kiem tu khoa: %s", keyword)

        if self.is_element_present(SEARCH_TRIGGER, timeout=2):
            try:
                self.safe_click(SEARCH_TRIGGER)
                self.input_text(SEARCH_INPUT, keyword)
                search_input = self.wait_visible(SEARCH_INPUT)
                search_input.send_keys(Keys.ENTER)
                return
            except (
                TimeoutException,
                NoSuchElementException,
            ):
                logger.warning("Header search loi, chuyen sang fallback URL truc tiep")

        logger.info("Header search chua san sang, mo truc tiep link query: %s", keyword)

        query = quote_plus(keyword)
        self.open(f"{GITHUB_HOME_URL}/search?q={query}&type=repositories")

    def click_first_result(self) -> str:
        self.wait_visible(RESULTS_CONTAINER)
        candidates = self.driver.find_elements(*RESULT_LINKS)

        for candidate in candidates:
            href = candidate.get_attribute("href") or ""
            match = REPO_LINK_PATTERN.match(href)
            if not match:
                continue

            owner = match.group(1)
            repository = match.group(2)
            if owner.lower() in RESERVED_PATH_PREFIXES:
                continue

            repository_name = f"{owner}/{repository}"
            logger.info("Da tim thay repository hop le, dang click: %s", repository_name)
            self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", candidate)
            candidate.click()
            return repository_name

        logger.error("Khong tim thay link repo hop le nao trong ket qua tim kiem")
        raise RuntimeError("Khong tim thay link repository hop le (dang github.com/owner/repo) trong ket qua tim kiem")

    def search_and_open_first_result(self, keyword: str) -> str:
        self.search(keyword)
        return self.click_first_result()