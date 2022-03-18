
import secrets
import os
from xmlrpc.client import ResponseError
import server.database as db
from server.router import Route
from server.response import generate_response, redirect
from server.request import Request, sendBytes, formParser
#from server.request import formParser


def add_paths(router):
    router.add_route(Route('POST', '/image-upload', parseMultiPart))


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
        return 
           

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
    for tokenDict in tokenList:
        print("Token dict, ", tokenDict)
        print("token from request , ", tokenCheck.decode())
        if tokenCheck.decode() in tokenDict.values():
            return 1
    print("Nope not in here")
    response = generate_response(b"Forbidden. You do not have access. Submission denied.", 'text/plain; charset=utf-8', '403 Forbidden')
    handler.request.sendall(response)
    return 0