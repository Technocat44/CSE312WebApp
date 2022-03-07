

from server.fileHandling import sendBytes

class Request:
    new_line = b'\r\n'
    blank_line_boundary = b'\r\n\r\n'
  
    # this class creates an object of all the info we need to handle the TCP request

    def __init__(self, request: bytes):
        # the body is not going to be used in this 
        # part 1, take the incoming request and parse it out
        [request_line, headers_as_bytes, self.body] = split_request(request)
        # part 2, take the request line and parse that
        [self.method, self.path, self.http_version] = parse_request_line(request_line)
        # part 3, 
        self.headers = parse_headers(headers_as_bytes)
        print("This is sendBytes() >>>>>>>>>" , sendBytes(), '\n' )
        
        self.parts = {}

        """
        After the headers are parsed, we need to take care of the multipart boundary. 
        It will be in the Content-Type header -->  Content-Type: multipart/form-data; boundary=
        the boundary will look like this -->       ----WebKitFormBoundaryam94SD6c9rqAs6td
        B/c reasons we need to find that and then add "--" another two dashes for the full boundary
        We are going to use that boundary to split() up the multi parts
          There might be some newline characters mixed in the edges so I might need to strip()

        The last boundary is "--" + <boundary> + "--" \r\n
         """

      
        """
        From this ^^^ I can call, 
        self.body     --to get the body of the request,
        self.method   --to get the method type (GET or POST etc)
        self.path     --to get the path requested (/images or /index.html)
        self.http_version   
        self.headers  --to get a dictionary with all the headers 
        """

# this method takes in a request from a client and parses out the request line from the headers and the body
def split_request(request:bytes):
    # find returns the first instance of the new line
    first_new_line_boundary_index = request.find(Request.new_line)
    blank_line_boundary_index = request.find(Request.blank_line_boundary)

    # everything before the first new line char is the request line
    request_line = request[:first_new_line_boundary_index]
    print("request line: ", request_line)
    # everything inbetween the first new line char and the \r\n\r\n is the headers
    headers_as_bytes = request[(first_new_line_boundary_index + len(Request.new_line)):blank_line_boundary_index]
    print("headers as bytes: ", headers_as_bytes)
    # everything after the \r\n\r\n
    body = request[(blank_line_boundary_index + len(Request.blank_line_boundary)):]
    print("body: ", body)
    return [request_line, headers_as_bytes, body]

# I know the request line is a string so its safe to decode and split it
def parse_request_line(request_line: bytes):
    print("This is what the request line split is : ", request_line.decode().split(" "))
    return request_line.decode().split(" ")

def parse_headers(headers_raw: bytes):
    headers = {}
    lines_as_str = headers_raw.decode().split(Request.new_line.decode())
    for line in lines_as_str:
        splits = line.split(':', 1)
        headers[splits[0].strip()] = splits[1].strip()
    return headers 

# So if we want the Content-Length of a request we go
# Request.headers["Content-Length"] elsewhere in my code

# this little function will be called once we have read all the bytes of the file in html_paths.
# All it does is return all the bytes from the file we read, that won't happen until we hit the last line
# of the server, and we start handling the routes
def formParser(byteArray, count, multipartDict, headers):
    print("multipart dict " ,multipartDict , '\n\n')
   #  TODO: what if the multipart fits all in one request? Then the byteArray will be empty
    print("this is the og byte array, ",byteArray , '\n')
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
        # we know this is the end of the multipart request and we can return 
        # this is the "base case" for the recursion
        return multipartDict
    newByteArray = byteArray[(boundary_index) + len(boundary) + len(Request.new_line):]

    print("this is the new byte array with the first boundary cut off", newByteArray, '\n')
    print("for the last request the newByteArray should look like this '--'", newByteArray, '\n')
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
    crlf2_index = part1.find(Request.blank_line_boundary)
    newline_index = part1.find(Request.new_line)
    print(newline_index)
    part1headers = part1[:crlf2_index]
    part1body = part1[(crlf2_index + len(Request.blank_line_boundary)):].strip() # strip off the trailing whitespace
    print(f"part{count}headers",part1headers , '\n')
    print(f"part{count}body ", part1body, "size of body ," ,len(part1body) , '\n')
    part1headersDict = parse_headers(part1headers)
    print(f"part{count}headersDict",part1headersDict , '\n')
    formofData = part1headersDict.get("Content-Type")

    # set the name element as a key and the value to the body in the dictionary 
    print("THIS is the name element value: ", label_of_part)
    multipartDict[label_of_part] = part1body 

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
    # this is what I will actually have to do when the server is up and running
    contentType = headers["Content-Type"]
   # fakeContentType = b'multipart/form-data; boundary=----WebKitFormBoundarym2rAsFis2C5THAfW'
    dashes_index = contentType.find("----")
    boundary = b"--" + contentType[dashes_index:].encode()
    return boundary

