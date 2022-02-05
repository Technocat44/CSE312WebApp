# reference https://docs.python.org/3/library/socketserver.html?highlight=requesthandlerclass

import socketserver
import sys
import parse
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
        print(parse.strParser("hello"))
        # self.request is the TCP socket connected to the client
        received_data = self.request.recv(1024).strip()
      #  print(self.client_address[0] + " is sending data: " )
        # print(received_data.decode('utf-8'))
      #  print("The type of received data: ",type(received_data))
        rcvd_data_string = received_data.decode('utf-8')
      #  print("The type of the decode data: ",type(rcvd_data_string))
        # received data is a string of bytes, we decode to turn it into a string
      #  print(rcvd_data_string)
        #print("The length of the data is :" , strParser(rcvd_data_string))
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
        sys.stdout.flush()
        # just send back the same data, but upper-cased
        #print("\n\n")
        self.request.sendall("HTTP/1.1 200 OK\r\nContent-Length: 5\r\n\r\nWhat's up world!!".encode())

if __name__ == "__main__":
    HOST, PORT = "localhost", 8080

    server = socketserver.ThreadingTCPServer((HOST, PORT),MyTCPHandler)
    server.serve_forever()
    # interrupt the program with Ctrl-C