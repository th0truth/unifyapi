from fastapi import HTTPException, status

# https://developer.mozilla.org/en-US/docs/Web/HTTP/Status
# https://learn.microsoft.com/en-us/windows/win32/winhttp/http-status-codes

# ======= 200 =======

class OK(HTTPException):
    """200 OK (sucessfully)"""
    def __init__(self, detail = None, headers = None):
        super().__init__(status_code = status.HTTP_200_OK, detail = detail, headers = headers) 

class CREATED(HTTPException):
    """201 Accepted"""
    def __init__(self, detail = None, headers = None):
        super().__init__(status_code = status.HTTP_201_CREATED, detail = detail, headers = headers)

# ======= 400 =======

class BAD_REQUESTS(HTTPException):
    """400 Bad Requests"""
    def __init__(self, detail = None, headers = None):
        super().__init__(status_code = status.HTTP_400_BAD_REQUEST, detail = detail, headers = headers)

class UNAUTHORIZED(HTTPException):
    """401 Unauthorized"""
    def __init__(self, detail = None, headers = None):
        super().__init__(status_code = status.HTTP_401_UNAUTHORIZED, detail = detail, headers = headers)

class FORBIDDEN(HTTPException):
    """403 Forbidden | The server understood the request, but cannot fulfill it."""
    def __init__(self, detail = None, headers = None):
        super().__init__(detail, headers, status_code=status.HTTP_403_FORBIDDEN)

class NOT_FOUND(HTTPException):
    """404 Not Found""" 
    def __init__(self, detail = None, headers = None):
        super().__init__(status_code = status.HTTP_404_NOT_FOUND, detail = detail, headers = headers)

class METHOD_NOT_ALLOWED(HTTPException):
    """405 Method Not Allowed"""
    def __init__(self, detail = None, headers = None):
        super().__init__(status_code = status.HTTP_405_METHOD_NOT_ALLOWED, detail = detail, headers = headers)

class CONFLICT(HTTPException):
    "409 | The request could not be completed due to a conflict with the current state of the target resource."
    def __init__(self, detail = None, headers = None):
        super().__init__(detail, headers, status_code = status.HTTP_409_CONFLICT)

class UNPROCESSABLE_CONTENT(HTTPException):
    """422 Unprocessable Content | The request was well-formed but was unable to be followed due to semantic errors."""
    def __init__(self, detail = None, headers = None):
        super().__init__(status_code = status.HTTP_422_UNPROCESSABLE_ENTITY, detail = detail, headers = headers)

# ======= 500 =======

class INTERNAL_SERVER_ERROR(HTTPException):
    """500 Internal Server Error | The server encountered an unexpected condition that prevented it from fulfilling the request."""
    def __init__(self, detail = None, headers = None):
        super().__init__(status_code = status.HTTP_500_INTERNAL_SERVER_ERROR, detail = detail, headers = headers)