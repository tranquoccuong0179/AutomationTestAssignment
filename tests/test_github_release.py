"""
test_github_release.py: Kich ban test chinh, thuc hien dung 3 buoc de bai yeu cau:
    1. Login GitHub
    2. Search "Bootstrap", vao repo, vao trang release moi nhat, tai file .zip
    3. Doi ten file dung format yyyyMMdd_ThuVien_Bootstrap_v{version}.zip

QUY UOC KIEN TRUC (xem chi tiet trong pages/ va services/):
    - Buoc CHI can thao tac UI don thuan (login, search) -> goi THANG pages/
    - Buoc co THEM logic xu ly ngoai UI (doi file, doi ten) -> goi qua services/

Gom 3 buoc vao 1 CLASS (khong phai 3 ham doc lap o ngoai) vi can DUNG CHUNG
1 driver (fixture scope="class" trong conftest.py) de giu nguyen trang thai
dang nhap xuyen suot ca 3 buoc - neu tach thanh 3 ham doc lap voi fixture
scope mac dinh, moi ham se bi cap 1 Chrome MOI, mat dang nhap giua cac buoc.
"""

from configs.settings import GITHUB_USERNAME, GITHUB_PASSWORD
from core.logger import get_logger
from pages.login_page import LoginPage
from pages.search_page import SearchPage
from pages.release_page import ReleasePage
from services import file_service
from utils.datetime_helper import get_today_str

logger = get_logger(__name__)


class TestGithubBootstrapDownload:
    """
    Kich ban lien tuc: login -> search Bootstrap -> tai release moi nhat.
    Chia thanh 3 ham test_xxx() rieng de neu buoc nao fail, biet ngay
    CHINH XAC buoc do (thay vi 1 ham to gom het, kho debug).
    """

    def test_01_login(self, driver):
        """Buoc 1: Dang nhap GitHub. Goi THANG pages/login_page.py (chi can UI)."""
        login_page = LoginPage(driver)
        login_page.open_login_page()
        login_page.login(GITHUB_USERNAME, GITHUB_PASSWORD)

        assert login_page.is_logged_in(), (
            "Login GitHub that bai - kiem tra lai GITHUB_USERNAME/GITHUB_PASSWORD "
            "trong .env, hoac tai khoan co dang bat 2FA khong (xem canh bao "
            "trong pages/login_page.py)."
        )

    def test_02_search_bootstrap(self, driver):
        """Buoc 2a: Tim kiem 'Bootstrap', vao repo dau tien. Goi THANG pages/search_page.py."""
        search_page = SearchPage(driver)
        search_page.open_home()
        search_page.search_and_open_first_result("Bootstrap")

        assert "bootstrap" in driver.current_url.lower(), (
            f"Khong vao dung trang repo Bootstrap, URL hien tai: {driver.current_url}"
        )

    def test_03_download_and_rename(self, driver):
        """
        Buoc 2b: Vao trang release moi nhat, lay version, tai file .zip,
        doi ten dung format. Ket hop pages/release_page.py (UI, can driver)
        + services/file_service.py (xu ly file, KHONG can driver).
        """
        release_page = ReleasePage(driver)

        file_service.prepare_download_folder()

        release_page.open_latest_release()
        version = release_page.get_latest_version()
        release_page.download_source_zip()

        new_filename = f"{get_today_str()}_ThuVien_Bootstrap_v{version}.zip"
        zip_path = file_service.wait_and_rename(new_filename)

        assert zip_path.exists(), f"File .zip khong duoc tao ra: {zip_path}"
        logger.info("Test hoan tat, file da san sang: %s", zip_path)