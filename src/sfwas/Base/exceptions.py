class BaseSFWASException(Exception):
    """Base exception for SFWAS."""

    def __init__(self, *message):
        super().__init__(*message)
        if message:
            try:
                self.message = "\n".join(message)
            except TypeError:
                self.message = ""
                for m in message:
                    self.message += f"\n{m}"

    def __str__(self):
        return self.message


class SFConnectionError(BaseSFWASException):
    """Raised when the connection fails."""

    def __init__(self, message="Connection failed."):
        super().__init__(message)


class SFInvalidURL(BaseSFWASException):
    """Raised when the URL is invalid."""

    def __init__(self, message="Invalid URL."):
        super().__init__(message)


class NotFound(BaseSFWASException):
    """Raised when a clan is not found."""

    def __init__(self, message="Tag not found!"):
        super().__init__(message)
