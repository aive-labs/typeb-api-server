import json
from datetime import datetime

import pytz
from fastapi import HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.status import HTTP_422_UNPROCESSABLE_ENTITY

from src.main.contextvars_context import correlation_id_var
from src.main.logging import logger

local_timezone = pytz.timezone("Asia/Seoul")


def write_error_log(correlation_id, exc, request):
    if request.client is None:
        client_ip = "UnknownIP"
    else:
        client_ip = request.client.host

    try:
        # 요청 바디 가져오기
        body = request.state.body.decode("utf-8")
        body_json = json.loads(body)

        # 민감한 데이터 마스킹
        if "password" in body_json:
            body_json["password"] = "****"
    except (AttributeError, json.JSONDecodeError):
        body_json = None

    # JSON 형태로 로그 구성
    log_data = {
        "message": "Exception occurred",
        "path": str(request.url),
        "method": request.method,
        "headers": dict(request.headers),
        "query_params": dict(request.query_params),
        "client_ip": client_ip,
        "exception": str(exc),
        "exception_detail": getattr(exc, "detail", None),
        "correlation_id": correlation_id,
        "body": body_json,
    }

    # 로깅
    logger.error(
        json.dumps(log_data, ensure_ascii=False, indent=2),
        extra={"correlation_id": correlation_id},
        exc_info=exc if exc else False,
    )

    return correlation_id


def global_exception_handler(request: Request, exc: HTTPException):
    correlation_id = correlation_id_var.get()
    write_error_log(correlation_id, exc, request)

    return JSONResponse(
        status_code=exc.status_code,
        content={
            "correlation_id": correlation_id,
            "timestamp": datetime.now(local_timezone).isoformat() + "Z",
            "path": str(request.url),
            "detail": exc.detail,
        },
    )


async def validation_exception_handler(request: Request, exc: RequestValidationError):
    correlation_id = correlation_id_var.get()
    write_error_log(correlation_id, exc, request)

    # 커스텀 에러 메시지 포맷
    return JSONResponse(
        status_code=HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "correlation_id": correlation_id,
            "timestamp": datetime.now(local_timezone).isoformat() + "Z",
            "path": str(request.url),
            "detail": {
                "message": "요청 데이터의 타입이 유효하지 않습니다."
            },  # Pydantic이 제공하는 에러 메시지
            "error": exc.errors(),  # 요청 본문을 그대로 반환할 수도 있음
        },
    )
