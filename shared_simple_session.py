import pyhttputil
import time

session = [
    {
        "url": "/index.php",
        "repeat": 10,
        "doassert": {
            "status": "200",
        }
    },
    {
        "method": "get",
        "url": "/get_all_users.php",
        "params": {
            "uid": "' or 1=1#",
        },
        "cookies": {
            "c": "c",
            "a": "a"
        },
        "doassert": {
            "status": "403",
        }

    },
    {
        "method": "get",
        "url": "/get_all_users.php",
        "params": {
            "uid": "' union select 1,2,3,4,5#",
        },
        "doassert": {
            "status": "403",
        }
    },
    {
        "url": "/index.php",
        "repeat": 10,
        "doassert": {
            "status": "200",
        }
    },
    {
        "method": "get",
        "url": "/get_all_users.php",
        "params": {
            "uid": "' union select 1,2,3,4,5,6,7#",
        },
        "doassert": {
            "status": "403",
        }
    },
    {
        "method": "get",
        "url": "/get_all_users.php",
        "params": {
            "uid": "' union select 1,version(),3,4,5,6,7#",
        },
        "doassert": {
            "status": "403",
        }
    },
    {
        "url": "/index.php",
        "repeat": 10,
        "doassert": {
            "status": "200",
        }
    },
    {
        "method": "get",
        "url": "/get_all_users.php",
        "params": {
            "uid": "' union select 1,login,password,4,5,6,7 from users#",
        },
        "doassert": {
            "status": "403",
        }
    },

    {
        "method": "get",
        "url": "/index.php",
        "params": {
            "test": "asdasdasd",
        },
        "doassert": {
            "status": "200",
        }
    },
    {
        "url": "/index.php",
        "repeat": 10,
        "doassert": {
            "status": "200",
        }
    },

    {
        "method": "post",
        "url": "/post_message.php",
        "payload": {
            "post": "<script>alert();<script>",
        },
        "doassert": {
            "status": "403",
        }
    },
    {
        "method": "post",
        "url": "/post_message.php",
        "payload": {
            "post": "<script>document.getElementByID(\"qwe\")<script>",
        },
        "doassert": {
            "status": "403",
        }
    },

    {
        "url": "/index.php",
        "repeat": 10,
        "doassert": {
            "status": "200",
        }
    },

    {
        "method": "post",
        "url": "/post_message.php",
        "payload": {
            "post": """<!DOCTYPE test SYSTEM "test.dtd"><test></test>""",
        },
        "doassert": {
            "status": "403",
        }
    },
    {
        "method": "post",
        "url": "/index.php",
        "payload": {
            "files": {
                # "file": {
                #     "filename": "@/home/bykov/Projects/backend_bykov/www/shells/DAws.php",
                #     "mimetype": "application/octet-stream",
                #     "filecontent": """<div>asdfasd</div>""",
                # },
                "test1": {
                    "filename": "test1.txt",
                    "mimetype": "text/plain",
                    "filecontent": """<?= passthru($content);?>""",
                },
            },
            "uid": "' union select 1,login,password,4,5,6,7 from users#",
        },
        "enctype": 1,
        "doassert": {
            "status": "403",
        }
    },
    {
        "url": "/index.php",
        "repeat": 10,
        "doassert": {
            "status": "200",
        }
    },

]


tr_session = pyhttputil.HTTPSession(flow=session,
                                         session_cookies={"b": "b"},
                                         debug=True,
                                         resp_format="all")

