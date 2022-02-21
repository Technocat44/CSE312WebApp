import buildResponse
import json
import database

def build201Response(length: str, body: str):
    response = buildUserResponse(length, "201 Created", "application/json", body)
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
# this method only works for body request that our strings!!! TODO: create a different response builder for images, etc
def buildUserResponse(length: str, statusCode: str, mimetype: str, body):
    r = f"HTTP/1.1 {statusCode}\r\n"
    r += f"Content-Length: {length}\r\n"
    r += f"Content-Type: {mimetype}\r\n" # I might have to change the content-type to application/json if it isn't alreay
    # the body is a json string
    body_dict_with_id = createUser(body)
    r += "\r\n"
    r = r.encode()
    r += body_dict_with_id.encode()

    return r

# this function takes in a json string containing a dictionary with a username and email
# 
def createUser(body):
    # the body is a json string
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
    return json.dumps(body_dict)