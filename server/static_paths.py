
from server.router import Route
from server.response import generate_response, redirect

"""
This method creates a Route object. A route object has a 
    -method >>> the request method such as GET, or POST
    -path   >>> the route the request wants
    -action >>> the callback function to handle the specific route
"""

# this method replaces the if-else
def add_paths(router):
    router.add_route(Route('GET', "/hi", hi))
    router.add_route(Route('GET', "/hello", hello))
    router.add_route(Route('GET', "/functions.js", js))
    router.add_route(Route('GET', "/style.css", style))
    router.add_route(Route('GET', "/image/.", image))
    router.add_route(Route('GET', "/.", four_oh_four))
    router.add_route(Route('GET', "/", home))
 
def four_oh_four(request, handler):
    r = generate_response(b"Page does not exist","text/plain; charset=utf-8", "404 Not Found")
    handler.request.sendall(r)

def hi(request, handler):
    r = redirect("/hello")
    handler.request.sendall(r)

def hello(request, handler):
    r = generate_response(b"Hello there", "text/plain; charset=utf-8", "200 OK")
    print("this is the reponse", r)
    handler.request.sendall(r)

def home(request, handler):
    send_file("static/index.html", "text/html; charset=utf-8", request, handler)

def js(request, handler):
    send_file("static/functions.js", "text/javascript; charset=utf-8", request, handler) 

def style(request, handler):
    send_file("static/style.css", "text/css; charset=utf-8", request, handler)

def image(request, handler):
    path_prefix = "/image/"
    # we are looking for the first instance of the /image/ tag in the path,  
    image_name = request.path[request.path.find(path_prefix)+len(path_prefix):]
    image_name = image_name.replace("/", "")
    send_file('static/image/' + image_name, "image/jpg", request, handler)

# this handles the files in my static folder, such as images or index.html
def send_file(filename, mimetype, request, handler):
    with open(filename, "rb") as content:
        body = content.read()
        response = generate_response(body, mimetype, '200 OK')
        handler.request.sendall(response)

  