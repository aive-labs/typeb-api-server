from typing import Any

from fastapi import HTTPException, status


class BadRequestException(HTTPException):
    def __init__(self, detail: Any = None, headers: dict[str, Any] | None = None) -> None:
        super().__init__(status.HTTP_400_BAD_REQUEST, detail, headers)


class DuplicatedException(HTTPException):
    def __init__(self, detail: Any = None, headers: dict[str, Any] | None = None) -> None:
        super().__init__(status.HTTP_400_BAD_REQUEST, detail, headers)


class AuthorizationException(HTTPException):
    def __init__(self, detail: Any = None, headers: dict[str, Any] | None = None) -> None:
        super().__init__(status.HTTP_403_FORBIDDEN, detail, headers)


class SubscriptionException(HTTPException):
    def __init__(self, detail: Any = None, headers: dict[str, Any] | None = None) -> None:
        super().__init__(status.HTTP_401_UNAUTHORIZED, detail, headers)


class AuthException(HTTPException):
    def __init__(self, detail: Any = None, headers: dict[str, Any] | None = None) -> None:
        super().__init__(status.HTTP_403_FORBIDDEN, detail, headers)


class CredentialException(HTTPException):
    def __init__(self, detail: Any = None, headers: dict[str, Any] | None = None) -> None:
        super().__init__(status.HTTP_401_UNAUTHORIZED, detail, {"WWW-Authenticate": "Bearer"})


class NotFoundException(HTTPException):
    def __init__(self, detail: Any = None, headers: dict[str, Any] | None = None) -> None:
        super().__init__(status.HTTP_404_NOT_FOUND, detail, headers)


class ValidationException(HTTPException):
    def __init__(self, detail: Any = None, headers: dict[str, Any] | None = None) -> None:
        super().__init__(status.HTTP_422_UNPROCESSABLE_ENTITY, detail, headers)


class ConvertException(HTTPException):
    def __init__(self, detail: Any = None, headers: dict[str, Any] | None = None) -> None:
        super().__init__(status.HTTP_500_INTERNAL_SERVER_ERROR, detail, headers)


class LinkedCampaignException(HTTPException):
    def __init__(self, detail: Any = None, headers: dict[str, Any] | None = None) -> None:
        super().__init__(status.HTTP_500_INTERNAL_SERVER_ERROR, detail, headers)


class PolicyException(HTTPException):
    def __init__(self, detail: Any = None, headers: dict[str, Any] | None = None) -> None:
        super().__init__(status.HTTP_400_BAD_REQUEST, detail, headers)


class ImageFormatException(HTTPException):
    def __init__(self, detail: Any = None, headers: dict[str, Any] | None = None) -> None:
        super().__init__(status.HTTP_400_BAD_REQUEST, detail, headers)


class Cafe24Exception(HTTPException):
    def __init__(self, detail: Any = None, headers: dict[str, Any] | None = None) -> None:
        super().__init__(status.HTTP_503_SERVICE_UNAVAILABLE, detail, headers)


class ConsistencyException(HTTPException):
    def __init__(self, detail: Any = None, headers: dict[str, Any] | None = None) -> None:
        super().__init__(status.HTTP_500_INTERNAL_SERVER_ERROR, detail, headers)


class PpurioException(HTTPException):
    def __init__(self, detail: Any = None, headers: dict[str, Any] | None = None) -> None:
        super().__init__(status.HTTP_503_SERVICE_UNAVAILABLE, detail, headers)


class AwsException(HTTPException):
    def __init__(self, detail: Any = None, headers: dict[str, Any] | None = None) -> None:
        super().__init__(status.HTTP_503_SERVICE_UNAVAILABLE, detail, headers)


class PaymentException(HTTPException):
    def __init__(self, detail: Any = None, headers: dict[str, Any] | None = None) -> None:
        super().__init__(status.HTTP_500_INTERNAL_SERVER_ERROR, detail, headers)


class GoogleTagException(HTTPException):
    def __init__(self, detail: Any = None, headers: dict[str, Any] | None = None) -> None:
        super().__init__(status.HTTP_503_SERVICE_UNAVAILABLE, detail, headers)
