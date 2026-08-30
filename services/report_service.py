import time
from typing import Optional

from core.logger import get_logger
from utils.datetime_helper import format_duration, now_readable

logger = get_logger(__name__)


class ResultCollector:
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
        self.failures.append({
            "failed_step": failed_step,
            "error_message": error_message,
            "screenshot_path": screenshot_path,
        })
        logger.error("Ghi nhan test fail: %s | Loi: %s", failed_step, error_message)

    def record_artifact(self, path) -> None:
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
        if self._start_time is None or self._end_time is None:
            logger.warning("Chua goi start()/finish() day du, tra ve 00:00:00")
            return "00:00:00"
        return format_duration(self._start_time, self._end_time)

    def is_all_passed(self) -> bool:
        return self.failed == 0 and self.error == 0 and self.passed > 0

    def to_summary_dict(self) -> dict:
        return {
            "execution_time": self.get_execution_time(),
            "total_tests": self.total_tests,
            "passed": self.passed,
            "failed": self.failed,
            "skipped": self.skipped,
            "error": self.error,
            "is_all_passed": self.is_all_passed(),
            "artifact_path": self.artifact_path,
        }

collector = ResultCollector()