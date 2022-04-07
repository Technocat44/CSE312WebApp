# https://stackoverflow.com/questions/10411085/converting-integer-to-binary-in-python

import json

def formatInt2Bin(integer):
    formatted = '{0:08b}'.format(integer)
    return formatted

def parseWebSocket(sockFrame):
    opMask = 15
    print("binary of 15", bin(opMask))
    formatBinary = formatInt2Bin(opMask)
    print("formatted: " ,formatBinary)
    firstbyte = sockFrame[0]
    print("firstbyte :", firstbyte)
    byte = firstbyte & opMask
    print("opCode: ", byte, type(byte))
    firstbytes = sockFrame[0]
    print("first byte in binary: ", formatInt2Bin(firstbytes))
    # print('\n')

    secondbytes = sockFrame[1]
    print("second byte in binary:" , formatInt2Bin(secondbytes))
    secondbyte= formatInt2Bin(secondbytes)
    # mask second byte to elimnate the first byte
    mask = 127
    payload_length = secondbytes & mask
    print(payload_length)
    # how to pretty print all these bytes?
    # make a loop over the socket frame, accumulate four formatted nibbles into a string, and then print the string
    # reset the string and continue the loop 
    payloadmask = 127
    payload = 255
    print(formatInt2Bin(payloadmask))
    print(formatInt2Bin(payload))
    plength = payload & payloadmask
    print(f"payload mask of 127 and payload of {payload} bitwise &: ", formatInt2Bin(plength))
    print("p length: ", plength)

    print('\n\n')
    fourBytes = ""
    count = -1
    for b in sockFrame:
        count +=1
       # print(count)
        if count > 0 and count % 4 == 0:
            print(count,fourBytes)
            # clear fourBytes
            fourBytes = ""
        fourBytes += formatInt2Bin(sockFrame[count]) + " " 
       # print(formatInt2Bin(sockFrame[b]))
    if fourBytes != '':
        print(count+1,fourBytes)
    print("payload length: ",payload_length)
    opcode = 1000
    close = opcode & opMask
    print("closing byte: ",formatInt2Bin(close))
    print("value of close byte: ", close)



    movePastStartingBytes = 2 # set this to 2 so we start parsing at the mask, 
    smallMask = ""
    the_payload = ""
    for bytes in sockFrame:
        # print("len of sockFrame:",len(sockFrame))
        # print(movePastStartingBytes)
        if movePastStartingBytes == len(sockFrame): # we know we've reached the end when the length == the # of bytes chunks
            break
        elif movePastStartingBytes < 6: # we know that bytes 2,3,4,5 are the mask so only iterate over them
            smallMask += formatInt2Bin(sockFrame[movePastStartingBytes]) + " "  
            # setting up the mask and the payload to have a space so I can split on that and have a list of bytes to work
            movePastStartingBytes+=1 # move on to the next set of bytes
        else:
            # rest of bytes are the payload
            the_payload += formatInt2Bin(sockFrame[movePastStartingBytes]) + " "
            movePastStartingBytes+=1
    print("smallMask:   ",smallMask, "length of small mask", len(smallMask))
    print("the payload: ",the_payload, "payload length: ", len(the_payload)/8 )

 

    test=                "1000001010000010"
    bi = int(test,2)^int("0111110110101010",2)
    # XOR the two bytes in binary
    b = bin(bi)[2:].zfill(len(test))
    # how to convert a string representation of a binary number into an int
    # bin(bi) converts the integer bi into intos binary representation
    # the [2:] skips over the first two bits that are the 0b
    # zfill will pad the left of the binary with zeros and do so the length of the inital binary
    print(bi)
    print(b)
    # print(8 % 32)
    # print(16 & 32)
    # print(24 % 32 )
    # message = ""
    # xor = ""
    # bytecount = 0
    # # loop over payload, and match the mask with the payload and xor it one byte at a time
    # for bits in range(len(the_payload)):
    #     # for each 8 bytes, use smallMAsk on payload
    #     if bits > 0 and bits % 8 != 0:
            
    # message = int(the_payload[:33],2)^ int(smallMask,2)
    # print("message:",message)
    # print("message decode: ", bin(message)[2:].zfill(len(smallMask)))
    """
    1. split the binary data on whitespace so now we have a list of bytes
    2. call int(x, base) with the binary encoding as x, and 2 as base to convert each binary encoding to a decimal integer
    """
    smallMaskList = smallMask.split()
    print(smallMaskList)
    payloadList = the_payload.split()
    print(len(payloadList))
    ascii = "" # this will be the message
    payDex = 0 # need to create this variable so it is not tied to the loop index
    for payIndex in range(0,len(payloadList),4): # skipping by 4 will match us with the next set of bytes for the mask!
        # print("payIndex", payIndex)
        # at the end of the inner loop payDex will be == 4 so we know we are at the correct next set of 4 bytes!!!!!
        for smIndex in range(len(smallMaskList)): # smIndex will always be 0,1,2,3 so we guarantee to iterate the mask length
            if payDex == len(payloadList): # is the payDex accumulator == len of payload we know to stop iterating
                break
            # print("paydex: ",payDex)
            # here we xor the bytes in the small mask that correspond to the payload list
            xor = int(smallMaskList[smIndex],2) ^ int(payloadList[payDex],2) 
           # print("xor: ", bin(xor)[2:].zfill(len(smallMaskList[smIndex])))
            payDex+=1 
            ascii_ch = chr(xor) # convert the xor into its ascii character and add it to the ascii string
            ascii += ascii_ch 
    print("message decoded: ",ascii)
    dict =json.loads(ascii) 
    print(type(dict)) 
    if dict.get("messageType") == "chatMessage": # this could be a webrtc so we have to check 
        comment = dict["comment"]
        print("this is the comment: ", comment)
        # need to escape the html of the comment
        escapedComment = escape_html(comment)
        print("this is the escaped comment: ", escapedComment)

        
    return 0

