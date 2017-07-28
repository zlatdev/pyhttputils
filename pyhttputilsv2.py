'''
Created on 12.05.2012
@author: bykov
@todo: update send request to generate request inside sendrequest
@todo: Add checks for cookie per request are ended with ;
@todo: Add support to request, session cookies, and not rewrite them.
@todo: Add precedense session above request, rewrite in matching.'''

from urllib.parse import urlencode
from random import sample, randint
from uuid import uuid4
from io import StringIO
from copy import deepcopy

import time
import socket
import ssl
import threading
import multiprocessing
import argparse
import base64

BUFF_READ_SIZE = 4096


HEADER_EXPECT100C = "Expect: 100-Continue"
HEADER_CONNECTION_CLOSE = "Connection: Close"

HEADER_CONTENT_LENGTH = "content-length"
HEADER_TRANSFER_ENCODING = "transfer-encoding"


DEFAULT_REQUEST_ENCODING = "ascii"
DEFAULT_HTTP_DELIMETER = "\r\n"

DEFAULT_LENGTH_URL = 25
DEFAULT_LENGTH_FT = 5
DEFAULT_LENGTH_HEADER = 25
DEFAULT_LENGTH_PARAM = 25
DEFAULT_LENGTH_VALUE = 50

POST_TYPE_URLENCODED = 0
POST_TYPE_MULTIPART = 1
POST_TYPE_RAW = 2
POST_TYPE_JSON = 3
POST_TYPE_XML = 4
POST_TYPE_FILE = 5

DATA_TYPES = {
                POST_TYPE_URLENCODED: "application/x-www-form-urlencoded",
                POST_TYPE_MULTIPART: "",
                POST_TYPE_RAW: "",
                POST_TYPE_JSON: "text/json;",
                POST_TYPE_XML: "text/xml;",

              }

RESPONSE_STATUS = 1
RESPONSE_HEADERS = 2
RESPONSE_BODY = 3






class HTTPRequestv2(object):
    """
        Class for HTTP request which will be send
    """
    __slots__ = ("method", "url", "headers","cookies","payload","chunk_size","version","enctype","repeat","resp_format","request")

    def __init__ (self,method="GET", url="/", headers=None, payload=None, chunk_size=0, version="HTTP/1.1", enctype=POST_TYPE_URLENCODED, repeat=1, resp_format=None):
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
        self.cookies = HTTPCookies()

        if headers: 
            self.updateRequestHeaders(headers)       
        self.payload = payload
        self.chunk_size = chunk_size
        self.version = version
        self.enctype = enctype
        self.repeat=repeat
        self.resp_format = resp_format
        
        self.request = None

    def updateRequestHeaders(self, headers={}) :
        if not headers:
            return

        if "Cookie" in headers:
            self.cookies.setCookies(cookies = headers["Cookie"])
            del headers["Cookie"]

        for header,value in headers.items():
            self.headers.append((header,value))

    def generateRequest(self):
        """
        Generate request for single use
        """
        

        if self.cookies.cookies:
            self.headers.append(("Cookie",self.cookies.getCookieHeaderValue()))
        
        self.request = generateRequestv2(self.method, self.url, self.headers, self.payload, self.chunk_size, self.version, self.enctype)

    
    def generateRawRequest(self):
        
       
        
        if not self.request:
            self.generateRequest()
        
        request_h = DEFAULT_HTTP_DELIMETER.join(self.request[0])
        # print (request_h)

        if self.request[1]:

            body_payload = ""
            if len(self.request[1]) >1:
                for chunk in request[1]:
                    body_payload += DEFAULT_HTTP_DELIMETER.join(chunk)
            else:
                body_payload = self.request[1][0]

            return request_h.encode() + body_payload.encode()
        else:
            return request_h.encode() + b""
        
    def generateSessionRequest(self):
        """
        Generate request to use in in session
        """
        
        return (self, self.repeat, self.resp_format)

    def getResponse(self,host=None,use_ssl=False,sock=None,use_ipv6=False,resp_format = None):
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
        
        if not self.request:
            self.generateRequest()
        
        return sendRequest(self.request, host, use_ssl, sock, self.resp_format, use_ipv6)

class HTTPRequestv3(object):
    """
        Class for HTTP request which will be send
    """
    __slots__ = ("method", "url", "headers","cookies","params","payload","chunk_size","version","enctype","repeat","resp_format","request","doassert")

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
                 resp_format="None",
                 doassert=None):
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
        self.cookies = HTTPCookies(cookies = cookies)

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



    def updateRequestHeaders(self, headers=None) :
        if not headers:
            return

        if "Cookie" in headers:
            self.cookies.setCookies(cookies=headers["Cookie"])
            del headers["Cookie"]

        for header,value in headers.items():
            self.headers.append((header, value))

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
            if len(self.request[1]) >1:
                for chunk in self.request[1]:
                    body_payload += DEFAULT_HTTP_DELIMETER.join(chunk)
            else:
                body_payload = self.request[1][0]

            return request_h.encode() + body_payload.encode()
        else:
            return request_h.encode() + b""
        
    def generateSessionRequest(self):
        """
        Generate request to use in in session
        """
        
        return (self, self.repeat, self.resp_format, self.doassert)

    def getResponse(self,host=None, use_ssl=False, sock=None, use_ipv6=False, resp_format=None):
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
        
        if not self.request:
            self.generateRequest()
        
        return sendRequest(self.request, host, use_ssl, sock, self.resp_format, use_ipv6, doassert=self.doassert)

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
        if headers == None:
            headers=[]
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

        self.resassert = self.checkAssertion(doassert)

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

class HTTPCookies(object):

    def __init__(self, headers=None, cookies=None):
        if headers:
            self.cookies = parseCookie(headers)
        else:
            self.cookies = {}
        if cookies:
            self.cookies.update(cookies)

    def __str__(self):
        return self.getCookieHeaderValue()

    def updateCookies(self, headers=None):
        if headers:
            cookies_from_headers = parseCookie(headers)
            self.cookies.update(cookies_from_headers)

    def setCookies(self, cookies=None):
        if cookies:
            self.cookies.update(cookies)

    def getCookies(self):
        return self.cookies

    def getCookieHeaderValue(self, cookies=None):
        if cookies:
            self.cookies.update(cookies)
        return "; ".join(["%s=%s" % (n, v) for (n, v) in self.cookies.items()])

    def getCookieHeader(self, cookies=None):
        if cookies:
            self.cookies.update(cookies)
        return  {"Cookie":"; ".join(["%s=%s" % (n,v) for (n,v) in self.cookies.items()])}

class HTTPRequest(object):
    pass

