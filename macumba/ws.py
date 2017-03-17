from ws4py.client.threadedclient import WebSocketClient
import json
import threading
import logging
from .errors import ConnectionClosedError, UnknownRequestError

log = logging.getLogger('macumba')


class JujuWS(WebSocketClient):

    def __init__(self, url, protocols=['https-only'],
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

    def do_connect(self):
        self.connect()
        self.open_done.wait()
        self.open_done.clear()

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
