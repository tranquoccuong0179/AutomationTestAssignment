"""
test_github_release.py: Kich ban test chinh, thuc hien dung 3 buoc de bai yeu cau:
    1. Login GitHub
    2. Search "Bootstrap", vao repo, vao trang release moi nhat, tai file .zip
    3. Doi ten file dung format yyyyMMdd_ThuVien_Bootstrap_v{version}.zip

QUY UOC KIEN TRUC:
    - Buoc CHI can thao tac UI don thuan (login, search) -> goi THANG pages/
    - Buoc co THEM logic xu ly ngoai UI (doi file, doi ten) -> goi qua services/
    - KHONG gui email o day - email chi duoc gui tu run.py, SAU KHI toan bo
      pytest chay xong (xem services/report_service.py va run.py).
    - test_03 CHU DONG bao lai duong dan file .zip cho collector (qua
      record_artifact()), de run.py biet file nao can dinh kem khi PASS.
"""

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
    """
    Kich ban lien tuc: login -> search Bootstrap -> tai release moi nhat.
    Chia thanh 3 ham test_xxx() rieng de neu buoc nao fail, biet ngay
    CHINH XAC buoc do.
    """

    def test_01_login(self, driver):
        """
        Buoc 1: Dang nhap GitHub.

        Neu tai khoan (du khong bat 2FA) van bi GitHub hoi "xac minh thiet
        bi la" (mot lan duy nhat cho thiet bi/trinh duyet moi - xem giai
        thich chi tiet da trao doi truoc do), vong lap duoi day cho toi da
        45 GIAY THAT SU de nguoi van hanh kip xac nhan thu cong tren man
        hinh trinh duyet dang mo, thay vi that bai ngay lap tuc.

        LUU Y: day CHI la co che PHONG THU cho lan chay DAU TIEN tren 1
        thiet bi/profile moi. Muc tieu chinh van la dung tai khoan test
        KHONG 2FA + Chrome profile co dinh (xem core/driver_factory.py)
        de KHONG BAO GIO can can thiep thu cong trong cac lan chay sau.
        """
        login_page = LoginPage(driver)
        login_page.open_login_page()
        login_page.login(GITHUB_USERNAME, GITHUB_PASSWORD)

        logger.info(">>> Neu bi hoi xac minh thiet bi, xac nhan thu cong trong 45s... <<<")
        logged_in = False
        for _ in range(45):
          if login_page.is_logged_in(timeout=1):
              logged_in = True
              break

        assert logged_in, "Login GitHub that bai - Het thoi gian cho hoac thong tin sai."

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

        # Bao lai duong dan file cho collector, de run.py biet file nao
        # can dinh kem khi goi email_service.notify_success()
        collector.record_artifact(zip_path)

        logger.info("Test hoan tat, file da san sang: %s", zip_path)