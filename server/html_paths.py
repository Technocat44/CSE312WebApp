
import server.database as db
from server.router import Route
from server.response import generate_response, redirect


def add_paths(router):
    router.add_route(Route('POST', '/images-upload', parse))


def parse(request, handler):
    return 0
