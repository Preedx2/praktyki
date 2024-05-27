import pymongo.database
from faker import Faker

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
      "author": [{
        "id": {
          "bsonType": "objectId"
        },
        "username": {
          "bsonType": "string"
        },
        "email": {
          "bsonType": "string"
        }
      }]
    }
  }
}


def create_articles_collection(database: pymongo.database.Database) -> None:
    """
    Create new collection of "articles"
    :param database: connected mongodb database
    :return: None
    """
    if database.list_collection_names().count("articles") == 0:
        database.create_collection("articles", validator=articles_validation)


def add_random_article(database: pymongo.database.Database) -> None:
    """
    Adds random article generated with Faker for testing purposes.
    User gets randomly sellected from existing collection of users
    :param database: connected mongodb database
    :return: None
    """
    if database.list_collection_names().count("articles") == 0:
        raise RuntimeError("There is no \"articles\" collection")

    # author = database.random_one("users")
    collection = database.get_collection("users")
    author = collection.aggregate([{'$sample': {'size': 1}}])
    author = list(author)[0]
    print(type(author), flush=True)

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
