from datetime import datetime

import pytz
from fastapi import HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.status import HTTP_422_UNPROCESSABLE_ENTITY

local_timezone = pytz.timezone("Asia/Seoul")


def global_exception_handler(request: Request, exc: HTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "timestamp": datetime.now(local_timezone).isoformat() + "Z",
            "path": str(request.url),
            "detail": exc.detail,
        },
    )


async def validation_exception_handler(request: Request, exc: RequestValidationError):
    # 커스텀 에러 메시지 포맷
    return JSONResponse(
        status_code=HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "timestamp": datetime.now(local_timezone).isoformat() + "Z",
            "path": str(request.url),
            "detail": {
                "message": "요청 데이터가 유효하지 않습니다."
            },  # Pydantic이 제공하는 에러 메시지
            "error": exc.errors(),  # 요청 본문을 그대로 반환할 수도 있음
        },
    )
