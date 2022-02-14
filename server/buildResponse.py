import osHandlers
import os

def buildHTMLResponse(mimetype, fileName):
    with open(os.path.join(osHandlers.addForwardSlash(os.getcwd() + f"/static/{fileName}"))) as f:
        serve = f.read()
        print(serve)
        print("Content-Length:", len(serve))

    response = "HTTP/1.1 200 OK\r\n"
    response += f"Content-Length: {str(len(serve))}\r\n"
    response += "X-Content-Type-Options: nosniff\r\n"
    response += f"Content-Type: {mimetype}; charset=utf-8\r\n"  
    response += '\r\n'
    response += serve
    # print(response)
    # print("From the HTML response\n")
    return response

def buildNonASCIIResponse(mimetype, filename):
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



def build200Response(mimeType, content):
    r = buildBasicResponse("200 OK",mimeType, content)
    return r

def build404Response(mimeType, content):
    r = buildBasicResponse("404 Not Found", mimeType, content)
    return r

def build301Response(location):
    response = "HTTP/1.1 301 Moved Permanently\r\n"
    response += "Content-Length: 0\r\n"
    response += f"Location: http://localhost:8080{location}\r\n\r\n"
    return response

def buildBasicResponse(code, mimeType, content):
    print("OHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHH")
    response = f"HTTP/1.1 {code}\r\n"
    response += f"Content-Type: {mimeType}\r\n"
    response += "X-Content-Type-Options: nosniff\r\n"
    response += f"Content-Length: {str(len(content))}\r\n"
    response += "\r\n"
    response += content
    return response