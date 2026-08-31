# GitHub Latest Release Automation

Automation test project sử dụng **Python, Selenium WebDriver và Pytest** để tự động đăng nhập GitHub, tìm kiếm repository, xác định release mới nhất, tải **Source code (zip)**, đổi tên artifact theo quy ước và gửi email thông báo kết quả **PASSED / FAILED**.

Project được tổ chức theo **Page Object Model (POM)** và tách riêng các trách nhiệm về browser interaction, file handling, reporting, logging và email notification nhằm đảm bảo code **Clean, Maintainable, Reusable, Stable và Scalable** trong phạm vi automation assignment.

## Table of Contents

- [1. Project Overview](#1-project-overview)
- [2. Folder Structure](#2-folder-structure)
- [3. Prerequisites & Installation](#3-prerequisites--installation)
- [4. How to Run](#4-how-to-run)
- [5. Reports & Artifacts](#5-reports--artifacts)
- [6. Environment Variables](#6-environment-variables)
- [7. Troubleshooting](#7-troubleshooting)
- [8. Main Dependencies](#8-main-dependencies)
- [Quick Start](#quick-start)

---

## 1. Project Overview

### 1.1. Automation flow

Flow chính hiện tại được triển khai cho thư viện **Bootstrap**:

1. Mở `https://github.com/`.
2. Click **Sign in** và đăng nhập GitHub.
3. Mở GitHub Search và tìm `Bootstrap`.
4. Mở repository hợp lệ đầu tiên trong kết quả tìm kiếm.
5. Điều hướng đến release được đánh dấu **Latest**.
6. Xác định version mới nhất từ release URL.
7. Tải **Source code (zip)**.
8. Chờ Chrome download hoàn tất.
9. Đổi tên ZIP theo format:

   ```text
   yyyyMMdd_ThuVien_Bootstrap_v<version>.zip
   ```

   Ví dụ:

   ```text
   20260831_ThuVien_Bootstrap_v5.3.8.zip
   ```

10. Nếu test **PASSED**:
    - Generate HTML report.
    - Gửi email subject `Automation Test Result – PASSED`.
    - Đính kèm ZIP artifact nếu SMTP attachment thành công.
    - Nếu attachment gặp lỗi, retry email PASSED không kèm file.
11. Nếu test **FAILED**:
    - Ghi nhận bước đang thực hiện.
    - Ghi nhận exception/error message.
    - Chụp screenshot browser.
    - Gửi email subject `[Automation] Test Execution – FAILED` kèm screenshot nếu có.

### 1.2. Technical highlights

- Selenium WebDriver điều khiển Google Chrome.
- Page Object Model cho Home, Login, Search và Release pages.
- Explicit wait với `WebDriverWait`.
- UI-first strategy kết hợp URL fallback tại các bước cần tăng độ ổn định.
- Theo dõi `.crdownload` để xác định download đã hoàn tất.
- HTML report bằng `pytest-html`.
- Centralized logging ra console và file.
- `ResultCollector` theo dõi execution time, test result, failed step và artifact.
- SMTP notification sử dụng HTML template bằng Jinja2.
- Credentials/config tách khỏi source qua `.env`.
- Date/time sử dụng timezone `Asia/Ho_Chi_Minh`.

---

## 2. Folder Structure

```text
AssignmentSelenium/
├── configs/                              # Quản lý cấu hình runtime của automation
│   ├── __init__.py                       # Đánh dấu configs là Python package
│   └── settings.py                       # Load .env, parse config và validate biến môi trường bắt buộc
│
├── constants/                            # Các giá trị cố định dùng chung trong project
│   └── email_templates.py                # Khai báo subject email PASSED / FAILED
│
├── core/                                 # Thành phần nền tảng dùng chung cho Selenium framework
│   ├── __init__.py                       # Đánh dấu core là Python package
│   ├── base_page.py                      # Các thao tác Selenium dùng chung: wait, click, input, scroll...
│   ├── driver_factory.py                 # Khởi tạo và cấu hình Chrome WebDriver
│   └── logger.py                         # Cấu hình centralized logging cho console và file
│
├── docs/                                 # Tài liệu phục vụ review và bàn giao project
│   └── TestCases.xlsx                    # Danh sách test case, expected result, status và evidence
│
├── pages/                                # Page Object Model
│   └── github/                           # Các Page Object dành cho GitHub
│       ├── __init__.py                   # Đánh dấu github là Python package
│       ├── home_page.py                  # Mở GitHub homepage và click Sign in
│       ├── login_page.py                 # Nhập credentials, submit và verify login
│       ├── search_page.py                # Search repository và mở kết quả hợp lệ đầu tiên
│       └── release_page.py               # Mở Latest release, lấy version và download Source code ZIP
│
├── services/                             # Business services không phụ thuộc trực tiếp vào UI locator
│   ├── __init__.py                       # Đánh dấu services là Python package
│   ├── email_service.py                  # Render và gửi email PASSED / FAILED
│   ├── file_service.py                   # Chuẩn bị download folder, chờ file và đổi tên artifact
│   └── report_service.py                 # ResultCollector: lưu execution time, result, failed step, artifact
│
├── templates/                            # HTML template cho email notification
│   ├── email_failed.html                 # Nội dung email khi automation FAILED
│   └── email_passed.html                 # Nội dung email khi automation PASSED
│
├── tests/                                # Pytest test suite
│   ├── conftest.py                       # WebDriver fixture, pytest hooks, screenshot và result collection
│   └── test_github_release.py            # E2E testcase chính cho GitHub Bootstrap release flow
│
├── utils/                                # Các helper low-level có thể tái sử dụng
│   ├── __init__.py                       # Đánh dấu utils là Python package
│   ├── datetime_helper.py                # Date/time theo Asia/Ho_Chi_Minh và format execution time
│   ├── file_helper.py                    # Poll .crdownload/.zip, cleanup, sanitize và rename file
│   ├── screenshot_helper.py              # Capture screenshot khi test fail
│   └── smtp_client.py                    # Tạo email, attach file, STARTTLS, login và gửi SMTP
│
├── downloads/                            # Runtime: chứa ZIP đã tải và rename theo DOWNLOAD_DIR
├── reports/                              # Runtime: chứa report, log và screenshot
│   ├── html/                             # HTML report được generate bởi pytest-html
│   ├── logs/                             # Chứa automation.log
│   └── screenshots/                      # Screenshot được tạo khi test fail
│
├── .env                                  # Local config/credentials, không commit Git
├── .env.example                          # File mẫu để người dùng tạo .env
├── .gitignore                            # Ignore credentials, cache và runtime artifacts
├── pytest.ini                            # Pytest discovery và cấu hình HTML report
├── requirements.txt                      # Danh sách Python dependencies
├── run.py                                # Entry point: validate → pytest → summary → gửi email
└── README.md                             # Tài liệu hướng dẫn project
```

### Thành phần chính

**`configs/settings.py`**
- Load `.env` bằng `python-dotenv`.
- Parse boolean/integer configuration.
- Quản lý GitHub credentials, browser config, timeout, download directory và SMTP config.
- Resolve `DOWNLOAD_DIR` thành absolute path.
- `validate()` kiểm tra các biến bắt buộc trước khi chạy automation.

**`core/base_page.py`**
- Cung cấp các thao tác Selenium dùng chung như `open()`, `wait_visible()`, `wait_clickable()`, `safe_click()`, `input_text()`, `get_text()`, `is_element_present()` và `scroll_to()`.
- `safe_click()` có JavaScript fallback khi native Selenium click bị intercept.

**`core/driver_factory.py`**
- Khởi tạo Chrome WebDriver.
- Hỗ trợ headless mode.
- Cấu hình download trực tiếp vào `DOWNLOAD_DIR`.
- Sử dụng Selenium Manager nên thông thường không cần đặt `chromedriver.exe` thủ công trong project.

**`pages/github/`**
- Chứa toàn bộ locator và hành vi UI theo từng màn hình GitHub.
- Tách riêng Home, Login, Search và Release để dễ bảo trì khi UI thay đổi.

**`services/file_service.py`**
- Chuẩn bị download folder.
- Chờ Chrome download hoàn tất.
- Đổi tên ZIP artifact theo naming convention.

**`services/report_service.py`**
- Quản lý start/end time.
- Lưu số lượng passed/failed/skipped/error.
- Theo dõi automation step hiện tại.
- Ghi nhận failure detail và artifact path.
- Tạo summary dùng cho email notification.

**`services/email_service.py`**
- Render HTML email bằng Jinja2.
- Gửi PASSED email kèm ZIP artifact.
- Retry PASSED email không attachment nếu attachment send thất bại.
- Gửi FAILED email kèm screenshot nếu screenshot tồn tại.

**`tests/conftest.py`**
- Tạo và đóng Chrome WebDriver bằng Pytest fixture.
- Khởi tạo/kết thúc `ResultCollector`.
- Capture screenshot khi test fail.
- Ghi nhận failed step và exception message.

**`tests/test_github_release.py`**
- E2E testcase chính.
- Điều phối toàn bộ business flow từ login đến download/rename artifact.
- Gọi `collector.set_current_step()` để xác định chính xác bước lỗi khi test fail.

**`utils/file_helper.py`**
- Theo dõi `.crdownload` và `.zip`.
- Xác định download đã hoàn tất.
- Cleanup file cũ.
- Sanitize và rename filename.

**`utils/screenshot_helper.py`**
- Chụp browser screenshot khi test fail.
- Lưu screenshot vào `reports/screenshots/`.

**`utils/smtp_client.py`**
- Tạo `EmailMessage`.
- Attach file nếu có.
- Kết nối SMTP bằng STARTTLS.
- Login và gửi email.

---

## 3. Prerequisites & Installation

### 3.1. Prerequisites

- **Python 3.10+** (project đã được chạy thực tế với Python 3.12).
- **Google Chrome**.
- **Git** nếu clone project từ repository.
- Internet access tới GitHub và SMTP server.
- GitHub account hợp lệ.
- SMTP account hợp lệ.

> Virtual environment (`venv`) **không bắt buộc** để chạy project. Tuy nhiên, nên sử dụng nếu muốn cô lập dependencies của project khỏi Python environment chung trên máy.

### 3.2. Clone repository

```bash
git clone <repository-url>
cd AssignmentSelenium
```

### 3.3. Install dependencies

```bash
pip install -r requirements.txt
```

> Nếu máy có nhiều Python version, có thể dùng `python -m pip install -r requirements.txt` để đảm bảo package được cài đúng Python interpreter.

### 3.4. Create `.env`

Project không commit credentials lên Git. Sau khi clone, cần tạo file `.env` từ `.env.example`.

#### Windows PowerShell

```powershell
Copy-Item .env.example .env
```

#### Windows Command Prompt

```cmd
copy .env.example .env
```

#### macOS / Linux

```bash
cp .env.example .env
```

Sau đó cập nhật `.env`:

```env
# GitHub credentials
GITHUB_USERNAME=your_email@gmail.com
GITHUB_PASSWORD=your_github_password

# Browser config
BROWSER=chrome
HEADLESS=false
DEFAULT_TIMEOUT=10

# Download config
DOWNLOAD_DIR=./downloads

# SMTP config
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your_email@gmail.com
SMTP_PASSWORD=your_app_password
EMAIL_FROM=your_email@gmail.com
EMAIL_TO=recipient@example.com
```

> Không commit `.env`. File `.env.example` chỉ chứa giá trị mẫu và có thể commit lên repository.

### 3.5. Gmail SMTP

Nếu sử dụng Gmail, nên sử dụng **Google App Password** cho `SMTP_PASSWORD` thay vì password Google account thông thường.

Thông thường cần bật **2-Step Verification**, tạo App Password và điền giá trị đó vào:

```env
SMTP_PASSWORD=your_app_password
```

---

## 4. How to Run

Sau khi đã cài dependencies và cấu hình `.env`, chạy:

```bash
python run.py
```

`run.py` là entry point chính của project và thực hiện toàn bộ workflow:

```text
Validate .env
    ↓
Run Pytest
    ↓
Run Selenium E2E test
    ↓
Generate HTML report
    ↓
Collect test summary
    ↓
PASSED → Send PASSED email + ZIP artifact
FAILED → Send FAILED email + screenshot
```

Nếu `.env` thiếu biến bắt buộc, chương trình sẽ dừng trước khi Chrome được khởi tạo và hiển thị danh sách biến còn thiếu.

### Headless mode

Để chạy Chrome không hiển thị UI, sửa trong `.env`:

```env
HEADLESS=true
```

Sau đó chạy lại:

```bash
python run.py
```

### Custom download directory

Mặc định:

```env
DOWNLOAD_DIR=./downloads
```

Có thể thay bằng thư mục riêng, ví dụ:

```env
DOWNLOAD_DIR=./automation_downloads
```

`prepare_download_folder()` sẽ dọn file cũ trong `DOWNLOAD_DIR` trước khi testcase bắt đầu. Vì vậy `DOWNLOAD_DIR` nên là **folder riêng dành cho automation**, không nên trỏ tới thư mục có dữ liệu cần giữ lại.

---

## 5. Reports & Artifacts

### 5.1. Downloaded ZIP

Folder lưu artifact được cấu hình qua:

```env
DOWNLOAD_DIR=./downloads
```

Với cấu hình mặc định, file sau khi tải và rename nằm tại:

```text
downloads/
```

Ví dụ:

```text
downloads/20260831_ThuVien_Bootstrap_v5.3.8.zip
```

Naming convention:

```text
yyyyMMdd_ThuVien_<Library>_v<version>.zip
```

Ngày được tạo theo timezone `Asia/Ho_Chi_Minh`.

### 5.2. HTML Test Report

Pytest HTML report được generate tại:

```text
reports/html/report.html
```

Đây là self-contained HTML report và có thể mở trực tiếp bằng browser.

### 5.3. Automation Log

Execution log được lưu tại:

```text
reports/logs/automation.log
```

Log bao gồm:

- Browser lifecycle.
- Automation step hiện tại.
- Login/search/release navigation.
- Version được xác định.
- Download status.
- Artifact rename.
- Failure details.
- SMTP/email status.

### 5.4. Failure Screenshots

Khi testcase fail trong execution flow, browser screenshot được lưu tại:

```text
reports/screenshots/
```

Naming convention:

```text
<test_name>_yyyyMMdd_HHmmss.png
```

Ví dụ:

```text
reports/screenshots/test_github_bootstrap_download_20260831_164048.png
```

Screenshot được dùng làm attachment của FAILED email nếu capture thành công.

### 5.5. PASSED email

Subject:

```text
Automation Test Result – PASSED
```

Email bao gồm:

- Status: `PASSED`.
- Environment: `Chrome`.
- Execution Time.
- Artifact filename.
- ZIP attachment nếu SMTP gửi attachment thành công.

Nếu gửi attachment thất bại, automation retry gửi PASSED email không kèm attachment.

### 5.6. FAILED email

Subject:

```text
[Automation] Test Execution – FAILED
```

Email bao gồm:

- Status: `FAILED`.
- Environment.
- Execution Time.
- Failed step.
- Error message.
- Screenshot attachment nếu screenshot được capture thành công.

### 5.7. Runtime artifacts and Git

Các runtime folder:

```text
downloads/
reports/
```

được `.gitignore` để tránh commit file sinh ra sau mỗi lần chạy và giữ repository sạch.

---

## 6. Environment Variables

| Variable | Required | Description |
|---|---:|---|
| `GITHUB_USERNAME` | Yes | GitHub username/email dùng để login |
| `GITHUB_PASSWORD` | Yes | GitHub password |
| `BROWSER` | No | Browser environment; project hiện chạy Chrome |
| `HEADLESS` | No | `true` để chạy Chrome headless, default `false` |
| `DEFAULT_TIMEOUT` | No | Selenium explicit wait timeout, default `10` giây |
| `DOWNLOAD_DIR` | No | Download artifact directory, default `./downloads` |
| `SMTP_HOST` | Yes | SMTP server, ví dụ `smtp.gmail.com` |
| `SMTP_PORT` | No | SMTP port, default `587` |
| `SMTP_USERNAME` | Yes | SMTP login account |
| `SMTP_PASSWORD` | Yes | SMTP password/App Password |
| `EMAIL_FROM` | Yes | Sender email |
| `EMAIL_TO` | Yes | Recipient email |

---

## 7. Troubleshooting

### Missing environment configuration

Nếu automation dừng ngay khi start, kiểm tra các biến bắt buộc trong `.env`:

```text
GITHUB_USERNAME
GITHUB_PASSWORD
SMTP_HOST
SMTP_USERNAME
SMTP_PASSWORD
EMAIL_FROM
EMAIL_TO
```

### Chrome cannot start

Kiểm tra:

- Google Chrome đã được cài.
- Dependencies đã được cài bằng `requirements.txt`.
- Máy có internet để Selenium Manager resolve ChromeDriver khi cần.

```bash
pip install -r requirements.txt
```

### GitHub login failed

Kiểm tra GitHub credentials trong `.env`.

Nếu GitHub yêu cầu security verification/challenge cho account hoặc environment mới, automation có thể không hoàn tất login tự động.

### Download timeout

Kiểm tra:

- Internet connection.
- `DOWNLOAD_DIR` có quyền ghi file.
- Chrome download không bị system policy chặn.
- Latest release có Source code ZIP.

Download wait mặc định hiện tại là **60 giây**.

### SMTP failed

Với Gmail, kiểm tra:

```env
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your_email@gmail.com
SMTP_PASSWORD=your_app_password
```

Chi tiết lỗi được ghi tại:

```text
reports/logs/automation.log
```

---

## 8. Main Dependencies

| Package | Purpose |
|---|---|
| `selenium` | Browser automation |
| `pytest` | Test runner/framework |
| `pytest-html` | Generate self-contained HTML report |
| `python-dotenv` | Load `.env` configuration |
| `jinja2` | Render PASSED/FAILED email templates |
| `tzdata` | Timezone data cho `Asia/Ho_Chi_Minh` |

Version chi tiết được quản lý tại:

```text
requirements.txt
```

---

## Quick Start

```bash
git clone <repository-url>
cd AssignmentSelenium

pip install -r requirements.txt

Tạo tệp `.env` tại thư mục gốc dự án dựa theo mẫu `.env.example` và điền cấu hình
# Cập nhật credentials/config trong .env

python run.py
```

Sau khi chạy, các output chính nằm tại:

```text
DOWNLOAD_DIR                    -> ZIP artifact đã download và rename
reports/html/report.html        -> HTML test report
reports/logs/automation.log     -> detailed execution log
reports/screenshots/            -> screenshots được tạo khi test fail
```

> `venv` là optional. Nếu muốn cô lập dependencies, có thể tạo virtual environment trước bước `pip install`.
