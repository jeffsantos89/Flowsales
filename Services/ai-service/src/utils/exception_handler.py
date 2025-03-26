class APIError(Exception):
    def __init__(self, message, status_code=400):
        super().__init__(message)
        self.status_code = status_code

class NotFoundError(APIError):
    def __init__(self, message="Resource not found"):
        super().__init__(message, 404)

class UnauthorizedError(APIError):
    def __init__(self, message="Unauthorized access"):
        super().__init__(message, 401)
        class BadRequestError(APIError):
            def __init__(self, message="Bad request"):
                super().__init__(message, 400)

        class ForbiddenError(APIError):
            def __init__(self, message="Forbidden"):
                super().__init__(message, 403)

        class ConflictError(APIError):
            def __init__(self, message="Conflict"):
                super().__init__(message, 409)

        class InternalServerError(APIError):
            def __init__(self, message="Internal server error"):
                super().__init__(message, 500)

        def handle_exception(error):
            if isinstance(error, APIError):
                response = {
                    'error': error.__class__.__name__,
                    'message': str(error),
                    'status_code': error.status_code
                }
            else:
                response = {
                    'error': 'InternalServerError',
                    'message': 'An unexpected error occurred.',
                    'status_code': 500
                }
            return response