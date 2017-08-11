from .HTTPRequest import *
from .HTTPResponse import *
from .HTTPCookies import *

import time

class HTTPSession(object):
    '''
    Class for genrating HTTP session. have method to send on request,
    create http flow from several requests and send on by one
    '''

    __slots__ = ("debug", "request", "session_cookies", "sock",
                 "response", "session", "host", "secure", "session_headers",
                 "session_cookies", "prefix_url", "resp_format",
                 "session_http_version", "ipv6", "delay","doassert")

    def __init__(self, host=None, secure=False, request=None, flow=None,
                 session_headers=None, session_cookies=None,
                 prefix_url="", session_http_version="", resp_format=None,
                 *args, **kwargs):
        '''
        @param host:used for configuring remote host ("host",port)
        @type host:tuple
        @param secure:is ssl connection used or not
        @type secure:boolen
        @param request: instance of HTTPRequest class
        @type request:HTTPRequest
        @param flow: list of dict, describing the request
        @type flow: list
        @param session_headers: additional headers for session adds for each r
        @type session_headers: dict
        @param session_cookies: additional cookies for session adds for each r
        @type session_cookies: dict
        @param prefix_url:
        @type prefix_url: string
        @param session_http_version:
        @type session_headers: string
        '''
        try:
            if kwargs["delay"]:
                self.delay = kwargs["delay"]
            else:
                self.delay = 0
        except KeyError:
            self.delay = 0

        try:
            if kwargs["debug"] is True:
                self.debug = True
            else:
                self.debug = False
        except KeyError:
            self.debug = False

        try:
            if kwargs["use_ipv6"] is True:
                self.ipv6 = True
            else:
                self.ipv6 = False
        except KeyError:
                self.ipv6 = False

        self.sock = None
        self.response = None

        self.session_cookies = HTTPCookies(cookies=session_cookies)
        self.session = []

        if request and isinstance(request, HTTPRequest):
            self.addSessionRequestv3(request)
            self.request = None
        else:
            self.request = None

        if host:
            self.host = host
        else:
            self.host = None

        if secure:
            self.secure = True
        else:
            self.secure = False

        if session_headers:
            if "Cookie" in session_headers:
                self.session_cookies.setCookies(session_headers["Cookie"])
                del session_headers["Cookie"]
            self.session_headers = session_headers
        else:
            self.session_headers = {}

        if session_cookies:
            self.session_cookies.setCookies(session_cookies)

        if prefix_url:
            self.prefix_url = prefix_url
        else:
            self.prefix_url = ""

        if session_http_version:
            self.session_http_version = session_http_version
        else:
            self.session_http_version = None

        if resp_format:
            self.resp_format = resp_format
        else:
            self.resp_format = None

        if flow:
            self.parseSessionv3(session_flow=flow)

    def parseSessionv3(self, session_flow=None, *args, **kwargs):
        '''
        Parse http session and generate requests for next usage. 
        Format of request :
        @TODO fix work with cookies as dict
        
        {
         "url":URL to send, 
         "method":Method to use GET|POST|HEAD
         "headers": dict of headers {"Header":"Value"}.
         "payload": payload to send could be dict {"param":"value} or raw text.
         "enctype": how enctype the payload 
                0 - urlencoded, 
                1-multipart, 
                2-as is,
         "repeat":how many times repeat request,
         "chunk_size":size of chunk, if send request payload chunked.
         "resp_format": all|body|headers|status
        }

        @param session:list of requests formated in special way. see examples
        @type session:list
        @param session_headers:dict of headers HeaderName:Header value, 
            which will be assigned to each request in session
        @type session_headers:dict
        @param prefix_url:prefix what will be added to each url in session 
        @type prefix_url:str
        @param session_http_version:
        @type session_http_version:
        '''

        for request in session_flow:
            self.addSessionRequestv3(HTTPRequest(**request))

    def addSessionRequestv3(self, request=None):

        if request and isinstance(request, HTTPRequest):
            self.session.append(request)
        elif request and isinstance(request, dict):
            self.session.append(HTTPRequest(**request))
        else:
            raise Exception("Invalid request object")

    def runSessionv3(self, host=None, secure=False, delay=False,
                     session_headers=None, session_cookies=None,
                     prefix_url="", resp_format=None, version=None,
                     debug=False, *args, **kwargs):
        '''
        Run session. Send each request from self.session list.

        @param delay:delay in seconds between requests
        @type delay:float
        @type self.request:HTTPRequest
        '''
        try:
            if kwargs["doassert"]:
                self.doassert = True
            else:
                self.doassert = False
        except KeyError:
            self.doassert = False

        if host:
            self.host = host
        if secure:
            self.secure = True
        if self.delay:
            delay = self.delay

        try:
            if kwargs["use_ipv6"] is True:
                self.ipv6 = True
            else:
                self.ipv6 = False
        except KeyError:
                self.ipv6 = False

        if delay:
            self.delay = delay

        if debug:
            self.debug = True

        if session_headers:
            self.session_headers.update(session_headers)

        if session_cookies:
            self.session_cookies.setCookies(cookies=session_cookies)

        self.prefix_url = prefix_url + self.prefix_url

        for self.request in self.session:
            for i in range(0, self.request.repeat):
                # save original headers and cookies
                req_cookie = self.request.cookies.getCookies().copy()
                req_headers = self.request.headers[:]
                url = self.request.url

                # update request header and cookie according new session headers
                if self.session_headers:
                    self.request.updateRequestHeaders(self.session_headers)

                # update cookie which was recieved from response and saved
                # into self.session_cookies

                if self.session_cookies.getCookies():
                    self.request.cookies.setCookies(self.session_cookies.getCookies())

                # update url in request with session prefix
                self.request.url = self.prefix_url + self.request.url

                # print (self.request.headers)

                # print (resp_format)
                if resp_format:
                    old_resp_format = self.request.resp_format
                    self.request.resp_format = resp_format
                elif self.resp_format:
                    old_resp_format = self.request.resp_format
                    self.request.resp_format = self.resp_format
                else:
                    pass

                # print (resp_format, old_resp_format, self.resp_format, self.request.resp_format)
                if version:
                    old_version = self.request.version
                    self.request.version = version

                # print (1)
                if self.sock:
                    self.response = self.request.getResponse(sock=self.sock)
                else:
                    self.response = self.request.getResponse(host=self.host,
                                                        use_ssl=self.secure, 
                                                        use_ipv6 = self.ipv6)
                # print (self.response.status)                    

                if self.response.sock:
                    self.sock = self.response.sock
                else:
                    self.sock = None
                # update cookie from response headers
                self.session_cookies.updateCookies(self.response.headers)

                # print (self.debug)
                if self.debug:
                    print(self.request.generateRawRequest())
                    # if self.session_cookies.cookies:
                    # for cookie in 
                    # print (self.request.headers["Cookie"])

                    if self.doassert:
                        print(self.response.doassert)
                    print_resp = self.request.resp_format.lower()
                    if "status" in print_resp:
                        print(self.response.status)
                    if "headers" in print_resp:
                        print(self.response.headers)
                    if "body" in print_resp:
                        print(self.response.payload)
                    if "all" in print_resp:
                        print(self.response.status)
                        print(self.response.headers)
                        print(self.response.payload)

                self.request.headers = req_headers
                self.request.cookies = HTTPCookies(cookies=req_cookie)

                # self.request.headers["Cookie"] = req_cookie

                if prefix_url:
                    self.request.url = url
                if resp_format or self.resp_format:
                    self.request.resp_format = old_resp_format
                if version:
                    self.request.version = old_version
                self.response = None
                time.sleep(delay)
            self.request = None

        self.closeSession()

    def runAllInOneSession (self, host = None, secure=False, delay=0, session_headers = None, prefix_url=None, resp_format=None, version=None, *args, **kwargs):
        '''
        Run All requests in one session. Send each request from self.session list. Session cookies are not removed between session 

        @param delay:delay in seconds between requests
        @type delay:float
        @type self.request:HTTPRequest
        '''
        if host:
            self.host = host
        if secure:
            self.secure = True
        
        try:
            if kwargs["use_ipv6"] == True:
                self.ipv6 = True
            else:
                self.ipv6 = False
        except KeyError:
                self.ipv6 = False


        if not session_headers:
            session_headers = {}
       

        for self.request in self.session:
            for i in range (0, self.request.repeat):
                # save old headers and cookies

                if self.request.headers:
                    req_headers = self.request.headers.copy()
                    if "Cookie" in self.request.headers:
                        req_cookie = self.request.headers["Cookie"].copy()                    
                        req_headers["Cookie"] = req_cookie
                else:
                    req_headers = { }
                
                # update request headers cookie according new session headers
                
                if self.session_cookies.cookies and "Cookie" in session_headers:
                   self.session_cookies.cookies.update(session_headers.pop("Cookie"))
                   self.request.headers.update(session_headers)
                else:
                    self.request.headers.update(session_headers)

                #update cookie which was recieved from response

                if self.session_cookies.cookies:
                    if "Cookie" in self.request.headers:
                        self.request.headers["Cookie"].update(self.session_cookies.cookies)
                    else:                        
                        self.request.headers.update({"Cookie":self.session_cookies.cookies})
                
                if prefix_url:
                    url = self.request.url
                    self.request.url = str(prefix_url) + self.request.url

                if resp_format:

                    old_resp_format = self.request.resp_format                    
                    self.request.resp_format=resp_format
                    # print (resp_format, old_resp_format, self.resp_format, self.request.resp_format)
                if version:
                    old_version = self.request.version
                    self.request.version=version
                    
                
                # print (1)
                if self.sock:
                    self.response = self.request.getResponse(sock=self.sock)
                else:
                    self.response = self.request.getResponse(host=self.host, use_ssl=self.secure, use_ipv6 = self.ipv6)
                # print (1)                    

                if self.response.sock:
                    self.sock = self.response.sock
                else:
                    self.sock = None
                
                self.session_cookies.updateCookies(self.response.headers)
                
                if self.debug:
                    print(self.request.generateRawRequest())
                    # if self.session_cookies.cookies:
                    #     for cookie in
                    #     print (self.request.headers["Cookie"])
                    print_resp = self.request.resp_format.lower()
                    if "status" in print_resp:
                        print(self.response.status)
                    if "headers" in print_resp:
                        print(self.response.headers)
                    if "body" in print_resp:
                        print(self.response.payload)
                    if "all" in print_resp:
                        print(self.response.status)
                        print(self.response.headers)
                        print(self.response.payload)

                self.request.headers = req_headers
                # self.request.headers["Cookie"] = req_cookie

                if prefix_url:
                    self.request.url = url
                if resp_format:
                    self.request.resp_format = old_resp_format
                if version:
                    self.request.version = old_version
                self.response = None                
                time.sleep(delay)
            self.request = None
            
        

        self.closeSession(one_session=True) 

    def closeSession(self, session_flow=False, one_session=False):
        """
        Close socket connections
        """
        # print (2)


        if session_flow:
            self.session = []
        if self.sock:            
            self.sock.shutdown(socket.SHUT_RDWR)
            self.sock.close()
            self.sock=None
            self.secure=False
        else:
            self.sock=None
            self.secure=False
        
        self.request=None
        self.response=None      
        if not one_session:  
            self.session_cookies=HTTPCookies()

    

    def getHTTPSessionRawRequests (self,filename=None,session_headers=None):
        if not filename:
            return 1
        else:
            f = open(filename,"w")
            for req in self.session:
                if req.headers:
                    req_headers = req.headers.copy()
                    if "Cookie" in req.headers:
                        req_cookie = req.headers["Cookie"].copy()                    
                        req_headers["Cookie"] = req_cookie
                else:
                    req_headers = {}
                    
                if session_headers:
                    req.headers.update(session_headers)                
                f.write(req.generateRawRequest())
                f.write("\r\n")
                req.headers = req_headers
            f.close()
