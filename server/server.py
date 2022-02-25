# reference https://docs.python.org/3/library/socketserver.html?highlight=requesthandlerclass

import socketserver
import sys
import headerParser
import osHandlers
import buildResponse
import usersResponse 
# I am testing out WSL and git
# test.sayHello()
gh = osHandlers.addForwardSlash("\http\gggg\www\.com")
print(gh)
"""
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

        # TODO: change the received data to not strip
        # then I will have to rework the header parsers
        received_data = self.request.recv(1024)
        print(self.client_address[0] + " is sending data: " )
        clients.append(self.client_address[0])

        # received data is a string of bytes, we decode to turn it into a string    
    #    print("The type of received data: ",type(received_data))
        decoded_received_string = received_data.decode('utf-8')
    #    print("decoded received string: ", decoded_received_string)
        bodySplit = decoded_received_string.split('\r\n\r\n')
        bodyFromRequest = bodySplit[-1]
        print("This is the bodyFrom the request: ", bodyFromRequest)
        raw_byte_data_list = decoded_received_string.split('\r\n')
   #     print("RAWWWWWWWWWWW: ", raw_byte_data_list)
        request_line_string = raw_byte_data_list[0]
       
   #     print(f"RRRRRRRRRRRRRRRRRRRRRRRRRRR\n This is the request line before splitting: {request_line_string}" )
    
        request_line_list = request_line_string.split(" ")
   #     print(f"RRRRRRRRRRRRRRRRRRRRRRRRRRR\n This is the request line after splitting: {request_line_list}" )
       # <Request_Method> <Path> <HTTP_version>
        request_method = request_line_list[0]
        
        request_path = request_line_list[1]
      #  request_version = request_line_list[2]
   #         print("REQUEST PATHHHHHHHH", request_path)
    #    print(repr(f"FFFFFFFFFFFFFFFFFFFFF This is the byte string raw  {received_data}"))
        print('\n\n')
        #print(repr(f"YYYYYYYYYYYYYYYYYYYYY This is the decoded string raw {decoded_received_string}"))
        print('\r\n')
     #   print(f"GGGGGGGGGGGGGGGGGGGGGGGG This is the decoded string split on rnrn :", raw_data_for_headers)
        headerDict = headerParser.buildHeaderDict(raw_byte_data_list)
        print("******************************** This is headerDict", headerDict)
        body = headerDict['Body']
        print("the value of body from the headerDict" ,body)
        start = 0
        print("FROM the request/client\n")
        for s in raw_byte_data_list:
            
            print(f"This is line {start}: ", s)
            start+=1
        print(f"Request path: {request_path}, Request method: {request_method}")
        if (request_method == "GET" and request_path == "/"):
            print("Hey I am here in the index/html response")
            respond = buildResponse.buildIndexHTMLResponse()
            print("'HTML response, ", respond)
            self.request.sendall(respond)

        if (request_method == "GET" and request_path == "/style.css"):
            respond = buildResponse.buildCSSResponse()
            self.request.sendall(respond)  

        if (request_method == "GET" and request_path == "/functions.js"):
            respond = buildResponse.buildFunctionJSResponse()
            print("TJIS IS THE CONTENT AFTER I ENCODE IT: ", respond)
            print("\n")
            print("THIS IS THE LENGTH OF THE FILE AFTER ENCODEING IT :" , len(respond))
            self.request.sendall(respond)

        if (request_method == "GET" and request_path.startswith("/image")):
            extension = request_path.split("/")
            # I am getting the file type so I know how to set the mimetype
            response = buildResponse.buildImageResponse(extension)
            self.request.sendall(response)

        if (request_method == "GET" and request_path == "/hello"):
            respond = buildResponse.build200Response()
            print("Hello response: ", respond)
            self.request.sendall(respond)
            
        if (request_method == "GET" and request_path == "/hi"):
            respond = buildResponse.build301Response()
            self.request.sendall(respond)

        ###########################################################
        #
        # POST request for DB
        # A Post request will contain the content length, content type and the body which contains what the user wants to post
        #
        ###########################################################
        # The body of the request will be a JSON object with email and username fields
        if (request_method == "DELETE" and "/users/" in request_path):
            user = request_path.split("/")
            userId = user[-1]
            r = usersResponse.buildDeleteResponse(int(userId))
            self.request.sendall(r)

        if (request_method == "PUT" and "/users/" in request_path):
            # use userCollection.update({"id":idNumber}, {"$set": {"email":"<whatever is in the body>", "username":"<whatever is in the body>"}})
            # can update any field except the id!
            print("hey I am following the put request")
            user = request_path.split("/")
            userId = user[-1]
            r = usersResponse.buildUpdateResponse(int(userId), bodyFromRequest)
            print("this is the response, ", r)
            self.request.sendall(r)

        if (request_method == "GET" and "/users/" in request_path):
            # have to split up the path
            user = request_path.split("/")
            userId = user[-1]
            print(f"This is the user id: {userId}, and this is the type of userId {type(userId)}")
            r = usersResponse.buildSingleUserResponse(int(userId))
            self.request.sendall(r)

        if (request_method == "GET" and request_path == "/users"):
            r = usersResponse.buildAllUsersResponse()
            print(f"this is the response for a GET request to /users which sends back all the users {r}")
            self.request.sendall(r)

        if (request_method == "POST" and request_path == "/users"):
            contentLength = headerDict["Content-Length"]
            contentType = headerDict["Content-Type"] # TODO:  I dont know if I need the content type from a request or not 
            body = headerDict["Body"]
            print("THIS IS FOR A POST REQUEST FOR /users. contentLength: ", contentLength, " contentType : ", contentType ," body :" ,bodyFromRequest, "\n")
            r = usersResponse.buildCreateResponse(contentLength, bodyFromRequest)
            self.request.sendall(r)

        else:                                           
            respond = buildResponse.build404Response("Page Does Not Exist")
            self.request.sendall(respond)
            
        
       
        # r = decoded_received_string.split('\r\n\r\n')
        # start = 0
        # for s in r:
        #     print(f"this is line {start} of split on \\r\\n\\r\\n:\n", s)
        #     start+=1
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
        sys.stderr.flush()
        sys.stdout.flush() # a way to see the output in the terminal even if its buffering

        print("\n\n")
        #self.request.sendall("HTTP/1.1 200 OK\r\nContent-Length: 5\r\n\r\nWhat's up world!!".encode())


if __name__ == "__main__":
    HOST, PORT = "0.0.0.0", 8080

    server = socketserver.ThreadingTCPServer((HOST, PORT),MyTCPHandler)
    server.serve_forever()
    
    # interrupt the program with Ctrl-C

