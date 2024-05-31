import json
from urllib import parse

import source.exceptions as ex
from source.auth import Auth
from source.database import Database
from source.handler import Handler
from source.utils import HTTP_STATUS


class Application:
    """
    Main class of the application, routes user requests
    """
    def __init__(self, environ, start_response):
        """
        Initiates environment and database connection
        :param environ:
        :param start_response:
        """
        self.environ = environ
        self.start_response = start_response
        self.auth = Auth()

        self.database = Database()
        self.handle = Handler(self.database)

    def __iter__(self):
        """
        Iterator handles request given from the server.py
        :return: response to the server
        """
        print("Received http request")
        path = self.environ['PATH_INFO']

        method = self.environ['REQUEST_METHOD']
        get_input = parse.parse_qs(self.environ['QUERY_STRING'])
        post_input = {}
        if method == "POST":
            input_obj = self.environ['wsgi.input']
            input_len = int(self.environ['CONTENT_LENGTH'])
            post_input = json.loads(input_obj.read(input_len).decode())

        status = "501 Not Implemented"
        response = b"501 Not Implemented"
        try:
            auth_token = None
            username = None
            if 'HTTP_AUTH' in self.environ:
                auth_token = self.environ['HTTP_AUTH']
                username = self.auth.authenticate(auth_token)

            match path:
                case "/test":
                    pass
                case "/":
                    response = b"Index"
                    status = HTTP_STATUS[200]
                case "/insert_random_user":
                    response, status = self.handle.insert_random_user()
                case "/insert_random_art":
                    response, satus = self.handle.insert_random_article()
                case "/insert_random_comment":
                    response, status = self.handle.insert_random_comment()
                case "/get_articles":
                    response, status = self.handle.get_articles()
                case "/get_articles_textless":
                    response, status = self.handle.get_articles_textless()
                case "/get_article":
                    response, status = self.handle.get_article(get_input)
                case "/get_forbidden":
                    response, status = self.handle.get_forbidden()
                case "/get_users":
                    response, status = self.handle.get_users()
                case "/add_article":
                    self.access_method(method)
                    self.authorized_access(auth_token)
                    response, status = self.handle.add_article(username, post_input)
                case "/add_comment":
                    self.access_method(method)
                    self.authorized_access(auth_token)
                    response, status = self.handle.add_comment(username, post_input)
                case "/add_forbidden":
                    self.access_method(method)
                    self.authorized_access(auth_token)
                    response, status = self.handle.add_forbidden(post_input)
                case "/register":
                    self.access_method(method)
                    response, status = self.handle.register(post_input)
                case "/login":
                    self.access_method(method)
                    response, status = self.handle.login(post_input)
                case "/reset_password":
                    self.access_method(method)
                    response, status = self.handle.reset_password(post_input)
                case "/protected":
                    self.authorized_access(auth_token)
                    response = f"Welcome {username}".encode()
                    status = HTTP_STATUS[200]
                case "/edit_forbidden":
                    pass
                case _:
                    response = b"404 Not Found"
                    status = HTTP_STATUS[404]
        except Exception as error:
            response, status = self.handle.error_handler(error)

        headers = [
            ("Content-Type", "text/html"),
            ("content-Length", str(len(response)))
        ]

        self.start_response(status, headers)
        yield response

    @staticmethod
    def access_method(method: str, allowed: list[str] = None) -> None:
        """
        Raises MethodNotAllowedException if method is not in allowed
        @param method: method of access in string
        @param allowed: list of allowed methods, by default ['POST']
        """
        if allowed is None:
            allowed = 'POST'
        if method not in allowed:
            raise ex.MethodNotAllowedError(allowed)

    @staticmethod
    def authorized_access(auth_token: str) -> None:
        """
        Raises NotLoggedInException if auth_token is None
        @param auth_token: authentication token from environment
        """
        if auth_token is None:
            raise ex.NotLoggedInError

