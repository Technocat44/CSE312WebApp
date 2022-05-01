
def generate_response(body: bytes, content_type: str = 'text/plain; charset=utf-8', response_code: str = '200 OK'):
    r = b'HTTP/1.1 ' + response_code.encode()
    r += b'\r\nContent-Length: ' + str(len(body)).encode() 
    r += b'\r\nContent-Type: ' + content_type.encode()
    r += b'\r\nX-Content-Type-Options: nosniff'
    r += b'\r\n\r\n'
    r += body
    return r

def generate_visit_cookie_response(body, content_type, response_code, num_visits) -> bytes:
    r = b'HTTP/1.1 ' + response_code.encode()
    r += b'\r\nContent-Length: ' + str(len(body)).encode() 
    r += b'\r\nContent-Type: ' + content_type.encode()
    r += b'\r\nSet-Cookie: ' + b'visits=' + f'{num_visits}'.encode()
    r += b'\r\nSet-Cookie: ' + b';Max-Age=7200'
    r += b'\r\nX-Content-Type-Options: nosniff'
    r += b'\r\n\r\n'
    r += body
    return r

def generate_auth_token_cookie_response(body, content_type, response_code, num_visits, auth_token, path) -> bytes:
    r = b'HTTP/1.1 ' + response_code.encode()
    r += b'\r\nContent-Length: ' + str(len(body)).encode() 
    r += b'\r\nContent-Type: ' + content_type.encode()
    r += b'\r\nSet-Cookie: ' + b'visits=' + f'{num_visits}'.encode() + b';Max-Age=7200' 
    r += b'\r\nSet-Cookie: ' + b'auth_token=' + f'{auth_token}'.encode() + b';Max-Age=7200' + b';HttpOnly'
    r += b'\r\nLocation: ' + path.encode()
    r += b'\r\nX-Content-Type-Options: nosniff'
    r += b'\r\n\r\n'
    r += body
    return r

def redirect(path: str):
    r = b'HTTP/1.1 301 Moved Permanently'
    r += b'\r\nContent-Length: 0'
    r += b'\r\nLocation: ' + path.encode()
    r += b'\r\n\r\n'
    return r