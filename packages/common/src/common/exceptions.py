"""Domain exception hierarchy."""


class AppException(Exception):
    """Base exception for all application errors."""

    def __init__(self, message: str, code: str = "INTERNAL_ERROR", status_code: int = 500):
        super().__init__(message)
        self.message = message
        self.code = code
        self.status_code = status_code


class NotFoundError(AppException):
    """Raised when a requested resource does not exist."""

    def __init__(self, message: str = "Resource not found", code: str = "NOT_FOUND"):
        super().__init__(message=message, code=code, status_code=404)


class BadRequestError(AppException):
    """Raised when request payload or parameters violate domain invariants."""

    def __init__(self, message: str = "Invalid request", code: str = "BAD_REQUEST"):
        super().__init__(message=message, code=code, status_code=400)


class ConflictError(AppException):
    """Raised when an operation conflicts with existing entity state."""

    def __init__(self, message: str = "Resource conflict", code: str = "CONFLICT"):
        super().__init__(message=message, code=code, status_code=409)


class UnauthorizedError(AppException):
    """Raised when authentication credentials are missing or invalid."""

    def __init__(self, message: str = "Unauthorized", code: str = "UNAUTHORIZED"):
        super().__init__(message=message, code=code, status_code=401)
