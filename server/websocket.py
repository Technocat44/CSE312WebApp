import re
from server.response import generate_response
from server.router import Route
from server.request import Request
import server.database as db
import sys
import hashlib
import base64
import random
import os
import json
import sys
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
    router.add_route(Route('GET', '/chat-history', getChatHistory))

"""
Use your database to store all of the chat history for your app. This will allow the chat history
 to persist after a server restart.

Add a path to you server of "GET chat-history" which returns every saves chat message and returns
 them as a JSON string in the format:

[
{'username': 'user596', 'comment': 'hello world'},
{'username': 'user1', 'comment': 'welcome to the chat!'}
]

The Content-Type of your response should be 'application/json; charset=utf-8'.
"""
def getChatHistory(request,handler):
    chat = db.get_wehsocket_chat()
    chaty = json.dumps(chat).encode()
    res = generate_response(chaty, 'application/json; charset=utf-8', "200 OK")
    handler.request.sendall(res)
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
               b'1 0 0 0 0 0 0 1 0 0 1 1 1 0 1 0'
               b'1 0 0 0 0 0 0 1 0 0 1 1 0 0 0 0{"messageType": "chatMessage", "username": "User947", "comment": "hello "}'

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
  #  print("we have entered the websocket \n")
    res = generate_websocket_response(b"","text/plain; charset=utf-8",'101 Switching Protocols', request)
   # print("this is response for websocket >>>>>>>>>>>>>>>>>>>>: ", res)
    handler.request.sendall(res)
    username = "User" + str(random.randint(0,1000))
    MyTCPHandler.websocket_connections.append({'username': username, 'websocket': handler})
    websocketString = b''


    while True:
    # write code to 
      #  print("[[INITIATING WEBSOCKET]]",flush =True)
        websock_frame = handler.request.recv(1024)
        #TODO: Change this to be the len(readbytes
        # )
        """
        I change it to be the length of websocket
        """
        readbytes = len(websock_frame)
     #   print("this is the size of the INITIAL read bytes : ", readbytes, flush=True)
        #readbytes = 1024
        opcodeMask = 15
        byteOne = websock_frame[0]
        opcode = byteOne & opcodeMask
        if opcode == 8:
       #     print("yeah the opcode is 8")
       #     print("this is the webscoket connection list before: ", MyTCPHandler.websocket_connections)
            byteArrayClose= bytearray()
            respondFirstByteWeb = 136
            byteArrayClose.append(respondFirstByteWeb)
            handler.request.sendall(byteArrayClose)
            for dict in MyTCPHandler.websocket_connections:
       #         print("this is a dict in the websocket_connection list :", dict, flush =True)
        #        print(f"is username:{username} in ws_dict:{dict} ? ", username in dict , flush=True)
                if username in dict.values():
         #           print("yes the username is in the dictionary!", flush=True)
                    MyTCPHandler.websocket_connections.remove(dict)
                    break
        #    print("this is the list after we removed the disconnecting socket: ", MyTCPHandler.websocket_connections, flush=True)

            break
            # for dicts in range(len(MyTCPHandler.websocket_connections)):
            #     if dicts >= len(MyTCPHandler.websocket_connections):
            #         break
            #     print("this is a dict in the websocket list: ", MyTCPHandler.websocket_connections[dicts], flush=True)
            #     for k in MyTCPHandler.websocket_connections[dicts].keys():
            #     #    print("this is the keys: ", k, flush=True)
            #     #    print("this is the username ", username, flush=True)
            #         if MyTCPHandler.websocket_connections[dicts][k] == username:
            #             MyTCPHandler.websocket_connections.pop(dicts)
            #             break
            # print("now this the websocket connection list after: ", MyTCPHandler.websocket_connections, flush =True)
            # break
        byteTwo = websock_frame[1]
        payLoadMask = 127
        decodeMe = ""
        initial_payLoadLength_via_byte2 = byteTwo & payLoadMask
        the_real_payload_length = 0
        if initial_payLoadLength_via_byte2 < 126:
            the_real_payload_length = initial_payLoadLength_via_byte2
        #    prettyPrint(websock_frame, initial_payLoadLength_via_byte2)
            smallMaskList= createMaskList(websock_frame, 2, 6)
            smallpayloadList = createPayLoad(websock_frame, 6, the_real_payload_length+6)
            decodeMe = decodeMessage(smallpayloadList, smallMaskList)
    #        print("the length of the payload is: ", len(smallpayloadList), flush=True)
    #        print("message decoded of <125 plength: ",decodeMe, flush=True)
             

            escapedComment = ""
            # print("the result of decodeMe.find('chatmessage'): ", decodeMe.find("chatMessage") , flush=True)
            # print("the result of decodeMe.find('webRTC-offer'): ", decodeMe.find("webRTC-offer") , flush=True)
            # print("the result of decodeMe.find('webRTC-candidate'): ", decodeMe.find("webRTC-candidate") , flush=True)
            # print("the result of decodeMe.find('webRTC-answer'): ", decodeMe.find("webRTC-answer") , flush=True)

            if decodeMe.find("chatMessage") == 16: # this could be a webrtc so we have to check 
         #       print("yes the message does contain a chatMessage", flush=True)
                messageDict = json.loads(decodeMe)
                comment = messageDict["comment"]
            # print("this is the comment: ", comment)
                # need to escape the html of the comment
                escapedComment = escape_html(comment)
                db.store_wehsocket_chat(username, escapedComment)

            #  print("this is the escaped comment: ", escapedComment)
                frameToSend = sendFrames(escapedComment, username, the_real_payload_length)
        #        print("the frame we are sending back >>>> ", frameToSend, flush=True)
                for connections in MyTCPHandler.websocket_connections:
                
               #     print("the connections is a >>>> ",type(connections))
                    handle = connections["websocket"]
                    handle.request.sendall(frameToSend)
                # print(frameToSend, flush=True)
                # handler.request.sendall(frameToSend)
                # print('\n', flush=True)
                
                #{'messageType': 'webRTC-offer', 'offer': offer}
                #{'messageType': 'webRTC-answer', 'answer': answer}
                #{'messageType': 'webRTC-candidate', 'candidate': candidate}
                


            elif decodeMe.find("webRTC-offer") == 16:
        #        print("yes we got an OFFER", flush = True)
                frameSending = sendWebRTCFrames(decodeMe, "offer")

                for hand in MyTCPHandler.websocket_connections:
          #          print("this is the dict : ", hand,flush=True)
                    # if the username doesn't match we know this is the other user we are trying to connect to
                    if username != hand["username"]:
                        # print("current username", username, flush=True)
                        # print("opposite username", hand["username"], flush=True)
                    # we want to find the handler that isn't the current and send it to the other
                        otherHandler = hand["websocket"]
                    # we send those frames to that specific handler on the websocket connection
                        otherHandler.request.sendall(frameSending)
                        # print("send the frame to the other user, ", flush=True)
                        break
                # print("this is the frame we are sending back: ", frameSending, flush=True)

            elif decodeMe.find("webRTC-answer") == 16:
                # print("yes we got an ANSWER < 126 ", flush=True)
                frameSending = sendWebRTCFrames(decodeMe, "answer")

                for hand in MyTCPHandler.websocket_connections:
                    # print("this is the dict : ", hand,flush=True)
                    # if the username doesn't match we know this is the other user we are trying to connect to
                    if username != hand["username"]:
                        # print("current username", username, flush=True)
                        # print("opposite username", hand["username"], flush=True)
                    # we want to find the handler that isn't the current and send it to the other
                        otherHandler = hand["websocket"]
                    # we send those frames to that specific handler on the websocket connection
                        otherHandler.request.sendall(frameSending)
                        # print("send the frame to the other user, ", flush=True)
                        break
                # print("this is the frame we are sending back: ", frameSending, flush=True)

            elif decodeMe.find("webRTC-candidate") == 16:
                # print("we got a CANDIDATE" , flush = True)
                frameSending = sendWebRTCFrames(decodeMe, "candidate")

                for hand in MyTCPHandler.websocket_connections:
                    # print("this is the dict : ", hand,flush=True)
                    # if the username doesn't match we know this is the other user we are trying to connect to
                    if username != hand["username"]:
                        # print("current username", username, flush=True)
                        # print("opposite username", hand["username"], flush=True)
                    # we want to find the handler that isn't the current and send it to the other
                        otherHandler = hand["websocket"]
                    # we send those frames to that specific handler on the websocket connection
                        otherHandler.request.sendall(frameSending)
                        # print("send the frame to the other user, ", flush=True)
                        break
                # print("this is the frame we are sending back: ", frameSending, flush=True)

                # Your task is to extract the payload of these WebSocket messages, verify that they are not chat messages 
                # (and are WebRTC messages), then send the payload to the other WebSocket connection. 
                # The clients will do the rest through the front end.
                # Extract the payload from the WB frame, build a new frame with the exact payload and send it to the other peer





        elif initial_payLoadLength_via_byte2 == 126:
            # I don't think I have to add the inital length to the rest of the payload but I will see soon
            # print("THE INITIAL LENGTH OF PAYLOAD IS 126", flush=True)
            # print("the inital payloadlength from the byte", initial_payLoadLength_via_byte2, flush=True)
            byte1 = initial_payLoadLength_via_byte2
      #      print("inital lenght of payload: ", initial_payLoadLength_via_byte2, flush=True)
            the_real_payload_length = calculatePayloadLength(websock_frame, 2,4) 
            # print("the real payload length: ", the_real_payload_length, flush=True) 
            medMaskList = createMaskList(websock_frame, 4, 8)
            # we need to go back to the websocket to retrieve data 
            # while bytes read is < the real payload length :
                # go back to the handler and accumulate the bytes
                # 

            """
        
            count the length of the websocket frame, cant assume that I am reading 1024 bytes on each 

            """
      #      print("this is the size of the payloadLength" , the_real_payload_length+8, flush=True)
            while(readbytes <= the_real_payload_length + 8):
        #        print("yes readbytes is less than the payload length readbytes = " , readbytes, flush =True)
                if the_real_payload_length+8 - readbytes < 1024:
         #           print("the payload length - readbytes =  :" , the_real_payload_length+8 - readbytes, flush=True)
                    websock_frame += handler.request.recv(the_real_payload_length+8-readbytes)
                    readbytes = len(websock_frame)
                    break
                else:
                    websock_frame += handler.request.recv(1024)
           #         print("no the payload length - read bytes is not < 1024, the lenght of the websock frame is:  ",len(websock_frame), flush=True )
                    

                    readbytes = len(websock_frame)
         #           print("this is how many bytes weve read: ", readbytes, flush=True)
                """
                changed this to count the length of the bytes read so we can get exact
                """
                
       #     print("this is the length of read bytes inside of 126, ", readbytes, flush=True)
                # readbytes+=1024

            readbytes=0
            # print(f"this is how many bytes were read {readbytes}, and this is how large the payload length is {the_real_payload_length} ", flush = True)
            # prettyPrint(websock_frame, the_real_payload_length)
            """
            # TODO: I am not going to reset the bytes here
            """
            # readbytes = 1024
            medPayLoadList = createPayLoad(websock_frame, 8, the_real_payload_length+1)
            # print(f"THIS IS THE PAYLOAD size {len(medPayLoadList)} ", flush=True)
            # print(f"This is the maskList size {len(medMaskList)} and LIST: ", medMaskList, flush=True)
            decodeMe = decodeMessage(medPayLoadList, medMaskList)
           # print("the length of the payload is : ", len(medPayLoadList), flush=True)
         #   print("message decoded from 126 plength: ",decodeMe, flush=True)
            escapedComment = ""
        #    print("the decoded message is :" , decodeMe, " LENGTH OF THE DECODED MESSAGE: ", len(decodeMe), flush=True)
            # print("the result of decodeMe.find('chatmessage'): ", decodeMe.find("chatMessage") , flush=True)
            # print("the result of decodeMe.find('webRTC-offer'): ", decodeMe.find("webRTC-offer") , flush=True)
            # print("the result of decodeMe.find('webRTC-candidate'): ", decodeMe.find("webRTC-candidate") , flush=True)
            # print("the result of decodeMe.find('webRTC-answer'): ", decodeMe.find("webRTC-answer") , flush=True)

            if decodeMe.find("chatMessage") == 16: # this could be a webrtc so we have to check 
                # print("yes the message does contain a chatMessage", flush=True)
                messageDict = json.loads(decodeMe)    
                comment = messageDict["comment"]
            # print("this is the comment: ", comment)
                # need to escape the html of the comment
                escapedComment = escape_html(comment)
                db.store_wehsocket_chat(username, escapedComment)
            #  print("this is the escaped comment: ", escapedComment)
                frameToSend = sendFrames(escapedComment, username, the_real_payload_length)
                # print("the frame we are sending back >>>> ", frameToSend, flush=True)
                for connections in MyTCPHandler.websocket_connections:
                
         #           print("the connections is a >>>> ",type(connections))
                    handle = connections["websocket"]
                    handle.request.sendall(frameToSend)
            # elif messageDict.get("messageType") == "webRTC-offer":
            #     print("yes we got an OFFER", flush = True)
            # elif messageDict.get("messageType") == "webRTC-answer":
            #     pass
            # elif messageDict.get("messageType") == "webRTC-candidate":
            #     print("we got a CANDIDATE" , flush = True)
            elif decodeMe.find("webRTC-offer") == 16:
                # print("yes we got an OFFER", flush = True)
                frameSending = sendWebRTCFrames(decodeMe, "offer")

                for hand in MyTCPHandler.websocket_connections:
                    # print("this is the dict : ", hand,flush=True)
                    # if the username doesn't match we know this is the other user we are trying to connect to
                    if username != hand["username"]:
                        # print("current username", username, flush=True)
                        # print("opposite username", hand["username"], flush=True)
                    # we want to find the handler that isn't the current and send it to the other
                        otherHandler = hand["websocket"]
                    # we send those frames to that specific handler on the websocket connection
                        otherHandler.request.sendall(frameSending)
                        # print("send the frame to the other user, ", flush=True)
                        break
                # print("this is the frame we are sending back: ", frameSending, flush=True)
            elif decodeMe.find("webRTC-answer") == 16:
                # print("yes we got an ANSWER", flush=True)
                frameSending = sendWebRTCFrames(decodeMe, "answer")

                for hand in MyTCPHandler.websocket_connections:
                    # print("this is the dict : ", hand,flush=True)
                    # if the username doesn't match we know this is the other user we are trying to connect to
                    if username != hand["username"]:
                        # print("current username", username, flush=True)
                        # print("opposite username", hand["username"], flush=True)
                    # we want to find the handler that isn't the current and send it to the other
                        otherHandler = hand["websocket"]
                    # we send those frames to that specific handler on the websocket connection
                        otherHandler.request.sendall(frameSending)
                        # print("send the frame to the other user, ", flush=True)
                        break
                # print("this is the frame we are sending back: ", frameSending, flush=True)

            elif decodeMe.find("webRTC-candidate") == 16:
                # print("we got a CANDIDATE" , flush = True)
                frameSending = sendWebRTCFrames(decodeMe, "candidate")

                for hand in MyTCPHandler.websocket_connections:
                    # print("this is the dict : ", hand,flush=True)
                    # if the username doesn't match we know this is the other user we are trying to connect to
                    if username != hand["username"]:
                        # print("current username", username, flush=True)
                        # print("opposite username", hand["username"], flush=True)
                    # we want to find the handler that isn't the current and send it to the other
                        otherHandler = hand["websocket"]
                    # we send those frames to that specific handler on the websocket connection
                        otherHandler.request.sendall(frameSending)
                        # print("send the frame to the other user, ", flush=True)
                        break
                # print("this is the frame we are sending back: ", frameSending, flush=True)











        elif initial_payLoadLength_via_byte2 > 126:
       #     print("THE INITIAL LENGTH OF PAYLOAD IS 127", flush=True)
       #     print("the inital payloadlength from the byte", initial_payLoadLength_via_byte2, flush=True)
            byteUno = initial_payLoadLength_via_byte2
            the_real_payload_length = calculatePayloadLength(websock_frame, 2, 10) 
       #     print("the real payload length = ",the_real_payload_length, flush=True)

            lgMaskList = createMaskList(websock_frame, 10, 14)
        #    print("this is the size of the payloadLength" , the_real_payload_length+14, flush=True)
            while(readbytes <= the_real_payload_length + 14):
         #       print("yes readbytes is less than the payload length readbytes = " , readbytes, flush =True)
                if the_real_payload_length+14 - readbytes < 1024:
          #          print("the payload length - readbytes =  :" , the_real_payload_length+14 - readbytes, flush=True)
                    websock_frame += handler.request.recv(the_real_payload_length+14-readbytes)
                    readbytes = len(websock_frame)
                    break
                else:
                    websock_frame += handler.request.recv(1024)
          #          print("no the payload length - read bytes is not < 1024, the lenght of the websock frame is:  ",len(websock_frame), flush=True )
                    

                    readbytes = len(websock_frame)
         #           print("this is how many bytes weve read: ", readbytes, flush=True)
                """
                changed this to count the length of the bytes read so we can get exact
                """
                
         #   print("this is the length of read bytes inside of 126, ", readbytes, flush=True)
           # prettyPrint(websock_frame, the_real_payload_length)
            """
            # TODO: I am commenting this out and not resetting it
            """
            readbytes =0
            # TODO: I am only creating a payload of the payloaf length size + 1
            # testing this out
            lgPayLoadList = createPayLoad(websock_frame, 14, the_real_payload_length+1)
      #      print("size of large payload list, ", len(lgPayLoadList), flush=True)
            decodeMe = decodeMessage(lgPayLoadList, lgMaskList)
     #       print("the decoded message is :" , decodeMe, "LENGTH OF THE DECODED MESSAGE: ", len(decodeMe), flush=True)
        #    print("the length of lgPayloadList:  ", len(lgPayLoadList), flush=True)
          #  messageDict = json.loads(decodeMe)    

            escapedComment = ""
         #   print("LENGTH OF THE DECODED MESSAGE , ", len(decodeMe), flush=True)

            # the chat messsage index should be 17  {"messageType":"chatMessage"
            if decodeMe.find("chatMessage") == 16: # this could be a webrtc so we have to check 
                # print("yes the message does contain a chatMessage", flush=True)
                messageDict = json.loads(decodeMe) 
                comment = messageDict["comment"]
               # print("this is the comment: ", comment, flush =True)
                # need to escape the html of the comment
                escapedComment = escape_html(comment)

                db.store_wehsocket_chat(username, escapedComment)

            #  print("this is the escaped comment: ", escapedComment)
                frameToSend = sendFrames(escapedComment, username, the_real_payload_length)
         #       print("the length of the frame we are sending back: ".upper(), len(frameToSend), flush=True)
          #      print("the frame we are sending back >>>> ", frameToSend, flush=True)
                for connections in MyTCPHandler.websocket_connections:
                
            #        print("the connections is a >>>> ",type(connections))
                    handle = connections["websocket"]
                    handle.request.sendall(frameToSend)
            elif decodeMe.find("webRTC-offer") == 16:
                pass
            elif decodeMe.find("webRTC-answer") == 16:
                pass
            elif decodeMe.find("webRTC-candidate") == 16:
                pass
        # messageDict = json.loads(decodeMe)    

        # escapedComment = ""
        # if messageDict.get("messageType") == "chatMessage": # this could be a webrtc so we have to check 
        #     comment = messageDict["comment"]
        # # print("this is the comment: ", comment)
        #     # need to escape the html of the comment
        #     escapedComment = escape_html(comment)
        # #  print("this is the escaped comment: ", escapedComment)
        #     frameToSend = sendFrames(escapedComment, username, the_real_payload_length)
        #     # print(frameToSend,flush=True)
            
        #     for connections in MyTCPHandler.websocket_connections:
                
        #         print("the connections is a >>>> ",type(connections))
        #         handle = connections["websocket"]
        #         handle.request.sendall(frameToSend)
          #  handler.request.sendall(frameToSend)
          #  print('\n')
        #  print("this is the length of the websocketString: ",len(websocketString), flush = True)
        # print("websocket frame = : ", websocketString, flush=True)

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


