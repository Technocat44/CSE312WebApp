# https://stackoverflow.com/questions/10411085/converting-integer-to-binary-in-python

from encodings import utf_8


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
    payload = 127
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



    movePastStartingBytes = 2
    smallMask = ""
    the_payload = ""
    for bytes in sockFrame:
        # print("len of sockFrame:",len(sockFrame))
        # print(movePastStartingBytes)
        if movePastStartingBytes == len(sockFrame):
            break
        elif movePastStartingBytes < 6:
            smallMask += formatInt2Bin(sockFrame[movePastStartingBytes]) + " "
            movePastStartingBytes+=1
        else:
            # rest of bytes are the payload
            the_payload += formatInt2Bin(sockFrame[movePastStartingBytes]) + " "
            movePastStartingBytes+=1
    print("smallMask:   ",smallMask, "length of small mask", len(smallMask))
    print("the payload: ",the_payload, "payload length: ", len(the_payload)/8 )

 

    test=                "1000001010000010"
    bi = int(test,2)^int("0111110110101010",2)
    b = bin(bi)[2:].zfill(len(test))
    # how to convert a string representation of a binary number into an int
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
    ascii = ""
    payDex = 0
    for payIndex in range(0,len(payloadList),4):
        print("payIndex", payIndex)
        
        for smIndex in range(len(smallMaskList)):
            if payDex == len(payloadList):
                break
            print("paydex: ",payDex)
            xor = int(smallMaskList[smIndex],2) ^ int(payloadList[payDex],2)
           # print("xor: ", bin(xor)[2:].zfill(len(smallMaskList[smIndex])))
            payDex+=1
            ascii_ch = chr(xor)
            ascii += ascii_ch
    print(ascii)
        
    return 0

def mask(frame):
    opcodeMask = 15
    byte1 = frame[0]
    opcode = byte1 & opcodeMask
    if opcode == 8:
        pass # break
    byte2 = frame[1]
    payMask = 127
    payLoadLength = byte2 & payMask
    if payLoadLength < 126:
        mask = frame[2:6]
        #print(mask, type(mask))
        for bytes in range(len(frame)):
            for b in range(len(mask)):
              
                decode = frame[b] ^ mask[b]
              
               

def parseFrame(frame):
    opMask = 15
    firstbyte = frame[0]
    opCode = firstbyte & opMask
    if opCode == 8:
        pass # break (will be break in the while True loop)
    payload_mask = 127
    payload_length = frame[1] & payload_mask
    if payload_length < 126:
        pass
        # only need to read the next 4 bytes are the mask 

    elif payload_length == 126:
        pass
    else:
        pass



if __name__ == '__main__':
    websockFrame = b'\x81\xba\xe0\x9e\x8f\x12\x9b\xbc\xe2w\x93\xed\xeeu\x85\xca\xf6b\x85\xbc\xb50\x83\xf6\xeef\xad\xfb\xfca\x81\xf9\xea0\xcc\xbc\xec}\x8d\xf3\xea|\x94\xbc\xb50\xad\xe7\xaft\x89\xec\xfcf\xc0\xf3\xeaa\x93\xff\xe8w\xc2\xe3'
    parseWebSocket(websockFrame)
    mask(websockFrame)
   # print(type(websockFrame))
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
