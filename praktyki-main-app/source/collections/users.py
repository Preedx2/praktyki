import pymongo.database
from faker import Faker

from source.database import Database


class User:
    # Validation schema for 'users' collection
    validation = {
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
            "bsonType": "binData"
          },
          "salt": {
            "bsonType": "binData"
          },
          "active": {
            "bsonType": "bool"
          },
          "date_created": {
            "bsonType": "date"
          },
          "last_login": {
            "bsonType": "date"
          },
          "last_active": {
            "bsonType": "date"
          }
        }
      }
    }

    @staticmethod
    def create_users_collection(database: pymongo.database.Database) -> None:
        """
        Create new collection of "users"
        :param database: connected mongodb database
        :return: None
        """
        if database.list_collection_names().count("users") == 0:
            database.create_collection("users", validator=User.validation)

    @staticmethod
    def add_random_user(database: Database) -> None:
        """
        Adds random user  generated with Faker for testing purposes.
        Login for generated user is impossible because of randomly generated and unrelated salt and hashed password
        :param database: connected mongodb database
        :return: None
        """

        fake = Faker()
        database.insert("users", {
            "username": fake.user_name(),
            "email": fake.email(),
            "password": fake.binary(512),
            "salt": fake.binary(32),
            "active": fake.boolean(),
            "date_created": fake.date_time()
        })