"""
Do we need to add a mask bit?

Do we base sending the message over the websocket on the initial payload length or the payload length of the response 
message we created with the username and the messageType?
                                M
frame example = 1 0 0 0 0 0 0 1 0 

What happens if the length is greater than 127? How do we create the bytes? To pack into the websocket frame we send back?

If I bit shift >> 1 it puts a 0 on the front and makes the lowest value byte disappear
If I & mask it, itll keep the highest bit value as 1

Maybe do some math where I am subtracting 128 from the first byte?
Or maybe covert the integer to binary and bit shift it to place a 0 at the front of the byte? 
so if we had a       128 in binary
this              = 1 0 0 0 0 0 0 0 
this = this >> 1  = 0 1 0 0 0 0 0 0  == 64 now

"""
def sendWebRTCFrames(decodedMessage, typeOfMessage):

    messageToSendJSON = decodedMessage.encode()
    framePayloadLength = len(messageToSendJSON)
    byteArray = bytearray()
    firstbyte = 129
    byteArray.append(firstbyte)
    if framePayloadLength < 126:
        byteArray.append(framePayloadLength)
        byteArray+=messageToSendJSON
        return byteArray
    elif framePayloadLength >=126 and framePayloadLength < 65536:
        byteArray.append(126)
        newPay = framePayloadLength.to_bytes(2, byteorder="big")
        byteArray += newPay
        byteArray += messageToSendJSON
        return byteArray
    elif framePayloadLength >= 65536:
        byteArray.append(127)
        newPay = framePayloadLength.to_bytes(8, byteorder="big")
        byteArray += newPay
        byteArray += messageToSendJSON
        return byteArray

