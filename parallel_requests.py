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

]


if __name__ == '__main__':

    session_parameters = [ 
    # {
    #     "num_of_pools":1,
    #     "num_of_clients" : 1,
    #     "host" : ("10.10.10.53",80),
    #     "secure" : False,
    #     "delay" : 1,
    #     "repeat" : 900,
    #     "flow" : flow,
    #     "session_headers" : {"Host":"test.me.localy"},
    #     "prefix_url": "",
    #     "session_http_version" : "HTTP/1.1",
    #     "resp_format" : "status",
    #     "debug" : False,
    #     "xff": True,

    # },
    # {
    #     "num_of_pools":1,
    #     "num_of_clients" : 1,
    #     "host" : ("10.10.10.54",80),
    #     "secure" : False,
    #     "delay" : 1,
    #     "repeat" : 900,
    #     "flow" : flow,
    #     "session_headers" : {"Host":"test54.me.localy"},
    #     "prefix_url": "",
    #     "session_http_version" : "HTTP/1.1",
    #     "resp_format" : "status",
    #     "debug" : False,
    #     "xff": True,

    # },
    {
        "num_of_pools":1,
        "num_of_clients" : 2,
        "host" : ("172.29.70.53",81),
        "secure" : False,
        "delay" : 1,
        "repeat" : 900,
        "flow" : flow,
        "session_headers" : {"Host":"test53.me.localy"},
        "prefix_url": "",
        "session_http_version" : "HTTP/1.1",
        "resp_format" : "all",
        "debug" : True,
        "xff": True,

    },
    ]


    traffic = pyhttputilsv2.HTTPClientsTraffic(session_parameters)
    traffic.run()

