from rest_framework.exceptions import APIException


class APIError:
    """Base class for API errors."""

    class MissingSpace(APIException):
        status_code = 400
        default_detail = "Missing space uuid in request data"
        default_code = "missing_space"

    class InvalidSpace(APIException):
        status_code = 400
        default_detail = "Space uuid is invalid"
        default_code = "invalid_space"

    class InvalidPermissions(APIException):
        status_code = 403
        default_detail = "API key does not have the required permissions."
        default_code = "invalid_permissions"
