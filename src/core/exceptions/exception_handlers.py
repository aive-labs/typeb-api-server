from datetime import datetime

from fastapi import HTTPException, Request
from fastapi.responses import JSONResponse


def global_exception_handler(request: Request, exc: HTTPException):
    return JSONResponse(
        content={
            "timestamp": datetime.now().isoformat() + "Z",
            "path": str(request.url),
            "detail": exc.detail,
        }
    )
