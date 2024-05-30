from bson.json_util import dumps

HTTP_STATUS = {
    200: "200 OK",
    201: "201 Created",
    204: "204 No content",
    303: "303 See Other",
    304: "304 Not Modified",
    400: "400 Bad Request",
    401: "401 Unauthorized",
    403: "403 Forbidden",
    404: "404 Not Found",
    405: "405 Method Not Allowed",
    422: "422 Unprocessable Entity",
    500: "500 Internal Server Error",
    501: "501 Not implemented",
}

JSON_INDENT = 2     # how big are indents in generated JSON files
JSON_SEPARATORS = (',', ': ')   # separators in generated JSON files

REGEX_EMAIL = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,7}\b'  # regex for recognizing email
HASH_ITERS = 100000     # number of iterations of hashing function - 100000 results in ~ 10 ms delay


def jsonify(dictionary: dict | list[dict]) -> str:
    return dumps(dictionary, sort_keys=True, indent=JSON_INDENT, separators=JSON_SEPARATORS)

