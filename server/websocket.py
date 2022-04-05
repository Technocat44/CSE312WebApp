from server.router import Route
from server.request import Request
import sys
import hashlib
import base64
import random

"""
--
Try doing docker-compose up [-d if you use it] --build --force-recreate to tell Docker that it must build 
the containers from scratch.

To remove anything saved to your DB, run docker volume prune to delete any unused volumes on your system 
(such as the volume for your DB). 
If you have Docker running containers for things other than this class on your system, see docker volume rm.
"""

def add_paths(router):
    router.add_route(Route('GET', '/websocket', handshake))


"""
Websocket parsing:
Read frames at bit level
Frames come in like this:
      0                   1                   2                   3
      0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1
     +-+-+-+-+-------+-+-------------+-------------------------------+
     |F|R|R|R| opcode|M| Payload len |    Extended payload length    |
     |I|S|S|S|  (4)  |A|     (7)     |             (16/64)           |
     |N|V|V|V|       |S|             |   (if payload len==126/127)   |
     | |1|2|3|       |K|             |                               |
     +-+-+-+-+-------+-+-------------+ - - - - - - - - - - - - - - - +
     |     Extended payload length continued, if payload len == 127  |
     + - - - - - - - - - - - - - - - +-------------------------------+
     |                               |Masking-key, if MASK set to 1  |
     +-------------------------------+-------------------------------+
     | Masking-key (continued)       |          Payload Data         |
     +-------------------------------- - - - - - - - - - - - - - - - +
     :                     Payload Data continued ...                :
     + - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - +
     |                     Payload Data continued ...                |
     +---------------------------------------------------------------+

We can access any byte and extract the bits we need
Helpful to recall that bytes are represented as 8-bit integer values in most languages (0-255)

Parsing bits:
    First byte / byte[0]
            Bit Example - To read the opcode:
                • get the byte at index 0
                • Bitwise AND (& in most languages) this byte with a "bit mask" of 15
                • Since 15 == 00001111 as a byte this will 0 out the 4 higher order bits
                • We now have an int from 0-15 representing the opcode
            FIN: The finish bit [bit 0 in frame]
                • 1 - This is the last frame for this message
                • 0 - There will be continuation frames containing more data for the same message
                • [You can assume this is always 1 for the HW]
            RSV: Reserved bits  [bits 1-3 in frame]
                • Used to specify any extensions being used
                • [You can assume these are always 000 for the HW]
            opcode: Operation code [bits 4-7 in frame]
                • Specifies the type of information contained in the payload
                • Ex: 0001 for text, 0010 for binary, 1000 to close the connection
                Most frames will have 0001. 
                When a user closes the tab, this will trigger the browser to send the 1000 to sever the connection
                *** Make sure to check what the op-code is and handle appropriatley 

    Second byte / byte[1]    
            MASK: Mask bit [bit 8 in frame]
                • Set to 1 if a mask is being used (the masking key exist) [this is how it will always be when we receive a frame]
                • Set to 0 if no mask is being used (the masking key does not exist) [when sending the response set the mask to 0]
                • This will be 1 when receiving messages from a client 
            The next bits will represent payload length in bytes [bits 9-15 in frame]
                • Similar to Content-Length
                • The length can be represented in 7, 16, or 64 bits
                                                    2^6, 2^5, 2^4, 2^3, 2^2, 2^1, 2^0
                                        (1111111) ==  64 + 32 + 16 + 8  + 4  + 2 +  1  == 127
                                        (1111110) ==  64 + 32 + 16 + 8  + 4  + 2 +  0  == 126
                                        (1111101) ==  64 + 32 + 16 + 8  + 4  + 2 +  0  == 125
            If the length is <126 bytes [125 or less] (1111101) ==  64 + 32 + 16 + 8  + 4  + 2 +  0  == 125       
                • The length is represented in 7 bits, sharing a byte with the MASK bit
                • The next bit after the length is either the mask or payload
                [[[
                         0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1
                        +-+-+-+-+-------+-+-------------+-------------------------------+
                        |F|R|R|R| opcode|M| Payload len |  Masking key bits start here  |
                        |I|S|S|S|  (4)  |A|     (7)     |           (16 bits)           |
                        |N|V|V|V|       |S|  (1111101)  | (if payload len==125/or less) |
                        | |1|2|3|       |K|   or less   |                               |
                        +-+-+-+-+-------+-+-------------+ - - - - - - - - - - - - - - - +
                        | Masking-key (continued)       |          Payload Data         |
                        +-------------------------------+-------------------------------+
                                                If the MASK bit == 1
                ]]]


            Else If the length is >=126 and <65536 bytes
                • The 7 bit length will be exactly 126 (1111110) ==  64 + 32 + 16 + 8  + 4  + 2 +  0  == 126
                • The next {{16 bits}} represents the payload length [bits 16-31 in the frame] 
                *** So we need to read the next two bytes and combine them into a single int to know how long
                    the payload length is
                [[[
                         0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1
                        +-+-+-+-+-------+-+-------------+-------------------------------+
                        |F|R|R|R| opcode|M| Payload len |    Extended payload length    |
                        |I|S|S|S|  (4)  |A|     (7)     |             (32bits)          |
                        |N|V|V|V|       |S|             |       (The next 4 bytes)      |
                        | |1|2|3|       |K|             |      (if payload len==126)    |
                        +-+-+-+-+-------+-+-------------+ - - - - - - - - - - - - - - - +
                        |                               |          (4 bytes)            |
                        |   Extended payload length     |   Masking key starts here     |
                        + - - - - - - - - - - - - - - - + - - - - - - - - - - - - - - - +
                        | Masking-key (continued)       |          Payload Data         |
                        +-------------------------------+-------------------------------+
                        :                     Payload Data continued ...                :
                        + - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - +
                        |                     Payload Data continued ...                |
                        +---------------------------------------------------------------+
                                                If the MASK bit == 1
                ]]]


             Else if the length is >=65536 bytes
                • The 7 bit length will be exactly 127 (1111111) ==  64 + 32 + 16 + 8  + 4  + 2 +  1  == 127
                • The next {{64 bits}} represents the payload length
                • 18,446,744,073,709,551,615 max length
                • 16 exabytes / 16,000,000 terabytes 
                *** the next 8 bytes will be the payload length then [bits 16-79 in the frame]
            
                [[[
                        0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1
                        +-+-+-+-+-------+-+-------------+-------------------------------+
                        |F|R|R|R| opcode|M| Payload len |    Extended payload length    |
                        |I|S|S|S|  (4)  |A|     (7)     |           (64bits)            |
                        |N|V|V|V|       |S|             |          (8 bytes)            |
                        | |1|2|3|       |K|             |    (if payload len==127)      |
                        +-+-+-+-+-------+-+-------------+ - - - - - - - - - - - - - - - +
                        |     Extended payload length continued, if payload len == 127  |
                        + - - - - - - - - - - - - - - - +-------------------------------+
                        |  Extended payload length      | Masking-key, (4 bytes)        |
                        +-------------------------------+-------------------------------+
                        | Masking-key (continued)       |          Payload Data         |
                        +-------------------------------- - - - - - - - - - - - - - - - +
                        :                     Payload Data continued ...                :
                        + - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - +
                        |                     Payload Data continued ...                |
                        +---------------------------------------------------------------+
                                                If the mask bit == 1
                    
                ]]]
    Summary:
            To read the frame length, read the 7 bit length
                • If the value is 126, read the next 16 bits as the length
                • If the value is 127, read the next 64 bits as the length
                • Else, the value itself is the length
    The Mask
        • Each 4 bytes of the payload has been XORed with the mask by the client
        • Read the payload 4 bytes at a time and XOR the bytes with the mask
        • If the length is not a multiple of 4, use only the bytes of the mask that are
        needed
        • Ie. Always reading 4 bytes will cause an index out of bounds error
        [[reccommeded to mask 1 byte at a time:
          Use modular arithmetic to match the correct part of the payload with the mask]]
    Final Message:
        • Once the payload is XORed with the mask 4 bytes at time we get the entire message
        • Then process the message
    After we parse the request:
        To send a message to a client set up a websocket frame:
                        
                           MASK bit is set to 0, DO NOT MASK sending frames

                 0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1
                +-+-+-+-+-------+-+-------------+-------------------------------+
                |F|R|R|R| opcode|M| Payload len |                               |
                |I|S|S|S|  (4)  |A|  (matches   |  if payload length is <126    |
                |N|V|V|V|       |S|   payload   |   This will be the Payload    |
                | |1|2|3|       |K|   received) |                               |
                +-+-+-+-+-------+-+-------------+ - - - - - - - - - - - - - - - +
                 1 0 0 0 0 0 0 1 0 

    The request sent from the client will always either be:
    • Therefore, the first byte is either 10000001 == 129 or 10001000 == 136
"""


