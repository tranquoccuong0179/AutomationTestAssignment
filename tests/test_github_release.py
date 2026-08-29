import time

from configs.settings import GITHUB_PASSWORD, GITHUB_USERNAME
from core.logger import get_logger
from pages.github.login_page import LoginPage
from pages.github.release_page import ReleasePage
from pages.github.search_page import SearchPage
from services import file_service
from utils.datetime_helper import get_today_str
from services import email_service, file_service
from services.report_service import collector
import glob

logger = get_logger(__name__)


class TestGithubBootstrapDownload:
  """Kich ban lien tuc: login -> search Bootstrap -> tai release moi nhat."""

  def test_01_login(self, driver):
    """Buoc 1: Dang nhap GitHub va cho xac nhan dang nhap."""
    login_page = LoginPage(driver)
    login_page.open_login_page()
    login_page.login(GITHUB_USERNAME, GITHUB_PASSWORD)

    logger.info(">>> VUI LONG XAC THUC OTP TREN TRINH DUYET (45s)... <<<")
    logged_in = False
    for _ in range(45):
      if login_page.is_logged_in():
        logged_in = True
        break
      time.sleep(1)

    assert (
        logged_in
    ), "Login GitHub that bai - Het thoi gian cho hoac thong tin sai."

  def test_02_search_bootstrap(self, driver):
    """Buoc 2a: Tim kiem 'Bootstrap', vao repo dau tien."""
    search_page = SearchPage(driver)
    search_page.open_home()
    search_page.search_and_open_first_result("Bootstrap")

    assert "bootstrap" in driver.current_url.lower(), (
        f"Khong vao dung trang repo Bootstrap, URL hien tai:"
        f" {driver.current_url}"
    )

  def test_03_download_and_rename(self, driver):
    """Buoc 2b: Vao trang release moi nhat, lay version, tai file .zip, doi ten."""
    release_page = ReleasePage(driver)

    file_service.prepare_download_folder()

    release_page.open_latest_release()
    version = release_page.get_latest_version()
    release_page.download_source_zip()

    new_filename = f"{get_today_str()}_ThuVien_Bootstrap_v{version}.zip"
    zip_path = file_service.wait_and_rename(new_filename)

    assert zip_path.exists(), f"File .zip khong duoc tao ra: {zip_path}"
    logger.info("Test hoan tat, file da san sang: %s", zip_path)