class TCPChannel(object):
    def __init__(self, host = None, data=None, secure=False, use_ipv6=False):
        
        self.session = False
        self.__sock = None

        self.send_data = data
        self.recieved_data = None
        self.ipv6 = use_ipv6
        self.secure = secure

        if not host :
            raise Exception("No host")
        else:
            self.host = host



    def _connect(self):
        if self.ipv6:
            sock = socket.socket(socket.AF_INET6,socket.SOCK_STREAM)
        else:
            sock = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
        #sock.settimeout(60)

        if self.secure:
            # print ("05")

            try:
                security_context=ssl.SSLContext(ssl.PROTOCOL_SSLv23)
                self.session = security_context.wrap_socket(sock)
             

            except ssl.SSLError as e:
                if self.session:
                    self.session.shutdown(socket.SHUT_RDWR)
                    self.session.close()  
                    sel.session = None
                    
                self.recieved_data = ( e.errno,e.strerror)

            
        else:
            # print ("06")
            self.session = sock

        #del sock
        # print ("07")
        try:
            self.session.connect(self.host)
        except OSError as e:
            self.recieved_data = ( e.errno,e.strerror) 

def generateRequestv2 (method, url, headers=None, payload=None, chunk_size=0,version="HTTP/1.1",post_type=POST_TYPE_URLENCODED):
    """
    Function generate request from parameters

    @param method: request method
    @type method: string
    @param url: requested url
    @type url: string
    @param headers: list of tuple (header_name, header_value)
    @type headers: list
    @param payload: data which send with 
    @type payload: any
    @param chunk_size: chunk size for Chunked requests. if 0, request is not chunked
    @type chunk_size: integer
    @param version: http version
    @type version: string
    @param post_type: encoding for data: 0 - urlencoding for GET and POST requests, 1 - multipart, 2 - raw data as is 
    @type post_type: integer
    
     
    """

    request_headers = []
    request_body = []
    request_str = "%s %s %s"

    if headers == None:
        headers = {}
    
    if payload:
        if isinstance(payload,dict) and "RANDOM_VALUE" in payload :
            name_tmp = payload ["RANDOM_VALUE"]
            del  payload ["RANDOM_VALUE"]
            payload.update({name_tmp:uuid4()})    
    
    if payload:
        if post_type == POST_TYPE_URLENCODED:
            ready_payload = (generateURLEncodedPayload(payload),)
        elif post_type == POST_TYPE_MULTIPART:               
            ready_payload = generateMultipartPayload(payload)
        elif post_type == POST_TYPE_RAW:
            ready_payload = (str(payload),)
        else:
            ready_payload = (generateURLEncodedPayload(payload,not_urlenc = True ),)
    else:
        ready_payload = None


    
    if (method.lower().strip() == "get"):
        if ready_payload:
            request_headers.append(request_str % (method.upper(), url+"?"+ ready_payload[0], version))            
        else:
            request_headers.append(request_str % (method.upper(), url, version))
        request_body=[]
        
    elif (method.lower().strip() == "post"):
        
        request_headers.append(request_str % (method.upper(), url, version))
        
        if ready_payload:
            
            if post_type == POST_TYPE_URLENCODED:
            
                request_headers.append("Content-Type: application/x-www-form-urlencoded")                

                if chunk_size>0:
                    request_headers.append("Transfer-Encoding: chunked")    
                    request_body = _generateChunkBody(chunk_size,ready_payload[0])
                
                else:                
                    request_body = []
                    request_headers.append("Content-Length: %d" % len(ready_payload[0]))
                 

                    request_body.append(ready_payload[0])
            
            elif post_type == POST_TYPE_MULTIPART:
               
                multipart_payload = generateMultipartPayload(payload)
                request_headers.append("Content-Type: multipart/form-data; boundary=%s" % ready_payload[1])
                
                if (chunk_size>0):
                    request_body = _generateChunkBody(chunk_size,multipart_payload[0])
                    request_headers.append("Transfer-Encoding: chunked")
                else:
                    request_body=[]
                    request_headers.append("Content-Length: %d" % len(multipart_payload[0]))
                    
                    request_body.append(multipart_payload[0])
                
            
            elif post_type == POST_TYPE_RAW:

                if chunk_size > 0:

                    request_headers.append("Transfer-Encoding: chunked")
                    request_body = _generateChunkBody(chunk_size,ready_payload[0])
                   
                else:
                    request_body = []
                    request_headers.append("Content-Length: %d" % len(str(ready_payload[0])))
                    request_body.append(ready_payload[0])
                
            
        else:
            request_body = []
    
            request_headers.append("Content-Length: 0")
    
    elif (method.lower().strip() == "patch"):
        
        request_headers.append(request_str % (method.upper(), url, version))
        
        if payload:

                if chunk_size > 0:

                    request_headers.append("Transfer-Encoding: chunked")
                    request_body = _generateChunkBody(chunk_size,payload)
                   
                else:
                    request_body = []
                    request_headers.append("Content-Length: %d" % len(str(payload)))
                    request_body.append(str(payload))

        

            
        else:
            request_body = []
            #request.append("Content-Type : application/x-www-form-urlencoded")
            request_headers.append("Content-Length: 0")
            

        for header,value in headers:
            if "Cookie" not in header:
                request_headers.append("%s: %s" %(header, value))
            else:
                cookie_header_value = ""
                for cookie_name, cookie_value in value.items():
                    cookie_header_value += "%s=%s; " % (cookie_name, cookie_value)
                request_headers.append ("%s: %s" %(header, cookie_header_value))
                
                
        request_headers.append("")
        request_headers.append("")                
        # print (request_headers, request_body)
        return (request_headers, request_body)        
            
    else:
        if payload:
            request_headers.append(request_str % (method.upper(), url, version))
            request_headers.append("Content-Length: %d" % len(str(payload)))
            request_body = str(payload)
        else:
            request_headers.append(request_str % (method.upper(), url, version))
            request_body = ""        
             


    for header,value in headers:
        # print (header,value)
        request_headers.append("%s: %s" %(header, value))
        
        # if "Cookie" not in header:
        #     request_headers.append("%s: %s" %(header, value))
        # else:
        #     # cookie_header_value = ""
        #     # try:
        #     #     for cookie_name, cookie_value in value.items():
        #     #         cookie_header_value += "%s=%s; " % (cookie_name, cookie_value)
        #     # except AttributeError:
        #         request_headers.append ("%s: %s" %(header, value))
            

        
            
    request_headers.append("") 
    request_headers.append("")       
       
   

    return (request_headers, request_body)