def mask(frame):
    opcodeMask = 15
    byteOne = frame[0]
    opcode = byteOne & opcodeMask
    if opcode == 8:
        pass # break
    byteTwo = frame[1]
    payMask = 127
    payLoadLength = byteTwo & payMask
    if payLoadLength < 126:
        mask = frame[2:6]
        smallMaskList = []
        print(mask, type(mask))
        for bytes in mask: # this will create a string list of bytes
            smallMaskList.append(formatInt2Bin(bytes))
        print(smallMaskList)
        payLoad = frame[6:]
        smallpayloadList = []
        for bytes in payLoad: # this will create a string list of bytes
            smallpayloadList.append(formatInt2Bin(bytes))
        print(len(smallpayloadList))
        decodeMes = decodeMessage(smallpayloadList, smallMaskList)
        print("message decoded of <125 plength: ",decodeMes)
    elif payLoadLength == 126:
        # have to combine the int values of the three bytes to know the length
        byte1 = payLoadLength
        byte2, byte3 = frame[2], frame[3]
        print("first byte of length: ",byte1)
        print(formatInt2Bin(byte1))
        print(byte2, byte3)
        print(formatInt2Bin(byte2))
        print(formatInt2Bin(byte3))
        # I will need to use the total payload length later when sending the frames
        totalPayloadLength = byte1 + byte2 + byte3
        print("totalPayload Length = ", totalPayloadLength)
        medMask = frame[4:8]
        medMaskList = []
        for bytes in medMask:
            medMaskList.append(formatInt2Bin(bytes))
        print("medMask: ", medMask)
        medPayLoad = frame[8:]
        medPayLoadList = []
        for bytes in medPayLoad:
            medPayLoadList.append(formatInt2Bin(bytes))
        print(len(medPayLoadList))
        decodedMessage = decodeMessage(medPayLoadList, medMaskList)
        print("message decoded from 126 plength: ",decodedMessage)
        # bytes 1,2,3 will make up the payload length
        # bytes 4,5,6,7 will make up the mask
        # bytes 8-end will make up the payload 
    elif payLoadLength > 126:
        pass
        # bytes 1,2,3,4,5,6,7,8,9will make up the payload length
        # bytes 10,11,12,13 will make up the mask
        # bytes 14 - end make up the payload
               

