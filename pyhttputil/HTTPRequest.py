from .utils import *
from .HTTPCookies import *


class HTTPRequest(object):
    """
        Class for HTTP request which will be send
    """
    __slots__ = ("method", "url", "headers", "cookies", "params", "payload", "chunk_size", "version", "enctype", "repeat", "resp_format", "request", "doassert", "doaction")

    def __init__(self,
                 method="GET",
                 url="/",
                 headers=None,
                 cookies=None,
                 params=None,
                 payload=None,
                 chunk_size=0,
                 version="HTTP/1.1",
                 enctype=POST_TYPE_URLENCODED,
                 repeat=1,
                 resp_format=None,
                 doassert=None,
                 doaction=None):
        """
        Constructor for HTTP request.
        @param method:request method
        @type method:str
        @param url:requested url
        @type url:str
        @param headers:request headers
        @type headers:dict
        @param payload:request payload, could be dict or string.
        @type payload:mixed
        @param chunk_size:size of chunk which is used to send payload
        @type chunk_size:int
        @param version:HTTP protocol version
        @type version:str
        @param enctype:type of payload encoding : 0- urlencoded, 1-multipart, 2 - raw.
        @type enctype:int
        @param repeat:number of time to send request
        @type repeat:int
        @param resp_format:format of response to represent for user: all|body|headers|status
        @type resp_format:str
        """
        self.method = method
        self.url = url
        self.headers = []
        self.cookies = HTTPCookies(cookies=cookies)

        if headers:
            self.updateRequestHeaders(headers)
        self.params = params
        self.payload = payload
        self.chunk_size = chunk_size
        self.version = version
        self.enctype = enctype
        self.repeat = repeat
        self.resp_format = resp_format
        self.request = None
        self.doassert = doassert
        self.doaction = doaction

    def updateRequestHeaders(self, headers=None):
        if not headers:
            return

        if "Cookie" in headers:
            self.cookies.setCookies(cookies=headers["Cookie"])
            del headers["Cookie"]
        # print(3, headers)
        for header, value in headers.items():
            # print(3, header, value)
            self.headers.append((header, value))
        # print(3, self.headers)

    def generateRequest(self):
        """
        Generate request for single use
        """

        self.request = generateRequestv3(self.method, self.url, self.headers, self.cookies, self.params, self.payload, self.chunk_size, self.version, self.enctype)

    def generateRawRequest(self):

        if not self.request:
            self.generateRequest()

        request_h = DEFAULT_HTTP_DELIMETER.join(self.request[0])
        # print (request_h)

        if self.request[1]:

            body_payload = ""
            if len(self.request[1]) > 1:
                for chunk in self.request[1]:
                    body_payload += DEFAULT_HTTP_DELIMETER.join(chunk)
            else:
                body_payload = self.request[1][0]

            return request_h.encode() + body_payload.encode()
        else:
            return request_h.encode() + b""

    def getResponse(self, host=None, use_ssl=False, sock=None, use_ipv6=False, resp_format=None):
        """
        Send request and get response and return response object

        @param host: tuple of host ("ip",port)
        @type host:tuple
        @param use_ssl:use ssl connection or not
        @type use_ssl:boolen
        @param sock:socket object if already was opened
        @type sock:socket
        """

        if resp_format:
            self.resp_format = resp_format

        # if not self.request:
        self.generateRequest()
        return sendRequest(self.request, host, use_ssl, sock, self.resp_format, use_ipv6, doassert=self.doassert, doaction=self.doaction)

