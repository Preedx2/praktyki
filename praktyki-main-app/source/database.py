import pymongo.collection
from pymongo import MongoClient
from pymongo.server_api import ServerApi
from bson.json_util import dumps

import source.collections.users as users
import source.collections.articles as articles


class Database:
    """
    Class representing database connection
    """
    def __init__(self):
        """
           On creation object communicates with remote database using informations contained in mongodb-login file.
           The file should contain name of the mongodb cluster, login and password, each on separate line
        """
        with open("mongodb-login", 'r') as file:
            _cluster = file.readline()[:-1]
            _login = file.readline()[:-1]
            _password = file.readline()[:-1]

        uri = f"mongodb+srv://{_login}:{_password}@{_cluster}.mongodb.net/?retryWrites=true&w=majority&appName=praktyki0"
        self.client = MongoClient(uri, server_api=ServerApi('1'))
        self.database = self.client.get_database("praktyki_app_db")

    def __del__(self) -> None:
        """
        On deletion object closes connection to database
        @return: None
        """
        if hasattr(self, 'client'):
            self.client.close()

    def list_all(self, collection_name: str) -> str:
        """
        Lists all entries in a collection, mostly for test purposes
        :param collection_name: name of collection from database
        :return: string of all entries in bson format, hard to read for humans
        """
        collection = self.database.get_collection(collection_name)
        cursor = collection.find({})
        records = [record for record in cursor]
        output = f"<pre>{dumps(records, sort_keys=True, indent=4, separators=(',', ': '))}</pre"

        return output

    def add_random_user(self) -> None:
        users.add_random_user(self.database)

    def add_random_article(self) -> None:
        articles.add_random_article(self.database)

    def search(self, collection_name: str, query: dict) -> dict:
        """
        searches for one instance of query in collection collection_name
        @param collection_name: name of the collection to search, str
        @param query: query to search - dict consisting of key: value pairs
        @return: dict with all attributes of an object satisfying query result,
                or empty dictionary if query was unsuccessful
        """
        collection = self.database.get_collection(collection_name)
        return collection.find_one(query)

    def random_one(self, collection_name: str) -> dict:
        collection = self.database.get_collection(collection_name)
        return dict(collection.aggregate({"$sample": {"size": 1}}))

    def find_one_and_update(self, collection_name: str, query: dict, update: dict) -> dict:
        """
        searches for one instance of query in collection and updates its values
        @param collection_name: name of the collection to search
        @param query: query to search - dict consisting of key: value pairs
        @param update: values to update - consisting of key: value pairs
        @return: dict with updated object or empty dictionary if query was unsuccessful
        """
        collection = self.database.get_collection(collection_name)
        return collection.find_one_and_update(query, update)

    def insert(self, collection_name: str, object_dict: dict) -> None:
        """
        inserts one object into specified collection
        @param collection_name: name of the collection you insert object into
        @param object_dict: object to insert, represented as key: value pairs
        @return: None
        """
        collection = self.database.get_collection(collection_name)
        collection.insert_one(object_dict)
