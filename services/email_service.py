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


def notify_success(zip_path: str, summary: dict) -> bool:
    logger.info("Dang soan email PASSED...")

    artifact = Path(zip_path)
    if not artifact.is_file():
        logger.error("Khong tim thay file artifact: %s", artifact)
        return False
    
    template = _jinja_env.get_template("email_passed.html")
    body_html = template.render(
        zip_filename=artifact.name,
        environment=BROWSER.capitalize(),
        **summary,
    )

    return send_email(
        subject=SUBJECT_PASSED,
        body_html=body_html,
        attachments=[str(artifact)],
    )


def notify_failure(failed_step: str, error_message: str, screenshot_path: str, summary: dict) -> bool:
    logger.info("Dang soan email FAILED cho buoc: %s", failed_step)

    template = _jinja_env.get_template("email_failed.html")
    body_html = template.render(
        failed_step=failed_step,
        error_message=error_message,
        environment=BROWSER.capitalize(),
        **summary,
    )

    attachments = [screenshot_path] if screenshot_path else []

    return send_email(
        subject=SUBJECT_FAILED,
        body_html=body_html,
        attachments=attachments,
    )