from urllib.parse import urlencode, quote_plus
from random import sample, randint
from uuid import uuid4
from io import StringIO
from copy import deepcopy
from .HTTPResponse import *



import socket
import ssl
# import threading
# import multiprocessing
# import argparse
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


def generateRequestv3(method, url, headers=None, cookies=None, params=None, payload=None, chunk_size=0, version="HTTP/1.1", post_type=POST_TYPE_URLENCODED):
    """
        Function generate request from parameters

        @param method: request method
        @type method: string
        @param url: requested url
        @type url: string
        @param headers: list of tuple (header_name, header_value)
        @type headers: list
        @param cookies: dict of cookies name: value
        @type cookies: dict
        @param params: dict of params which will be send in QS
        @type params: dict
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

    if headers is None:
        headers = {}

    if params:
        if isinstance(params, dict) and "RANDOM_VALUE" in params:
            name_tmp = params["RANDOM_VALUE"]
            del params["RANDOM_VALUE"]
            params.update({name_tmp: uuid4()})

    if payload:
        if isinstance(payload, dict) and "RANDOM_VALUE" in payload:
            name_tmp = payload["RANDOM_VALUE"]
            del payload["RANDOM_VALUE"]
            payload.update({name_tmp: uuid4()})

    if payload:
        if post_type == POST_TYPE_URLENCODED:
            ready_payload = (generateURLEncodedPayload(payload),)
        elif post_type == POST_TYPE_MULTIPART:
            ready_payload = generateMultipartPayload(payload)
        elif post_type == POST_TYPE_RAW:
            ready_payload = (str(payload),)
        else:
            ready_payload = (generateURLEncodedPayload(payload, not_urlenc=True),)
    else:
        ready_payload = None

    if params:
        request_headers.append(request_str % (method.upper(), url + "?" + generateURLEncodedPayload(params), version))
    else:
        request_headers.append(request_str % (method.upper(), url, version))

    if (method.lower().strip() == "get"):
        request_body = []

    elif (method.lower().strip() == "post"):

        if ready_payload:

            if post_type == POST_TYPE_URLENCODED:

                request_headers.append("Content-Type: application/x-www-form-urlencoded")

                if chunk_size > 0:
                    request_headers.append("Transfer-Encoding: chunked")
                    request_body = _generateChunkBody(chunk_size, ready_payload[0])

                else:
                    request_body = []
                    request_headers.append("Content-Length: %d" % len(ready_payload[0]))
                    request_body.append(ready_payload[0])

            elif post_type == POST_TYPE_MULTIPART:

                request_headers.append("Content-Type: multipart/form-data; boundary=%s" % ready_payload[1])

                if chunk_size > 0:
                    request_body = _generateChunkBody(chunk_size, ready_payload[0])
                    request_headers.append("Transfer-Encoding: chunked")
                else:
                    request_body = []
                    request_headers.append("Content-Length: %d" % len(ready_payload[0]))

                    request_body.append(ready_payload[0])

            elif post_type == POST_TYPE_RAW:

                if chunk_size > 0:

                    request_headers.append("Transfer-Encoding: chunked")
                    request_body = _generateChunkBody(chunk_size, ready_payload[0])

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
                    request_body = _generateChunkBody(chunk_size, payload)

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

    for header, value in headers:
        # print (header,value)
        request_headers.append("%s: %s" % (header, value))

    if cookies.getCookies():
        request_headers.append("%s: %s" % ("Cookie", str(cookies)))

    request_headers.append("")
    request_headers.append("")

    return (request_headers, request_body)


def sendRequest(request_obj, host=None, use_ssl=False, sock=None, resp_format=None, use_ipv6=False, raw_request=None, is_chunked=False, doassert=None, doaction=None):
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
    resp_body = bytearray()

    is_chunked = False
    content_length = False
    connection_close = False

    if not host and not sock:
        raise Exception("No host or socket provided")

    # if (isinstance(request_obj, HTTPRequest)):
    #     request = request_obj.generateRequest()
    # el
    if (isinstance(request_obj, dict)):
        request = generateRequestv3(**request_obj)
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
                sock = socket.socket(socket.AF_INET6, socket.SOCK_STREAM)
            else:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

            sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
            # sock.settimeout(60)

            if use_ssl:
                # print ("05")

                try:
                    security_context = ssl.SSLContext(ssl.PROTOCOL_SSLv23)
                    session = security_context.wrap_socket(sock)

                except ssl.SSLError as e:
                    if session:
                        session.shutdown(socket.SHUT_RDWR)
                        session.close()
                        session = None

                    return HTTPResponse(headers=[str(e.errno)],
                                        payload=[e.strerror],
                                        sock=session)

                # session = ssl.SSLSocket(sock)
            else:
                # print ("06")
                session = sock

            # del sock
            # print ("07")
            try:
                session.connect(host)
            except OSError as e:
                return HTTPResponse(headers=[str(e.errno)],
                                    payload=[e.strerror], sock=None)

        if raw_request:
            raw_req_len = len(raw_request)

            len_sent = session.send(raw_request.encode(DEFAULT_REQUEST_ENCODING), errors="replace")
            if len_sent != raw_req_len:
                    raise socket.error("Not full request headers were send. Drop connection!")

            chunk = session.recv(BUFF_READ_SIZE)

        else:

            request_h = DEFAULT_HTTP_DELIMETER.join(request[0]).encode(DEFAULT_REQUEST_ENCODING, errors="replace")

            len_request_h = len(request_h)

            if HEADER_EXPECT100C in request[0]:
                # print ("08")
                len_sent = session.send(request_h)

                if len_sent != len_request_h:
                    raise socket.error("Not full request headers were send. Drop connection!")
                chunk = session.recv(BUFF_READ_SIZE)

                if chunk == 0:
                    raise socket.error("Remote side send FIN")

                if request[1]:
                    # print ("09")
                    try:
                        status = chunk.decode().split()[1].strip()

                        if int(status) == 100:

                            request_b = request[1].encode(DEFAULT_REQUEST_ENCODING, errors="replace")
                            len_request_b = len(request_b)
                            len_sent = session.send(request_b)

                            if len_sent != len_request_b:
                                raise socket.error("Not full request payload were send. Drop connection!")

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
                    if "Transfer-Encoding: chunked" in request[0]:
                        len_sent = session.send(request_h)

                        if len_sent != len_request_h:
                            print ("Not full request were send.Drop connection!")
                            raise socket.error ("Not full request were send.Drop connection!")
                        for req_chunk in request[1]:
                            request_b = DEFAULT_HTTP_DELIMETER.join(req_chunk).encode(DEFAULT_REQUEST_ENCODING, errors="replace")
                            len_request_b = len(request_b)
                            len_sent = session.send (request_b)
                    
                            if len_sent != len_request_b:
                                raise socket.error("Not full request were send. Drop connection!")
                    else:
                        
                        request_b = request[1][0].encode(DEFAULT_REQUEST_ENCODING, errors="replace")
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
                    (h_chunk, b_chunk) = chunk.split((DEFAULT_HTTP_DELIMETER*2).encode(DEFAULT_REQUEST_ENCODING, errors="replace"),1)
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
                        if len(resp_body) == 0:
                            break
                        b_chunk = session.recv(BUFF_READ_SIZE)
                        while len(b_chunk) == BUFF_READ_SIZE:
                            resp_body += b_chunk
                            b_chunk = session.recv(BUFF_READ_SIZE)

                            if len(b_chunk) != BUFF_READ_SIZE:
                                resp_body += b_chunk
                                break
                        break

                    # print (resp_body)

                except ValueError:
                    # print ("015")
                    resp_headers += chunk
                    chunk = session.recv(BUFF_READ_SIZE)
                    # if chunk == 0:
                    #     raise socket.error("Remote side send FIN")
        else:
            resp_headers = ["No http headers were sent"]
            resp_body = chunk
            connection_close = True

        if connection_close:
            session.shutdown(socket.SHUT_RDWR)
            session.close()
            session = None

        if not resp_format:
            return HTTPResponse(headers=resp_headers, payload=b"", sock=session, doassert=doassert, doaction=doaction)
        elif "body" in resp_format:
            return HTTPResponse(headers=resp_headers, payload=resp_body, sock=session, doassert=doassert, doaction=doaction)
        elif "all" in resp_format:
            return HTTPResponse(headers=resp_headers, payload=resp_body, sock=session, doassert=doassert, doaction=doaction)
        elif "headers" in resp_format:
            return HTTPResponse(headers=resp_headers, payload=b"", sock=session, doassert=doassert, doaction=doaction)
        elif "status" in resp_format:
            return HTTPResponse(headers=resp_headers, payload=b"", sock=session, doassert=doassert, doaction=doaction)
        else:
            return HTTPResponse(headers=resp_headers, payload=b"", sock=session, doassert=doassert, doaction=doaction)

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


def _generateSampleAlphaChars(length):
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


def _generateSampleAlphaNumMetaChar(length):
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


def _generateMultipartBoundary(length):
    """
    Generate random boundary for multipart messages
    """

    pop_us = "1234567890ABCDEFGHIJKLMNOPQURSTUVWXYZabcdefghijklmnopqrstuvwxyz01234567890"
    if length > len(pop_us):
        pop = pop_us * (2 * int((length / len(pop_us))))
    else:
        pop = pop_us
    return "".join(sample(pop, length))


def _generateChunkBody(chunk_size, payload):
    pass


def parseCookie(responseHeaders):
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


def _isChunked(responseHeaders):

    transferencoding = False
    try:
        for header, value in responseHeaders:
            if header == "Transfer-Encoding" and value.lower() == "chunked":
                transferencoding = True
                break
            else:
                continue
    except ValueError:
        for cheader in responseHeaders:
            if cheader.lower().startswith("transfer-encoding"):
                header, value = cheader.split(":")
                if value.lower() == "chunked":
                    transferencoding is True
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


def generateMultipartPayload(data):
    """
    Generate multipart body message

    """

    multipartdata = []
    boundary = _generateMultipartBoundary(70)

    if "files" in data:
        multipartdata.extend(_generateMultipartFile(data["files"], boundary))
        del data["files"]

    for name, value in data.items():
            multipartdata.append("--%s" % boundary)
            multipartdata.append("Content-Disposition: form-data; name=\"%s\"" % name)
            multipartdata.append("")
            multipartdata.append(value)
    multipartdata.append("--%s--" % boundary)

    return (DEFAULT_HTTP_DELIMETER.join(multipartdata), boundary)


def _generateMultipartFile(files, boundary):
    """
        Generate multipart part of file upload
    """

    multipartdata = []
    for name, filedata in files.items():
        if filedata.setdefault("filename", "").startswith("@"):
            fp = open(filedata["filename"][1:], "r")
            content = fp.read()
            fp.close

            multipartdata.append("--%s" % boundary)
            multipartdata.append("Content-Disposition: form-data; name=\"{name}\"; filename=\"{filename}\"".format(name=quote_plus(name), filename=quote_plus(filedata["filename"][1:])))
            multipartdata.append("Content-Type: {}".format(filedata.get("mimetype", "text/plain")))
            multipartdata.append("")
            multipartdata.append(content)
        else:
            multipartdata.append("--%s" % boundary)
            multipartdata.append("Content-Disposition: form-data; name=\"{name}\"; filename=\"{filename}\"".format(name=quote_plus(name), filename=quote_plus(filedata["filename"])))
            multipartdata.append("Content-Type: {}".format(filedata.get("mimetype", "text/plain")))
            multipartdata.append("")
            multipartdata.append(filedata.get("filecontent", ""))

    return multipartdata