def generateRequestv3 (method, url, headers=None, cookies = None, params = None, payload=None, chunk_size=0,version="HTTP/1.1",post_type=POST_TYPE_URLENCODED):
    """
    Function generate request from parameters

    @param method: request method
    @type method: string
    @param url: requested url
    @type url: string
    @param headers: list of tuple (header_name, header_value)
    @type headers: list
    @param payload: data which send with 
    @type payload: any
    @param chunk_size: chunk size for Chunked requests. if 0, request is not chunked
    @type chunk_size: integer
    @param version: http version
    @type version: string
    @param post_type: encoding for data: 0 - urlencoding for GET and POST requests, 1 - multipart, 2 - raw data as is 
    @type post_type: integer
    
     
    """

    request_headers = []
    request_body = []
    request_str = "%s %s %s"

    if headers == None:
        headers = {}
    
    if params:
        if isinstance(params,dict) and "RANDOM_VALUE" in params :
            name_tmp = params ["RANDOM_VALUE"]
            del  params ["RANDOM_VALUE"]
            params.update({name_tmp:uuid4()})    
    
    if payload:
        if isinstance(payload,dict) and "RANDOM_VALUE" in payload :
            name_tmp = payload ["RANDOM_VALUE"]
            del  payload ["RANDOM_VALUE"]
            payload.update({name_tmp:uuid4()}) 
    
    if payload:
        if post_type == POST_TYPE_URLENCODED:
            ready_payload = (generateURLEncodedPayload(payload),)
        elif post_type == POST_TYPE_MULTIPART:               
            ready_payload = generateMultipartPayload(payload)
        elif post_type == POST_TYPE_RAW:
            ready_payload = (str(payload),)
        else:
            ready_payload = (generateURLEncodedPayload(payload,not_urlenc = True ),)
    else:
        ready_payload = None



    if params:
        request_headers.append(request_str % (method.upper(), url+"?"+ generateURLEncodedPayload(params), version))
    else:
        request_headers.append(request_str % (method.upper(), url, version))  
    
    if (method.lower().strip() == "get"):        
        request_body=[]
        
    elif (method.lower().strip() == "post"):
        
        if ready_payload:
            
            if post_type == POST_TYPE_URLENCODED:
            
                request_headers.append("Content-Type: application/x-www-form-urlencoded")                

                if chunk_size>0:
                    request_headers.append("Transfer-Encoding: chunked")    
                    request_body = _generateChunkBody(chunk_size,ready_payload[0])
                
                else:                
                    request_body = []
                    request_headers.append("Content-Length: %d" % len(ready_payload[0]))
                 

                    request_body.append(ready_payload[0])
            
            elif post_type == POST_TYPE_MULTIPART:
               
                multipart_payload = generateMultipartPayload(payload)
                request_headers.append("Content-Type: multipart/form-data; boundary=%s" % ready_payload[1])
                
                if (chunk_size>0):
                    request_body = _generateChunkBody(chunk_size,multipart_payload[0])
                    request_headers.append("Transfer-Encoding: chunked")
                else:
                    request_body=[]
                    request_headers.append("Content-Length: %d" % len(multipart_payload[0]))
                    
                    request_body.append(multipart_payload[0])
                
            
            elif post_type == POST_TYPE_RAW:

                if chunk_size > 0:

                    request_headers.append("Transfer-Encoding: chunked")
                    request_body = _generateChunkBody(chunk_size,ready_payload[0])
                   
                else:
                    request_body = []
                    request_headers.append("Content-Length: %d" % len(str(ready_payload[0])))
                    request_body.append(ready_payload[0])
                
            
        else:
            request_body = []
    
            request_headers.append("Content-Length: 0")
    
    elif (method.lower().strip() == "patch"):
        
        if ready_payload:

                if chunk_size > 0:

                    request_headers.append("Transfer-Encoding: chunked")
                    request_body = _generateChunkBody(chunk_size,payload)
                   
                else:
                    request_body = []
                    request_headers.append("Content-Length: %d" % len(str(payload)))
                    request_body.append(ready_payload[0])

        

            
        else:
            request_body = []
            #request.append("Content-Type : application/x-www-form-urlencoded")
            request_headers.append("Content-Length: 0")
            
   
            
    else:
        if payload:
            request_headers.append(request_str % (method.upper(), url, version))
            request_headers.append("Content-Length: %d" % len(str(payload)))
            request_body = str(payload)
        else:
            request_headers.append(request_str % (method.upper(), url, version))
            request_body = ""        
             


    for header,value in headers:
        # print (header,value)
        request_headers.append("%s: %s" % (header, value))
    

    if cookies.getCookies() :    
        request_headers.append("%s: %s" % ("Cookie",str(cookies)))
        
            

        
            
    request_headers.append("") 
    request_headers.append("")       
       
   

    return (request_headers, request_body)

