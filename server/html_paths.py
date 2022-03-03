
import server.database as db
from server.router import Route
from server.response import generate_response, redirect
from server.fileHandling import all_bytes_of_file


def add_paths(router):
    router.add_route(Route('POST', '/image-upload', parse))


def parse(request, handler):
    print('\n\n\n\n\n')
    print("I am inside the html_paths file, testing what my all_bytes_from_file produces")
    print("This is the length of all the bytes in the file: ", len(all_bytes_of_file))
    print("this is the length ")
    r = redirect("/")
    handler.request.sendall(r)