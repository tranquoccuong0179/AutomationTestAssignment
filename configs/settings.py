import os
from pathlib import Path
from dotenv import load_dotenv

# Tim va load file .env o thu muc goc project
BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")


def _get_bool(key: str, default: bool = False) -> bool:
    """Chuyen gia tri string trong .env ('true'/'false') thanh bool."""
    value = os.getenv(key, str(default))
    return value.strip().lower() in ("1", "true", "yes")


def _get_int(key: str, default: int) -> int:
    """Chuyen gia tri string trong .env thanh int, fallback ve default neu loi."""
    try:
        return int(os.getenv(key, default))
    except (TypeError, ValueError):
        return default


# ==== GitHub credentials ====
GITHUB_USERNAME = os.getenv("GITHUB_USERNAME", "")
GITHUB_PASSWORD = os.getenv("GITHUB_PASSWORD", "")

# ==== Browser config ====
BROWSER = os.getenv("BROWSER", "chrome").lower()
HEADLESS = _get_bool("HEADLESS", default=False)
IMPLICIT_WAIT = _get_int("IMPLICIT_WAIT", default=10)

# ==== Download config ====
DOWNLOAD_DIR = str((BASE_DIR / os.getenv("DOWNLOAD_DIR", "./downloads")).resolve())

# ==== SMTP config ====
SMTP_HOST = os.getenv("SMTP_HOST", "")
SMTP_PORT = _get_int("SMTP_PORT", default=587)
SMTP_USERNAME = os.getenv("SMTP_USERNAME", "")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD", "")
EMAIL_FROM = os.getenv("EMAIL_FROM", "")
EMAIL_TO = os.getenv("EMAIL_TO", "")


def validate() -> None:
    """
    Kiem tra nhanh cac bien bat buoc da duoc dien chua.
    Goi ham nay o dau run.py de fail som neu thieu config,
    thay vi de Selenium/SMTP bao loi kho hieu ve sau.
    """
    missing = []
    required = {
        "GITHUB_USERNAME": GITHUB_USERNAME,
        "GITHUB_PASSWORD": GITHUB_PASSWORD,
        "SMTP_HOST": SMTP_HOST,
        "EMAIL_FROM": EMAIL_FROM,
        "EMAIL_TO": EMAIL_TO,
    }
    for key, value in required.items():
        if not value:
            missing.append(key)
    if missing:
        raise EnvironmentError(
            f"Thieu bien moi truong trong .env: {', '.join(missing)}. "
            f"Hay copy .env.example thanh .env va dien day du."
        )