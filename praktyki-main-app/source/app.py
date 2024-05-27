import json

import jwt
import pymongo.collection
from pymongo import MongoClient
from pymongo.server_api import ServerApi
from bson.json_util import dumps

import source.collections.users as users
import source.auth as auth


class Application:
    """
    Main class of the application, handles user requests and manages database connection
    """
    def __init__(self, environ, start_response):
        """
        Initiates environment and database connection
        :param environ:
        :param start_response:
        """
        with open("mongodb-login", 'r') as file:
            _cluster = file.readline()[:-1]
            _login = file.readline()[:-1]
            _password = file.readline()[:-1]

        uri = f"mongodb+srv://{_login}:{_password}@{_cluster}.mongodb.net/?retryWrites=true&w=majority&appName=praktyki0"
        self.client = MongoClient(uri, server_api=ServerApi('1'))
        self.database = self.client.get_database("praktyki_app_db")

        self.environ = environ
        self.start_response = start_response

    def __del__(self):
        """
        Closes database connection
        :return:
        """
        if hasattr(self, 'client'):
            self.client.close()

    def list_all(self, collection: pymongo.collection.Collection) -> str:
        """
        Lists all entries in a collection, mostly for test purposes
        :param collection: collection from the database
        :return: string of all entries in bson format, hard to read for humans
        """

        cursor = collection.find({})
        records = [record for record in cursor]
        output = dumps(records, sort_keys=True, indent=4, separators=(',', ': '))
        # print(output)
        return output

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
                users.add_random_user(self.database)
                response = b"Inserted random user"
                status = "200 OK"
            case "/get_users":
                collection = self.database.get_collection("users")
                response = self.list_all(collection).encode()
                status = "200 OK"
            case "/register":
                if method == "POST":
                    try:
                        collection = self.database.get_collection("users")
                        auth.register(
                                post_input["username"],
                                post_input["email"],
                                post_input["password"],
                                collection
                            )
                        response = b"Successful registration"
                        status = "200 OK"
                    except Exception as e:
                        print(e)
                        response = f"Error of type: {type(e)}".encode()
                        status = "400 Bad Request"
                else:
                    response = b"405 Method not allowed"
                    status = "405 Method not allowed"
            case "/login":
                if method == "POST":
                    try:
                        collection = self.database.get_collection("users")
                        response = auth.login(
                            post_input["login_str"],
                            post_input["password"],
                            collection
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
                        collection = self.database.get_collection("users")
                        auth.reset_password(
                            post_input["email"],
                            post_input["new_password"],
                            collection
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
                except (jwt.exceptions.DecodeError):
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
