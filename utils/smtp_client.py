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
    path = Path(file_path)
    if not path.is_file():
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

    except (smtplib.SMTPException, OSError) as e:
        logger.error("Gui email that bai: %s", str(e))
        return False