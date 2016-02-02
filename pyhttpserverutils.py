import socket
import threading
import ssl
import time


BUF_SIZE = 1024

class ProcessRequest(threading.Thread) :


    def __init__(self, sock=None, claddr = None ):
        threading.Thread.__init__(self)
        if not sock:
            raise socket.erro

        self.sock = sock
        self.claddr = claddr



    def run(self):
        print ("Request recieved!", threading.current_thread().name)
        req = bytearray()
        data = bytearray()
        use_length = False
        use_chunk = False
        use_CRLF = False

        # print (1)
        while True:
            # print (2)


            data=sock.recv(BUF_SIZE)
           
            # print (data)

            if not req and b"\r\n" in data:
                try:
                    req_line = data.split(b"\r\n",1)
                    # print (req_line)
                    (method, url, version, *others) = req_line[0].split(b"\x20")
                    # print (method, url, version, others)
                    if not url.strip():
                        print ("no url")
                        req = data
                        use_CRLF = False
                        break
                    elif b"HTTP/" not in version.strip():

                        print ("no or bad version")
                        req = data
                        use_CRLF = False
                        break
                    else:
                        req += data   
                except ValueError:
                    print ("Some Errors in Request Line!")
                    req = data
                    use_CRLF = False
                    break
            else:
                 req += data




            if b"Content-Length" in req:
                # print (3)
                use_length = True
            # else:
            #     print ("no")
            
            if b"Transfer-Encoding" in req:
                # print (4)
                use_chunk = True

            # else:
            #     print ("no")
            


            if b"\r\n\r\n" in req or b"\n\n" in req:
                # print (5)
                use_CRLF = True
                # print (data)
                # print (req)
                break
            
        if not use_CRLF:
            print (req)
            req = b"<html><head></head><body>"+req + b"\r\nCCN_SSN: 078-05-1120 4929883237589543\r\nRespAttackSig: index of / .., Error Message: System.Data.OleDb.OleDbException\r\n</body></html>"
            req_len = len(req)
           
            resp = "HTTP/1.1 200 OK\r\n"
            resp += "Content-Length: %d\r\n" % req_len
            resp += "Content-Type: text/plain\r\n"
            resp += "Connection: close\r\n"
            resp += "\r\n"
            resp = resp.encode() + req 
        else:
            req_h, req_b = req.split(b"\r\n\r\n",1) 
            print (req_h)
            if use_length:
                # print (6)
                content_length = []
                req_headers = req_h.split(b"\r\n")
                for c_header in req_headers:
                    if b"Content-Length" in c_header:
                        content_length.append(int(c_header[c_header.index(b":")+1:].strip()))
                        # break
                
                if len(content_length) > 1 :
                    cl = min(content_length)
                else :
                    cl = content_length[0]


                # print (cl)
                len_b = len (req_b)
                while len_b < cl:
               
                    data = sock.recv(BUF_SIZE)
                    req_b += data
                    len_b = len (req_b)
                
            elif use_chunk:
                req_headers = req_h.split(b"\r\n")
                for c_header in req_headers:
                    if b"Transfer-Encoding" in c_header:
                        if not b"chunked" in c_header:
                            req_b = "not chunked request"
                            get_payload = False
                        else:
                            get_payload = True


                if get_payload:
                    # print (req_b)
                    while True:
                        if b"0\r\n\r\n" in req_b[-11:] or b"\r\n\r\n" in req_b[-11:] or b"\n\n" in req[-11:]:
                            break

                        data = sock.recv(BUF_SIZE)
                        req_b += data
                        
                        # if req_b.endswith(b"0\r\n\r\n")  or req_b.endswith(b"\r\n\r\n"):                            
                        #     break                            
                        # data = sock.recv(BUF_SIZE)
                        # req_b += data
                        # print (req_b)
            else:
                pass
            # print (req_h, req_b)
            # print ("headers",req_h)
            # print ("Payload",req_b)

            req = req_h+req_b
            req = b"<html><head></head><body>"+req + b"\r\nCCN_SSN: 078-05-1120 4929883237589543\r\nRespAttackSig: index of / .., Error Message: System.Data.OleDb.OleDbException\r\n</body></html>"
            # print (req)

            req_len = len(req)
            
            resp = "HTTP/1.1 200 Connection Established\r\n"
            # resp += "Content-Length: %d\r\n" % req_len
            # resp += "Content-Type: text/plain\r\n"
            # resp += "Connection: close\r\n"
            resp += "\r\n"
            resp = resp.encode()# + req + b"invlid"            
        sock.send(resp)

        sock.close()

        print ("Response send in thread", threading.current_thread().name)
        # return






if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description="Run simple HTTP server")
    parser.add_argument("host",type=str, help="ip address of server")
    parser.add_argument("port",type=str, help="port of server")
    parser.add_argument("secure",type=int,help="run using ssl")
    
    cli_params = vars(parser.parse_args())

    Clients = []

    try:
        
        if cli_params["secure"]:
            context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
            context.load_cert_chain(certfile="certs/server.crt", keyfile="certs/server.key")
        
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            
        server.bind ((str(cli_params["host"]),int(cli_params["port"])))

        server.listen(5)
        print ("Server is running!")

        while True:

            if cli_params["secure"]:
                sock, addr = server.accept()
                cl_sock = context.wrap_socket(sock, server_side=True)
            else:
                sock, addr = server.accept()
                cl_sock = sock
            
            cl = ProcessRequest(cl_sock,addr)      
            
            cl.start()
            
            Clients.append(cl)
            print ("before checks",len(Clients), Clients)               
            for c in Clients:
                c.join (1)
                if not c.is_alive():
                    # print ("Remove dead thread",c)
                    del Clients[Clients.index(c)]
            print ("after checks", len(Clients), Clients)



            

    except socket.error as e:
        print ("Some error!",e.errno, e.strerror)
        time.sleep (60)




    