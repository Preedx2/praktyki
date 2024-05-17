import json

import pymongo.collection
from pymongo import MongoClient
from pymongo.server_api import ServerApi
from bson.json_util import dumps

import app.collections.users as users
import app.auth as auth


class Application:
    def __init__(self, environ, start_response):

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
        if hasattr(self, 'client'):
            self.client.close()

    def list_all(self, collection: pymongo.collection.Collection) -> str:
        cursor = collection.find({})
        records = [record for record in cursor]
        output = dumps(records, sort_keys=True, indent=4, separators=(',', ': '))
        # print(output)
        return output

    def __iter__(self):
        path = self.environ['PATH_INFO']
        method = self.environ['REQUEST_METHOD']
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
                        response = b"Successfull registration"
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
            case _:
                response = b"404 Not Found"
                status = "404 Not Found"
        headers = [
            ("Content-Type", "text/html"),
            ("content-Length", str(len(response)))
        ]
        self.start_response(status, headers)

        yield response
