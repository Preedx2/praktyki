import pymongo.collection
from pymongo import MongoClient
from pymongo.server_api import ServerApi


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

    def list_all(self, collection_name: str) -> list[dict]:
        """
        Lists all entries in a collection, mostly for test purposes
        :param collection_name: name of collection from database
        :return: string of all entries in bson format, hard to read for humans
        """
        collection = self.database.get_collection(collection_name)
        cursor = collection.find({})
        records = [record for record in cursor]
        return records

    def search_one(self, collection_name: str, query: dict) -> dict:
        """
        searches for one instance of query in collection collection_name
        @param collection_name: name of the collection to search, str
        @param query: query to search - dict consisting of key: value pairs
        @return: dict with all attributes of an object satisfying query result,
                or empty dictionary if query was unsuccessful
        """
        collection = self.database.get_collection(collection_name)
        return collection.find_one(query)

    def search_all(self, collection_name: str, query: dict) -> list[dict]:
        """
        searches for all instances of query in collection collection_name
        @param collection_name: name of the collection to search, str
        @param query: query to search - dict consisting of key: value pairs
        @return: dict with all attributes of an object satisfying query result,
                or empty dictionary if query was unsuccessful
        """
        results = []
        collection = self.database.get_collection(collection_name)
        for result in collection.find(query):
            results.append(result)

        return results

    def count(self, collection_name: str, query: dict) -> int:
        """
        counts all instances of query in collection collection_name
        @param collection_name: name of the collection to search, str
        @param query: query to search - dict consisting of key: value pairs
        @return: number of objects satisfying query in collection
        """
        collection = self.database.get_collection(collection_name)
        return collection.count_documents(query)

    def random_one(self, collection_name: str) -> dict:
        """
        retrieves random object from collection
        @param collection_name: name of the collection to retrieve sample from
        @return: object from the collection in dictionary key: value form
        """
        collection = self.database.get_collection(collection_name)
        return list(collection.aggregate([{"$sample": {"size": 1}}]))[0]

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

    def create_collection(self, name: str, validator: dict = None) -> None:
        if validator is None:
            validator = {}
        if self.database.list_collection_names().count(name) == 0:
            self.database.create_collection(name, validator=validator)

