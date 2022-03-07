

import server.database as db
from server.router import Route
from server.response import generate_response, redirect
from server.fileHandling import all_bytes_of_file, sendBytes
from server.request import Request
#from server.request import formParser


def add_paths(router):
    router.add_route(Route('POST', '/image-upload', parse))


def parse(request, handler):
    print('\n\n\n\n\n')
    print("I am inside the html_paths file, testing what my all_bytes_from_file produces")
    bytesOfFile = sendBytes()
    print("This is the length of all the bytes in the file: ", len(bytesOfFile) )
    print("this is the type of bytes in the dict >>>>>>>>>>>>>>>>>>>>>>>>>", type(bytesOfFile))
    # print("this is type of bytes in file after cast >>>>>>>>>>>>>>>>>>>>>>", type(int(bytesOfFile)))

    print("this is the bytes accumulated from the file upload, the body of the request >>> ", bytesOfFile)
   # print("this is me combining the bytes accumulated from going back to socket over and over, and the initial body recevied", request.body + bytesOfFile["bytes"])
    
    
    """
    After the headers are parsed, we need to take care of the multipart boundary. 
    It will be in the Content-Type header -->  Content-Type: multipart/form-data; boundary=
    the boundary will look like this -->       ----WebKitFormBoundaryam94SD6c9rqAs6td
    B/c reasons we need to find that and then add "--" another two dashes for the full boundary
    We are going to use that boundary to split() up the multi parts
        There might be some newline characters mixed in the edges so I might need to strip()

    The last boundary is "--" + <boundary> + "--" \r\n
        """
    # contains the mutliparts of the request
    bodyOfImage = bytesOfFile

    boundary = request.headers["Content-Type"]


    r = redirect("/")
    handler.request.sendall(r)



