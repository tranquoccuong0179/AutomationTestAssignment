from configs.settings import GITHUB_USERNAME, GITHUB_PASSWORD
from core.logger import get_logger
from pages.github.login_page import LoginPage
from pages.github.search_page import SearchPage
from pages.github.release_page import ReleasePage
from services import file_service
from services.report_service import collector
from utils.datetime_helper import get_today_str

logger = get_logger(__name__)


class TestGithubBootstrapDownload:
    def test_github_bootstrap_download(self, driver):
        login_page = LoginPage(driver)
        search_page = SearchPage(driver)
        release_page = ReleasePage(driver)

        # Login
        login_page.open_login_page()
        login_page.login(GITHUB_USERNAME, GITHUB_PASSWORD)

        logger.info(">>> Neu bi hoi xac minh thiet bi, xac nhan thu cong trong 45s... <<<")

        logged_in = False

        for _ in range(45):
            if login_page.is_logged_in(timeout=1):
                logged_in = True
                break

        assert logged_in, (
            "Login GitHub that bai - "
            "Het thoi gian cho hoac thong tin sai."
        )

        # Search repository
        search_page.open_home()
        search_page.search_and_open_first_result("Bootstrap")

        assert "bootstrap" in driver.current_url.lower(), (
            f"Khong vao dung trang repo Bootstrap, "
            f"URL hien tai: {driver.current_url}"
        )

        # Download latest release
        file_service.prepare_download_folder()

        release_page.open_latest_release()

        version = release_page.get_latest_version()
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