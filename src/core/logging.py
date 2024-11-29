import logging
import os
from logging.handlers import TimedRotatingFileHandler

# 로그 디렉토리 생성
LOG_DIR = "./logs"
ERROR_DIR = "./logs/errors"
if not os.path.exists(LOG_DIR):
    os.makedirs(LOG_DIR)

if not os.path.exists(ERROR_DIR):
    os.makedirs(ERROR_DIR)

# 로거 생성
logger = logging.getLogger("api_logger")
logger.setLevel(logging.INFO)

# 포매터 설정
formatter = logging.Formatter("[%(asctime)s][%(levelname)s][%(correlation_id)s] - %(message)s")

# 전체 로그 파일 핸들러 (INFO 레벨 이상)
info_handler = TimedRotatingFileHandler(
    filename=os.path.join(LOG_DIR, "app.log"),
    when="midnight",
    interval=1,
    backupCount=7,
    encoding="utf-8",
)
info_handler.setLevel(logging.INFO)
info_handler.setFormatter(formatter)

# 에러 로그 파일 핸들러 (ERROR 레벨 이상)
error_handler = TimedRotatingFileHandler(
    filename=os.path.join(LOG_DIR, "errors/error.log"),
    when="midnight",
    interval=1,
    backupCount=7,
    encoding="utf-8",
)
error_handler.setLevel(logging.ERROR)
error_handler.setFormatter(formatter)

# 로거에 핸들러 추가
logger.addHandler(info_handler)
logger.addHandler(error_handler)
