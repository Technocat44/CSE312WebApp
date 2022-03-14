import os

def addForwardSlash(aStr) :
    return aStr.replace(os.sep, "/")

path = os.getcwd()
print("current directory", path, '\n\n\n')

newPath = addForwardSlash(path)
# print("new ",newPath, '\n')

# os.chdir("home/jamesaqu/CSE312WebApp/static/")
# nPath = addForwardSlash(os.getcwd())

# print("newPAth",nPath, "\n\n\n")

# os.makedirs('TestingDirectory/ImInside')
print("list directoy: ",os.listdir(), '\n\n\n')

# os.rmdir('TestingDirectory/ImInside')
# print(os.listdir(), '\n')

import secrets



def randomNameForImages():
    # TODO: import secrets and create a random name for an image concatenated with the file upload name. This way
    # I cam safely store the file on disk and not risk it being the same name, and I can then still read the file name and
    # know what image it is. 
    rand_token = secrets.token_urlsafe(10)
    print("this is the randomtoken :", rand_token)
    return rand_token

def storeImageUpload(image, nameOfOG):
    print("hey we are inside the storeImageUpload XXXXXXXXXXXXXXXXXXXXXXXXXXX")
    # naming convention
    randomName = randomNameForImages()
    randomOGMix = nameOfOG.decode() + randomName  
    with open(os.path.join(os.getcwd() + f"/static/image/{randomOGMix}.jpg"), "wb") as out_file:
        out_file.write(image)
        out_file.close()

# with open(os.path.join(os.getcwd() + "/static/image/cat.jpg"), "rb") as f:
#     serve = f.read()
#     storeImageUpload(serve, b"CoolPicture")


"""
super important for finding the correct size of an image
"""
# print(os.stat('cat.jpg'))
# print(os.stat("cat.jpg").st_size)
# print(type(os.stat('cat.jpg').st_size))

# print('\n\n')
# for dirpath, dirnames, filenames in os.walk('C:/Users/north/CSE312/CSE312WebApp/src'):
#     print("Current path: ", dirpath)
#     print("Directories: ", dirnames)
#     print("Filenames: ", filenames)
#     print(" ")