def sendRequest(request_obj, host=None, use_ssl=False, sock=None,
                resp_format=None, use_ipv6=False, raw_request=None,
                is_chunked=False, doassert=None):
    """
    Send request passed in first parameter as tuple of HTTPSession headers(list) and request body(str) 
    
    
    @param request: request headers and body
    @type request: tuple
    @param host: ip address and port
    @type host: tuple
    @param use_ssl: use ssl or not
    @type use_ssl: boolen
    @param sock: contains already opened socket
    @type sock: socket object
    
    
    """
    
    # print ("01")


    resp_headers = bytearray()
    resp_body =    bytearray()
    
    
    is_chunked = False
    content_length = False
    connection_close=False
    
    if not host and not sock:
        raise Exception("No host or socket provided")
    
    # if (isinstance(request_obj, HTTPRequest)):
    #     request = request_obj.generateRequest()
    # el
    if (isinstance(request_obj,dict)):
        request = generateRequestv2(**request_obj)
    elif isinstance(request_obj, HTTPRequestv2):
        request = request_obj.generateRequestv2()
    elif isinstance(request_obj, HTTPRequestv3):
        request = request_obj.generateRequestv3()
    else:
        request = request_obj
    # print ("02")
    
    try:
        # print ("03")
        if sock:
            session = sock
            # del sock
        else:
            # print ("04")
            if use_ipv6:
                sock = socket.socket(socket.AF_INET6,socket.SOCK_STREAM)
            else:
                sock = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
            
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
            #sock.settimeout(60)

            if use_ssl:
                # print ("05")

                try:
                    security_context=ssl.SSLContext(ssl.PROTOCOL_SSLv23)
                    session = security_context.wrap_socket(sock)
                 

                except ssl.SSLError as e:
                    if session:
                        session.shutdown(socket.SHUT_RDWR)
                        session.close()  
                        session = None
                        
                    return HTTPResponse(headers = [str(e.errno)],payload = [e.strerror],sock = session) 

                #session = ssl.SSLSocket(sock)
            else:
                # print ("06")
                session = sock

            #del sock
            # print ("07")
            try:
                session.connect(host)
            except OSError as e:
                return HTTPResponse(headers = [str(e.errno)],payload = [e.strerror],sock = None) 
    
        if raw_request:
            raw_req_len = len (raw_request)
            
            len_sent = session.send (raw_request.encode(DEFAULT_REQUEST_ENCODING))
            if len_sent != raw_req_len:
                    raise socket.error("Not full request headers were send. Drop connection!")

            chunk = session.recv(BUFF_READ_SIZE)

        else:


            request_h = DEFAULT_HTTP_DELIMETER.join(request[0]).encode(DEFAULT_REQUEST_ENCODING)

            len_request_h = len(request_h)

            if HEADER_EXPECT100C in request[0] :
                # print ("08")
                len_sent = session.send (request_h)
                    
                if len_sent != len_request_h:                
                    raise socket.error("Not full request headers were send. Drop connection!")
                chunk = session.recv(BUFF_READ_SIZE)
                
                if chunk == 0:
                    raise socket.error("Remote side send FIN")

                if request[1]:               
                    # print ("09")
                    try:
                        status = chunk.decode().split()[1].strip()
                        
                        if int(status) == 100 :
                            
                            request_b = request[1].encode(DEFAULT_REQUEST_ENCODING)
                            len_request_b = len(request_b)
                            len_sent = session.send(request_b)

                            if len_sent != len_request_b:                        
                                raise socket.error ("Not full request payload were send. Drop connection!")
                            
                            chunk = session.recv(BUFF_READ_SIZE)
                            if chunk == 0:
                                raise socket.error("Remote side send FIN")
                        else:
                            chunk = session.recv(BUFF_READ_SIZE)
                            if chunk == 0:
                                raise socket.error("Remote side send FIN")

                    except IndexError:
                        raise socket.error("Some Network Issue")
                
            else:
                # print ("010")
                if request[1]:
                    # print ("010_1")
                    # @todo rewrite for correct chunk send. use _generate chunk function
                    if ("Transfer-Encoding: chunked" in request[0]):
                        len_sent = session.send (request_h)
                    
                        if len_sent != len_request_h:
                            print ("Not full request were send.Drop connection!")
                            raise socket.error ("Not full request were send.Drop connection!")
                        for req_chunk in request[1]:
                            request_b = DEFAULT_HTTP_DELIMETER.join(req_chunk).encode(DEFAULT_REQUEST_ENCODING)
                            len_request_b = len(request_b)
                            len_sent = session.send (request_b)
                    
                            if len_sent != len_request_b:
                                raise socket.error("Not full request were send. Drop connection!")
                    else:
                        
                        request_b = request[1][0].encode(DEFAULT_REQUEST_ENCODING)
                        len_request_b = len(request_b)

                        len_sent = session.send (request_h+request_b)
                    
                        if len_sent != len_request_b+len_request_h:
                        
                            raise socket.error("Not full request were send. Drop connection!")






                    # request_b = request[1].encode(DEFAULT_REQUEST_ENCODING)
                    # len_request_b = len(request_b)

                    # len_sent = session.send (request_h+request_b)
                    
                    # if len_sent != len_request_b+len_request_h:
                        
                    #     raise socket.error("Not full request were send. Drop connection!")
                    
                else:
                    # print ("010_2")
                    len_sent = session.send (request_h)
                    
                    if len_sent != len_request_h:
                        print ("Not full request were send.Drop connection!")
                        raise socket.error
                # print ("010_3")
                chunk = session.recv(BUFF_READ_SIZE)
                # print ("010_4")                        
                    

        #read response
        
                
        # session.settimeout(60.0)

        protocol = chunk[0:5]
        if protocol == b"HTTP/":
            
            while True:
                # print ("011")
                try:
                    (h_chunk, b_chunk) = chunk.split((DEFAULT_HTTP_DELIMETER*2).encode(DEFAULT_REQUEST_ENCODING),1)
                    # print (chunk,h_chunk,b_chunk)
                    resp_headers += h_chunk
                    resp_body += b_chunk
                    # print (type(resp_headers))
                    resp_headers = resp_headers.decode("utf-8").splitlines()
        
                    for c_header in resp_headers:
                        #print (c_header)
                        if c_header.lower().startswith(HEADER_TRANSFER_ENCODING):
                            c_value = c_header[c_header.index(":")+1:].strip()
                            if c_value.lower() == "chunked":
                                is_chunked=True
                            else:
                                is_chunked=False
                            
                        elif c_header.lower().startswith(HEADER_CONTENT_LENGTH):

                            content_length = int(c_header[c_header.index(":")+1:].strip())
                            # print (content_length, c_header)
                            
                        elif c_header.lower().strip() == HEADER_CONNECTION_CLOSE.lower():
                                connection_close = True
                        else:
                            pass

                    if is_chunked:
                        # print ("012")

                        while True:
                            if b"0\r\n\r\n" in resp_body[-11:]:
                                break
                            b_chunk = session.recv(BUFF_READ_SIZE)
                            # if len(b_chunk) != BUFF_READ_SIZE:
                            #     # print (len(b_chunk), b_chunk)
                            #     resp_body += b_chunk
                            #     # break

                            resp_body += b_chunk

                        # resp_body += b_chunk
                        break
                    elif content_length:
                        # print ("013")                        
                        # print (len(resp_body), content_length)
                        
                        while len(resp_body) < content_length:
                            # print ("013_1")
                            # print (len(resp_body), content_length)
                            # print (resp_body)


                            b_chunk =  session.recv(BUFF_READ_SIZE)
                            
                            # print ("013_2")
                            # print (len(resp_body), content_length)

                            resp_body += b_chunk
                            
                            # if len(b_chunk) != BUFF_READ_SIZE:
                            #     # print ("013_3")
                            #     # print (len(b_chunk), b_chunk)
                            #     resp_body += b_chunk
                            #     # break
                            # else:                   
                            #     # print ("013_3_1")
                            #     # print (len(b_chunk), b_chunk)     
                            #     resp_body += b_chunk
                            
                            # print (len(resp_body), content_length)

                            if len(resp_body)>=content_length:
                                # print ("013_4")
                                break
                        break
                    else:
                        # print ("014")
                        if (len(resp_body) == 0 ):
                            break
                        b_chunk = session.recv(BUFF_READ_SIZE)
                        while len(b_chunk)==BUFF_READ_SIZE:
                            resp_body += b_chunk
                            b_chunk = session.recv(BUFF_READ_SIZE)

                            
                            
                            if len(b_chunk) != BUFF_READ_SIZE:
                                resp_body += b_chunk
                                break
                        break


                    #print (resp_body)
                    
                except ValueError:
                    # print ("015")
                    resp_headers += chunk
                    chunk = session.recv(BUFF_READ_SIZE)
                    # if chunk == 0:
                    #     raise socket.error("Remote side send FIN")
        else:
            resp_headers=["No http headers were sent"]
            resp_body = chunk
            connection_close = True       
        
        if connection_close:
            session.shutdown(socket.SHUT_RDWR)
            session.close()
            session = None
        
        if not resp_format:
            return HTTPResponse(headers=resp_headers, payload=b"", sock=session, doassert=doassert)
        elif "body" in resp_format:
            return HTTPResponse(headers = resp_headers, payload = resp_body,sock = session, doassert=doassert)   
        elif "all" in resp_format:
            return HTTPResponse(headers = resp_headers, payload = resp_body,sock = session, doassert=doassert)
        elif "headers" in resp_format:
            return HTTPResponse(headers = resp_headers, payload = b"",sock = session, doassert=doassert)
        elif "status" in resp_format:
            return HTTPResponse(headers = resp_headers, payload = b"",sock = session, doassert=doassert)
        else:
            return HTTPResponse(headers = resp_headers, payload = b"",sock = session, doassert=doassert)

        del resp_headers
        del resp_body 

    except socket.error as e:
        # print ("016")

        if session:
            session.close()  
            session = None          
        return HTTPResponse(headers = [str(e.errno)],payload = [e.strerror],sock = session)
    except KeyboardInterrupt:
        print ("request interrupted!")


