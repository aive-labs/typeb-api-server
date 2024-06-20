from fastapi import FastAPI, HTTPException

from src.core.exceptions.exception_handlers import global_exception_handler


def register_exception_handlers(app: FastAPI):
    app.add_exception_handler(HTTPException, global_exception_handler)
