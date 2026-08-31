from configs.settings import GITHUB_USERNAME, GITHUB_PASSWORD
from core.logger import get_logger
from pages.github.login_page import LoginPage
from pages.github.search_page import SearchPage
from pages.github.release_page import ReleasePage
from pages.github.home_page import HomePage
from services import file_service
from services.report_service import collector
from utils.datetime_helper import get_today_str
import pytest

logger = get_logger(__name__)


class TestGithubBootstrapDownload:
    def test_github_bootstrap_download(self, driver):
        login_page = LoginPage(driver)
        search_page = SearchPage(driver)
        release_page = ReleasePage(driver)
        home_page = HomePage(driver)

        # Open GitHub and login
        collector.set_current_step("1 Open GitHub homepage")
        home_page.open_home_page()

        collector.set_current_step("2 Click Sign in")
        home_page.click_sign_in()

        # Login
        collector.set_current_step("3 Login GitHub")
        login_page.login(GITHUB_USERNAME, GITHUB_PASSWORD)

        logger.info(">>> Neu bi hoi xac minh thiet bi, xac nhan thu cong trong 55s... <<<")

        collector.set_current_step("4 Verify GitHub login")
        logged_in = False
        for _ in range(9):
            if login_page.has_login_error(timeout=1):
                error_message = login_page.get_error_message()
                pytest.fail(f"Login GitHub that bai: {error_message}")

            if login_page.is_logged_in(timeout=5):
                logged_in = True
                break

        assert logged_in, (
            "Login GitHub that bai - "
            "Het thoi gian cho hoac thong tin sai."
        )

        collector.set_current_step("5 search_and_open_first_result")
        # Search repository
        search_page.search_and_open_first_result("Bootstrap")

        assert "bootstrap" in driver.current_url.lower(), (
            f"Khong vao dung trang repo Bootstrap, "
            f"URL hien tai: {driver.current_url}"
        )

        # Download latest release
        collector.set_current_step("6 prepare_download_folder")
        file_service.prepare_download_folder()

        collector.set_current_step("7 navigate_to_latest_release")
        release_page.navigate_to_latest_release()

        collector.set_current_step("8 get_latest_version")
        version = release_page.get_latest_version()

        collector.set_current_step("9 download_source_zip")
        release_page.download_source_zip()

        new_filename = (
            f"{get_today_str()}_ThuVien_Bootstrap_v{version}.zip"
        )

        zip_path = file_service.wait_and_rename(new_filename)

        assert zip_path.exists(), (
            f"File .zip khong duoc tao ra: {zip_path}"
        )

        collector.record_artifact(zip_path)

        logger.info(
            "Test hoan tat, file da san sang: %s",
            zip_path,
        )