def _generateSampleAlphaChars (length):
    """
        Generate random char string exact length
        
        
        @param length: string length of random string
        @return: random string 
        
    """
    pop_us = "ABCDEFGHIJKLMNOPQURSTUVWXYZabcdefghijklmnopqrstuvwxyz"
    if length > len(pop_us):
        pop= pop_us * (2*int((length/len(pop_us))))
    else :
        pop = pop_us
    return "".join(sample(pop, length))

def _generateSampleAlphaNumMetaChar (length):
    """
        Generate random alpha num meta char string exact length
        
        
        @param length: string length of random string
        @return: random string 
        
    """
    pop_us = "ABCDEFGHIJKLMNOPQURSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789!@#$%^&*(()_+=-<>,./?\`~|\}]{["
    if length > len(pop_us):
        pop= pop_us * (2*int((length/len(pop_us))))
    else :
        pop = pop_us
    return "".join(sample(pop, length))

def _generateMultipartBoundary (length):
    """
    Generate random boundary for multipart messages
    """
    
    pop_us = "1234567890ABCDEFGHIJKLMNOPQURSTUVWXYZabcdefghijklmnopqrstuvwxyz01234567890"
    if length > len(pop_us):
        pop= pop_us * (2*int((length/len(pop_us))))
    else :
        pop = pop_us
    return "".join(sample(pop, length))
    
def _generateChunkBody(chunk_size,payload):
    request_body=[]

def parseCookie (responseHeaders):
    """

    """

    cookie_pair_list = {}
    try:
        for header,value in responseHeaders:
            if header == "Set-Cookie":
                try :
                    cookie = value[:value.index("; ")]
                except ValueError:
                    cookie = value
                else:
                    n,v = cookie.split("=")
                    cookie_pair_list.update({n:v})
            else:
                continue
    except ValueError:
        for cheader in responseHeaders:
            if cheader.lower().startswith("set-cookie"):
                s = cheader.index(":")
                try:
                    e = cheader.index(";")
                except ValueError:
                    e = len(cheader)
                cookie = cheader[s+1:e]
                n,v = cookie.split("=")
                cookie_pair_list.update({n.strip():v.strip()})
    return cookie_pair_list

def _isChunked (responseHeaders):
    
    transferencoding = False
    
    
    try: 
        for header,value in responseHeaders:
            if header == "Transfer-Encoding" and value.lower() == "chunked":
                transferencoding=True
                break                
            else:
                continue
    except ValueError:
        for cheader in responseHeaders:
            if cheader.lower().startswith("transfer-encoding"):
                header,value = cheader.split(":")
                if value.lower() == "chunked":
                    transferencoding == True
                    break
                else:
                    continue
                
    return transferencoding

def generateListOfURLS (number, predefined=False,urlftk=0.1):
    """ 
    @param number: amount of generated URLS
    @return: list of generate random urls
    """
    url_list = []
    # while number:
    #     if predefined:
    #         url_list.append("/%d_this_is_predefined_url_with_possible_long_name.%dftype" % (number,number))
    #     else:
    #         url_list.append("/%s.%s" % (_generateSampleAlphaChars(DEFAULT_LENGTH_URL),_generateSampleAlphaChars(DEFAULT_LENGTH_FT)))
    #     number -= 1

    for i in range(1,number+1):
        if predefined:
            url_list.append("/%d_this_is_predefined_url_with_possible_long_name.%dftype" % (i,int(i*urlftk)))
        else:
            url_list.append("/%s.%s" % (_generateSampleAlphaChars(DEFAULT_LENGTH_URL),_generateSampleAlphaChars(DEFAULT_LENGTH_FT)))
             

    return url_list

def generateListOfURLSwMetaChars (number):
    """ 
    @param number: amount of generated URLS
    @return: list of generate random urls
    """
    url_list = []
    while number:
        url_list.append("/%s.%s" % (_generateSampleAlphaNumMetaChar(DEFAULT_LENGTH_URL),_generateSampleAlphaChars(DEFAULT_LENGTH_FT)))
        number -= 1
    return url_list

def generateListOfHeaders (number):
    """ 
    @param number: amount of generated headers
    @return: list of generate random headers
    """
    header_list = {}
    while number:
        header_list["H"+_generateSampleAlphaChars(DEFAULT_LENGTH_HEADER)]= _generateSampleAlphaChars(DEFAULT_LENGTH_HEADER)
        number -= 1
    return header_list

def generateListOfParameters (number,predefined=False):
    """ 
    @param number: amount of generated parameters    
    @return: list of generate random parameters
    """
    param_list = []
    # while number:
    #     if predefined:
    #         param_list.append("%d_this_parameter_is_predefined" % (number))
    #     else:
    #         param_list.append("%s" % (_generateSampleAlphaChars(DEFAULT_LENGTH_PARAM)))
    #     number -=1

    for i in range (number):
        if predefined:
            param_list.append("%d_this_parameter_is_predefined" % (i))
        else:
            param_list.append("%s" % (_generateSampleAlphaChars(DEFAULT_LENGTH_PARAM)))
    return param_list

def generateListOfValues (number):
    """ 
    @param number: amount of generated parameters    
    @return: list of generate random parameters
    """
    value_list = []
    while number:
        value_list.append("%s<script><xml>; drop</xml>document.createElement(alert())</script>" % (_generateSampleAlphaNumMetaChar(DEFAULT_LENGTH_VALUE)))
        number -=1
    return value_list

def generateIPv4Address():
    return "%s.%s.%s.%s" % (randint(1,255),randint(1,255),randint(1,255),randint(1,255))

def mapParameterValue(listParam, listValue):
    datadict = {}

    if (len(listParam) == len(listValue)):
        for i in range (0,len(listParam)):
            datadict [listParam[i]] = listValue[i]
    else: 
        for param in listParam:
            datadict [param] = listValue[randint(0,len(listValue)-1)]        
    
    return datadict
   
def generateURLEncodedPayload (data, not_urlenc = False):
    if isinstance(data,dict):
        if not_urlenc:
            qs =""
            for key,value in data.items():
                qs += "%s=%s&" % (key,value)
            return qs[:len(qs)-1]

        else:
            return urlencode(data)
    elif isinstance(data, str):
        return data
    else:
        return ""

