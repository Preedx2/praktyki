import pymongo.database
from faker import Faker

from source.database import Database

# Validation schema for 'articles' collection
articles_validation = {
  "$jsonSchema": {
    "bsonType": "object",
    "title": "Articles schema validation",
    "required": [ "title", "text", "date_created", "author"],
    "properties": {
      "title": {
        "bsonType": "string"
      },
      "text": {
        "bsonType": "string"
      },
      "date_created": {
        "bsonType": "date"
      },
      "author": {
        "id": {
          "bsonType": "objectId"
        },
        "username": {
          "bsonType": "string"
        },
        "email": {
          "bsonType": "string"
        }
      }
    }
  }
}


def create_articles_collection(database: pymongo.database.Database) -> None:
    """
    Create new collection of "users"
    :param database: connected mongodb database
    :return: None
    """
    if database.list_collection_names().count("users") == 0:
        database.create_collection("users", validator=articles_validation)


def add_random_article(database: pymongo.database.Database) -> None:
    """
    Adds random user  generated with Faker for testing purposes.
    Login for generated user is impossible because of randomly generated and unrelated salt and hashed password
    Raises runtime error when users database has not been initialized
    :param database: connected mongodb database
    :return: None
    """
    if database.list_collection_names().count("users") == 0:
        raise RuntimeError("There is no \"users\" collection")

    author = database.random_one("users")
    fake = Faker()
    collection = database.get_collection("articles")
    collection.insert_one({
        "title": fake.sentence(),
        "text": fake.paragraph(nb_sentences=10),
        "date_created": fake.date_time(),
        "author": {
          "id": author.get("_id"),
          "username": author.get("username"),
          "email": author.get("email")
        }
    })
