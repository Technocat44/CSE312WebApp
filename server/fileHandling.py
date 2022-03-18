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



def formParser(byteArray, count, multipartDict, headers):
  #  print("multipart dict " ,multipartDict , '\n\n')
   #  TODO: what if the multipart fits all in one request? Then the byteArray will be empty
  #  print("this is the og byte array, ",byteArray , '\n')
    count+=1
    # I don't think this will ever be true, so I can comment it out
    # if (headers.get("Content-Type") == None):
    #     return {}
    boundary = getBoundary(headers)
    
   # print("this is the boundary, ",boundary , '\n')
    # lets create a newbyte Array by chopping off the first boundary
    boundary_index = byteArray.find(boundary)
    # TODO: test out the base case

    print("does the final value of the final multipart end with '--' ? === ",byteArray[(boundary_index) + len(boundary):].startswith(b"--") )
    if (byteArray[(boundary_index) + len(boundary):].startswith(b"--")):
        print("INSIDE THE BASE CASE!!!!!!!!!!!!!!")
     #   print("the mutipart dict inside the base case!!!!!!!!!!!!!!!!", multipartDict)
        # we know this is the end of the multipart request and we can return 
        # this is the "base case" for the recursion
        return 
    newByteArray = byteArray[(boundary_index) + len(boundary) + len(new_line):]

#    print("this is the new byte array with the first boundary cut off", newByteArray, '\n')
 #   print("for the last request the newByteArray should look like this '--'", newByteArray, '\n')
    # now with the new byte array with the top boundary cut off, we can find the next boundary. 
    # finding the next boundary, everything before that will be one whole part of the multipart form
    part_index = newByteArray.find(boundary)
    # this is a very important index marker, it represents the index we will return. Then using the original byteArray, the 
    # for the second call to the next multipart, all we will need is that index and we can parse 
    part1 = newByteArray[:part_index]
    part2 = newByteArray[part_index :]
  #  print(f"this is part{count+1} that I will pass on , ", part2, '\n')
  #  print(f"this is part {count} of the multipart form , ", part1, '\n')
    label_of_part = grabElementName(part1)
    file_name_from_upload = grabFileName(part1)
    print("commment name , ", label_of_part)
    print("file name from upload, ", file_name_from_upload)
    # this will separate the headers from the body
    crlf2_index = part1.find(blank_line_boundary)
    newline_index = part1.find(new_line)
    print(newline_index)
    part1headers = part1[:crlf2_index]
    part1body = part1[(crlf2_index + len(blank_line_boundary)):].strip() # strip off the trailing whitespace
    print(f"part{count}headers",part1headers , '\n')
 #   print(f"part{count}body ", part1body, "size of body ," ,len(part1body) , '\n')
    part1headersDict = parse_headers(part1headers)
    print(f"part{count}headersDict",part1headersDict , '\n')

    # set the name element as a key and the value to the body in the dictionary 
    print("THIS is the name element value: ", label_of_part)
    # this is how we are setting each section of the multipart in the dictionary, which we can use later in request.parts
    multipartDict[label_of_part] = part1body 
    if file_name_from_upload != None:
      multipartDict[b"fileName"] = file_name_from_upload
    # recursively call formparser while there are still parts of the form to be parsed out
    formParser(part2, count, multipartDict, headers)
  
    # if formofData == None:
    #     # create a new function that will handle a comment 
    #     print("yeah a comment")
    
    #     multipartDict["comment"] = part1body
    #     Request.parts = part1body
    #     # TODO: return dictionary for request.parts when should I return it? Once everything is parsed
    #     formParser(part2, count, multipartDict,headers)
    #     return multipartDict
    #    # Request.parts = multipartDict
    #     # call that new function
    #     #newFunction(part1body) and handles placing this data in the db and posting it to the html page
    #     # then call this recursively on the part2
    # else:
    #     # going to be an image probably
    #     if formofData.startswith("image"):
    #         print("yeah an image")
        
    #         multipartDict["upload"] = part1body
    #         Request.parts = multipartDict
    #         # create a new function that will handle an upload
            
    #     else:
    #         print("doesn't start with image")

def getBoundary(headers):
    contentType = headers["Content-Type"]
   # fakeContentType = b'multipart/form-data; boundary=----WebKitFormBoundarym2rAsFis2C5THAfW'
    dashes_index = contentType.find("----")
    boundary = b"--" + contentType[dashes_index:].encode()
    return boundary

