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

    class NoAPIKey(APIException):
        status_code = 403
        default_detail = "No API key was provided. Please provide an API key in the Authorization header. (Authorization: Api-Key <key>)"
        default_code = "no_api_key"

    class InvalidAPIKey(APIException):
        status_code = 403
        default_detail = "Invalid API key."
        default_code = "invalid_api_key"
