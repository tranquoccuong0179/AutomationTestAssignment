"""
run.py: Entry point DUY NHAT cua toan bo automation framework.

Luong xu ly:
    1. Validate .env da du thong tin chua (fail SOM neu thieu config, thay
       vi de Selenium/SMTP bao loi kho hieu ve sau giua chung qua trinh).
    2. Chay toan bo pytest (cac flag --html, testpaths... da cau hinh san
       trong pytest.ini). Trong luc chay, tests/conftest.py TU DONG ghi
       nhan ket qua (passed/failed/skipped, chi tiet loi, duong dan file
       zip) vao services.report_service.collector qua cac hook pytest.
    3. Sau khi pytest.main() TRA VE (nghia la da chay xong HOAN TOAN),
       doc lai collector - KHONG tu doan/tu tinh gi them, chi dung du lieu
       THAT da duoc ghi nhan trong buoc 2.
    4. Neu TOAN BO PASS -> goi email_service.notify_success(), dinh kem
       file .zip da tai.
       Neu CO FAIL -> goi email_service.notify_failure() voi chi tiet loi
       DAU TIEN (buoc nao, loi gi, screenshot dau).

Cach chay:
    python run.py
"""

import sys

import pytest

from configs import settings
from core.logger import get_logger
from services import email_service
from services.report_service import collector
from pathlib import Path

logger = get_logger(__name__)


def main() -> int:
    try:
        settings.validate()
    except EnvironmentError as e:
        logger.error("Cau hinh .env chua day du, dung lai truoc khi chay: %s", e)
        return 1

    logger.info("=" * 60)
    logger.info("BAT DAU CHAY AUTOMATION TEST SUITE")
    logger.info("=" * 60)

    Path("reports/html").mkdir(parents=True, exist_ok=True)

    # exit_code = pytest.main()
    exit_code = pytest.main(
        ["-v", "--html=reports/html/report.html", "--self-contained-html"]
    )
    summary = collector.to_summary_dict()
    logger.info("Ket qua sau khi pytest chay xong: %s", summary)

    if collector.is_all_passed():
        zip_path = collector.artifact_path
        if not zip_path:
            logger.warning(
                "Toan bo test PASS nhung khong ghi nhan duoc duong dan file .zip "
                "(co the test_03_download_and_rename khong goi collector.record_artifact())"
            )

        sent = email_service.notify_success(zip_path=zip_path, summary=summary)
        logger.info("Da gui email PASSED: %s", "thanh cong" if sent else "THAT BAI")

    else:
        failure = collector.get_first_failure()
        sent = email_service.notify_failure(
            failed_step=failure["failed_step"],
            error_message=failure["error_message"],
            screenshot_path=failure["screenshot_path"],
            summary=summary,
        )
        logger.info("Da gui email FAILED: %s", "thanh cong" if sent else "THAT BAI")

    logger.info("=" * 60)
    logger.info("HOAN TAT. Xem chi tiet: reports/html/report.html")
    logger.info("=" * 60)

    return exit_code


if __name__ == "__main__":
    sys.exit(main())