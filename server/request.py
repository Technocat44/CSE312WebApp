from urllib import request


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

if __name__ == '__main__':
   # sample_GET_request = b'GET /hkgkg HTTP/1.1\r\nHost: localhost:8080\r\nConnection: keep-alive\r\nPragma: no-cache\r\nCache-Control: no-cache\r\nsec-ch-ua: " Not A;Brand";v="99", "Chromium";v="98", "Google Chrome";v="98"\r\nsec-ch-ua-mobile: ?0\r\nsec-ch-ua-platform: "Windows"\r\nDNT: 1\r\nUpgrade-Insecure-Requests: 1\r\nUser-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/98.0.4758.102 Safari/537.36\r\nAccept: text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9\r\nSec-Fetch-Site: none\r\nSec-Fetch-Mode: navigate\r\nSec-Fetch-User: ?1\r\nSec-Fetch-Dest: document\r\nAccept-Encoding: gzip, deflate, br\r\nAccept-Language: en-US,en;q=0.9\r\n\r\n'
   # request = Request(sample_GET_request)
    sample_htmlform_request = b'POST /image-upload HTTP/1.1\r\nHost: localhost:8080\r\nConnection: keep-alive\r\nContent-Length: 287\r\nPragma: no-cache\r\nCache-Control: no-cache\r\nsec-ch-ua: " Not A;Brand";v="99", "Chromium";v="98", "Google Chrome";v="98"\r\nsec-ch-ua-mobile: ?0\r\nsec-ch-ua-platform: "Windows"\r\nOrigin: http://localhost:8080\r\nUpgrade-Insecure-Requests: 1\r\nDNT: 1\r\nContent-Type: multipart/form-data; boundary=----WebKitFormBoundaryam94SD6c9rqAs6td\r\nUser-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/98.0.4758.102 Safari/537.36\r\nAccept: text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9\r\nSec-Fetch-Site: same-origin\r\nSec-Fetch-Mode: navigate\r\nSec-Fetch-User: ?1\r\nSec-Fetch-Dest: document\r\nReferer: http://localhost:8080/\r\nAccept-Encoding: gzip, deflate, br\r\nAccept-Language: en-US,en;q=0.9\r\n\r\n------WebKitFormBoundaryam94SD6c9rqAs6td\r\nContent-Disposition: form-data; name="comment"\r\n\r\nhey\r\n------WebKitFormBoundaryam'
    request = Request(sample_htmlform_request)
    pass 