sessions = [
    # {"host": ("10.0.209.148", 80)},
    # {"host": ("10.0.208.219", 80)}
    # {"host": ("10.0.211.74", 80)},
    # {"host": ("10.0.223.120", 80)},
    # {"host": ("10.0.223.122", 80)},
    # {"host": ("10.0.223.123", 80)}
    # {"host": ("172.29.70.51",80)},
    # {"host": ("172.29.70.52",80)}

    # {
    #     "host": ("10.2.208.120", 80),
    #     "session_headers": {
    #                             "Host": "clusteraa.tmsk.test",
    #                             "Connection": "keep-alive",
    #                             },
    #     "bind_source": ("172.29.70.249", 0)
    # },
    # {
    #     "host": ("10.2.208.120", 80),
    #     "session_headers": {
    #                             "Host": "clusteraa.tmsk.test",
    #                             "Connection": "keep-alive",
    #                             },
    #     "bind_source": ("172.29.70.253", 0)
    # },
    # {
    #     "host": ("10.2.208.120", 80),
    #     "session_headers": {
    #                             "Host": "clusteraa.tmsk.test",
    #                             "Connection": "keep-alive",
    #                             },
    #     "bind_source": ("172.29.71.253", 0)
    # },
    # {
    #     "host": ("172.29.70.12", 80),
    #     "session_headers": {
    #                             "Host": "clusteraa1.tomsk.test",
    #                             "Connection": "keep-alive",
    #                             },
    # },
    # {
    #     "host": ("10.2.208.108", 80),
    #     "session_headers": {
    #                             "Host": "clusteraa.tmsk.test",
    #                             "Connection": "keep-alive",
    #                             },
    #     "bind_source": ("172.29.70.249", 0)
    # },
    # {
    #     "host": ("172.29.70.11", 80),
    #     "session_headers": {
    #                             "Host": "clusteraa.tomsk.test",
    #                             "Connection": "keep-alive",
    #                             },
    #     "bind_source": ("172.29.70.253", 0)
    #
    # },
    # {
    #     "host": ("172.29.70.13", 80),
    #     "session_headers": {
    #                             "Host": "clusteras.tomsk.test",
    #                             "Connection": "keep-alive",
    #                             },
    #     "bind_source": ("172.29.70.249", 0)
    # },
    {
        "host": ("172.29.70.13", 80),
        "session_headers": {
                                "Host": "clusteras.tomsk.test",
                                "Connection": "keep-alive",
                                },
        "bind_source": ("172.29.70.253", 0)
    },
    # {
    #     "host": ("172.29.70.14", 80),
    #     "session_headers": {
    #                             "Host": "clusteraa1.tmsk.test",
    #                             "Connection": "keep-alive",
    #                             },
    #     "bind_source": ("172.29.70.249", 0)
    # },
    # {
    #     "host": ("172.29.70.14", 80),
    #     "session_headers": {
    #                             "Host": "clusteraa1.tmsk.test",
    #                             "Connection": "keep-alive",
    #                             },
    #     "bind_source": ("172.29.70.253", 0)
    # },
    # {
    #     "host": ("172.29.70.15", 80),
    #     "session_headers": {
    #                             "Host": "clusteraa2.tmsk.test",
    #                             "Connection": "keep-alive",
    #                             },
    #     "bind_source": ("172.29.70.249", 0)
    # },
    # {
    #     "host": ("172.29.70.15", 80),
    #     "session_headers": {
    #                             "Host": "clusteraa2.tmsk.test",
    #                             "Connection": "keep-alive",
    #                             },
    #     "bind_source": ("172.29.70.253", 0)
    # },
    # {
    #     "host": ("172.29.70.16", 80),
    #     "session_headers": {
    #                             "Host": "clusteraa2.tmsk.test",
    #                             "Connection": "keep-alive",
    #                             },
    #     "bind_source": ("172.29.70.249", 0)
    # },
    # {
    #     "host": ("172.29.70.16", 80),
    #     "session_headers": {
    #                             "Host": "clusteraa2.tmsk.test",
    #                             "Connection": "keep-alive",
    #                             },
    #     "bind_source": ("172.29.70.253", 0)
    # },
    # {
    #     "host": ("10.2.208.128", 80),
    #     "session_headers": {
    #                             "Host": "ha-aa-app1.test.me",
    #                             "Connection": "keep-alive",
    #                             },
    #     # "bind_source": ("172.29.70.253", 0)
    # },
    # {
    #     "host": ("10.2.208.128", 80),
    #     "session_headers": {
    #                             "Host": "ha-aa-app2.test.me",
    #                             "Connection": "keep-alive",
    #                             },
    #     # "bind_source": ("172.29.70.249", 0)
    # },
    # {
    #     "host": ("10.2.208.128", 80),
    #     "session_headers": {
    #                             "Host": "ha-aa-app3.test.me",
    #                             "Connection": "keep-alive",
    #                             },
    #     # "bind_source": ("172.29.70.253", 0)
    # },
    # {
    #     "host": ("10.2.208.128", 80),
    #     "session_headers": {
    #                             "Host": "ha-aa-app4.test.me",
    #                             "Connection": "keep-alive",
    #                             },
    #     # "bind_source": ("172.29.70.249", 0)
    # },
    # {
    #     "host": ("10.2.208.146", 80),
    #     "session_headers": {
    #                             "Host": "clusteraa2.tmsk.test",
    #                             "Connection": "keep-alive",
    #                             },
    #     "bind_source": ("172.29.70.249", 0)
    # },

]

st = time.time()

while time.time() - st < 0.0001:

    for sess in sessions:
        # print(0, sess)
        tr_session.runSession(**sess,
                            delay=0,
                            doassert=True)
