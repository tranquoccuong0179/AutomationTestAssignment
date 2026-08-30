"""
report_service.py: KHO DU LIEU THUAN (data holder) cho ket qua 1 phien test.

QUAN TRONG - file nay KHONG PHAI la pytest plugin, KHONG dinh gi den
driver/Selenium - chi la 1 class de LUU va DINH DANG du lieu.

Cac hook pytest THAT (pytest_sessionstart, pytest_terminal_summary,
pytest_runtest_makereport) duoc dat trong tests/conftest.py - vi hook
pytest_runtest_makereport CAN truy cap "driver" de chup screenshot, dieu
do se vi pham quy tac "services/ khong dung driver" neu dat o day.
conftest.py GOI cac ham PLAIN cua class nay (start, finish, record_failure)
de ghi lai ket qua.

Dung 1 SINGLETON (collector, o cuoi file) de conftest.py (ghi) va run.py
(doc, sau khi pytest.main() chay xong) deu tham chieu DUNG 1 object.
"""

import time
from typing import Optional

from core.logger import get_logger
from utils.datetime_helper import format_duration, now_readable

logger = get_logger(__name__)


class ResultCollector:
    """
    Kho du lieu THUAN cho 1 phien chay test - khong dung pytest hook,
    khong dung driver. Chi co cac ham PLAIN de GHI (goi tu conftest.py)
    va DOC (goi tu run.py).
    """

    def __init__(self) -> None:
        self._start_time: Optional[float] = None
        self._end_time: Optional[float] = None
        self.total_tests: int = 0
        self.passed: int = 0
        self.failed: int = 0
        self.skipped: int = 0
        self.error: int = 0
        self.failures: list[dict] = []
        self.artifact_path: str = ""

    def start(self) -> None:
        """
        Ghi lai thoi diem bat dau va RESET toan bo state cu ve 0.

        Bat buoc phai reset vi collector la SINGLETON (dung chung, khong
        tao moi moi lan chay) - neu khong, du lieu (dac biet la failures)
        tu lan chay TRUOC se con sot, lam sai ket qua cua lan chay nay.
        """
        self._start_time = time.time()
        self._end_time = None
        self.total_tests = 0
        self.passed = 0
        self.failed = 0
        self.skipped = 0
        self.error = 0
        self.failures.clear()
        self.artifact_path = ""
        logger.info("Bat dau phien test luc: %s", now_readable())

    def finish(self, passed: int, failed: int, skipped: int = 0, error: int = 0) -> None:
        """
        Ghi lai ket qua CUOI CUNG - cac tham so nay PHAI lay tu
        terminalreporter.stats (pytest tu phan loai chinh xac), KHONG tu
        dem/tu suy luan lai.
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
        Ghi lai chi tiet 1 test bi fail. Goi tu conftest.py (hook
        pytest_runtest_makereport) - hook do can driver de chup anh, nen
        CHI nhan KET QUA (duong dan anh) da chup san, khong tu chup o day.
        """
        self.failures.append({
            "failed_step": failed_step,
            "error_message": error_message,
            "screenshot_path": screenshot_path,
        })
        logger.error("Ghi nhan test fail: %s | Loi: %s", failed_step, error_message)

    def record_artifact(self, path) -> None:
        """
        Ghi lai duong dan file .zip da tai/doi ten thanh cong - de run.py
        biet duoc file nao can dinh kem khi goi email_service.notify_success(),
        vi collector khong tu chay Selenium nen khong the tu biet duong dan
        nay - phai duoc test_github_release.py CHU DONG bao lai sau khi
        file_service.wait_and_rename() tra ve.
        """
        self.artifact_path = str(path)
        logger.info("Ghi nhan file ket qua: %s", self.artifact_path)

    def get_first_failure(self) -> dict:
        """Tra ve chi tiet test fail dau tien (dung cho notify_failure())."""
        if not self.failures:
            return {
                "failed_step": "Khong xac dinh",
                "error_message": "Khong co chi tiet loi",
                "screenshot_path": "",
            }
        return self.failures[0]

    def get_execution_time(self) -> str:
        """Tra ve thoi gian chay dang HH:MM:SS."""
        if self._start_time is None or self._end_time is None:
            logger.warning("Chua goi start()/finish() day du, tra ve 00:00:00")
            return "00:00:00"
        return format_duration(self._start_time, self._end_time)

    def is_all_passed(self) -> bool:
        """
        True neu tat ca test deu PASS hop le:
        - Khong co test FAIL hoac ERROR.
        - Co it nhat 1 test PASS THAT SU (khong tinh la "toan bo pass" neu
          moi test deu bi SKIP - tranh gui nham email "PASSED" khi thuc ra
          khong co gi duoc xac nhan chay dung).
        """
        return self.failed == 0 and self.error == 0 and self.passed > 0

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