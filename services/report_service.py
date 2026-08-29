"""
report_service.py: KHO DU LIEU THUAN (data holder) cho ket qua 1 phien test.

QUAN TRONG - file nay KHONG PHAI la pytest plugin, KHONG dinh gi den
driver/Selenium - chi la 1 class de LUU va DINH DANG du lieu, dung nguyen
tac "services/ khong bao gio dung driver" da thong nhat xuyen suot project.

Cac hook pytest THAT (pytest_sessionstart, pytest_terminal_summary,
pytest_runtest_makereport) duoc dat trong tests/conftest.py - vi hook
pytest_runtest_makereport CAN truy cap "driver" (qua item.funcargs) de
chup screenshot, ma dieu do vi pham quy tac "services/ khong dung driver"
neu dat o day. conftest.py se GOI cac ham PLAIN (khong phai hook) cua class
nay (start(), finish(), record_failure()) de ghi lai ket qua.

Dung 1 INSTANCE DUNG CHUNG (singleton o cuoi file) de ca conftest.py (ghi
du lieu vao) va run.py (doc du lieu ra, sau khi pytest.main() chay xong)
deu tham chieu DUNG 1 object nay - khong tao instance moi o tung noi.

Cach dung o tests/conftest.py (ghi du lieu):
    from services.report_service import collector

    def pytest_sessionstart(session):
        collector.start()

    def pytest_terminal_summary(terminalreporter, exitstatus, config):
        collector.finish(
            passed=len(terminalreporter.stats.get("passed", [])),
            failed=len(terminalreporter.stats.get("failed", [])),
            skipped=len(terminalreporter.stats.get("skipped", [])),
            error=len(terminalreporter.stats.get("error", [])),
        )

Cach dung o run.py (doc du lieu, SAU KHI pytest.main() chay xong):
    from services.report_service import collector

    summary = collector.to_summary_dict()
    if collector.is_all_passed():
        email_service.notify_success(zip_path=..., summary=summary)
    else:
        failure = collector.get_first_failure()
        email_service.notify_failure(
            failed_step=failure["failed_step"],
            error_message=failure["error_message"],
            screenshot_path=failure["screenshot_path"],
            summary=summary,
        )
"""

import time

from core.logger import get_logger
from utils.datetime_helper import format_duration, now_readable

logger = get_logger(__name__)


class ResultCollector:
    """
    Kho du lieu THUAN cho 1 phien chay test - khong dung pytest hook,
    khong dung driver. Chi co cac ham PLAIN de GHI (goi tu conftest.py)
    va DOC (goi tu run.py).
    """

    def __init__(self):
        self._start_time: float = None
        self._end_time: float = None
        self.total_tests: int = 0
        self.passed: int = 0
        self.failed: int = 0
        self.skipped: int = 0
        self.error: int = 0
        self.failures: list = []   # danh sach dict, moi phan tu la 1 test bi fail

    def start(self) -> None:
        """
        Ghi lai thoi diem bat dau. Goi tu conftest.py, trong hook pytest_sessionstart.

        QUAN TRONG: vi collector la SINGLETON (dung chung, khong tao moi
        moi lan chay), can RESET toan bo du lieu cu ve 0 o day - neu khong,
        du lieu con sot tu lan chay pytest TRUOC (vd: failures cu) se lan
        vao ket qua cua lan chay nay, gay sai lech.
        """
        self._start_time = time.time()
        self._end_time = None
        self.total_tests = 0
        self.passed = 0
        self.failed = 0
        self.skipped = 0
        self.error = 0
        self.failures.clear()
        logger.info("Bat dau phien test luc: %s", now_readable())

    def finish(self, passed: int, failed: int, skipped: int = 0, error: int = 0) -> None:
        """
        Ghi lai ket qua CUOI CUNG - cac tham so nay PHAI lay tu
        terminalreporter.stats (xem docstring dau file), KHONG tu dem/tu
        suy luan lai (tranh sai so khi co test Skip/Error).
        """
        self._end_time = time.time()
        self.passed = passed
        self.failed = failed
        self.skipped = skipped
        self.error = error
        self.total_tests = passed + failed + skipped + error
        logger.info(
            "Ket thuc phien test luc: %s (passed=%s, failed=%s, skipped=%s, error=%s)",
            now_readable(), passed, failed, skipped, error,
        )

    def record_failure(self, failed_step: str, error_message: str, screenshot_path: str) -> None:
        """
        Ghi lai chi tiet 1 test bi fail (buoc nao, loi gi, screenshot dau).
        Goi tu conftest.py, trong hook pytest_runtest_makereport - vi hook
        do can driver (de chup anh), nen KHONG dat logic chup anh o day,
        chi nhan KET QUA (duong dan anh) da duoc chup san tu ben ngoai.
        """
        self.failures.append({
            "failed_step": failed_step,
            "error_message": error_message,
            "screenshot_path": screenshot_path,
        })
        logger.error("Ghi nhan test fail: %s | Loi: %s", failed_step, error_message)

    def get_first_failure(self) -> dict:
        """
        Tra ve chi tiet CUA TEST FAIL DAU TIEN (dung cho notify_failure(),
        vi email chi bao 1 loi dai dien, khong liet ke het moi loi neu co
        nhieu test cung fail).
        Tra ve dict rong neu khong co fail nao duoc ghi nhan.
        """
        if not self.failures:
            return {"failed_step": "Khong xac dinh", "error_message": "Khong co chi tiet loi", "screenshot_path": ""}
        return self.failures[0]

    def get_execution_time(self) -> str:
        """Tra ve thoi gian chay dang HH:MM:SS."""
        if self._start_time is None or self._end_time is None:
            logger.warning("Chua goi start()/finish() day du, tra ve 00:00:00")
            return "00:00:00"
        return format_duration(self._start_time, self._end_time)

    def is_all_passed(self) -> bool:
        """True neu khong co test nao FAIL hoac ERROR (skip khong tinh la that bai)."""
        return self.failed == 0 and self.error == 0 and self.total_tests > 0

    def to_summary_dict(self) -> dict:
        """Dong goi ket qua thanh 1 dict (DTO), dua vao email_service.py qua **summary."""
        return {
            "execution_time": self.get_execution_time(),
            "total_tests": self.total_tests,
            "passed": self.passed,
            "failed": self.failed,
            "skipped": self.skipped,
            "error": self.error,
            "is_all_passed": self.is_all_passed(),
        }


# Singleton dung chung - conftest.py GHI vao, run.py DOC ra tu CHINH instance nay.
collector = ResultCollector()