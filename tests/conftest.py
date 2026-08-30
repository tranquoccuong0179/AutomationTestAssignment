import pytest

from core.driver_factory import create_driver
from core.logger import get_logger
from services.report_service import collector
from utils.screenshot_helper import capture_screenshot

logger = get_logger(__name__)


@pytest.fixture(scope="class")
def driver():
    logger.info("Fixture 'driver': dang khoi tao Chrome...")
    drv = create_driver()
    yield drv
    logger.info("Fixture 'driver': dang dong Chrome...")
    drv.quit()


def pytest_sessionstart(session) -> None:
    collector.start()


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
    outcome = yield
    report = outcome.get_result()

    if report.when == "call" and report.failed:
        driver_instance = item.funcargs.get("driver")
        screenshot_path = ""

        if driver_instance:
            screenshot_path = capture_screenshot(driver_instance, test_name=item.name)
        else:
            logger.warning("Test fail nhung khong tim thay fixture 'driver' de chup anh")

        error_message = str(call.excinfo.value) if call.excinfo else "Khong xac dinh duoc loi"

        collector.record_failure(
            failed_step=item.nodeid,
            error_message=error_message,
            screenshot_path=screenshot_path,
        )


def pytest_terminal_summary(terminalreporter, exitstatus, config) -> None:
    stats = terminalreporter.stats
    collector.finish(
        passed=len(stats.get("passed") or []),
        failed=len(stats.get("failed") or []),
        skipped=len(stats.get("skipped") or []),
        error=len(stats.get("error") or []),
    )