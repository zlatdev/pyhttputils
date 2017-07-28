from .utils import *


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