"""
email_service.py: Dieu phoi luong "soan va gui email ket qua test".

Ket hop: constants/ (subject) + templates/ (khung HTML) + jinja2 (render)
+ utils/smtp_client.py (gui thuc su) thanh 1 luong hoan chinh.

KHAC voi utils/smtp_client.py (chi biet gui payload tho) - file nay BIET RO
nghiep vu: PASSED thi soan gi, FAILED thi soan gi, dinh kem file nao.

Cach dung o tests/ hoac run.py:
    from services.email_service import notify_success, notify_failure

    notify_success(zip_path="downloads/20260827_ThuVien_Bootstrap_v5.3.8.zip",
                    execution_time="00:05:32", total_tests=4)

    notify_failure(failed_step="test_02_search_and_download",
                    error_message="TimeoutException: khong tim thay nut Download",
                    screenshot_path="reports/screenshots/test_02_xxx.png",
                    execution_time="00:02:10")
"""

from pathlib import Path

from jinja2 import Environment, FileSystemLoader

from configs.settings import BROWSER
from constants.email_templates import SUBJECT_PASSED, SUBJECT_FAILED
from core.logger import get_logger
from utils.smtp_client import send_email

logger = get_logger(__name__)

BASE_DIR = Path(__file__).resolve().parent.parent
TEMPLATES_DIR = BASE_DIR / "templates"

_jinja_env = Environment(loader=FileSystemLoader(str(TEMPLATES_DIR)))


def notify_success(zip_path: str, execution_time: str, total_tests: int) -> bool:
    logger.info("Dang soan email PASSED...")

    # SỬA LẠI THÀNH email_passed.html
    template = _jinja_env.get_template("email_passed.html")

    zip_name = Path(zip_path).name if zip_path else "No file"

    body_html = template.render(
        execution_time=execution_time,
        total_tests=total_tests,
        zip_filename=zip_name,
        environment=BROWSER.capitalize(),
    )

    attachments = [zip_path] if zip_path and Path(zip_path).is_file() else []

    return send_email(
        subject=SUBJECT_PASSED,
        body_html=body_html,
        attachments=attachments,
    )


def notify_failure(
    failed_step: str, error_message: str, screenshot_path: str, execution_time: str
) -> bool:
    """
    Soan va gui email bao FAILED, dinh kem anh chup man hinh luc loi.
    Neu screenshot_path rong "" (chup that bai), van gui email nhung khong dinh kem anh.
    """
    logger.info("Dang soan email FAILED cho buoc: %s", failed_step)

    template = _jinja_env.get_template("email_failed.html")
    body_html = template.render(
        execution_time=execution_time,
        failed_step=failed_step,
        error_message=error_message,
        environment=BROWSER.capitalize(),
    )

    attachments = [screenshot_path] if screenshot_path else []

    return send_email(
        subject=SUBJECT_FAILED,
        body_html=body_html,
        attachments=attachments,
    )