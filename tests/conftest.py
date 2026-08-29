"""
conftest.py: File dac biet pytest TU DONG nhan dien (khong can import thu cong).

Chua 2 loai:
1. FIXTURE - chuan bi san "driver" (mo Chrome dau test, dong cuoi test) de
   moi ham test_xxx() trong tests/ chi can khai bao tham so "driver" la dung duoc.
2. HOOK - cac ham dac biet pytest TU GOI dung luc trong vong doi chay test:
   - pytest_sessionstart      -> luc BAT DAU ca phien test
   - pytest_runtest_makereport -> ngay SAU MOI test (dung de bat fail + chup anh)
   - pytest_terminal_summary   -> luc KET THUC ca phien, co san so lieu tong ket THAT

Hook o day CHI goi cac ham PLAIN cua services.report_service.collector
(start, finish, record_failure) - KHONG tu tinh toan logic nghiep vu gi,
dung nguyen tac da thong nhat: pytest tu lam viec cua no, minh chi "phu 1 tay"
lay du lieu THAT tu pytest, dua vao collector de dung sau nay (run.py doc lai).
"""

import pytest

from core.driver_factory import create_driver
from core.logger import get_logger
from services.report_service import collector
from utils.screenshot_helper import capture_screenshot

logger = get_logger(__name__)


@pytest.fixture
def driver():
    """
    Fixture tao driver Chrome cho MOI ham test_xxx() co khai bao tham so "driver".
    yield tra driver ve cho test dung, sau khi test XONG (du pass hay fail),
    code sau dong yield se chay de dong driver - dam bao KHONG bao gio
    quen quit(), tranh rac Chrome process con sot lai.
    """
    logger.info("Fixture 'driver': dang khoi tao Chrome...")
    drv = create_driver()
    yield drv
    logger.info("Fixture 'driver': dang dong Chrome...")
    drv.quit()


def pytest_sessionstart(session) -> None:
    """Hook pytest TU GOI ngay khi phien test BAT DAU. Ghi lai thoi diem bat dau."""
    collector.start()


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
    """
    Hook pytest TU GOI ngay SAU KHI 1 test chay xong (moi giai doan setup/call/teardown).
    Dung hookwrapper=True de lay duoc KET QUA CUOI CUNG (report) sau khi
    cac plugin khac (vd: pytest-html) da xu ly xong.

    CHI xu ly khi report.when == "call" (giai doan chay THAN test, khong
    phai setup/teardown) VA report.failed (test that bai that su).
    """
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
    """
    Hook pytest TU GOI luc KET THUC ca phien test, SAU KHI da chay het moi test.
    terminalreporter.stats la noi PYTEST TU PHAN LOAI ket qua chinh xac
    (passed/failed/skipped/error) - doc truc tiep tu day, KHONG tu dem lai,
    tranh sai so nhu da phat hien truoc do.
    """
    stats = terminalreporter.stats
    collector.finish(
        passed=len(stats.get("passed") or []),
        failed=len(stats.get("failed") or []),
        skipped=len(stats.get("skipped") or []),
        error=len(stats.get("error") or []),
    )