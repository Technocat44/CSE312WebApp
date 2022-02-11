import os

def addForwardSlash(aStr) :
    return aStr.replace(os.sep, "/")

path = os.getcwd()

newPath = addForwardSlash(path)
# print("new ",newPath, '\n')

os.chdir("C:/Users/north/CSE312/")
nPath = addForwardSlash(os.getcwd())

print("newPAth",nPath, "\n")

# os.makedirs('TestingDirectory/ImInside')
print("list directoy: ",os.listdir(), '\n')

# os.rmdir('TestingDirectory/ImInside')
# print(os.listdir(), '\n')

# with open(os.path.join(addForwardSlash(os.getcwd() + "/CSE312WebApp/static/index.html"))) as f:
#         serve = f.read()
#         print(serve)

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