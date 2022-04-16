
import secrets
import os
import server.database as db
from server.router import Route
from server.response import generate_cookie_response, generate_response, redirect
from server.request import Request, sendBytes, formParser
#from server.request import formParser
import bcrypt
from server.auth import check_password_match_and_length
from server.static_paths import verify_if_visits_cookies_in_headers
from server.template_engine import render_template

def add_paths(router):
    router.add_route(Route('POST', '/image-upload', parseMultiPart))
    router.add_route(Route('POST', "/register", parseRegistration))
    router.add_route(Route('POST', '/login', parseLogin))

def parseLogin(request, handler):
    print("I am inside of parseLogin")
    bytesFromForm = sendBytes()
    formParser(bytesFromForm, 0, request.login, request.headers)
    print(request.login, "$$$$$$$$$$$$$$$$$$$$$$$$$$$$login dictionary$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$")
    r = redirect("/")
    handler.request.sendall(r)

def parseRegistration(request, handler):
    print("i am inside of parseRegistration")
    bytesFromFile = sendBytes()
    formParser(bytesFromFile, 0, request.register, request.headers)
    print(request.register, '##########################register dictionary#####################################')
    """
    1. validate password matches
    1. generate some salt
    
    """
    """
        if password_match is -1 password is less than 8 characters try again
        if password_match is 0 we know they are trying to register but the passwords dont match
        if password_match is 1 we know they are trying to register and the passwords match!
    """
 
    # I have to store the registered dictionary in the database otherwise it disappears on a redirect
    password_match = check_password_match_and_length(request.register[b"password1"], request.register[b"password2"])
    if password_match == 0 or password_match == -1:
        """
        we need to render the homepage from html_paths because the registration dict only exist in this instance, if 
        we redirect the dictionary disappears.
        """
        message = db.list_all_comments()
        # this is grabbing the number of visits a user visited our page
        num_visits = verify_if_visits_cookies_in_headers(request)
        # means it wasn't a matching password
        # want to render the home page with a passwords do not match warning
        # render template and generate_cookie_response
        content = render_template("static/index.html",{"loop_data": message}, num_visits, password_match )
        res = generate_cookie_response(content.encode(), "text/html; charset=utf-8", "200 Ok", num_visits)
        handler.request.sendall(res)
    elif password_match == 1:
        # means it was a matching password so continue processing
        pass

    r = redirect("/")
    handler.request.sendall(r)

def parseMultiPart(request, handler):
    print('\n\n\n\n\n')
    print("I am inside the html_paths file, testing what my all_bytes_from_file produces")
    bytesOfFile = sendBytes()
    print("This is the length of all the bytes in the file: ", len(bytesOfFile) )
    print("this is the type of bytes in the dict >>>>>>>>>>>>>>>>>>>>>>>>>", type(bytesOfFile))
    formParser(bytesOfFile, 0, request.parts, request.headers)
    # this dynamically adds the dictionary from the formParser to the object we are passing around. 
    # very cool
    print(request.parts, '@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@\n\n')


    # retrieve created tokens from the db, check to verify if the xsrf_token is in the request.parts dictionary.
    # if it is, great we continue processing the request, if not, we send a 403 forbidden response
    checker = token_checker(request, handler)
    print("this is what checker returns " , checker)
    if checker == 0:
        r = redirect("/")
        handler.request.sendall(r)
           

    # TODO: Now I have to add these parts from the dictionary to the HTML template 
    commentFromUser = escape_html(request.parts[b"comment"].decode())
    imageUploaded = request.parts[b"upload"] # don't EVER decode this
    # TODO: Add the commentFromUser to the database and store the filename associated with the comment if possible
    # TODO: Store the file on my server somewhere. I will have to open the file and write it to disk. Also have to design a naming convention
    randomNameOfImage = request.parts.get(b"fileName", 0)
    """
    store the image file name in the db. ### need to add the .jpg to the end for easier lookup once retrieved from db
    link it to the comment.

    for ex:
        {"comment" : "check out my pic", "imageName" : "ACoolPicture00dankv3i5n4"}
        {"comment" : "hey" , "imageName" : "" }
    """
    print("this is the nameOfOGImage: This should be the name if there is a file name, should be 0 if there isn't",randomNameOfImage)
    if randomNameOfImage == 0:
        db.store_comment_only(commentFromUser)
        r = redirect("/")
        handler.request.sendall(r)
    else:
        side_effect_randomNameMix = storeImageUpload(imageUploaded, randomNameOfImage)
        # do the work for the database here as well then to ensure the comment has an image
        db.store_comment_and_image(commentFromUser, side_effect_randomNameMix)
        r = redirect("/")
        handler.request.sendall(r)

def escape_html(hacker):
    return hacker.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')


# this function will take the bytes of an image, and the name of the file given by the user. 
# it generates a random token and concats that to the filename given by the user. 
# then it stores the image in the server (on disk) 
# it also returns the random name it generated as a STRING .
# For example:
#        -user uploads a file named "ACoolPicture.jpg"
#        -the return value after this function call will be ACoolPictureji3uf8^7n
def storeImageUpload(image, nameOfOG):
    print("hey we are inside the storeImageUpload XXXXXXXXXXXXXXXXXXXXXXXXXXX")
    # naming convention
    randomName = secrets.token_urlsafe(7)
    randomNameMix = nameOfOG.decode() + randomName   
    with open(os.path.join(os.getcwd() + f"/static/image/{randomNameMix}.jpg"), "wb") as out_file:
        out_file.write(image)
        out_file.close()
    return randomNameMix + ".jpg"

# def randomNameForImages():
#     # TODO: import secrets and create a random name for an image concatenated with the file upload name. This way
#     # I cam safley store the file on disk and not risk it being the same name, and I can then still read the file name and
#     # know what image it is. 
#     rand_token = secrets.token_urlsafe(7)
#     print("this is the randomtoken :", rand_token)
#     return rand_token

 

def token_checker(request, handler):
    tokenList = db.verify_tokens()
    print("&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&")
    print(tokenList)
    tokenCheck = request.parts.get(b"xsrf_token", 0)
    if tokenCheck == 0:
        return 0
    for tokenDict in tokenList:
        print("Token dict, ", tokenDict)
        print("token from request , ", tokenCheck.decode())
        if tokenCheck.decode() in tokenDict.values():
            return 1
    print("Nope not in here")
    response = generate_response(b"Forbidden. You do not have access. Submission denied.", 'text/plain; charset=utf-8', '403 Forbidden')
    handler.request.sendall(response)
    return 0

