from .HTTPCookies import *


class HTTPResponse(object):
    """
        Class for http response

        @self.status : response status
    """

    def __init__(self, headers = None, payload = b"", sock = None, resp_format=None, doassert=None):
        """
            object Constructor

            @param: headers list of headers            
            @payload: bytearray of response body
            @sock: socket.socket of connection

        """
        if headers is None:
            headers = []
        else:
            try:
                self.status = headers[0]
                self.status_code = int(self.status[9:12])
            except (IndexError, ValueError):
                self.status = None
                self.status_code = None
            try:
                self.headers = headers[1:]
            except IndexError:
                self.headers = []

        self.cookies = HTTPCookies(self.headers)
        self.sock = sock
        self.payload = payload

        self.doassert = self.checkAssertion(doassert)

    def checkAssertion(self, cond=None):
        if cond:
            results = []
            for assert_item in cond.items():
                try:
                    key, value = assert_item
                    if key == "payload":
                        assert value.encode() in self[key]
                        results.append(True)

                    if key == "headers":
                        for header in self[key]:
                            try:
                                assert value in header
                                results.append(True)
                                break
                            except AssertionError:
                                continue
                        else:
                            results.append(False)
                    if key == "status":
                        assert value in self[key]
                        results.append(True)
                except AssertionError:
                    results.append(False)
            return all(results)
        else:
            return False

    def __getitem__(self, name):
        if name in self.__dict__:
            return self.__dict__[name]
