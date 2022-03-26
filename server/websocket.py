from server.router import Route
from server.request import Request
import hashlib
import base64



def add_paths(router):
    router.add_route(Route('GET', '/websocket', handshake))

# example key                       Sec-WebSocket-Key: 25dJisszYN+6UXLJCSqTEw==
# example of proper response key:   sec-websocket-accept: vdlhb7ci/qt6pmGqd9J31pZtxss=
def handshake(request, handler):
    print("we have entered the websocket \n")
    res = generate_websocket_response(b"","text/plain; charset=utf-8",'101 Switching Protocols', request)
    print("this is response for websocket >>>>>>>>>>>>>>>>>>>>: ", res)
    handler.request.sendall(res)



def generate_websocket_response(body, content_type, response_code, request):
    r = b'HTTP/1.1 ' + response_code.encode()
    r += b'\r\nContent-Length: ' + str(len(body)).encode() 
    r += b'\r\nContent-Type: ' + content_type.encode()
    r += b'\r\nX-Content-Type-Options: nosniff'
    r += b'\r\nConnection: Upgrade'
    r += b'\r\nUpgrade: websocket'
    r += generate_sha(request)
    r += b'\r\n\r\n'
    return r

def generate_sha(request):
    request_key = request.headers["Sec-WebSocket-Key"]
    full_hash_key = request_key + "258EAFA5-E914-47DA-95CA-C5AB0DC85B11"  
    hash_object = hashlib.sha1(full_hash_key.encode()).hexdigest()
    hashy = base64.b64encode(bytes.fromhex(hash_object)).decode()
    rethash = b"\r\nSec-WebSocket-Accept: " + hashy.encode()
    return rethash

  