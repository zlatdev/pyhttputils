from .HTTPCookies import *

import zlib


class HTTPResponse(object):
    """
        Class for http response

        @self.status : response status

        @todo add callable for doaction, doassert
    """

    def __init__(self, headers=None, payload=b"", sock=None, doassert=None, doaction=None):
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
        self.raw_payload = payload

        self.doassert = self.checkAssertion(doassert)


        if doaction:
            self.callAction(doaction)

    def callAction(self, doaction):
        self.doactionresult = doaction(self)

    def checkAssertion(self, cond=None):
        if cond:
            results = []
            try:
                for assert_item in cond.items():
                    try:
                        key, value = assert_item

                        if key == "payload":
                            assert value.encode() in self[key]
                            results.append(True)

                        if key == "headers":
                            for assert_header, assert_value in value.items():
                                assert_result = "{}: {}".format(assert_header, assert_value)
                                for header in self[key]:
                                    try:
                                        assert assert_result in header
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
            except TypeError:
                results.append(False)
            return all(results)
        else:
            return None

    def unchunkPayload(self):

        data = self.payload.split(b"\r\n")

        c_data = bytes()

        for i in range(1, len(data), 2):
            if data[i - 1].decode() == str(hex(len(data[i])))[2:] and data[i - i].decode() != "0":
                c_data += data[i]
        self.payload = c_data
        return self

    def decompressPayload(self):
        self.payload = zlib.decompress(self.payload, 47)
        return self



    def __getitem__(self, name):
        if name in self.__dict__:
            return self.__dict__[name]

