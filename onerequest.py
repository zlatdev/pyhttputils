from pyhttputilsv2 import HTTPRequestv2

import pyhttputilsv2


req = {

    "method":"get",
    "url":"/",
    "headers":{
        "Host":"test25.me",
        "Referer":"http://catch.me",
        # "Content-Type":"text/xml",
        "Origin":"catch.me",
        "Cookies": "a=b",
    },

    # "payload":{
    #     "param":"test"
    # },
    # "payload":"""<?xml version="1.0" encoding="UTF-8" ?>
    # # <root>
    # #     <name1>test</name>
    # #     <group1>group</group>
    # # </root>
    # """,
    "enctype":0,
    "resp_format":"all",
    # "chunk_size":100,



}


# req = { 
# "method":"POST",
# "url": "/xml_endpoint.php",
# "headers" : {
# "User-Agent": "Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko)",
# "Host": "ptaf-kickstart-cl9.rd.ptsecurity.ru",
# "Content-Type": "text/xml",

#     },
#  "payload" : """<?xml version="1.0"?>
# <root>
# <auth>
# <user>test1</user>
# <group>WAF_super_admins</group>
# </auth>
# </root>
# """,
# "enctype":2,

# }

call = pyhttputilsv2.HTTPRequestv2(**req)

print (call.generateRawRequest())

resp = call.getResponse(host=("10.0.210.35",80))

print (resp.status)
print (resp.headers)
print (resp.payload)

# for i in range (1,100):
#     if resp.sock:
#         resp = call.getResponse(sock = resp.sock)
#     else:
#         print ("connection dropped")
#         break
#     # resp = call.getResponse(host=("10.0.210.35",8080))
#     # resp = call.getResponse(host=("10.0.209.148",8080))
#     # resp = call.getResponse(host=("10.0.210.45",80))
#     # resp = call.getResponse(host=("172.29.70.52",443),use_ssl=True)
#     # resp = call.getResponse(host=("10.10.10.52",443),use_ssl=True)
#     # resp = call.getResponse(host=("10.10.10.10",80))

#     # resp = call.getResponse(host=("10.0.208.183",80))
#     #
#     # print (resp.status)
#     print (resp.status)
#     print (resp.headers)
#     print (resp.payload)

#     pyhttputilsv2.time.sleep(10)





