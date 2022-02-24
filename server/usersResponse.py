import buildResponse
import json
import database

def build201Response(length, body: str):
    response = buildUserResponse(length, "201 Created", "application/json")
    body_dict_with_id = createUser(body)
    # I am attaching a copy of the dictionary that was sent to the db as the response of the body
    response += body_dict_with_id 
    return response

def buildSingleUserResponse(idNumber):
    showSingleUser = database.list_one(idNumber)
    print("Show single user: ", showSingleUser)
    showSingleUserJsonBytes = json.dumps(showSingleUser).encode()
    print("This is the single user: ", showSingleUserJsonBytes)
    if showSingleUser == None:
        r = buildResponse.build404Response("User Does Not Exist")
        return r
    r = buildUserResponse(len(showSingleUserJsonBytes), "200 OK", "application/json")
    r += showSingleUserJsonBytes
    return r


def buildAllUsersResponse():
    # grab all users from db
    showAllUsers = database.list_all()
    print(f"here is the users from the db {showAllUsers}")
    # make the dictionary of users a json string and then encode it to make it a byte string
    userList = json.dumps(showAllUsers).encode()
    # take the length of the byte string
    userListLength = len(userList)
    response = buildUserResponse(userListLength, "200 OK", "application/json")
    response += userList
    return response
"""
  response = f"HTTP/1.1 {status_code}\r\n"
    response += f"Content-Length: {str(len(content))}\r\n"
    if (status_code == "301 Moved Permanently"): # THIS is NOT the mimetype for 301 its actually the location 
        response += f"Location: http://localhost:8080{mimetype}\r\n\r\n"
    response += f"Content-Type: {mimetype}\r\n"
    response += "X-Content-Type-Options: nosniff\r\n"
    response += "\r\n"
"""

def build404Response():
    content = "User Does Not Exist"
    r = buildUserResponse(len(content), "404 Not Found", "text/plain; charset=utf-8")
    r += content
    return r.encode()

# this method only works for body request that our strings!!! TODO: create a different response builder for images, etc
def buildUserResponse(length, statusCode: str, mimetype: str):
    r = f"HTTP/1.1 {statusCode}\r\n"
    r += f"Content-Length: {length}\r\n"
    r += f"Content-Type: {mimetype}\r\n" # I might have to change the content-type to application/json if it isn't alreay
    r += "X-Content-Type-Options: nosniff\r\n"
    # the body is a json string
    r += "\r\n"
    r = r.encode()
    print(f"this is the general userResponse {r}")

    return r

# this function takes in a json string containing a dictionary with a username and email
# 
def createUser(body):
    # the body is a json string/dictionary object
    print("This is the body of the post: ", body)
    print("this is the type of the body: ", type(body))
    body_json_str = body   # thought I had to decode() this 
   
    # the json string is a dictionary
    body_dict = json.loads(body_json_str)
    # we create a new id for the user
    body_dict["id"] = database.get_next_id()
    # we call the create function from our database file to send that new user to the mongo db
    database.create(body_dict)
    # we turn the body back into a json string and TODO: do I need to encode it

    return json.dumps(body_dict).encode()
