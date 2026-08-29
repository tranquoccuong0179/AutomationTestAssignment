"""
smtp_client.py: Ket noi va gui email qua giao thuc SMTP thuan tuy.

CHI biet: nhan subject/body/attachment -> gui di.
KHONG biet: noi dung email la PASSED hay FAILED (do la viec cua services/email_service.py).

Cach dung o noi khac:
    from utils.smtp_client import send_email

    send_email(
        subject="Automation Test Result - PASSED",
        body_html="<h1>Test passed</h1>",
        attachments=["downloads/20260827_ThuVien_Bootstrap_v5.3.8.zip"]
    )
"""

import smtplib
import mimetypes
from email.message import EmailMessage
from pathlib import Path
from typing import List, Optional

from configs.settings import (
    SMTP_HOST,
    SMTP_PORT,
    SMTP_USERNAME,
    SMTP_PASSWORD,
    EMAIL_FROM,
    EMAIL_TO,
)
from core.logger import get_logger

logger = get_logger(__name__)


def _attach_file(message: EmailMessage, file_path: str) -> None:
    """Doc 1 file tu disk va dinh kem vao email message."""
    path = Path(file_path)
    if not path.exists():
        logger.warning("File dinh kem khong ton tai, bo qua: %s", file_path)
        return

    mime_type, _ = mimetypes.guess_type(path.name)
    maintype, subtype = (mime_type or "application/octet-stream").split("/", 1)

    with open(path, "rb") as f:
        message.add_attachment(
            f.read(), maintype=maintype, subtype=subtype, filename=path.name
        )
    logger.debug("Da dinh kem file: %s", path.name)


def send_email(
    subject: str,
    body_html: str,
    attachments: Optional[List[str]] = None,
    to_email: Optional[str] = None,
) -> bool:
    """
    Gui 1 email qua SMTP.

    Tra ve True neu gui thanh cong, False neu that bai
    (khong raise exception de khong lam crash toan bo test suite
    chi vi ly do gui mail loi).
    """
    recipient = to_email or EMAIL_TO

    message = EmailMessage()
    message["Subject"] = subject
    message["From"] = EMAIL_FROM
    message["To"] = recipient
    message.set_content("Vui long xem noi dung o dinh dang HTML.")
    message.add_alternative(body_html, subtype="html")

    for file_path in attachments or []:
        _attach_file(message, file_path)

    try:
        logger.info("Dang ket noi SMTP: %s:%s", SMTP_HOST, SMTP_PORT)
        with smtplib.SMTP(SMTP_HOST, SMTP_PORT, timeout=30) as server:
            server.starttls()
            server.login(SMTP_USERNAME, SMTP_PASSWORD)
            server.send_message(message)

        logger.info("Da gui email thanh cong den %s (subject=%s)", recipient, subject)
        return True

    except Exception as e:
        logger.error("Gui email that bai: %s", str(e))
        return False