def generateMultipartPayload (data):
    """
    Generate multipart body message
    
    """
    
    
    multipartdata = [] 
    boundary = _generateMultipartBoundary(70)
    for name,value in data.items():
        multipartdata.append("--%s" % boundary )
        multipartdata.append ("Content-Disposition: form-data; name=\"%s\"" % name)
        multipartdata.append ("")
        multipartdata.append (value)
    multipartdata.append("--%s--" % boundary)
  
    return  (DEFAULT_HTTP_DELIMETER.join(multipartdata),boundary)
    

class HTTPSessionv2(object):
    '''
    Class for genrating HTTP session. have method to send on request, create http flow from several requests and send on by one
    
    '''
    __slots__ = ("debug","request","session_cookies","sock","response","session","host","secure","session_headers","prefix_url","resp_format","session_http_version","ipv6","delay")

    def __init__(self, host=None, secure = False, request=None, flow=None, session_headers = None, prefix_url="", session_http_version="", resp_format=None, *args, **kwargs):
        '''
        
        @param host:used for configuring remote host ("host",port)
        @type host:tuple
        @param secure:is ssl connection used or not
        @type secure:boolen
        @param request: instance of HTTPRequest class
        @type request:HTTPRequest
        @param flow: list of dict, describing the request
        @type flow: list
        @param session_headers:
        @type session_headers: dict
        @param prefix_url:
        @type prefix_url: string
        @param session_http_version:
        @type session_headers: string
        '''
        
        try:
            if kwargs["delay"]: 
                self.delay = kwargs["delay"]
            else:
                self.delay = False
            
        except KeyError:
            self.delay = False
       

        try:
            if kwargs["debug"] == True:
                self.debug = True
            else:
                self.debug = False
            
        except KeyError:
            self.debug = False
        
        
        try:
            if kwargs["use_ipv6"] == True:
                self.ipv6 = True
            else:
                self.ipv6 = False
        except KeyError:
                self.ipv6 = False



        
        self.sock = None
        self.response=None
        
        self.session_cookies = HTTPCookies()
        self.session_headers = []
        
        self.session = []       
        
        if request and isinstance(request, HTTPRequestv2):
            self.addSessionRequestv2(request)
            self.request=None
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
        
        if prefix_url:
            self.prefix_url = prefix_url
        else:
            self.prefix_url = None
        
        if session_http_version:
            self.session_http_version = session_http_version
        else:
            self.session_http_version = None
        
        if resp_format:
            self.resp_format = resp_format
        else:
            self.resp_format = "None"

        if flow:            
            self.parseSessionv2(session_flow=flow)
        
    
    def parseSessionv2 (self,session_flow = None, *args, **kwargs):
        '''
        Parse http session and generate requests for next usage. Format of request :
        @TODO fix work with cookies as dict
        
        {
         "url":URL to send, 
         "method":Method to use GET|POST|HEAD
         "headers": dict of headers {"Header":"Value"}.
         "payload": payload to send could be dict {"param":"value} or raw text.
         "enctype": how enctype the payload 0 - urlencoded, 1-multipart, 2-as is,
         "repeat":how many times repeat request,
         "chunk_size":size of chunk, if send request payload chunked.
         "resp_format": all|body|headers|status
        }

        
        @param session:list of requests formated in special way. see examples
        @type session:list
        @param session_headers:dict of headers HeaderName:Header value, which will be assigned to each request in session
        @type session_headers:dict
        @param prefix_url:prefix what will be added to each url in session 
        @type prefix_url:str
        @param session_http_version:
        @type session_http_version:
        '''
     
        for request in session_flow:      

            try:
                method = request["method"]
            except KeyError:
                method = "GET"
          
            try:
                url = request["url"]
                if self.prefix_url:
                    url = self.prefix_url+url
            except KeyError:
                url="/"
            
            try:
                # print (request["headers"])
                url_headers = request["headers"]
                # print (url_headers)
                url_headers.update(self.session_headers)
                if self.session_cookies.cookies and "Cookie" in url_headers:
                    url_headers["Cookie"].update(self.session_cookies.getCookies())
                else:
                    if self.session_cookies.cookies:
                        url_headers["Cookie"] = self.session_cookies.getCookies()
            except KeyError:
                url_headers = {}
                url_headers.update(self.session_headers)            
                if self.session_cookies.cookies:
                    url_headers["Cookie"] = self.session_cookies.getCookies()
            

            try:
                url_payload = request["payload"]
            except KeyError:
                url_payload = None
            
            try:
                enctype = int(request["enctype"])
                
            except KeyError:
                enctype = 0    
            
            try:
                repeat = request["repeat"]
            except KeyError:
                repeat = 1
                
            try:
                chunk_size = request["chunk_size"]
            except KeyError:
                chunk_size = 0
            
            try:
                if not self.resp_format:
                    self.resp_format = request["resp_format"]
            except KeyError:
                self.resp_format = "None"

            try:
                http_version = request["version"]
            except KeyError:
                if self.session_http_version:
                    http_version = self.session_http_version
                else:
                    http_version = "HTTP/1.1"
            

            self.addSessionRequestv2(HTTPRequestv2(method, url, url_headers, url_payload, chunk_size, http_version, enctype, repeat, self.resp_format))
            
    def addSessionRequestv2 (self,request=None):

        if request and isinstance(request,HTTPRequestv2):
            self.session.append(request)        
        elif request and isinstance(request,dict):

            self.session.append(HTTPRequestv2(**request))
        else:
            raise Exception("Invalid request object")

    def runSessionv2(self, host = None, secure=False, delay=0, session_headers = None, prefix_url=None, resp_format=None, version=None, *args, **kwargs):
        '''
        Run session. Send each request from self.session list.
        
        @param delay:delay in seconds between requests
        @type delay:float
        @type self.request:HTTPRequest
        '''
        if host:
            self.host = host
        if secure:
            self.secure = True
        if self.delay:
            delay = self.delay
      
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
                # save original headers and cookies
                req_cookie = self.request.cookies.getCookies().copy()
                req_headers = self.request.headers[:]

                         

                
                
                # update request header and cookie according new session headers
                if session_headers:                
                    self.request.updateRequestHeaders(session_headers)

                
                #update cookie which was recieved from response and saved into self.session_cookies

                if self.session_cookies.cookies:
                    self.request.cookies.setCookies(self.session_cookies.getCookies())
                   
                
                # print (self.request.headers)
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
                #update cookie from response headers
                self.session_cookies.updateCookies(self.response.headers)
                
                if self.debug:
                    print (self.request.generateRawRequest())
                    # if self.session_cookies.cookies:
                    #     for cookie in 
                    #     print (self.request.headers["Cookie"])

                print_resp = self.request.resp_format.lower()
                if "status" in print_resp:
                    print (self.response.status)
                if "headers" in print_resp:
                    print (self.response.headers)
                if "body" in print_resp:
                    print (self.response.payload)
                if "all" in print_resp:
                    print (self.response.status)
                    print (self.response.headers)
                    print (self.response.payload)
                
                self.request.headers = req_headers
                self.request.cookies = HTTPCookies(cookies = req_cookie)
                
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
                    
                if self.debug:
                    print (self.request.generateRawRequest())
                    # if self.session_cookies.cookies:
                    #     for cookie in 
                    #     print (self.request.headers["Cookie"])
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
                

                print_resp = self.request.resp_format.lower()
                if "status" in print_resp:
                    print (self.response.status)
                if "headers" in print_resp:
                    print (self.response.headers)
                if "body" in print_resp:
                    print (self.response.payload)
                if "all" in print_resp:
                    print (self.response.status)
                    print (self.response.headers)
                    print (self.response.payload)
                
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

    def closeSession(self,session_flow = False,one_session = False):
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


