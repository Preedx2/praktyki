
class NotLoggedInError(Exception):
    def __init__(self):
        self.message = "You need to log in to proceed with this action"

    def __str__(self) -> str:
        return self.message


class MethodNotAllowedError(Exception):
    def __init__(self, allowed: list[str] | str):
        if isinstance(allowed, str):
            self.message = f"Wrong method, required method in this endpoint is {allowed}"
        else:
            methods = ' or '.join(allowed)
            self.message = f"Wrong method, allowed methods in this endpoint are {methods}"

    def __str__(self) -> str:
        return self.message


class ValidationError(Exception):
    def __init__(self, message: str):
        self.message = f"Validation Error: {message}"

    def __str__(self) -> str:
        return self.message