def grabElementName(part1):
    name_index = part1.find(b"name")
    crlf2_index = part1.find(Request.blank_line_boundary)
    # the name label is always name="
    # so name_index + 5 == name="
    name_value_array = part1[name_index + 6:]
    print("this is the name_value_array, ", name_value_array, '\n\n\n') 
    value_end_index = name_value_array.find(b"\"")
    # i have this now name_value_array == [upload";filename=""\r\nContent-Type ......] and the value_end_index is the first quote
    actual_value = name_value_array[:value_end_index]
    print("the actual_value from the grabElementName function : ", actual_value, '\n\n\n')
    # the actual value should be this b'comment' or b'upload'
    # name_and_label = part1[name_index:crlf2_index]
    # name_and_label_split = name_and_label.split(b"=")
    # # remove the quotes around the label
    # label = name_and_label_split[1].replace(b"\"", b"")
    # return label        
    return actual_value    

   

if __name__ == '__main__':
   # sample_GET_request = b'GET /hkgkg HTTP/1.1\r\nHost: localhost:8080\r\nConnection: keep-alive\r\nPragma: no-cache\r\nCache-Control: no-cache\r\nsec-ch-ua: " Not A;Brand";v="99", "Chromium";v="98", "Google Chrome";v="98"\r\nsec-ch-ua-mobile: ?0\r\nsec-ch-ua-platform: "Windows"\r\nDNT: 1\r\nUpgrade-Insecure-Requests: 1\r\nUser-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/98.0.4758.102 Safari/537.36\r\nAccept: text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9\r\nSec-Fetch-Site: none\r\nSec-Fetch-Mode: navigate\r\nSec-Fetch-User: ?1\r\nSec-Fetch-Dest: document\r\nAccept-Encoding: gzip, deflate, br\r\nAccept-Language: en-US,en;q=0.9\r\n\r\n'
   # request = Request(sample_GET_request)
    sample_htmlform_request = b'POST /image-upload HTTP/1.1\r\nHost: localhost:8080\r\nConnection: keep-alive\r\nContent-Length: 287\r\nPragma: no-cache\r\nCache-Control: no-cache\r\nsec-ch-ua: " Not A;Brand";v="99", "Chromium";v="98", "Google Chrome";v="98"\r\nsec-ch-ua-mobile: ?0\r\nsec-ch-ua-platform: "Windows"\r\nOrigin: http://localhost:8080\r\nUpgrade-Insecure-Requests: 1\r\nDNT: 1\r\n'
    sample_htmlform_request += b'Content-Type: multipart/form-data; boundary=----WebKitFormBoundaryam94SD6c9rqAs6td\r\nUser-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/98.0.4758.102 Safari/537.36\r\nAccept: text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9\r\nSec-Fetch-Site: same-origin\r\nSec-Fetch-Mode: navigate\r\nSec-Fetch-User: ?1\r\nSec-Fetch-Dest: document\r\nReferer: http://localhost:8080/\r\nAccept-Encoding: gzip, deflate, br\r\nAccept-Language: en-US,en;q=0.9'
    sample_htmlform_request += b'\r\n\r\n------WebKitFormBoundaryam94SD6c9rqAs6td\r\nContent-Disposition: form-data; name="comment"\r\n\r\nhey\r\n------WebKitFormBoundaryam'
 #   request = Request(sample_htmlform_request)
    pass 