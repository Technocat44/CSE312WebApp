import osHandlers
import os

# TODO: need to abstract this huge function like i did with the static responses
# break it up to build littler response: might even be able to use the buildStaticResponse function 
# in the server just simply call a catch-all buildDynamic Response
# once in here then read it by the file type
# 
def openFile(fileName:str, readType:str):
    with open(os.path.join(osHandlers.addForwardSlash(os.getcwd() + f"/static/{fileName}")), readType) as f:
        serveStrOrBytes = f.read()
        print("Content-Length:", len(serveStrOrBytes))
        return serveStrOrBytes

# def buildHTMLResponse(mimetype:str, fileName:str):
#     content = ""
#     if (fileName.startswith("/image")):
#         content = openFile(fileName, "rb")
#     else:
#         content = openFile(fileName, 'r')
#     r = buildStaticResponse("200 OK",mimetype,content)
#     # response = "HTTP/1.1 200 OK\r\n"
#     # response += f"Content-Length: {str(len(content))}\r\n"
#     # response += "X-Content-Type-Options: nosniff\r\n"
#     # response += f"Content-Type: {mimetype}; charset=utf-8\r\n"  
#     # response += '\r\n'
#     if (fileName.startswith("/image")):
#         # we encode the http response first, then simply concatenate the bytes of the file and return it
#         r = r.encode()
#         r += content
#         return r
#     r += content
#     # print(response)
#     # print("From the HTML response\n")
#     return r
# buildNonASCIIResponse("text/html; charset=utf-8", "index.html")
def buildIndexHTMLResponse():
    content = openFile("index.html", "rb")
    r = buildStaticResponse("200 OK", "text/html; charset=utf-8", content)
    r = r.encode()
    r += content
    return r

# buildHTMLResponse("text/css; charset=utf-8 ", "style.css" )
def buildCSSResponse():
    content = openFile("style.css", "r")
    r = buildStaticResponse("200 OK", "text/css; charset=utf-8", content)
    r += content
    return r.encode()

# buildNonASCIIResponse("application/javascript; charset=utf-8", "functions.js")
def buildFunctionJSResponse():
    content = openFile("functions.js", "rb")
    print("THIS IS MY JS CONTENT returned from the open file function: ", content )
    print("\n\n")
    r = buildStaticResponse("200 OK", "text/javascript; charset=utf-8", content)
    print("AND THIS IS THE JS CONTENT AFTER WE buILD THE STATIC RESPONSE", r)
    r = r.encode()
    r += content
    print("\n\n")
    print("THIS IS THE CONTENT BEFORE IT GETS ENCODED : ", r)
    print("Double chekcing the content length: ", len(r))
    return r

def buildImageResponse(extension):
    fullNameOfFile = extension[-1].split(".") # this is a list made from the request_path split on the (.) ex: ["flamingo", "jpg"]
    filetype = fullNameOfFile[1] # we grab the 2nd element which is the filetype, such as .jpg or .png
    content = openFile("image/"+extension[-1], "rb") # extnsion[-1] = flamingo.jpg 
    r = buildStaticResponse("200 OK", f"image/{filetype}", content)
    r = r.encode() # we encode the string first to convert it to bytes
    r += content # then we concatenate the image with the byte string
    return r
# this method is for content types that have non-ASCII characters
# i.e. I need to open the file as bytes because its not a string
# def buildNonASCIIResponse(mimetype:str, filename:str):
#     print("mimetype, ",mimetype)
#     print("filename, ", filename)
#     with open(os.path.join(osHandlers.addForwardSlash(os.getcwd() + f"/static/{filename}")), "rb") as b: 
#         serveBytes = b.read()
#         print('BBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBB')
#     r = "HTTP/1.1 200 OK\r\n"
#     r += f"Content-Length: {str(len(serveBytes))}\r\n"
#     r += "X-Content-Type-Options: nosniff\r\n"
#     r += f"Content-Type: {mimetype}\r\n"  
#     r += '\r\n'
#     r = r.encode()
#     r += serveBytes    
#     return r


"""
could i refactor this? 
I could make the build response methods use a status code

"""
def buildStaticResponse(status_code:str, mimetype:str, content:str):
    response = f"HTTP/1.1 {status_code}\r\n"
    response += f"Content-Length: {str(len(content))}\r\n" # TODO: fix html with non asci
    if (status_code == "301 Moved Permanently"): # THIS is NOT the mimetype for 301 its actually the location 
        response += f"Location: http://localhost:8080{mimetype}\r\n\r\n"
    response += f"Content-Type: {mimetype}\r\n"
    response += "X-Content-Type-Options: nosniff\r\n"
    response += "\r\n"
    # this function returns most of the response, its up the the calling function to handle the body of the request and encode it
    return response

def build200Response():
    content = "Hello there"
    r = buildStaticResponse("200 OK","text/plain; charset=utf-8",content)
    r += content
    return r.encode()

def build301Response():
    r = buildStaticResponse("301 Moved Permanently" ,"/hello", "")
    return r.encode()

def build404Response():
    content = "Page Does Not Exist"
    r = buildStaticResponse("404 Not Found", "text/plain; charset=utf-8","")
    r += content
    return r.encode()
