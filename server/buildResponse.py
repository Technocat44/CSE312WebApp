import osHandlers
import os
import parse

# TODO: need to abstract this huge function like i did with the static responses
# break it up to build littler response: might even be able to use the buildStaticResponse function 
def buildHTMLResponse(mimetype:str, fileName:str):
    openFileWith = ""
    if (fileName.startswith("/image")):
        openFileWith = "rb"
    else:
        openFileWith = "r"
    with open(os.path.join(osHandlers.addForwardSlash(os.getcwd() + f"/static/{fileName}")), openFileWith) as f:
        serve = f.read()
        
        print("Content-Length:", len(serve))
    response = "HTTP/1.1 200 OK\r\n"
    response += f"Content-Length: {str(len(serve))}\r\n"
    response += "X-Content-Type-Options: nosniff\r\n"
    response += f"Content-Type: {mimetype}; charset=utf-8\r\n"  
    response += '\r\n'
    if (openFileWith == "rb"):
        response = response.encode()
        response += serve
        return response
    response += serve
    # print(response)
    # print("From the HTML response\n")
    return response

# this method is for content types that have non-ASCII characters
# i.e. I need to open the file as bytes because its not a string
def buildNonASCIIResponse(mimetype:str, filename:str):
    print("mimetype, ",mimetype)
    print("filename, ", filename)
    with open(os.path.join(osHandlers.addForwardSlash(os.getcwd() + f"/static/{filename}")), "rb") as b: # TODO: for images us "rb"
        serveBytes = b.read()
        print('BBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBB')
    r = "HTTP/1.1 200 OK\r\n"
    r += f"Content-Length: {str(len(serveBytes))}\r\n"
    r += "X-Content-Type-Options: nosniff\r\n"
    r += f"Content-Type: {mimetype}\r\n"  
    r += '\r\n'
    r = r.encode()
    r += serveBytes    
    return r


"""
could i refactor this? 
I could make the build response methods use a status code

"""
def buildStaticResponse(status_code:str, mimetype:str, content:str):
    response = f"HTTP/1.1 {status_code}\r\n"
    response += f"Content-Length: {str(len(content))}\r\n"
    if (status_code == "301 Moved Permanently"): # THIS is not the mimetype its actuall the location 
        response += f"Location: http://localhost:8080{mimetype}\r\n\r\n"
    response += f"Content-Type: {mimetype}\r\n"
    response += "X-Content-Type-Options: nosniff\r\n"
    response += "\r\n"
    response += content
    return response 

def build200Response():
    r = buildStaticResponse("200 OK","text/plain; charset=utf-8", "Hello there")
    return r

def build301Response():
    r = buildStaticResponse("301 Moved Permanently" ,"/hello", "")
    return r

def build404Response():
    r = buildStaticResponse("404 Not Found", "text/plain; charset=utf-8", "Page Does Not Exist")
    return r
