
from server.router import Route
from server.response import generate_cookie_response, generate_response, redirect
from server.template_engine import render_template
import server.database as db
import json
from os.path import exists
import bcrypt

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
    """
    TODO: Create a cookie
    Headers:
    Set-Cookie: (used by server)
        Use this header in the HTTP response to tell the client to set cookie
        Syntax: <key>=<value>
        Example:
            Set-Cookie: id=Ky73vchyu7d
            Set-Cookie: visits=4
        We are telling the client "hey set this cookie so when you make another request I can check it"
        The browser then saves the cookie on that client's machine and every request after that they set those cookies 
        in the next request to the server
        

    Cookie: (used by client)
        Header used by clients to deliver all cookies that have been set
        Syntax: <key>=<value>
            All cookies in one header, with multiple cookies separated by ;
        Example:
            Cookie: id=Ky73vchyu7d; visits=4
    
    Set the directive for Expired to be longer than an hour
    
    """
 

    print("hey we're home")
    # message = [{"comment": "Whats up", "upload": "", "image_n": "kitten.jpg"},
    #             {"comment": "nothing much", "upload":"", "image_n": "elephant.jpg"},
    #             {"comment": "very cool", "upload": "", "image_n": "eagle.jpg"},
    #             {"comment": "wow", "upload": "", "image_n" : "dog.jpg"}]
  
    #### i think I have to json dumps
    message = db.list_all_comments()
    # creating a simple list for demoing purposes, need to set this up in my database
   # captionList.append({"comment" :request.parts.get(b"comment", b""),"upload" :request.parts.get(b"upload", b"")})
    
    # this is grabbing the number of visits a user visited our page
    num_visits = verify_if_visits_cookies_in_headers(request)

    content = render_template("static/index.html",{"loop_data": message}, num_visits )
    res = generate_cookie_response(content.encode(), "text/html; charset=utf-8", "200 Ok", num_visits)

        
    # res = generate_response(content.encode(), "text/html; charset=utf-8", "200 OK")
    handler.request.sendall(res)
   #TODO: set this back once I am done demoing send_file(content.encode(), "text/html; charset=utf-8", request, handler)
  #  send_file("static/index.html", "text/html; charset=utf-8", request, handler)


# this function verifies if the Cookie header exist, and if it does it returns the visits cookie value
def verify_if_visits_cookies_in_headers(request):
    print("entering the verify cookie function", flush=True)
    numberOfVisits = 0
    #TODO: check request.headers for the cookie
    verify_cookie_in_headers = request.headers.get("Cookie")
    if verify_cookie_in_headers != -1:
        cookies = request.headers["Cookie"]
        cookieList = cookies.split(";") if ";" in cookies else []
        if len(cookieList) > 0:
            for cookies in cookieList:
                if cookies.startswith("visits"):
                    print("YES the cookie does exist!" ,flush = True)
                    equalsIndex = cookies.find("=")
                    numberOfVisits = cookies[equalsIndex:]
                    numberOfVisits = int(numberOfVisits) + 1
                    return numberOfVisits
    # if we never return, we know the cookie doesn't exist yet
    print("Nope the cookie does not exist", flush=True)
    numberOfVisits = 1
    return numberOfVisits

def js(request, handler):
    send_file("static/functions.js", "text/javascript; charset=utf-8", request, handler) 

def style(request, handler):
    send_file("static/style.css", "text/css; charset=utf-8", request, handler)

def image(request, handler):
#    print("\n\n\n\n\n\n\n")
 #   print("image callback initiated, ++++++++++++++++++++++++++++++++++++++")
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
 #   print ('this is the extension ', extension)
    if extension in valid_mime_types:
        file_extension = valid_mime_types[extension]
        new_image_name = image_name
    else:
        file_extension = valid_mime_types["default"]
        new_image_name = image_name[:find_extension] + "." + file_extension

 #   print ("new image name: ", new_image_name)
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

# this is going to generate an xsrf token on page load and insert it into the html form and store it in the db
# def generateXSRFToken():
#     token = secrets.token_urlsafe(15)
#     db.store_xsrf_token(token)
#     newTemplate = insert_token(token) # this function is from template_engine and adds the token to the page
#     return newTemplate

  