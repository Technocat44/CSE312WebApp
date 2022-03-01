import re
from server.request import Request
from server.response import generate_response

# Basically, we get a request from the user and router handles the request
class Router:

    def __init__(self):
        self.routes = []
        self.route_404 = Route('', '', four_oh_four)


    def __str__(self):
        return f'Routes are {self.routes}'
    
    def __repr__(self):
        return f'Routes(routes = {self.routes})'

    """
        class Person:

            def __init__(self, person_name, person_age):
                self.name = person_name
                self.age = person_age

            def __str__(self):
                return f'Person name is {self.name} and age is {self.age}'

            def __repr__(self):
                return f'Person(name={self.name}, age={self.age})'


        p = Person('Pankaj', 34)

        print(p.__str__())
        print(p.__repr__())
    """

    def add_route(self, route):
        self.routes.append(route)

    # this method handles what callback function should handle a specific request
    # it will go through all the routes that are added,
    # if its a match: 
    def handle_request(self, request: Request, handler):
        # for each rpute I added, I check if its a match
        for route in self.routes:
            if route.is_request_match(request):
                route.handle_request(request, handler)
                return 

        self.route_404.handle_request(request, handler)




class Route:

    def __init__(self, method, path, action):
        self.method = method
        self.path = path
        self.action = action
    def __str__(self):
        return f"This is the path = {self.path}"
    def __repr__(self):
        return f"This is the path = {self.path}"

    def is_request_match(self, request: Request):
        if request.method != self.method:
            return False
            # the '^' matches the start of the string
        search_result = re.search('^' + self.path, request.path)
        if search_result:
            return True 
        else:
            return False
    
    def handle_request(self, request: Request, handler):
        self.action(request, handler)


def four_oh_four(self, request: Request, handler):
    r = generate_response(b"", "text/plain; charset=utf-8", "404 Not Found")
    handler.request.sendall(r)
