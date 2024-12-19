from fastapi import FastAPI, HTTPException
from fastapi.exceptions import RequestValidationError

from src.main.exceptions.exception_handlers import (
    global_exception_handler,
    validation_exception_handler,
)


def register_exception_handlers(app: FastAPI):
    app.add_exception_handler(RequestValidationError, validation_exception_handler)
    app.add_exception_handler(HTTPException, global_exception_handler)
