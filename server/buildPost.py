import buildResponse


def build201Response(length: str, mimetype: str):
    content = "hi"
    response = buildResponse.buildStaticResponse("201 Created", "application/json", content)
    return response.encode()
