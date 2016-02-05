# Copyright 2014-2016 Canonical, Ltd.
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.


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
