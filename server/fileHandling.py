#from server.request import parse_headers
 
# TODO: This is temporary will delete when not debugging 

byteDict = {"bytes":b''}
def all_bytes_of_file(read_bytes: bytes):
    byteDict["bytes"] = read_bytes
    
def sendBytes():
    return byteDict["bytes"]



new_line = b'\r\n'
blank_line_boundary = b'\r\n\r\n'
count = 0
def parse_headers(headers_raw: bytes):
    headers = {}
    lines_as_str = headers_raw.decode().split(new_line.decode())
    for line in lines_as_str:
        splits = line.split(':', 1)
        headers[splits[0].strip()] = splits[1].strip()
    return headers 



byteDict = {"bytes": b''}
def all_bytes_of_file(read_bytes: bytes):
    byteDict["bytes"] = read_bytes
    
def sendBytes():
    return byteDict["bytes"]



# def fileUploadParser(byteArray):
#     first_new_line_boundary_index = byteArray.find(new_line)
#     blank_line_boundary_index = byteArray.find(blank_line_boundary)

#     # now call the header parser to create a header dict
#     print("this is the original byteArray : ",byteArray , '\n')
#     fakeContentType = b'multipart/form-data; boundary=----WebKitFormBoundarym2rAsFis2C5THAfW'
#     # returns the index
#     findBoundary = fakeContentType.find(b"----")
#     #print("this is what find returns for the boundary ", findBoundary, '\n')
#     boundary = b'--' + fakeContentType[findBoundary:]
#     print("This is the boundary ,",boundary, '\n')
#     # maybe I could store each chunk into a dictionary? 
#     # what does find return if there is nothing there? 
#     # what = byteArray.find(b"jgjgjgjgjgjgjgjgjg")
#     # print(what, "this is what \n")
#     # if the sequence is not found then it returns a -1


#     firstChunkIndex = byteArray.find(boundary)
    
#     # should return everything inbetween the 
#     firstChunk = byteArray[(firstChunkIndex + len(boundary) + len(new_line)):blank_line_boundary_index]
#     print("this is first chunk ", firstChunk, "\n")
    

#     firstChunkHeadersDict = parse_headers(firstChunk)
#     print(firstChunkHeadersDict)
#     print(type(firstChunkHeadersDict["Content-Disposition"]))
#     valueOfFirstChunkDictContentDisposition = firstChunkHeadersDict["Content-Disposition"]
#     print("this is the value of the first chunk headers ," ,valueOfFirstChunkDictContentDisposition , '\n')
#     if (valueOfFirstChunkDictContentDisposition.find("comment") != -1):
#         print("we can use this body of this for the HTML ") 
    
#     newByteArray = byteArray[blank_line_boundary_index + len(blank_line_boundary):]
#     print("This is the new byte array, " ,newByteArray ,'\n')
#     get_the_body = newByteArray.find(boundary)
#     bodyOfOne = newByteArray[:get_the_body]
#     print("this is the body of the first chunk", bodyOfOne, '\n')

#     ##########################################################################


#     """
#     Ok I have to write a couple of helper functions that breaks it down into something nice and compact. 
    
#     One function to split the array up in the necessary parts, and it returns two things:  
#         1. It returns the original byte array input but with the previous part sliced off
#         2. It returns the body of the part we just extracted from the multipart
#         This can be done like in the Request class, where we returned a list like this = [part1, part2] 
#     Then using part1, we call the split function again, and that will return the next multipart as a list with two parts
#     This can then be done as many times as we need

#     Once we get to part with the image body we can handle that part a bit differently 
#     ### Since we know how many parts it is safe to assume that the first part will be the comment and the second part will be the image
#     ### if this changes we can somply add another line of code that calls the split function again

    # take the name of each part, and the body of each part, and store them in a dictionary. Do that for each part so 
    # we will have a dictionary with each part as keys and values
    # For example:
    #                file description                   file in bytes
    # '{"comment":"this is an image of ub", "upload":"x01\x00\x00\xff\xdb\x00\x84\x0"}'
    # Then return it and store it in the request namespace. Create a self.parts path in request, 
    # and since that will store a dictionary, we can call request.parts["comment"].decode() and that will return the body 
    

#     """

def getBoundary(byteArray):
    # this is what I will actually have to do when the server is up and running
    # contentType = request.headers["Content-Type"]
    fakeContentType = b'multipart/form-data; boundary=----WebKitFormBoundarym2rAsFis2C5THAfW'
    dashes_index = fakeContentType.find(b"----")
    boundary = b"--" + fakeContentType[dashes_index:]
    return boundary

def grabElementName(part1):
    name_index = part1.find(b"name")
    crlf2_index = part1.find(blank_line_boundary)
    name_and_label = part1[name_index:crlf2_index]
    name_and_label_split = name_and_label.split(b"=")
    # remove the quotes around the label
    label = name_and_label_split[1].replace(b"\"", b"")
    return label



