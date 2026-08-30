import sys
from pathlib import Path

import pytest

from configs import settings
from core.logger import get_logger
from services import email_service
from services.report_service import collector

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

    exit_code = pytest.main(
        ["-v", "-s", "--html=reports/html/report.html", "--self-contained-html"]
    )
    summary = collector.to_summary_dict()
    logger.info("Ket qua sau khi pytest chay xong: %s", summary)

    sent = False
    if exit_code == 0 and collector.is_all_passed():
        if not collector.artifact_path:
            logger.error("Toan bo test PASS nhung khong ghi nhan duoc file artifact")
            return 1
        sent = email_service.notify_success(zip_path=collector.artifact_path, summary=summary)
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

    if not sent:
        return 1
    
    logger.info("=" * 60)
    logger.info("HOAN TAT. Xem chi tiet: reports/html/report.html")
    logger.info("=" * 60)

    return int(exit_code)

if __name__ == "__main__":
    sys.exit(main())