def sendFrames(escapedCom, username, payLoadLength):
    
    messageToSendBack = {'messageType':'chatMessage', 'username': username, 'comment':escapedCom}
    messageToSendBackJSON = json.dumps(messageToSendBack).encode()
    framePayLoadLength = len(messageToSendBackJSON) 
 #   print("the length of the message to send back ", framePayLoadLength)
    # framePayLoadLength = b''
    byteArrayWeb = bytearray()
    respondFirstByteWeb = 129
    byteArrayWeb.append(respondFirstByteWeb)

    if framePayLoadLength < 126:
        # byteArrayWeb.append(maskbit)
        # we set the payload length the same thing as what was sent so no matter what the highest bit will be 0
        # so I don't have to worry about the mask bit example: (01111101)
        byteArrayWeb.append(framePayLoadLength)
        byteArrayWeb += messageToSendBackJSON
        return byteArrayWeb
    elif framePayLoadLength >= 126 and framePayLoadLength < 65536:
        # >=126 and <65536
        # if the payload length is 126 the highest bit will be 0 example = (01111110)
        # the first two bytes will be 
        byteArrayWeb.append(126)

        newPay = framePayLoadLength.to_bytes(2, byteorder="big")
        byteArrayWeb += newPay
        byteArrayWeb += messageToSendBackJSON
        return byteArrayWeb
    elif framePayLoadLength >= 65536:
        # if the payload length is greater than the first bit after the payload is (01111111) the rest of the payload
        # is the framePayload length but we need to convert that into 8 bytes
        byteArrayWeb.append(127)
        newPay = framePayLoadLength.to_bytes(8, byteorder="big")

        byteArrayWeb += newPay
        byteArrayWeb += messageToSendBackJSON
        return byteArrayWeb
        """
        int.to_bytes(length, byteorder, *, signed=False)
        Return an array of bytes representing an integer.

        >>>
        (1024).to_bytes(2, byteorder='big')
        b'\x04\x00'
        """

    # framePayLoadLength = formatInt2Bin(payLoadLength)[1:]
        # frame = frame + respondFirstByte + framePayLoadLength.encode() + messageToSendBackJSON.encode()
        # return frame
    #frame = frame + respondFirstByte + messageToSendBackJSON
