from multiprocessing import Process
from copy import deepcopy

from .HTTPClient import HTTPClient


class HTTPPool(Process):

    def __init__(self, num_of_clients=1,
                 host=None, secure=False,
                 delay=0, repeat=10,
                 flow=None,
                 session_headers=None, session_http_version="",
                 prefix_url="", xff=True, resp_format=None,
                 debug=False, *args, **kwargs):

        Process.__init__(self)
        self.num_of_clients = num_of_clients
        self.kwargs = {
            "host": host,
            "secure": secure,
            "delay": delay,
            "repeat": repeat,
            "flow": deepcopy(flow),
            "session_headers": session_headers,
            "prefix_url": prefix_url,
            "session_http_version": session_http_version,
            "xff": xff,
            "resp_format": resp_format,
            "debug": debug,
        }

    def run(self):
        client_pool = []
        for i in range(1, self.num_of_clients + 1):
            client = HTTPClient(**self.kwargs)
            client.start()
            client_pool.append(client)
            client = None

        while True:
            for th in client_pool:
                if not th.is_alive():
                    client_pool.pop(client_pool.index(th))
            if len(client_pool) < 1:
                break
        return
