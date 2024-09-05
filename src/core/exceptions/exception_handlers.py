from datetime import datetime

import pytz
from fastapi import HTTPException, Request
from fastapi.responses import JSONResponse


def global_exception_handler(request: Request, exc: HTTPException):
    local_timezone = pytz.timezone("Asia/Seoul")
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "timestamp": datetime.now(local_timezone).isoformat() + "Z",
            "path": str(request.url),
            "detail": exc.detail,
        },
    )
