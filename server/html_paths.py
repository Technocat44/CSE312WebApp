
import os
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
    # print("this is type of bytes in file after cast >>>>>>>>>>>>>>>>>>>>>>", type(int(bytesOfFile)))
 #   print("this is the bytes accumulated from the file upload, the body of the request >>> ", bytesOfFile)
   # print("this is me combining the bytes accumulated from going back to socket over and over, and the initial body recevied", request.body + bytesOfFile["bytes"])
    # contains the mutliparts of the request
    formParser(bytesOfFile, 0, request.parts, request.headers)
    # this dynamically adds the dictionary from the formParser to the object we are passing around. 
    # very cool
    print(request.parts, '@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@\n\n')

    # TODO: Now I have to add these parts from the dictionary to the HTML template 
    commentFromUser = escape_html(request.parts[b"comment"].decode())
    imageUploaded = request.parts[b"upload"] # don't EVER decode this
    # TODO: Add the commentFromUser to the datbase and store the filename associated with the comment if possible
    # TODO: Store the file on my server somewhere. I will have to open the file and write it to disk. Also have to design a naming convention
    print("image uploaded XXXXXXXXXXXXXXXXXXXXXXXX ", imageUploaded)
    # if a user only writes in a comment I don't want to accidently write an empty image
    if imageUploaded != b"":
        print("hey we entered the if to check if the image has a bytes in it XXXXXXXXXXXXXXXXXXXXXXXXXXXXX")
        storeImageUpload(imageUploaded)

    r = redirect("/")
    handler.request.sendall(r)

def escape_html(hacker):
    return hacker.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')



def storeImageUpload(image):
    print("hey we are inside the storeImageUpload XXXXXXXXXXXXXXXXXXXXXXXXXXX heres the imageID :", imageID)
    # naming convention
    imageID += 1
    print(imageID)
    filePath = f"static/image/image{imageID}.jpg"
    print("filepath: ",filePath)
    with open(f"static/image/image{imageID}.jpg", "wb") as out_image:
        print(out_image)
        out_image.write(image)
        print("the write out put ",out_image.write(image))
        out_image.close()

def randomName():
    # TODO: improt secrets and create a random name for an image concatenated with the file upload name. This way
    # I cam safley store the file on disk and not risk it being the same name, and I can then still read the file name and
    # know what image it is. 
    return 0