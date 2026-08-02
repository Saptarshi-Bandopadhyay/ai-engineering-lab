class DomainError(Exception):
    """Base class for all domain exceptions."""


class InvalidCredentialsError(DomainError):
    """Raised when authentication fails (wrong email or password)."""


class DuplicateResourceError(DomainError):
    """Raised when trying to create a resource that already exists."""
