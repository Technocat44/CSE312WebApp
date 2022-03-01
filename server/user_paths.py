import json


import server.database as db

from server.response import generate_response
from server.router import Route
from server.static_paths import four_oh_four

####################### CRUDL ########################

# POST = create
# PUT = update
# DELETE = delete
# GET = retrieve


def add_paths(router):
    router.add_route(Route('POST', '/users', create))
    router.add_route(Route('GET', '/users/.', retrieve))
    router.add_route(Route('GET', '/users', list_all))
    router.add_route(Route('PUT', '/users/.', update))
    router.add_route(Route('DELETE', '/users/.', delete))
    router.add_route(Route('POST', '/.', four_oh_four))

# POST /users    works
def create(request, handler):
    body_string = request.body.decode() # we are assuming its a string
    body_dict = json.loads(body_string) 
    body_dict['id'] = db.get_next_id()

    db.create(body_dict)

    response = generate_response(json.dumps(body_dict).encode(), 'appliation/json', '201 Created')
    handler.request.sendall(response)

# PUT /users/.    works 
def update(request, handler):
    print("hey we made it into this function for updating a user cool")
    body_string = request.body.decode()
    body_dict = json.loads(body_string)
    email = body_dict["email"]
    username = body_dict["username"]
    userIdSplit = request.path.split("/")
    print("this is the userId split from request.path = ",userIdSplit)
    userId = userIdSplit[-1]
    print("This is the userId from userIdSplit[-1], it should return the id numebr, ", userId)
    update = db.updateUser(int(userId), email, username)
    updateToJson = json.dumps(str(update)).encode()
    if update == None:
        r = generate_response(b"Cannot Update, User Does Not Exist","text/plain; charset=utf-8", "404 Not Found")
        handler.request.sendall(r)
    r = generate_response(updateToJson, "application/json", "200 OK")
    handler.request.sendall(r)

# retrieve a single user
# GET /users/.   works
def retrieve(request, handler):
    print("hey I am in the retrieve function in user_paths")
    userIdSplit = request.path.split("/")
    userId = userIdSplit[-1]
    showSingleUser = db.retrieve_one(int(userId))
    showSingleUserJsonBytes = json.dumps(showSingleUser).encode()
    if showSingleUser == None:
        r = generate_response(b"User Does Not Exist","text/plain; charset=utf-8", "404 Not Found")
        handler.request.sendall(r)
    r = generate_response(showSingleUserJsonBytes, "application/json", "200 OK")
    handler.request.sendall(r)

# GET /users   works
def list_all(request, handler):
    showAllUsers = db.list_all()
    userList = json.dumps(showAllUsers).encode()
    r = generate_response(userList, "application/json", "200 OK")
    handler.request.sendall(r)

# DELETE /users/.  works   
def delete(request, handler):
    userIdSplit = request.path.split("/")
    userId = userIdSplit[-1]
    deleted = db.deleteUser(int(userId))
    if deleted == 0:
        r = generate_response(b"No such user exist", "text/plain; charset=utf-8", "404 Not Found")
        handler.request.sendall(r)
    r = generate_response(b"", "text/plain; charset=utf-8", "204 No Content")
    handler.request.sendall(r)