def formParser(byteArray,count, multipartDict):
    print("multipart dict " ,multipartDict , '\n\n')
    print("this is the og byte array, ",byteArray , '\n')
    count+=1
    boundary = getBoundary(byteArray)
   # print("this is the boundary, ",boundary , '\n')
    # lets create a newbyte Array by chopping off the first boundary
    boundary_index = byteArray.find(boundary)
    newByteArray = byteArray[(boundary_index) + len(boundary) + len(new_line):]
  #  print("this is the new byte array with the first boundary cut off", newByteArray, '\n')
    # now with the new byte array with the top boundary cut off, we can find the next boundary. 
    # finding the next boundary, everything before that will be one whole part of the multipart form
    part_index = newByteArray.find(boundary)
    # this is a very important index marker, it represents the index we will return. Then using the original byteArray, the 
    # for the second call to the next multipart, all we will need is that index and we can parse 
    part1 = newByteArray[:part_index]
    part2 = newByteArray[part_index :]
    print(f"this is part{count+1} that I will pass on , ", part2, '\n')
    print(f"this is part {count} of the multipart form , ", part1, '\n')
    label_of_part = grabElementName(part1)
    print(label_of_part)
    # this will separate the headers from the body
    crlf2_index = part1.find(blank_line_boundary)
    newline_index = part1.find(new_line)
    print(newline_index)
    part1headers = part1[:crlf2_index]
    part1body = part1[(crlf2_index + len(blank_line_boundary)):].strip() # strip off the trailing whitespace
    print(f"part{count}headers",part1headers , '\n')
    print(f"part{count}body ", part1body, "size of body ," ,len(part1body) , '\n')
    part1headersDict = parse_headers(part1headers)
    print(f"part{count}headersDict",part1headersDict , '\n')
    formofData = part1headersDict.get("Content-Type")
    if formofData == None:
        # create a new function that will handle a comment 
        print("yeah a comment")
    
        multipartDict["comment"] = part1body

        # TODO: return dictionary for request.parts when should I return it? Once everything is parsed
        formParser(part2, count, multipartDict)
        return multipartDict
        # call that new function
        #newFunction(part1body) and handles placing this data in the db and posting it to the html page
        # then call this recursively on the part2
    else:
        # going to be an image probably
        if formofData.startswith("image"):
            print("yeah an image")
        
            multipartDict["upload"] = part1body
      
            # create a new function that will handle an upload
            
        else:
            print("doesn't start with image")
            

   
   
    # headersSplit = formofData.split("=")
    # print(headersSplit)
    # if headersSplit[1] == '"comment"':
      
    #     formParser(part2,count)
    # elif headersSplit[1] == '"upload"':
    #     print("yeah an upload")
        
    # else:
    #     # recursively call this function on part2
    #     return 0
   

 

if __name__ == '__main__':
   # sample_GET_request = b'GET /hkgkg HTTP/1.1\r\nHost: localhost:8080\r\nConnection: keep-alive\r\nPragma: no-cache\r\nCache-Control: no-cache\r\nsec-ch-ua: " Not A;Brand";v="99", "Chromium";v="98", "Google Chrome";v="98"\r\nsec-ch-ua-mobile: ?0\r\nsec-ch-ua-platform: "Windows"\r\nDNT: 1\r\nUpgrade-Insecure-Requests: 1\r\nUser-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/98.0.4758.102 Safari/537.36\r\nAccept: text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9\r\nSec-Fetch-Site: none\r\nSec-Fetch-Mode: navigate\r\nSec-Fetch-User: ?1\r\nSec-Fetch-Dest: document\r\nAccept-Encoding: gzip, deflate, br\r\nAccept-Language: en-US,en;q=0.9\r\n\r\n'
   # request = Request(sample_GET_request)
    file = b'------WebKitFormBoundarym2rAsFis2C5THAfW\r\nContent-Disposition: form-data; name="comment"\r\n\r\nI am making a fake post request\r\n------WebKitFormBoundarym2rAsFis2C5THAfW\r\nContent-Disposition: form-data; name="upload"; filename="UB.jpg"\r\nContent-Type: image/jpeg\r\n\r\n\xff\xd8\xff\xe0\x00\x10JFIF\x00\x01\x01\x00\x00\x01\x00\x01\x00\x00\xff\xdb\x00\x84\x00\t\x06\x07\x13\x12\x12\x15\x11\x12\x13\x16\x16\x12\x15\x19\x1d\x1b\x19\x18\x18\x18\x1e\x1f\x18\x1c\x18#\x19!\x1b\x1a\x1a \x18\x1a\x1d(\r\n \x1a\x1f%\x1b\x1e\r\n\r\n"!2!%)+... \x1f383.7(-.+\x01\n\n\n\x0e\r\x0e\x1b\x10\x10\x1a-& %--/-.22--++/2+----/-------------------------------\xff\xc0\x00\x11\x08\x00\xb8\x01\x13\x03\x01\x11\x00\x02\x11\x01\x03\x11\x01\xff\xc4\x00\x1c\x00\x01\x00\x03\x01\x01\x01\x01\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x05\x06\x07\x04\x03\x02\x01\x08\xff\xc4\x00N\x10\x00\x02\x01\x03\x02\x03\x05\x03\x05\x0c\x06\x08\x06\x03\x00\x00\x01\x02\x03\x00\x04\x11\x12!\x05\x061\x07\x13AQa"q\x81\r\n------WebKitFormBoundarym2rAsFis2C5THAfW--\r\n'
    #request = fileUploadParser(file)
    count = 0
    multipartDict = {}
    request = formParser(file,count, multipartDict)
    print("the return value of a request should be a dictionary: ", request)
    print("size of image body , " , len(request["upload"]))
    pass 