class HTTPSessionv3(object):
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

        if request and isinstance(request, HTTPRequestv3):
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
            self.addSessionRequestv3(HTTPRequestv3(**request))

    def addSessionRequestv3(self, request=None):

        if request and isinstance(request, HTTPRequestv3):
            self.session.append(request)
        elif request and isinstance(request, dict):
            self.session.append(HTTPRequestv3(**request))
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
                self.doassert = kwargs["doassert"]
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
                    try:
                        
                        key, value = list(self.doassert.items())[0]
                        if key in "payload":
                            assert bytes(value) in self.response[key]
                            print("passed")
                        else:
                            assert value in self.response[key]
                            print("passed")
                    except AssertionError:
                        print("failed. should be " + value)

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
                    
                if self.debug:
                    print (self.request.generateRawRequest())
                    # if self.session_cookies.cookies:
                    #     for cookie in 
                    #     print (self.request.headers["Cookie"])
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
                

                print_resp = self.request.resp_format.lower()
                if "status" in print_resp:
                    print (self.response.status)
                if "headers" in print_resp:
                    print (self.response.headers)
                if "body" in print_resp:
                    print (self.response.payload)
                if "all" in print_resp:
                    print (self.response.status)
                    print (self.response.headers)
                    print (self.response.payload)
                
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


class HTTPClient(threading.Thread):
    """
    
    """

    def __init__(self, host=None, secure = False, delay=0, repeat=10, flow=None, session_headers = None, prefix_url="", session_http_version="", resp_format=None, xff=True, debug=False, *args, **kwargs):
        
        """        
        @param command:
        @type command:
        @param c_args:
        @type c_args:
        @param c_kwargs:
        @type c_kwargs:

        """
        self.api_version = kwargs["v"]
        del (kwargs["v"])

        threading.Thread.__init__(self,*args,**kwargs)
        
        self.host = host
        self.secure = secure
        self.delay = delay
        self.time = repeat
        self.xff = xff

        if not session_headers:
            session_headers = {}
        
        if self.api_version == 2:
            self.runhttpsession = HTTPSessionv2(flow = flow, session_headers=session_headers.copy(), prefix_url=prefix_url, session_http_version=session_http_version, resp_format=resp_format, debug=debug)       
        else:
            self.runhttpsession = HTTPSessionv3(flow = flow, session_headers=session_headers.copy(), prefix_url=prefix_url, session_http_version=session_http_version, resp_format=resp_format, debug=debug)       

    def run(self):
        
        print("session start", threading.currentThread().name, multiprocessing.current_process().name, "on host:",self.host)
        
        ct = st = time.time()
        while ct-st < self.time:
            
            if self.xff:
                if self.api_version == 2:
                    self.runhttpsession.runSessionv2(self.host, self.secure, self.delay,session_headers = {"X-Forwarded-For": generateIPv4Address()})
                else:
                    self.runhttpsession.runSessionv3(self.host, self.secure, self.delay,session_headers = {"X-Forwarded-For": generateIPv4Address()})
            else:
                if self.api_version == 2:
                    self.runhttpsession.runSessionv2(self.host, self.secure, self.delay)
                else:
                    self.runhttpsession.runSessionv3(self.host, self.secure, self.delay)
            ct = time.time()         

        
        print("session finished", threading.currentThread().name, multiprocessing.current_process().name, "on host:",self.host)

        return


class HTTPClientsPool(multiprocessing.Process):
    
    def __init__(self, num_of_clients=1, host=None, secure = False, delay=0, repeat=10, flow=None, session_headers = None, prefix_url="", session_http_version="", xff = True, resp_format=None, debug=False,*args, **kwargs):
        multiprocessing.Process.__init__(self)
        self.num_of_clients = num_of_clients
        self.kwargs = {
            "host" : host,
            "secure" : secure,
            "delay" : delay,
            "repeat" : repeat,
            "flow" : deepcopy(flow),
            "session_headers" : session_headers,
            "prefix_url": prefix_url,
            "session_http_version" : session_http_version,
            "xff": xff,
            "resp_format" : resp_format,
            "debug" : debug,
        }
        
        
    def run(self):
        client_pool = []
        for i in range(1,self.num_of_clients+1):
            client = HTTPClient(**self.kwargs)
            client.start()
            client_pool.append(client)
            client = None

        while True:
            for th in client_pool:
                if not th.is_alive():
                    client_pool.pop(client_pool.index(th))
            if len(client_pool) < 1 : 
                    break 
        
        return

class HTTPClientsPools(object):
    def __init__(self, num_of_pools=1, num_of_clients=1, host=None, secure = False, delay=0, repeat=10, flow=None, session_headers = None, prefix_url="", session_http_version="", xff = True, resp_format=None, debug=False,*args, **kwargs):
        self.num_of_pools = num_of_pools
       
        self.kwargs = {
            "num_of_clients":num_of_clients,
            "host" : host,
            "secure" : secure,
            "delay" : delay,
            "repeat" : repeat,
            "flow" : flow,
            "session_headers" : session_headers,
            "prefix_url": prefix_url,
            "session_http_version" : session_http_version,
            "xff":xff,
            "resp_format" : resp_format,
            "debug" : debug,
        }
        
        
    def run(self):
        pool_pools = []
        for i in range(1,self.num_of_pools+1):
            pool = HTTPClientsPool(**self.kwargs)
            pool.start()
            pool_pools.append(pool)
            pool = None

        while True:
            for th in pool_pools:
                if not th.is_alive():
                    pool_pools.pop(pool_pools.index(th))
            if len(pool_pools) < 1 : 
                    break 
        
        return    


class HTTPClientsTraffic(object):
    def __init__(self, sessions_list,*args, **kwargs):
        self.sessions = sessions_list             
        
    def run(self):
        for session in self.sessions:
            pool_pools = []
            num_of_pools = session["num_of_pools"]
            del session["num_of_pools"]
            
            for i in range(1,num_of_pools+1):
                pool = HTTPClientsPool(**session)
                pool.start()
                pool_pools.append(pool)
                pool = None

        while True:
            for th in pool_pools:
                if not th.is_alive():
                    pool_pools.pop(pool_pools.index(th))
            if len(pool_pools) < 1 : 
                    break 
        
        return    



