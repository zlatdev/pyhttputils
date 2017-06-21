import pyhttputilsv2

flow = [
{
    
    "method":"get",
    "url":"/check/test.url",
    "headers":{
        "Host":"test.as.localy.me",
        "Referer":"http://catch.me",
        # "Content-Type":"text/xml",
        "User-Agent":"Yandex Browser 16",
        "Origin":"catch.me",
        "Cookies": "a=b",
        "Connection": "keep-alive",     
    }

},
{    
    "method":"POST",
    "url":"/check/test1.url",
    "headers":{
        "Host":"test.as.localy.me",
        "Referer":"http://catch.me",
        # "Content-Type":"text/xml",
        "User-Agent":"Yandex Browser 16",
        "Origin":"catch.me",
        "Cookies": "a=b",
        "Connection": "keep-alive",     
    },
    "payload":{
        "param":"url=*)(objectClass=users))(&(objectClass=foo",
        "param1":"<script>",
    },
},

{    
    "method":"get",
    "url":"/check/test2.url",
    "headers":{
        "Host":"test.as.localy.me",
        "Referer":"http://catch.me",
        # "Content-Type":"text/xml",
        "User-Agent":"Yandex Browser 16",
        "Origin":"catch.me",
        "Cookies": "a=b",
        "Connection": "keep-alive",     
    },
    "payload":{
        "param":"url=*)(objectClass=users))(&(objectClass=foo",
        "param1":"<script>",
    },
},

{
        "method":"get",
        "url":"/correlate.me",
        "payload":{
            "test":"' or 1=1#",
        },
    },
    {
        "method":"get",
        "url":"/correlate.me",
        "payload":{
            "test":"' union select 1,2,3,4,5#",
        },
    },
    {
        "method":"get",
        "url":"/correlate.me",
        "payload":{
            "test":"' union select 1,2,3,4,5,6,7#",
        },
    },
    {
        "method":"get",
        "url":"/correlate.me",
        "payload":{
            "test":"' union select 1,version(),3,4,5,6,7#",
        },
    },

    {
        "method":"get",
        "url":"/correlate.me",
        "payload":{
            "test":"' union select 1,login,password,4,5,6,7 from users#",
        },
    },

    {
        "method":"get",
        "url":"/login.php",
        "payload":{
            "test":"asdasdasd",
        },
    },
    {
        "method":"get",
        "url":"/login.php",
        "payload":{
            "test":"asdf",
        },
    },

    
    {
        "method":"get",
        "url":"/login.php",
        "payload":{
            "test":"asdasdas",


        },
    },

    {
        "method":"post",
        "url":"/post_message.php",
        "payload":{
            "post":"<script>alert();<script>",


        },
    },
    {
        "method":"post",
        "url":"/post_message.php",
        "payload":{
            "post":"<script>document.getElementByID(\"qwe\")<script>",


        },
    },
    {

        "method":"post",
        "url":"/post_message.php",        
        "payload": {
            "post":"""<script>alert()</script>""",
            "xxe":"""<!DOCTYPE input [
 <!ENTITY xxe SYSTEM "file:///C:/boot.ini" >
]>
<input></input>
]""",
        }
    },  
]



if __name__ == '__main__':

    session_parameters = [ 
    {
        "num_of_pools":2,
        "num_of_clients" : 2,
        "host" : ("10.0.209.148",80),
        "secure" : False,
        "delay" : .2,
        "repeat" : 243600,
        "flow" : flow,
        "session_headers" : {"Host":"test.me"},
        "prefix_url": "",
        "session_http_version" : "HTTP/1.1",
        "resp_format" : "status",
        "debug" : False,
        "xff": True,
        "v": 3,

    },
    {
        "num_of_pools":2,
        "num_of_clients" : 2,
        "host" : ("10.0.209.148",80),
        "secure" : False,
        "delay" : .1,
        "repeat" : 243600,
        "flow" : flow,
        "session_headers" : {"Host":"test20.me"},
        "prefix_url": "",
        "session_http_version" : "HTTP/1.1",
        "resp_format" : "status",
        "debug" : False,
        "xff": True,
        "v": 3,

    },
    # {
    #     "num_of_pools":1,
    #     "num_of_clients" : 2,
    #     "host" : ("cluster120.test.me",80),
    #     "secure" : False,
    #     "delay" : .1,
    #     "repeat" : 243600,
    #     "flow" : flow,
    #     "session_headers" : {"Host":"cluster120.test.me"},
    #     "prefix_url": "",
    #     "session_http_version" : "HTTP/1.1",
    #     "resp_format" : "status",
    #     "debug" : False,
    #     "xff": True,

    # },
    # {
    #     "num_of_pools":1,
    #     "num_of_clients" : 2,
    #     "host" : ("cluster121.test.me",80),
    #     "secure" : False,
    #     "delay" : 1,
    #     "repeat" : 360000,
    #     "flow" : flow,
    #     "session_headers" : {"Host":"cluster121.test.me"},
    #     "prefix_url": "",
    #     "session_http_version" : "HTTP/1.1",
    #     "resp_format" : "status",
    #     "debug" : False,
    #     "xff": True,

    # },
    # #     {
    #     "num_of_pools":1,
    #     "num_of_clients" : 2,
    #     "host" : ("172.29.70.55",8055),
    #     "secure" : False,
    #     "delay" : 1,
    #     "repeat" : 3600,
    #     "flow" : flow,
    #     "session_headers" : {"Host":"cl-test55.me.localy"},
    #     "prefix_url": "",
    #     "session_http_version" : "HTTP/1.1",
    #     "resp_format" : "status",
    #     "debug" : False,
    #     "xff": True,

    # },
    #     {
    #     "num_of_pools":1,
    #     "num_of_clients" : 2,
    #     "host" : ("172.29.70.56",8056),
    #     "secure" : False,
    #     "delay" : 1,
    #     "repeat" : 3600,
    #     "flow" : flow,
    #     "session_headers" : {"Host":"cl-test56.me.localy"},
    #     "prefix_url": "",
    #     "session_http_version" : "HTTP/1.1",
    #     "resp_format" : "status",
    #     "debug" : False,
    #     "xff": True,

    # },
    #     {
    #     "num_of_pools":3,
    #     "num_of_clients" : 3,
    #     "host" : ("10.0.208.55",80),
    #     "secure" : False,
    #     "delay" : 1,
    #     "repeat" : 3600,
    #     "flow" : flow,
    #     "session_headers" : {"Host":"ptaf-kickstart-cl41.rd.ptsecurity.ru"},
    #     "prefix_url": "",
    #     "session_http_version" : "HTTP/1.1",
    #     "resp_format" : "none",
    #     "debug" : False,
    #     "xff": True,

    # },
        #     {
    #     "num_of_pools":3,
    #     "num_of_clients" : 3,
    #     "host" : ("10.0.208.55",80),
    #     "secure" : False,
    #     "delay" : 1,
    #     "repeat" : 3600,
    #     "flow" : flow,
    #     "session_headers" : {"Host":"ptaf-kickstart-cl41.rd.ptsecurity.ru"},
    #     "prefix_url": "",
    #     "session_http_version" : "HTTP/1.1",
    #     "resp_format" : "none",
    #     "debug" : False,
    #     "xff": True,

    # },

    ]


    traffic = pyhttputilsv2.HTTPClientsTraffic(session_parameters)
    traffic.run()

