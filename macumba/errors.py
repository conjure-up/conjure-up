class MacumbaError(Exception):

    "Base error class"


class CharmNotFoundError(MacumbaError):

    "Error when getting charm store url"


class LoginError(MacumbaError):

    "Error logging in to juju api"


class ServerError(MacumbaError):

    "Generic error response from server"

    def __init__(self, message, response):
        self.response = response
        super().__init__(self, message)


class BadResponseError(MacumbaError):

    "Unable to parse response from server"


class ConnectionClosedError(MacumbaError):

    "Attempted to receive messages from closed connection"


class UnknownRequestError(MacumbaError):

    "Attempted to receive a message with an unknown ID"


class RequestTimeout(MacumbaError):

    "Request timed out"