def grabElementName(part1):
    name_index = part1.find(b"name")
  #  crlf2_index = part1.find(Request.blank_line_boundary)
    # the name label is always name="
    # so name_index + 5 == name="
    name_value_array = part1[name_index + 6:]
   # print("this is the name_value_array, ", name_value_array, '\n\n\n') 
    value_end_index = name_value_array.find(b"\"")
    # i have this now name_value_array == [upload";filename=""\r\nContent-Type ......] and the value_end_index is the first quote
    actual_value = name_value_array[:value_end_index]
  #  print("the actual_value from the grabElementName function : ", actual_value, '\n\n\n')
    # the actual value should be this b'comment' or b'upload'  
    return actual_value    

def grabFileName(part1):
    
    file_name_index = part1.find(b"filename")
    if file_name_index == -1:
      return None
    print("\n\n\n\n\n\n\n\n\n\n")
    print("inside the grabFileName function\n")
    print("this is the filename index", file_name_index)
    new_line_index = part1.find(b"\r\n")
    file_name_array = part1[file_name_index + 10:new_line_index]
    file_name_end_index = file_name_array.find(b".")
    if file_name_end_index != -1:
      name_of_file = file_name_array[:file_name_end_index]
      return name_of_file
    return None

 

if __name__ == '__main__':
   # sample_GET_request = b'GET /hkgkg HTTP/1.1\r\nHost: localhost:8080\r\nConnection: keep-alive\r\nPragma: no-cache\r\nCache-Control: no-cache\r\nsec-ch-ua: " Not A;Brand";v="99", "Chromium";v="98", "Google Chrome";v="98"\r\nsec-ch-ua-mobile: ?0\r\nsec-ch-ua-platform: "Windows"\r\nDNT: 1\r\nUpgrade-Insecure-Requests: 1\r\nUser-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/98.0.4758.102 Safari/537.36\r\nAccept: text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9\r\nSec-Fetch-Site: none\r\nSec-Fetch-Mode: navigate\r\nSec-Fetch-User: ?1\r\nSec-Fetch-Dest: document\r\nAccept-Encoding: gzip, deflate, br\r\nAccept-Language: en-US,en;q=0.9\r\n\r\n'
   # request = Request(sample_GET_request)
    byteArr = b'------WebKitFormBoundarym2rAsFis2C5THAfW\r\nContent-Disposition: form-data; name="xsrf_token"\r\n\r\nAQAAAjppCA8mhugn2UvwOTaKnVY\r\n------WebKitFormBoundarym2rAsFis2C5THAfW\r\nContent-Disposition: form-data; name="comment"\r\n\r\nI am making a fake post request\r\n------WebKitFormBoundarym2rAsFis2C5THAfW\r\nContent-Disposition: form-data; name="upload"; filename="UB.jpg"\r\nContent-Type: image/jpeg\r\n\r\n\xff\xd8\xff\xe0\x00\x10JFIF\x00\x01\x01\x00\x00\x01\x00\x01\x00\x00\xff\xdb\x00\x84\x00\t\x06\x07\x13\x12\x12\x15\x11\x12\x13\x16\x16\x12\x15\x19\x1d\x1b\x19\x18\x18\x18\x1e\x1f\x18\x1c\x18#\x19!\x1b\x1a\x1a \x18\x1a\x1d(\r\n \x1a\x1f%\x1b\x1e\r\n\r\n"!2!%)+... \x1f383.7(-.+\x01\n\n\n\x0e\r\x0e\x1b\x10\x10\x1a-& %--/-.22--++/2+----/-------------------------------\xff\xc0\x00\x11\x08\x00\xb8\x01\x13\x03\x01\x11\x00\x02\x11\x01\x03\x11\x01\xff\xc4\x00\x1c\x00\x01\x00\x03\x01\x01\x01\x01\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x05\x06\x07\x04\x03\x02\x01\x08\xff\xc4\x00N\x10\x00\x02\x01\x03\x02\x03\x05\x03\x05\x0c\x06\x08\x06\x03\x00\x00\x01\x02\x03\x00\x04\x11\x12!\x05\x061\x07\x13AQa"q\x81\r\n------WebKitFormBoundarym2rAsFis2C5THAfW--\r\n'
    #request = fileUploadParser(file)
    count = 0
    multipartDict = {}
    headers = {"Host": "localhost:8080", "Connection": "keep-alive", "Pragma": "no-cache", "Cache-Control": "no-cache", "Content-Type": "multipart/form-data; boundary=----WebKitFormBoundarym2rAsFis2C5THAfW"}
    request = formParser(byteArr,count, multipartDict, headers)
    print("the return value of a request should be a dictionary: ", request)
    # print("size of image body , " , len(request["upload"]))
    pass 