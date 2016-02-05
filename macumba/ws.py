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

from ws4py.client.threadedclient import WebSocketClient
import json
import threading
import logging
from .errors import ConnectionClosedError, UnknownRequestError

log = logging.getLogger('macumba')


class JujuWS(WebSocketClient):

    def __init__(self, url, password, protocols=['https-only'],
                 extensions=None, ssl_options=None, headers=None,
                 start_reqid=1):
        WebSocketClient.__init__(self, url, protocols, extensions,
                                 ssl_options=ssl_options, headers=headers)
        self.open_done = threading.Event()
        self.rid_lock = threading.RLock()
        self.msglock = threading.RLock()
        self.messages = {}
        self._cur_request_id = start_reqid

    # WebSocketClient subclass overrides, run in private thread:
    def opened(self):
        self.open_done.set()

    def received_message(self, m):
        msg = json.loads(m.data.decode('utf-8'))
        msg_req_id = msg['RequestId']
        with self.msglock:
            self.messages[msg_req_id] = msg

    def closed(self, code, reason=None):
        log.debug("socket closed: code:{} reason:{}".format(code, reason))

    # actions for users of the class:
    def get_current_request_id(self):
        "only intended to pass to constructor of a replacing client"
        return self._cur_request_id

    def do_close(self):
        self.close()

    def do_connect(self, creds):
        self.connect()
        self.open_done.wait()
        self.open_done.clear()
        rv = self.do_send(creds)
        return rv

    def do_send(self, json_message):
        with self.rid_lock:
            self._cur_request_id += 1
            request_id = self._cur_request_id

        json_message['RequestId'] = request_id

        self.send(json.dumps(json_message))

        with self.msglock:
            self.messages[request_id] = None

        return request_id

    def do_receive(self, request_id):
        """Checks for message matching request_id.

        Will return None if message has not arrived yet.

        Raises UnknownRequestError if request_id hasn't been sent yet
        (or was already received).

        """
        if self.terminated:
            raise ConnectionClosedError

        with self.msglock:
            if request_id not in self.messages:
                errmsg = ("{} not in messages. "
                          "cur = {}".format(request_id,
                                            self._cur_request_id))
                raise UnknownRequestError(errmsg)

            message = self.messages[request_id]
            if message is not None:
                del self.messages[request_id]

        return message