####
####
####
"""
Video from 3/28 -- 13:00 minutes:
    Discussing how to set up the while True to keep reading the socket, the loop will last the length of the connection
    Inside the loop, I will have a reference to the HTTP handler, which contains a reference to the TCP connection
    So if we create a data structure in the server.py file. The list websocket_connections = []
    Every instance

    

"""
###################################################################################
#MyTCPHandler.websocket_connections
###################################################################################

# example key                       Sec-WebSocket-Key: 25dJisszYN+6UXLJCSqTEw==
# example of proper response key:   sec-websocket-accept: vdlhb7ci/qt6pmGqd9J31pZtxss=
def handshake(request, handler):
    sys.path.append("..")
    from app import MyTCPHandler
    """
    we import the MyTCPHandler only when this function is called to avoid cicular dependecy issues
    """
    print("we have entered the websocket \n")
    res = generate_websocket_response(b"","text/plain; charset=utf-8",'101 Switching Protocols', request)
    print("this is response for websocket >>>>>>>>>>>>>>>>>>>>: ", res)
    handler.request.sendall(res)
    username = "User" + str(random.randint(0,1000))
    MyTCPHandler.websocket_connections.append({'username': username, 'websocket': handler})
    while True:
    # write code to 
        websock_frame = handler.request.recv(1024)
        print("this is the websocket frame: ", websock_frame, flush=True)
        



def generate_websocket_response(body, content_type, response_code, request):
    r = b'HTTP/1.1 ' + response_code.encode()
    r += b'\r\nContent-Length: ' + str(len(body)).encode() 
    r += b'\r\nContent-Type: ' + content_type.encode()
    r += b'\r\nX-Content-Type-Options: nosniff'
    r += b'\r\nConnection: Upgrade'
    r += b'\r\nUpgrade: websocket'
    r += generate_sha(request)
    r += b'\r\n\r\n'
    return r

def generate_sha(request):
    request_key = request.headers["Sec-WebSocket-Key"]
    full_hash_key = request_key + "258EAFA5-E914-47DA-95CA-C5AB0DC85B11"  
    hash_object = hashlib.sha1(full_hash_key.encode()).hexdigest()
    hashy = base64.b64encode(bytes.fromhex(hash_object)).decode()
    rethash = b"\r\nSec-WebSocket-Accept: " + hashy.encode()
    return rethash

  