def decodeMessage(payloadByteList: list, maskbyteList: list):
    asciiStr = ""
    payIndex = 0 # need to create this variable so it is not tied to the loop index
    for pIndex in range(0,len(payloadByteList), 4): # skipping by 4 will match us with the next set of bytes for the mask!
        # at the end of the inner loop payDex will be == 4 so we know we are at the correct next set of 4 bytes
        for mIndex in range(len(maskbyteList)): # mIndex will always be 0,1,2,3 so we guarantee to iterate the mask length
            if payIndex == len(payloadByteList):
                break  # is the payDex accumulator == len of payload we know to stop iterating
            # here we xor the bytes in the small mask that correspond to the payload list
            xor = int(maskbyteList[mIndex],2)^int(payloadByteList[payIndex],2)
            payIndex+=1 
            ascii_ch = chr(xor) # convert the xor into its ascii character and add it to the ascii string
            asciiStr += ascii_ch 
    return asciiStr

def escape_html(hacker):
    return hacker.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')


if __name__ == '__main__':
    websocketFrame = b'\x81\xba\xe0\x9e\x8f\x12\x9b\xbc\xe2w\x93\xed\xeeu\x85\xca\xf6b\x85\xbc\xb50\x83\xf6\xeef\xad\xfb\xfca\x81\xf9\xea0\xcc\xbc\xec}\x8d\xf3\xea|\x94\xbc\xb50\xad\xe7\xaft\x89\xec\xfcf\xc0\xf3\xeaa\x93\xff\xe8w\xc2\xe3'
    websocketFrame85 = b'\x81\xfe\x00\x7fy\xa3\xba\xbe\x02\x81\xd7\xdb\n\xd0\xdb\xd9\x1c\xf7\xc3\xce\x1c\x81\x80\x9c\x1a\xcb\xdb\xca4\xc6\xc9\xcd\x18\xc4\xdf\x9cU\x81\xd9\xd1\x14\xce\xdf\xd0\r\x81\x80\x9c\x11\xca\x96\x9e\x1c\xd5\xdf\xcc\x00\xcc\xd4\xdbY\xd7\xd2\xd7\n\x83\xd3\xcdY\xc2\x9a\xd3\x1c\xd0\xc9\xdf\x1e\xc6\x9a\xca\x11\xc2\xce\x9e\x10\xd0\x9a\xdb\x10\xc4\xd2\xca\x00\x8e\xdc\xd7\x0f\xc6\x9a\xdd\x11\xc2\xc8\xdf\x1a\xd7\xdf\xcc\n\x83\xd6\xd1\x17\xc4\x9a\xdf\x17\xc7\x9a\xd6\x16\xd4\x9a\xdf\x1b\xcc\xcf\xcaY\xd7\xd2\xdf\r\x81\xc7'
    
    #parseWebSocket(websocketFrame85)
    websocketFrameHuge = b'\x81\xfe\x02\xa5\xf5\xcb\xb8\xa9\x8e\xe9\xd5\xcc\x86\xb8\xd9\xce\x90\x9f\xc1\xd9\x90\xe9\x82\x8b\x96\xa3\xd9\xdd\xb8\xae\xcb\xda\x94\xac\xdd\x8b\xd9\xe9\xdb\xc6\x98\xa6\xdd\xc7\x81\xe9\x82\x8b\xb1\xb9\xd9\xca\x80\xa7\xd9\x93\xd5\x94\x8b\x89\xb8\xaa\xc1\x87\xd5\x89\xd1\xda\x81\xb9\xd1\xdd\x8f\xe5\xe7\x84\xd8\x87\xdd\xcf\x81\xeb\xf5\xdc\x9b\xa2\xdb\xc1\xd5\xaa\xcc\x89\xcd\xf1\x8b\x9c\xd5\x9b\x96\x89\xb8\xe5\x94\x89\x9a\xa5\x98\x98\x86\xbf\x98\xe4\x94\xb2\x94\x89\x94\xb9\xca\xc0\x83\xa2\xd6\xce\xd5\xaa\xcc\x89\xa3\xa2\xdd\xc7\x9b\xaa\x98\xcc\x94\xb9\xd4\xd0\xd5\xa5\xdd\xd1\x81\xeb\xd5\xc6\x87\xa5\xd1\xc7\x92\xf0\x98\xda\x9d\xa4\xcd\xc5\x91\xeb\xd0\xc8\x83\xae\x98\xc8\x87\xb9\xd1\xdf\x90\xaf\x98\xc8\x81\xeb\x8e\x93\xc1\xfd\x94\x89\x97\xbe\xcc\x89\x81\xb9\xd9\xc0\x9b\xeb\xcf\xc8\x86\xeb\xd9\xc7\xd5\xa3\xd7\xdc\x87\xeb\xd4\xc8\x81\xae\x96\x89\xb7\xbe\xdc\xc8\xd8\x9b\xdd\xda\x81\xa3\x98\xda\x90\xae\xd5\xda\xd5\xaa\x98\xde\x9a\xa5\xdc\xcc\x87\xad\xcd\xc5\xd5\xbb\xd4\xc8\x96\xae\x94\x89\x93\xb9\xd7\xc4\xd5\xbf\xd0\xcc\xd5\xac\xd4\xc0\x98\xbb\xcb\xcc\xd5\xbc\xd0\xc0\x96\xa3\x98\xe0\xd5\xac\xd7\xdd\xd5\xa4\xde\x89\x9c\xbf\x98\xcf\x87\xa4\xd5\x89\x81\xa3\xdd\x89\x81\xb9\xd9\xc0\x9b\xeb\xd9\xc7\x91\xeb\xcc\xc1\x90\xeb\xd4\xc0\x81\xbf\xd4\xcc\xd5\x82\x98\xca\x9a\xbe\xd4\xcd\xd5\xbc\xd9\xc5\x9e\xeb\xcc\xc1\x87\xa4\xcd\xce\x9d\xeb\xcc\xc1\x90\xeb\xcb\xdd\x87\xae\xdd\xdd\x86\xe5\x98\xe0\xd5\xad\xdd\xc8\x87\xae\xdc\x89\x81\xa4\x98\xce\x9a\xeb\xce\xcc\x87\xb2\x98\xcf\x94\xb9\x98\xcf\x87\xa4\xd5\x89\x81\xa3\xdd\x89\x86\xbf\xd9\xdd\x9c\xa4\xd6\x85\xd5\xaa\xcb\x89\x82\xae\x98\xc1\x94\xaf\x98\xc8\x87\xb9\xd1\xdf\x90\xaf\x98\xc5\x94\xbf\xdd\x89\x94\xa5\xdc\x89\x82\xa4\xcd\xc5\x91\xeb\xcb\xdd\x94\xb9\xcc\x89\x94\xb8\x98\xc7\x90\xaa\xca\x89\x81\xa3\xdd\x89\x96\xa4\xca\xdb\x90\xa8\xcc\x89\x81\xa2\xd5\xcc\xd5\xaa\xcb\x89\x85\xa4\xcb\xda\x9c\xa9\xd4\xcc\xdb\xeb\xec\xc1\x90\xeb\xd1\xc4\x85\xb9\xdd\xda\x86\xa2\xd7\xc7\xd5\x82\x98\xc1\x94\xaf\x98\xde\x94\xb8\x98\xdd\x9d\xaa\xcc\x89\x82\xae\x98\xde\x90\xb9\xdd\x89\x99\xae\xd9\xdf\x9c\xa5\xdf\x89\x81\xa3\xdd\x89\xa2\xae\xcb\xdd\xd5\xaa\xd6\xcd\xd5\xae\xd6\xdd\x90\xb9\xd1\xc7\x92\xeb\xcc\xc1\x90\xeb\xfd\xc8\x86\xbf\x83\x89\x81\xa3\xdd\x89\x98\xa4\xcb\xdd\xd5\xbc\xdd\xda\x81\xae\xca\xc7\xd5\xa4\xde\x89\x86\xbb\xd4\xcc\x9b\xaf\xd1\xcd\xd5\xa9\xca\xc0\x91\xac\xdd\xda\xd5\xa4\xce\xcc\x87\xeb\xcc\xc1\x90\xeb\xfc\xc8\x9b\xbe\xda\xcc\xd9\xeb\xcf\xc1\x9c\xa8\xd0\x89\x9c\xb8\x98\xc1\x90\xb9\xdd\x89\x9a\xad\x98\xc7\x9a\xa9\xd4\xcc\xd5\xbc\xd1\xcd\x81\xa3\x98\xc8\x9b\xaf\x98\xcd\x90\xbb\xcc\xc1\xd9\xeb\xcc\xc6\x9a\xa0\x98\xdc\x86\xeb\xd9\xc4\x9a\xa5\xdf\x89\x81\xa3\xdd\x89\x81\xb9\xd9\xcd\x9c\xbf\xd1\xc6\x9b\xb8\x98\xc6\x93\xeb\xec\xdc\x87\xa0\xd1\xda\x9d\xeb\xca\xdc\x99\xae\x96\x8b\x88'
    mask(websocketFrame)
    mask(websocketFrame85)
    
   # print(type(websockFrame))
   # print("the lenght of the message: ", len('{"messageType":"chatMessage","comment":"My first message"}'))
    pass

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
                        |I|S|S|S|  (4)  |A|     (7)     |                               |
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
                [[[             0               1               2             3
                         0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1
                        +-+-+-+-+-------+-+-------------+-------------------------------+
                        |F|R|R|R| opcode|M| Payload len |    Extended payload length    |
                        |I|S|S|S|  (4)  |A|     (7)     |             (16bits)          |
                        |N|V|V|V|       |S|             |       (The next 4 bytes)      |
                        | |1|2|3|       |K|             |      (if payload len==126)    |
                                4               5                6             7   
                        +-+-+-+-+-------+-+-------------+ - - - - - - - - - - - - - - - +
                        |                            (4 bytes)                          |
                        |                   Masking key starts here                     |
                        + - - - - - - - - - - - - - - - + - - - - - - - - - - - - - - - +
                                8               9              10              11
                        |                        Payload Data                           |
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
            
                [[[             0               1                2             3
                        0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1
                        +-+-+-+-+-------+-+-------------+-------------------------------+
                        |F|R|R|R| opcode|M| Payload len |    Extended payload length    |
                        |I|S|S|S|  (4)  |A|     (7)     |           (64bits)            |
                        |N|V|V|V|       |S|             |          (8 bytes)            |
                        | |1|2|3|       |K|             |    (if payload len==127)      |
                        +-+-+-+-+-------+-+-------------+ - - - - - - - - - - - - - - - +
                                4               5               6              7       
                        |     Extended payload length continued, if payload len == 127  |
                                8               9               10             11
                        + - - - - - - - - - - - - - - - +-------------------------------+
                        |  Extended payload length      | Masking-key, (4 bytes)        |
                        +-------------------------------+-------------------------------+
                                12             13              14               15
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
                • If the value is 126, read the next 2 bytes/ 16 bits as the length
                • If the value is 127, read the next 8 bytes / 64 bits as the length
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
