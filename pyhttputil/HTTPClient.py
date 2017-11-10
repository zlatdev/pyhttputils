import threading
import multiprocessing
import time

from .HTTPSession import HTTPSession
from .utils import generateIPv4Address


class HTTPClient(threading.Thread):
    """
    """

    def __init__(self, host=None, secure=False,
                 delay=0, during=10,
                 flow=None,
                 session_headers=None, session_http_version=None,
                 prefix_url=None, resp_format=None, xff=True, debug=False,
                 *args, **kwargs):

        threading.Thread.__init__(self)

        self.host = host
        self.secure = secure
        self.delay = delay
        self.time = during
        self.xff = xff

        if not session_headers:
            session_headers = {}

        self.currenthttpsession = HTTPSession(flow=flow,
                                          session_headers=session_headers.copy(),
                                          prefix_url=prefix_url,
                                          session_http_version=session_http_version,
                                          resp_format=resp_format,
                                          debug=debug, **kwargs)

    def run(self):

        print("Client ", threading.currentThread().name, multiprocessing.current_process().name, "start on host:", self.host)

        ct = st = time.time()
        while ct - st < self.time:

            if self.xff:
                self.currenthttpsession.runSession(self.host, self.secure, self.delay,
                                                   session_headers={"X-Forwarded-For": generateIPv4Address()})
            else:
                self.currenthttpsession.runSession(self.host, self.secure, self.delay)
            ct = time.time()

        print("Client", threading.currentThread().name, multiprocessing.current_process().name, "start on host:", self.host)



