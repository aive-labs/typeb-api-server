import json
from datetime import datetime

import pytz
from fastapi import HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.status import HTTP_422_UNPROCESSABLE_ENTITY

from src.core.logging import logger

local_timezone = pytz.timezone("Asia/Seoul")


def add_logging(exc, request):
    correlation_id = request.state.correlation_id
    if request.client is None:
        client_ip = "UnknownIP"
    else:
        client_ip = request.client.host
    # 요청 파라미터와 예외 정보 로그

    logger.error(
        f"Exception occurred:\n"
        f"Path: {request.url}\n"
        f"Method: {request.method}\n"
        f"Headers: {dict(request.headers)}\n"
        f"Query Params: {dict(request.query_params)}\n"
        f"Client IP: {client_ip}\n"
        f"Exception: {exc}\n"
        f"Exception Detail: {exc.detail}\n"
        f"Correlation ID: {correlation_id}",
        extra={"correlation_id": correlation_id},
        exc_info=True,  # 스택 트레이스 포함
    )
    try:
        # 요청 바디를 읽기 위해 미들웨어에서 저장한 바디 사용
        print("!!!!!")
        body = request.state.body.decode("utf-8")
        print(body)
        body_json = json.loads(body)
        print(body_json)
        if "password" in body_json:
            body_json["password"] = "****"
        logger.error(f"Request Body: {body_json}", extra={"correlation_id": correlation_id})
    except AttributeError:
        # 요청 바디가 없는 경우
        pass
    return correlation_id


def global_exception_handler(request: Request, exc: HTTPException):
    correlation_id = add_logging_to(exc, request)

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
    correlation_id = add_logging_to(exc, request)

    # 커스텀 에러 메시지 포맷
    return JSONResponse(
        status_code=HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "correlation_id": correlation_id,
            "timestamp": datetime.now(local_timezone).isoformat() + "Z",
            "path": str(request.url),
            "detail": {
                "message": "요청 데이터가 유효하지 않습니다."
            },  # Pydantic이 제공하는 에러 메시지
            "error": exc.errors(),  # 요청 본문을 그대로 반환할 수도 있음
        },
    )


def add_logging_to(exc, request):
    correlation_id = request.state.correlation_id
    if request.client is None:
        client_ip = "UnknownIP"
    else:
        client_ip = request.client.host
    # 요청 파라미터와 예외 정보 로그
    logger.error(
        f"Exception occurred:\n"
        f"Path: {request.url}\n"
        f"Method: {request.method}\n"
        f"Headers: {dict(request.headers)}\n"
        f"Query Params: {dict(request.query_params)}\n"
        f"Client IP: {client_ip}\n"
        f"Exception: {exc}\n"
        f"Exception Detail: {exc.detail}\n"
        f"Correlation ID: {correlation_id}",
        extra={"correlation_id": correlation_id},
        exc_info=True,  # 스택 트레이스 포함
    )
    try:
        # 요청 바디를 읽기 위해 미들웨어에서 저장한 바디 사용
        body = request.state.body.decode("utf-8")
        body_json = json.loads(body)
        if "password" in body_json:
            body_json["password"] = "****"
        logger.error(f"Request Body: {body_json}", extra={"correlation_id": correlation_id})
    except AttributeError:
        # 요청 바디가 없는 경우
        pass
    return correlation_id
