from fastapi import HTTPException, status

# https://developer.mozilla.org/en-US/docs/Web/HTTP/Status
# https://learn.microsoft.com/en-us/windows/win32/winhttp/http-status-codes

# ======= 200 =======

class OK(HTTPException):
    def __init__(self, status_code = status.HTTP_200_OK, detail = None, headers = None):
        """200 OK (sucessfully)"""
        super().__init__(status_code, detail, headers) 
        self.status_code = status_code
        self.detail = detail

class CREATED(HTTPException):
    def __init__(self, status_code = status.HTTP_201_CREATED, detail = None, headers = None):
        """201 Accepted"""
        super().__init__(status_code, detail, headers)
        self.status_code = status_code
        self.detail = detail

# ======= 400 =======

class BAD_REQUESTS(HTTPException):
    def __init__(self, status_code=status.HTTP_400_BAD_REQUEST, detail = None, headers = None):
        """400 Bad Requests"""
        super().__init__(status_code, detail, headers)
        self.status_code = status_code
        self.detail = detail

class UNAUTHORIZED(HTTPException):
    def __init__(self, detail = None, headers = None):
        """401 Unauthorized"""
        super().__init__(status_code = status.HTTP_401_UNAUTHORIZED, detail = detail, headers = headers)

class NOT_FOUND(HTTPException):
    def __init__(self, status_code = status.HTTP_404_NOT_FOUND, detail = None, headers = None):
        """404 Not Found""" 
        super().__init__(status_code, detail, headers)
        self.status_code = status_code
        self.detail = detail

class METHOD_NOT_ALLOWED(HTTPException):
    def __init__(self, status_code = status.HTTP_405_METHOD_NOT_ALLOWED, detail = None, headers = None):
        """405 Method Not Allowed"""
        super().__init__(status_code, detail, headers)
        self.status_code = status_code
        self.detail = detail

class UNPROCESSABLE_CONTENT(HTTPException):
    def __init__(self, status_code = status.HTTP_422_UNPROCESSABLE_ENTITY, detail = None, headers = None):
        """422 Unprocessable Content | The request was well-formed but was unable to be followed due to semantic errors."""
        super().__init__(status_code, detail, headers)
        self.status_code = status_code
        self.detail = detail

# ======= 500 =======

class INTERNAL_SERVER_ERROR(HTTPException):
    def __init__(self, status_code = status.HTTP_500_INTERNAL_SERVER_ERROR, detail = None, headers = None):
        """500 Internal Server Error | The server encountered an unexpected condition that prevented it from fulfilling the request."""
        super().__init__(status_code, detail, headers)
        self.status_code = status_code
        self.detail = detail