# reference https://docs.python.org/3/library/socketserver.html?highlight=requesthandlerclass

import socketserver
import sys
import test
import os
import parse
import osHandlers
import buildResponse
# I am testing out WSL and git
test.sayHello()
gh = osHandlers.addForwardSlash("\http\gggg\www\.com")
print(gh)
"""
HTTP Request:
The head of request will consist of three parts:
    1. A request line 
        <Request_Method> <Path> <HTTP_version>
    2. Header fields (in key-value pairs)
        <Header_name> <Header_value>
    3. Body of request (optional)
        -see POST body

    Example :

    GET / HTTP/1.1                  POST /path HTTP/1.1
    Host: cse312.com                Host: cse312.com
                                    Content-Length: 48

                                    {"data": "Some data in the body of the request"}


    Starting at the request line, this is where we talk about formatting
    and string parsing. With my TCP socket setup, and a broswer sends me
    a request, I will get a request following the above format and I have
    to do some string parsing to get the information I need out of it.

    For request-line, good practice is to read the line and do .split() on whitespace
    
    For the header fields there can be unlimited amout of key value pairs 
    separated by a colon and a space. At a minimum there will be a Content-Length
    
    The body is optional and is separated by \r\n\r\n

    The way this all works is you receive a request and then you process
    it and run some code inbetween in and do some cool stuff whatever the
    app does and then you send back a HTTP response. This all depends on
    the path they request too. 

HTTP Response:
    1. Response line
        <HTTP_version> <Response_Code> <Response_text>
    2. Specify the content length and the content type in headers
    3. Response itself goes in the body

    Example:

    HTTP/1.1 200 OK
    Content-Type: text/html
    Content-Length: 152

    <html>....</html>
"""
# collect all the headers into dictionary for easy access


clients = []


class MyTCPHandler(socketserver.BaseRequestHandler):
    """
    The request handler class for our server.

    It is instantiated once per connection to the server, and must
    override the handle() method to implement communication to the
    client.

    This function must do all the work required to service a request. 
    The default implementation does nothing. Several instance attributes
    are available to it; the request is available as self.request; 
    the client address as self.client_address; and the server instance 
    as self.server, in case it needs access to per-server information.

    The type of self.request is different for datagram or stream 
    services. For stream services, self.request is a socket object; 
    for datagram services, self.request is a pair of string and socket.
    """
    
    
    def handle(self):
        print("[SERVER INITIALZING]")
        # self.request is the TCP socket connected to the client
        received_data = self.request.recv(1024).strip()
        print(self.client_address[0] + " is sending data: " )
        clients.append(self.client_address[0])

              
        #print("The type of received data: ",type(received_data))
        decoded_received_string = received_data.decode('utf-8')
        #print("The type of the decode data: ",type(rcvd_data_string))
        # received data is a string of bytes, we decode to turn it into a string
        
        raw_byte_data_list = decoded_received_string.split('\r\n')
        request_line_string = raw_byte_data_list[0]
      
      #  print(f"RRRRRRRRRRRRRRRRRRRRRRRRRRR\n This is the request line before splitting: {request_line_string}" )
    
        request_line_list = request_line_string.split(" ")
      #  print(f"RRRRRRRRRRRRRRRRRRRRRRRRRRR\n This is the request line after splitting: {request_line_list}" )
       # <Request_Method> <Path> <HTTP_version>#  ffff
        request_method = request_line_list[0]
        request_path = request_line_list[1]
        request_version = request_line_list[2]
        print("REQUEST PATHHHHHHHH", request_path)
        # print(repr(f"FFFFFFFFFFFFFFFFFFFFF This is the byte string raw  {received_data}"))
        print('\n\n')
        # print(repr(f"YYYYYYYYYYYYYYYYYYYYY This is the decoded string raw {decoded_received_string}"))
        print('\r\n')
     #   print(f"GGGGGGGGGGGGGGGGGGGGGGGG This is the decoded string split on rnrn :", raw_data_for_headers)
        headerDict = parse.buildHeaderDict(raw_byte_data_list)
        # print("******************************** This is headerDict", headerDict)
        # useragent = headerDict['User-Agent']
        # print("the value of useragent from the headerDict" , useragent)
        start = 0
        print("FROM the request/client\n")
        for s in raw_byte_data_list:
            
            print(f"This is line {start}: ", s)
            start+=1

        if (request_method == "GET" and request_path == "/"):
            respond = buildResponse.buildNonASCIIResponse("text/html; charset=utf-8", "index.html")
            self.request.sendall(respond)
        if (request_method == "GET" and request_path == "/style.css"):
            respond = buildResponse.buildHTMLResponse("text/css; charset=utf-8 ", "style.css" )
            self.request.sendall(respond.encode())  
        if (request_method == "GET" and request_path == "/functions.js"):
            respond = buildResponse.buildNonASCIIResponse("application/javascript; charset=utf-8", "functions.js")
            self.request.sendall(respond)
        if (request_method == "GET" and request_path.startswith("/image")):
            extension = request_path.split("/")
            fullNameOfFile = extension[-1].split(".")
            nameOfFile = fullNameOfFile[0]
            filetype = fullNameOfFile[1]
            # if filetype == "jpg":
            #     filetype = "jpeg"
            # I am getting the file type so I know how to set the mimetype
            response = buildResponse.buildNonASCIIResponse(f"image/{filetype}", "image/"+extension[-1])
            self.request.sendall(response)
        if (request_method == "GET" and request_path == "/hello") :
            respond = buildResponse.build200Response("text/plain; charset=utf-8", "Hello there")
            self.request.sendall(respond.encode())
        if (request_method == "GET" and request_path == "/hi"):
            respond = buildResponse.build301Response("/hello")
            self.request.sendall(respond.encode())
        else: 
            respond = buildResponse.build404Response("text/plain; charset=utf-8", "Page Does Not Exist")
            self.request.sendall(respond.encode())
            
        
       
        # r = decoded_received_string.split('\r\n\r\n')
        # start = 0
        # for s in r:
        #     print(f"this is line {start} of split on \\r\\n\\r\\n:\n", s)
        #     start+=1
        # print("The length of the data via string parser :" , parse.strParser(decoded_received_string))
        """
        Content-Length is the number of bytes not number of characters
        to get the content length correct of a utf-8 STRING, 
            - convert to bytes first by decoding
            - get the length of the byte array with len()
        to get the content length of an image: 
        An image is already in bytes, it is not ENCODED IN UTF-8
            - read the bytes from the file
            - send the bytes as is
            - Content-Length is the size of the file
            - set the Content-Type to image/<image_type>
        """
        sys.stdout.flush() # a way to see the output in the terminal even if its buffering

        # just send back the same data, but upper-cased
        print("\n\n")
        #self.request.sendall("HTTP/1.1 200 OK\r\nContent-Length: 5\r\n\r\nWhat's up world!!".encode())


if __name__ == "__main__":
    HOST, PORT = "0.0.0.0", 8080

    server = socketserver.ThreadingTCPServer((HOST, PORT),MyTCPHandler)
    server.serve_forever()
    
    # interrupt the program with Ctrl-C

