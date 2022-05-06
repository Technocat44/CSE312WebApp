
import secrets
import os
import server.database as db
from server.router import Route
from server.response import generate_visit_cookie_response, generate_response, redirect, generate_auth_token_cookie_response
from server.request import Request, sendBytes, formParser
#from server.request import formParser
import bcrypt
from server.auth import check_password_match_and_length, generateSalt, generate_new_hashed_password_with_salt, store_auth_token_auth,\
store_user_and_password, find_user_in_collection, generate_auth_token, generate_hash_for_auth_token
from server.static_paths import verify_if_visits_cookies_in_headers, verify_if_signin_cookie_exist
from server.template_engine import render_template
# from server.static_paths import logged_in_auth_tokens


# I should store a dictionary with keys of the client address and the values as the username and to compute the
# username I could create a collection in the database that stores the username and auth token .
#   So I retrieve the username via the authtoken and then I use that username if it matches the current client address...
#
#
def add_paths(router):
    router.add_route(Route('POST', '/image-upload', parseMultiPart))
    router.add_route(Route('POST', "/register", parseRegistration))
    router.add_route(Route('POST', '/login', parseLogin))

def parseLogin(request, handler):
    print("I am inside of parseLogin")
    bytesFromForm = sendBytes()
    formParser(bytesFromForm, 0, request.login, request.headers)
    print(request.login, "$$$$$$$$$$$$$$$$$$$$$$$$$$$$login dictionary$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$")

    usernameLogin = request.login[b"userName"]
    passwordLogin = request.login[b"password"]
    user = request.login[b"userName"].decode()
    escapedUser = escape_html(user)
    # find username in database
    user = find_user_in_collection(escapedUser.encode())
    message = db.list_all_comments()
    # this is grabbing the number of visits a user visited our page
    num_visits = verify_if_visits_cookies_in_headers(request)
    print("type of the mongo db user ", type(user), "this is the user: ", user)
    if user:
        # user doesn't exist
        print("user does exist")
        # take the userDict and parse out the salt, and hashedpassoword
        # salt the login password and if it matches the hashed password they verified who they are!
        saltFromDb = user["salt"]
        print("this is the salt from the database: ", saltFromDb)
        print("the type of the password from login ")
        verifyHashedSaltPassword = generate_new_hashed_password_with_salt(saltFromDb, passwordLogin)
        print("thi sis the verify hashed salted password: ", verifyHashedSaltPassword)
        if verifyHashedSaltPassword == user["password"]:
            # this is the correct person!
            print("yes the registered user logged in correctly!!!!!!!!!")
            # now create an authentication token
            auth_token = generate_auth_token()
            print("this is the auth_token generated: ", auth_token, type(auth_token))
            # store auth_token in db as a hash, use auth_token as a cookie.
            hashed_auth_token = generate_hash_for_auth_token(auth_token)
            print("this is the hash_auth_token: ", hashed_auth_token, type(hashed_auth_token))
            """
            I hashed the authtoken and sent it to the database with the username
            When a user has an auth_token cookie, I will throw it at the generate_hash_for_auth_token
            and verify that the tokens match, if they do, I will grab the username and set it to the html template
            """
            store_auth_token_auth(hashed_auth_token.encode(), usernameLogin)
            # set the auth_token cookie:

            password_match = 1

            # logged_in_auth_tokens["auth_token"] = auth_token
            # logged_in_auth_tokens["user"] = usernameLogin

          
            # means it wasn't a matching password
            # want to render the home page with a passwords do not match warning
            # render template and generate_cookie_response
            content = render_template("static/index.html",{"loop_data": message}, num_visits, password_match, usernameLogin)
            res = generate_auth_token_cookie_response(content.encode(), "text/html; charset=utf-8", "200 Ok", num_visits, auth_token)
            handler.request.sendall(res)
            
        else:
            password_match = 0
            content = render_template("static/index.html",{"loop_data": message}, num_visits, password_match, username=None)
            res = generate_visit_cookie_response(content.encode(), "text/html; charset=utf-8", "200 Ok", num_visits)
            handler.request.sendall(res)
    else:
        password_match = -1
        content = render_template("static/index.html",{"loop_data": message}, num_visits, password_match, username=None)
        res = generate_visit_cookie_response(content.encode(), "text/html; charset=utf-8", "200 Ok", num_visits)
        handler.request.sendall(res)

            


def parseRegistration(request, handler):
    print("i am inside of parseRegistration")
    bytesFromFile = sendBytes()
    formParser(bytesFromFile, 0, request.register, request.headers)
    print(request.register, '##########################register dictionary#####################################')
    """
    1. validate password matches
    1. generate some salt
    
    """
    message = db.list_all_comments()
    # this is grabbing the number of visits a user visited our page
    num_visits = verify_if_visits_cookies_in_headers(request)
    """
        if password_match is -1 password is less than 8 characters try again
        if password_match is 0 we know they are trying to register but the passwords dont match
        if password_match is 1 we know they are trying to register and the passwords match!
    """
    password_match = check_password_match_and_length(request.register[b"password1"], request.register[b"password2"])
    if password_match == 0 or password_match == -1:
        """
        we need to render the homepage from html_paths!!!! because the registration dict only exist in this instance, if 
        we redirect the dictionary disappears.
        If the sign-up username and password has any errors we do not store anything in the database

        We render the homepage again but with a message letting the user know what they need to change 

        """
        message = db.list_all_comments()
        # this is grabbing the number of visits a user visited our page
        num_visits = verify_if_visits_cookies_in_headers(request)
        # means it wasn't a matching password
        # want to render the home page with a passwords do not match warning
        # render template and generate_cookie_response
        content = render_template("static/index.html",{"loop_data": message}, num_visits, password_match, username=None )
        res = generate_visit_cookie_response(content.encode(), "text/html; charset=utf-8", "200 Ok", num_visits)
        handler.request.sendall(res)
    elif password_match == 1:
        # means it was a matching password so continue processing, we are going to hash and salt the password and store 
        # the username with the hashed password and the salt in the db.
        """
        Go to auth.py file to create these hashes and salt
        1. generate some salt from bcrypt
        2. hash the password 
        • Randomly generate salt, appended to password
        • Hash the salted password
        """
        user = request.register[b"userName"].decode()
        escapedUser = escape_html(user)
       
        salt = generateSalt()
        print("this is the random salt: ", salt)
        hashedSaltedPassword = generate_new_hashed_password_with_salt(salt, request.register[b"password1"])
        print("this is the hashed salted password: ", hashedSaltedPassword)
        store_user_and_password(hashedSaltedPassword, escapedUser.encode(), salt)
        signedUp = 2
        # I could create a signup cookie that saves the state that the user signed up. it would only happen in this func
        content = render_template("static/index.html",{"loop_data": message}, num_visits, password_match, username=None )
        res = generate_visit_cookie_response(content.encode(), "text/html; charset=utf-8", "200 Ok", num_visits)
        handler.request.sendall(res)

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