"""
    Message == 
{
'messageType': 'chatMessage', 
'username': random_username, 
'comment': html_escaped_comment_submitted_by_user
}

"""


# This function generates the sha1 hash, base64 encodes it and establishes the websocket handshake
def generate_sha(request):
    request_key = request.headers["Sec-WebSocket-Key"]
    full_hash_key = request_key + "258EAFA5-E914-47DA-95CA-C5AB0DC85B11"  
    hash_object = hashlib.sha1(full_hash_key.encode()).hexdigest()
    hashy = base64.b64encode(bytes.fromhex(hash_object)).decode()
    rethash = b"\r\nSec-WebSocket-Accept: " + hashy.encode()
    return rethash

# this function takes in an integer and returns the binary values as a string
def formatInt2Bin(integer: bytes):
    formatted = '{0:08b}'.format(integer)
    return formatted


def mask(frame: bytes):
    opcodeMask = 15
    byteOne = frame[0]
    opcode = byteOne & opcodeMask
    if opcode == 8:
        pass # break
    byteTwo = frame[1]
    payMask = 127
    decodeMe = ""
    payLoadLength = byteTwo & payMask
    if payLoadLength < 126:
        pass
    elif payLoadLength == 126:
        pass
    elif payLoadLength > 126:
        pass

# this function take in the bytes of the payload and the bytes of the mask and XOR's the payload with the mask, decoding
# the message and returns the message as a string
def decodeMessage(payloadByteList: list, maskbyteList: list):
    asciiStr = ""
    payIndex = 0 # need to create this variable so it is not tied to the loop index
    for pIndex in range(0,len(payloadByteList), 4): # skipping by 4 will match us with the next set of bytes for the mask!
        # print("payIndex from inside decoded Message: ", payIndex)
        # at the end of the inner loop payDex will be == 4 so we know we are at the correct next set of 4 bytes
        for mIndex in range(len(maskbyteList)): # mIndex will always be 0,1,2,3 so we guarantee to iterate the mask length
         #   print(f"payindex: {payIndex}, len(payloadbytelist):{len(payloadByteList)}", flush=True)
            if payIndex == len(payloadByteList):
                break  # is the payDex accumulator == len of payload we know to stop iterating
            # here we xor the bytes in the small mask that correspond to the payload list
            xor = int(maskbyteList[mIndex],2)^int(payloadByteList[payIndex],2)
            payIndex+=1 
            ascii_ch = chr(xor) # convert the xor into its ascii character and add it to the ascii string
            asciiStr += ascii_ch 
    # print("this is the payindex size [Inside decodeMessage]: ",payIndex, flush=True)
    # print("payindex should match the payload length [inside decodeMessage]: ", len(payloadByteList), flush=True)
    return asciiStr