class RunStressTraffic(object):


    def __init__(self, cmd=None):
        self.cmd = cmd

    def runHighLoad (self,host,num_threads=5,repeat=10,id=1,delay=0,hostname="localhost"):
    
        threads = []
        
        for i in range (0,num_threads):
            th = threading.Thread (target=self.cmd, kwargs={"host":host,"repeat":repeat,"id": id,"delay":delay,"hostname":hostname})
            th.start()
            threads.append(th)
            
        while True:
            for th in threads:
                if not th.is_alive():
                    threads.pop(threads.index(th))
            if not threads: 
                    break
 
    
    def runStressTraffic(self):
    
        parser = argparse.ArgumentParser(description="Generate traffic for host")
        parser.add_argument("host",type=str, help="ip address of server")
        parser.add_argument("port",type=str, help="port of server")
        parser.add_argument("-t","--duration" , type=str, help="time in second during sending traffic")
        parser.add_argument("-p","--process" , type=str, help="number of process which generate traffic")
        parser.add_argument("-c","--clients" , type=str, help="number of clients per process")
        parser.add_argument("-d","--delay" , type=str, help="delay between requests")
        parser.add_argument("-n","--domain" , type=str, help="hostname")
        parser.add_argument("-s","--ssl",type=str,help="Use ssl connection")
        #parse cli arguments as list of values
        cli_params = vars(parser.parse_args())
        
        
        PAMOUNT = 1
        host = [(cli_params["host"],int(cli_params["port"]))]
        
        if not cli_params["duration"]:
            repeat = 1
        else:
            repeat = cli_params["duration"]
               
        if not cli_params["process"]:
            pamount = PAMOUNT
        else:
            pamount = cli_params["process"]        
        
        if not cli_params["clients"]:
            num_threads = 5
        else:
            num_threads = cli_params["clients"]        
        
        if not  cli_params["delay"]:
            delay=0
        else:
            delay = float(cli_params["delay"])
        
        if not cli_params["domain"]:
            domain = "localhost"
        else:
            domain = cli_params["domain"]

        if not cli_params["ssl"]:
            host.append(False)
        else:
            host.append(True)
     
        try :
            processes = []
            for i in range(2,int(pamount)+2):
                p = multiprocessing.Process(target=self.runHighLoad,kwargs={"host":host, "repeat":int(repeat),"num_threads":int(num_threads),"id":i,"delay":delay,"hostname": domain})
                try:
                    p.start()
                    processes.append(p)
                
                except KeyboardInterrupt:
                    print ("stop by user")

            
            while True:
                for p in processes:
                    if not p.is_alive():
                        processes.pop(processes.index(p))
                if not processes:
                        break
        except KeyboardInterrupt:
            print ("stop by user")
        else:
            print ("successfull stop!")

    def runStressTrafficIntercatively(self,host,num_process=1,num_threads=5,repeat=10,id=1,delay=0,hostname="localhost"):
        try :
            processes = []
            for i in range(2,int(num_process)+2):
                p = multiprocessing.Process(target=self.runHighLoad,kwargs={"host":host, "repeat":int(repeat),"num_threads":int(num_threads),"id":i,"delay":delay,"hostname": hostname} )
                try:
                    p.start()
                    processes.append(p)
                
                except KeyboardInterrupt:
                    print ("stop by user")

            
            while True:
                try:
                    for p in processes:
                        if not p.is_alive():
                            processes.pop(processes.index(p))
                    if not processes:
                            break
                except KeyboardInterrupt:
                    print ("stop by user")
        
        except KeyboardInterrupt:
            print ("stop by user")
        else:
            print ("successfull stop!")    


def HTTPcurrentClient():    
    return  "%s-%s-%s" % (multiprocessing.current_process().name, threading.currentThread().name, uuid4())


def GetCMDParameters():
    parser = argparse.ArgumentParser(description="Generate traffic for host")
    parser.add_argument("host",type=str, help="ip address of server")
    parser.add_argument("port",type=str, help="port of server")
    parser.add_argument("-t","--duration" , type=str, help="time in second during sending traffic")
    parser.add_argument("-p","--process" , type=str, help="number of process which generate traffic")
    parser.add_argument("-c","--clients" , type=str, help="number of clients per process")
    parser.add_argument("-d","--delay" , type=str, help="delay between requests")
    parser.add_argument("-n","--domain" , type=str, help="hostname")
    parser.add_argument("-s","--ssl",type=str,help="Use ssl connection")
    #parse cli arguments as list of values
    return vars(parser.parse_args())



   





if __name__=="__main__":
    flow  = [
    {"method":"get","url":"/index.php"},
    {"method":"post","url":"/login.php","payload":{"username":"asdfadsf","password":"password"}}
   ]
    session_parameters = {
            "host" : ("172.29.70.5",80),
            "secure" : False,
            "delay" : 2,
            "repeat" : 300,
            "flow" : flow,
            "session_headers" : {"Host":"asm.test.com"},
            "prefix_url": "",
            "session_http_version" : "HTTP/1.1",
            "resp_format" : "None",
            "debug" : False,
        }



    vs_ip_list = [ 
        # {
        #     "vs_ip":"172.29.70.42",
        #     "port_start":10000,
        #     "multi":False,
        #     "session_parameters": session_parameters,

        # },
        {
            "vs_ip":"172.29.70.43", 
            "port_start":10000,
            "multi":True,
            "session_parameters":session_parameters    
        }
    ]    
    try :

        for vs in vs_ip_list:


            processes = []
            for i in range(1,101):
                vs["session_parameters"]["host"] = (vs["vs_ip"],vs["port_start"]+i)
                if vs["multi"] == False:
                    vs["session_parameters"]["session_headers"]["X-Policy-Name"] = "asmpl_name%d" % i
                    p = HTTPClientsPool(num_of_clients=5,**vs["session_parameters"])
                    try:
                        p.start()
                        processes.append(p)
            
                    except KeyboardInterrupt:
                        print ("stop by user")
                else:
                    for j in range(1,6):

                        vs["session_parameters"]["session_headers"]["X-Policy-Name"] = "asmpl_name%d" % randint(1,51)
                        p = HTTPClientsPools(num_of_clients=2,**vs["session_parameters"])
                        try:
                            p.start()
                            processes.append(p)
                
                        except KeyboardInterrupt:
                            print ("stop by user")

        





        while True:
            for p in processes:
                if not p.is_alive():
                    processes.pop(processes.index(p))
            if not processes:
                    break
    except KeyboardInterrupt:
            print ("stop by user")
    else:
            print ("successfull stop!")
     