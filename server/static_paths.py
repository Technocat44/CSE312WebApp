
from server.router import Route
from server.response import generate_response, redirect
from server.template_engine import render_template
import server.database as db
import json
from os.path import exists
"""
This method creates a Route object. A route object has a 
    -method >>> the request method such as GET, or POST
    -path   >>> the route the request wants
    -action >>> the callback function to handle the specific route
"""
captionList = []
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
    # message = [{"comment": "Whats up", "upload": "", "image_n": "kitten.jpg"},
    #             {"comment": "nothing much", "upload":"", "image_n": "elephant.jpg"},
    #             {"comment": "very cool", "upload": "", "image_n": "eagle.jpg"},
    #             {"comment": "wow", "upload": "", "image_n" : "dog.jpg"}]

    #### i think I have to json dumps
    message = db.list_all_comments()
    # creating a simple list for demoing purposes, need to set this up in my database
   # captionList.append({"comment" :request.parts.get(b"comment", b""),"upload" :request.parts.get(b"upload", b"")})
    content = render_template("static/index.html",{"loop_data": message} )
    res = generate_response(content.encode(), "text/html; charset=utf-8", "200 OK")
    handler.request.sendall(res)
   #TODO: set this back once I am done demoing send_file(content.encode(), "text/html; charset=utf-8", request, handler)
  #  send_file("static/index.html", "text/html; charset=utf-8", request, handler)

def js(request, handler):
    send_file("static/functions.js", "text/javascript; charset=utf-8", request, handler) 

def style(request, handler):
    send_file("static/style.css", "text/css; charset=utf-8", request, handler)

def image(request, handler):
    print("\n\n\n\n\n\n\n")
    print("image callback initiated, ++++++++++++++++++++++++++++++++++++++")
    path_prefix = "/image/"
    # we are looking for the first instance of the /image/ tag in the path,  
    image_name = request.path[request.path.find(path_prefix)+len(path_prefix):]
    # can create a list of all valid file names and use that to check against to ensure no one trys hacking. Store the list
    # in the db and only add files that are uploaded. 
    # if image_name not in db list:
        # send a 404
    valid_mime_types = {"jpg": "jpeg", "png": "png", "ico":"ico", "default": "jpeg", }
  
    """
    If you want it to be dynamic, I would store a mapping of file extensions to MIME types and have a
        default MIME type if the extension is not in your mapping. 
    """
    # replacing the "/" in an image name prevents attackers from navigating your directory 
    image_name = image_name.replace("/", "")
    find_extension = image_name.find(".")
    extension = image_name[find_extension+1:]
    print ('this is the extension ', extension)
    if extension in valid_mime_types:
        file_extension = valid_mime_types[extension]
        new_image_name = image_name
    else:
        file_extension = valid_mime_types["default"]
        new_image_name = image_name[:find_extension] + "." + file_extension

    print ("new image name: ", new_image_name)
    # checks if the file path is valid before trying to open and read it
    file_exist = exists('static/image/' + new_image_name)
    if file_exist:
        send_file('static/image/' + new_image_name, f"image/{file_extension}", request, handler)

# this handles the files in my static folder, such as images or index.html
def send_file(filename, mimetype, request, handler):
    with open(filename, "rb") as content:
        body = content.read()
        response = generate_response(body, mimetype, '200 OK')
        handler.request.sendall(response)



  