# this function takes in a string and escapes any html injections
def escape_html(hacker: str):
    return hacker.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')

# this function takes in a websocket frame, and based on the payload length parses the bytes of the frame into a list
def createMaskList(frame: bytes, startingMaskIndex: int, endingMaskIndex: int):
    maskList = []
    mask = frame[startingMaskIndex:endingMaskIndex]
    for bytes in mask:
        maskList.append(formatInt2Bin(bytes))
    return maskList

# this function takes in a websocket frame, and based on the payload length parses the bytes of the frame into a list
def createPayLoad(frame: bytes, startingPayLoadIndex: int, payloadLength:int):
    payLoadList = []
    payload = frame[startingPayLoadIndex:]
   # print("the length of the payload when we create it [Inside createPayload], ", len(payload), flush=True)
    for bytes in payload:
        payLoadList.append(formatInt2Bin(bytes))
  #  print("pretty printing the payload list we created: ", flush=True)
    #prettyPrint(payload, len(payLoadList))
    return payLoadList

# this function takes in a frame and determines the integer value of the payload length from the websocket frame
def calculatePayloadLength(frame: bytes, startingPayLoadLengthIndex: int, endingPayLoadLengthIndex: int):
    payLoadLengthInBytes = frame[startingPayLoadLengthIndex:endingPayLoadLengthIndex]
    payLoadBinaryString = ""
    for b in payLoadLengthInBytes:
        payLoadBinaryString += formatInt2Bin(b)
    payLoadLength = int(payLoadBinaryString, 2)
    return payLoadLength

def prettyPrint(frame:bytes, payloadLength: int):
    # print("this is the size of the frame [inside pretty print]: ", len(frame), flush=True)
    # print("this is the size of the payload length [inside pretty print]: ", payloadLength, flush=True  )

    fourBytes = ""
    count = -1
    while(count < payloadLength):
        count +=1
        if count == payloadLength:
            break
        
        if count > 0 and count % 4 == 0:
            print(count,fourBytes)
            # clear fourBytes
            fourBytes = ""
        #print("this is the count index [inside pretty printing]: ", count, flush=True)
        fourBytes += formatInt2Bin(frame[count]) + " " 
    if fourBytes != '':
         print(count,fourBytes, flush=True)
    print("payload length: ",payloadLength, flush=True)