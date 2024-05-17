import os

from fastapi import APIRouter

print(os.getcwd())



token_router = APIRouter(
    tags=["Token"],
)
