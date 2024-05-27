import json

import jwt

import source.auth as auth
from source.database import Database
import source.collections.articles as articles


class Application:
    """
    Main class of the application, handles user requests
    """
    def __init__(self, environ, start_response):
        """
        Initiates environment and database connection
        :param environ:
        :param start_response:
        """
        self.environ = environ
        self.start_response = start_response

        self.database = Database()

    def __iter__(self):
        """
        Iterator handles request given from the server.py
        Handles most of the exceptions
        :return: response to the server
        """
        print("Received http request")
        path = self.environ['PATH_INFO']
        method = self.environ['REQUEST_METHOD']

        auth_token = None
        if 'HTTP_AUTH' in self.environ:
            auth_token = self.environ['HTTP_AUTH']

        post_input = {}
        if method == "POST":
            input_obj = self.environ['wsgi.input']
            input_len = int(self.environ['CONTENT_LENGTH'])
            post_input = json.loads(input_obj.read(input_len).decode())

        status = "501 Not Implemented"
        response = b"501 Not Implemented"
        match path:
            case "/insert_random_user":
                self.database.add_random_user()
                response = b"Inserted random user"
                status = "200 OK"
            case "/get_users":
                response = self.database.list_all("users").encode()
                status = "200 OK"
            case "/create_articles":
                articles.create_articles_collection(self.database.database)
                status = "200 OK"
            case "/insert_random_art":
                self.database.add_random_article()
                response = b"Inserted random article"
                status = "200 OK"
            case "/get_articles":
                response = self.database.list_all("users").encode()
                status = "200 OK"
            case "/register":
                if method == "POST":
                    try:
                        auth.register(
                                post_input["username"],
                                post_input["email"],
                                post_input["password"],
                                self.database
                            )
                        response = b"Successful registration"
                        status = "200 OK"
                    except Exception as e:
                        print(e)
                        response = f"Error: {e}".encode()
                        status = "400 Bad Request"
                else:
                    response = b"405 Method not allowed"
                    status = "405 Method not allowed"
            case "/login":
                if method == "POST":
                    try:
                        response = auth.login(
                            post_input["login_str"],
                            post_input["password"],
                            self.database
                        ).encode()
                        status = "200 OK"
                    except Exception as e:
                        print(e)
                        response = f"Error of type: {type(e)}".encode()
                        status = "400 Bad Request"
                else:
                    response = b"405 Method not allowed"
                    status = "405 Method not allowed"
            case "/reset_password":
                if method == "POST":
                    try:
                        auth.reset_password(
                            post_input["email"],
                            post_input["new_password"],
                            self.database
                        )
                        response = b"Password changed successfully"
                        status = "200 OK"
                    except Exception as e:
                        print(e)
                        response = f"Error of type: {type(e)}".encode()
                        status = "400 Bad Request"
                else:
                    response = b"405 Method not allowed"
                    status = "405 Method not allowed"
            case "/protected":
                try:
                    name = auth.authenticate(auth_token)
                    response = f"Welcome {name}".encode()
                    status = "200 OK"
                except (jwt.exceptions.ExpiredSignatureError, jwt.exceptions.InvalidSignatureError) as e:
                    response = f"{e}".encode()
                    status = "403 Forbidden"
                except jwt.exceptions.DecodeError:
                    response = b"You need to be authenticated to access this page"
                    status = "403 Forbidden"
            case _:
                response = b"404 Not Found"
                status = "404 Not Found"
        headers = [
            ("Content-Type", "text/html"),
            ("content-Length", str(len(response)))
        ]
        self.start_response(status, headers)

        yield response
