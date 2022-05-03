
from server.router import Route
from server.response import generate_auth_token_cookie_response, generate_visit_cookie_response, generate_response, redirect
from server.template_engine import render_template
from server.auth import find_auth_token_in_collection
import server.database as db
import json
from os.path import exists
import bcrypt
from server.auth import check_password_match_and_length

old_clients = []
js_auth_token_intercept_dict = {}
"""
This method creates a Route object. A route object has a 
    -method >>> the request method such as GET, or POST
    -path   >>> the route the request wants
    -action >>> the callback function to handle the specific route
"""
# this method replaces the if-else
def add_paths(router):
    router.add_route(Route('GET', '/auth', auth))
    router.add_route(Route('GET', "/hi", hi))
    router.add_route(Route('GET', "/hello", hello))
    router.add_route(Route('GET', "/functions.js", js))
    router.add_route(Route('GET', "/style.css", style))
    router.add_route(Route('GET', "/image/.", image))
    router.add_route(Route('GET', "/.", four_oh_four))
    router.add_route(Route('GET', "/", home))
 
def auth(request, handler):
    send_file("static/login.html", "text/html; charset=utf-8", request, handler)
    

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
    signInCookieUserName =  verify_if_signin_cookie_exist(request) # have this return the username
    
    print("this is the signincookie username $$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$: ", signInCookieUserName)

    """
    When a user opens a new tab they should get a new client id:
    Idea here is, that if I open another tab I don't want to try to open the websocket and homepage right away
    and that happens if I authenticate a tab, and then try to open a second one.
    So what I am doing is saying hey you might have the same cookie because it is stored across the tabs
    But if youre a different client id, you can't get at the homepage. Unless they referesh, then the client id
    should be in the old_list and then they can break the socket but thats not a feature i need to worry about
    """
    # from app import clients
    # for client in clients:
    #     print("inside static: these are the clients in client list", client)
    #     if client not in old_clients:
    #         old_clients.append(client)
    #         re=redirect("/auth")
    # if signInCookieUserName == None:
    #     re = redirect("/auth")
    #     handler.request.sendall(re)
    # if the user just registered and sent in their info, password1 will be a key in the dictionary

    """
        if password_match is -1 password is less than 8 characters try again
        if password_match is 0 we know they are trying to register but the passwords dont match
        if password_match is 1 we know they are trying to register and the passwords match!
    """
    password_match = 1
    
    content = render_template("static/index.html",{"loop_data": message}, num_visits, password_match, signInCookieUserName)
    res = generate_visit_cookie_response(content.encode(), "text/html; charset=utf-8", "200 Ok", num_visits)
 
    
    # res = generate_response(content.encode(), "text/html; charset=utf-8", "200 OK")
    handler.request.sendall(res)
   #TODO: set this back once I am done demoing send_file(content.encode(), "text/html; charset=utf-8", request, handler)
  #  send_file("static/index.html", "text/html; charset=utf-8", request, handler)


# this function verifies if the Cookie header exist, and if it does it returns the visits cookie value
def verify_if_visits_cookies_in_headers(request) -> int:
    print("entering the verify cookie function", flush=True)
    numberOfVisits = 0
    #TODO: check request.headers for the cookie
    verify_cookie_in_headers = request.headers.get("Cookie", -1)
    print("the value of calling get on the headers dictionary : ",verify_cookie_in_headers)
    if verify_cookie_in_headers != -1:
        cookies = request.headers["Cookie"]
        print("this should be the cookie value from the headers dict : ", cookies)
        if ";" in cookies:
            cookieList = cookies.split(";")
            
            print("cookieList in verify visits cookie:  ", cookieList)
            for cookies in cookieList:
                cookies = cookies.strip()
                if cookies.startswith("visits"):
                    print("YES the cookie does contain a ;" ,flush = True)
                    equalsIndex = cookies.find("=")
                    numberOfVisits = cookies[equalsIndex + len("="):]
                    print("number of visits: ",numberOfVisits, flush=True)
                    numberOfVisits = int(numberOfVisits) + 1
                    return numberOfVisits
        elif ";" not in cookies:
            print("yes we have a cookie, here it is: " , cookies)
            equalsIndex = cookies.find("=")
            numberOfVisits = cookies[equalsIndex + len("="):]
            numberOfVisits = int(numberOfVisits) + 1
            return numberOfVisits            
    # if we never return, we know the cookie doesn't exist yet
    print("Nope the cookie does not exist", flush=True)
    numberOfVisits = 1
    return numberOfVisits

# this function verifies if the auth_token exist and if it does, we verify the token is valid,
#  then we return the name of the user
def verify_if_signin_cookie_exist(request):
    print("we are entering the verify_if_signin_cookie_exist", flush=True)
    verify_if_cookie_header_exist = request.headers.get("Cookie", -1)
    print("/inside static verifying if the cookie header exist: ", verify_if_cookie_header_exist)
    if verify_if_cookie_header_exist != -1:
        cookies = request.headers["Cookie"]
        if ";" in cookies:
            cookieList = cookies.split(";")
            print("cookieList in verify sign in cookie : ", cookieList)
            for cookies in cookieList:
                cookies = cookies.strip()
                if cookies.startswith("auth_token"):
                    equalsIndex = cookies.find("=")
                    auth_token = cookies[equalsIndex + len("="):]
                    # need to verify if the auth_token matches 
                    print("this is the auth_token parsed from the headers: ", auth_token, flush=True)
                    
                    user_or_none = find_auth_token_in_collection(auth_token)
                    print("user name after validating the auth token in db", user_or_none, flush=True)
                    if user_or_none != None:
                        # we have a valid auth token! 
                        print("we have a valid user, ", user_or_none, flush=True)
                        print("this is the user", user_or_none)
                        print("this is the auth_token", auth_token)
                        # if auth_token not in logged_in_auth_tokens:
                        #     logged_in_auth_tokens["user"] = user_or_none
                        #     logged_in_auth_tokens["auth_token"] = auth_token
                        #     print("in static paths verify cookie,this is logged in auth tokens dict", logged_in_auth_tokens)
                        return user_or_none
                    else:
                        # the auth_token does not match someone is trying to hack!
                        print("the auth_token does not match someone is trying to hack!")
                        return None
    else:
        # if there is not ; in the cookies, we know there is not auth_token as there has to be a visits cookie set 
        print("there was no auth token!PPPPPPPPPPPPPPPPPPPPPPPPPPPPP")
        return None


    
def js(request, handler):
    # this will be the first time the user is requesting this because the user has to login in first
    # meaning we can create a temporary dictionary that stores the username and password and will be erased after the 
    # websocket connection is established. 
    # the js request will have the auth_token set so we can grab it.
    #
    # if the dictionary has a username in it already, we want to clear it since this will be a new request for the user
    if js_auth_token_intercept_dict:
        js_auth_token_intercept_dict.clear()
    user_name_from_auth_cookie_intercept = verify_if_signin_cookie_exist(request)
    print("this is the user name from the auth_cookie intercepted", user_name_from_auth_cookie_intercept)
    js_auth_token_intercept_dict["username"] = user_name_from_auth_cookie_intercept

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

  