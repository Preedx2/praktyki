import json

import pymongo.collection
from pymongo import MongoClient
from pymongo.server_api import ServerApi

import app.collections.users as users


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
        records = []
        for doc in cursor:
            records.append(str(doc))
            records.append("<br>")
        return "".join(records)

    def __iter__(self):
        path = self.environ['PATH_INFO']
        method = self.environ['REQUEST_METHOD']
        status = "501 Not Implemented"
        match path:
            case "/hello":
                response = b"Hello World"
                status = "200 OK"
            case "/dupa":
                response = b"Koscotrupa"
                status = "200 OK"
            case "/create_users_collection":
                users.create_users_collection(self.database)
                response = b"Created collection \"Users\""
                status = "200 OK"
            case "/insert_random_user":
                users.add_random_user(self.database)
                response = b"Inserted random user"
                status = "200 OK"
            case "/get_users":
                collection = self.database.get_collection("users")
                response = self.list_all(collection).encode()
            case _:
                response = b"404 Not Found"
                status = "404 Not Found"
        headers = [
            ("Content-Type", "text/html"),
            ("content-Length", str(len(response)))
        ]
        self.start_response(status, headers)

        yield response
