import pymongo.database
from faker import Faker
from pymongo import MongoClient
from pymongo.server_api import ServerApi

users_validation = {
  "$jsonSchema": {
    "bsonType": "object",
    "title": "User object validation",
    "required": [ "username", "email", "password"],
    "properties": {
      "username": {
        "bsonType": "string"
      },
      "email": {
        "bsonType": "string"
      },
      "password": {
        "bsonType": "string"
      },
      "salt": {
        "bsonType": "string"
      },
      "active": {
        "bsonType": "bool"
      },
      "date_created": {
        "bsonType": "date"
      },
      "last_login": {
        "bsonType": "timestamp"
      },
      "last_active": {
        "bsonType": "timestamp"
      }
    }
  }
}


def create_users_collection(database: pymongo.database.Database) -> None:
    if database.list_collection_names().count("users") == 0:
        database.create_collection("users", validator=users_validation)


def add_random_user(database: pymongo.database.Database) -> None:
    if database.list_collection_names().count("users") == 0:
        raise RuntimeError("There is no \"users\" collection")

    fake = Faker()
    collection = database.get_collection("users")
    collection.insert_one({
        "username": fake.user_name(),
        "email": fake.email(),
        "password": "for now just a string",
        "salt": "for now just a string",
        "active": fake.boolean(),
        "date_created": fake.date_time()
    })
