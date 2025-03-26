class ErrorCode:
    def __init__(self, code, message, http_status):
        self.code = code
        self.message = message
        self.http_status = http_status

    def __str__(self):
        return f"{self.code}: {self.message} (HTTP {self.http_status})"

class ErrorCodes:
    # Define error codes
    INVALID_INPUT = ErrorCode("E001", "Invalid input provided", 400)
    NOT_FOUND = ErrorCode("E002", "Resource not found", 404)
    INTERNAL_ERROR = ErrorCode("E003", "Internal server error", 500)
    UNAUTHORIZED = ErrorCode("E004", "Unauthorized access", 401)
    FORBIDDEN = ErrorCode("E005", "Forbidden access", 403)

    @classmethod
    def get_error(cls, code):
        for attr in dir(cls):
            if not attr.startswith("__"):
                error_code = getattr(cls, attr)
                if isinstance(error_code, ErrorCode) and error_code.code == code:
                    return error_code
        return None

# Example usage
if __name__ == "__main__":
    error = ErrorCodes.get_error("E002")
    if error:
        print(error)
    else:
        print("Error code not found")