from typing import Any

from fastapi import HTTPException, status


class DuplicatedException(HTTPException):
    def __init__(
        self, detail: Any = None, headers: dict[str, Any] | None = None
    ) -> None:
        super().__init__(status.HTTP_400_BAD_REQUEST, detail, headers)


class AuthException(HTTPException):
    def __init__(
        self, detail: Any = None, headers: dict[str, Any] | None = None
    ) -> None:
        super().__init__(status.HTTP_403_FORBIDDEN, detail, headers)


class CredentialException(HTTPException):
    def __init__(
        self, detail: Any = None, headers: dict[str, Any] | None = None
    ) -> None:
        super().__init__(
            status.HTTP_401_UNAUTHORIZED, detail, {"WWW-Authenticate": "Bearer"}
        )


class NotFoundException(HTTPException):
    def __init__(
        self, detail: Any = None, headers: dict[str, Any] | None = None
    ) -> None:
        super().__init__(status.HTTP_404_NOT_FOUND, detail, headers)


class ValidationError(HTTPException):
    def __init__(
        self, detail: Any = None, headers: dict[str, Any] | None = None
    ) -> None:
        super().__init__(status.HTTP_422_UNPROCESSABLE_ENTITY, detail, headers)
