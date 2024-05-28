from __future__ import annotations
from datetime import datetime

import pymongo.database
from faker import Faker
from bson.objectid import ObjectId

from source.database import Database
# from source.collections.users import User


class Comment:
    # Validation schema for 'articles' collection
    # currently not working
    validation = {
      "$jsonSchema": {
        "bsonType": "object",
        "title": "Articles schema validation",
        "required": [ "article_id", "text", "date_created", "author"],
        "properties": {
          "article_id": {
            "bsonType": "objectId"
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

    def __init__(self, article_id: ObjectId, text: str, date_created: datetime,
                 author_id: ObjectId, author_username: str, author_email: str):
        self.json = {
            "article_id": article_id,
            "text": text,
            "date_created": date_created,
            "author": {
                "id": author_id,
                "username": author_username,
                "email": author_email
            }
        }

    @property
    def article_id(self) -> ObjectId:
        return self.json["article_id"]

    @property
    def text(self) -> str:
        return self.json["text"]

    @property
    def date_created(self) -> datetime:
        return self.json["date_created"]

    @property
    def author(self) -> dict:
        return self.json["author"]

    @staticmethod
    def create_comments_collection(database: pymongo.database.Database) -> None:
        """
        Create new collection of "comments"
        :param database: connected mongodb database
        :return: None
        """
        if database.list_collection_names().count("comments") == 0:
            database.create_collection("comments", validator=Comment.validation)

    @staticmethod
    def create_random_comment(database: Database) -> Comment:
        """
        Adds random comment generated with Faker for testing purposes.
        User and article get randomly sellected from existing collections
        :param database: connected mongodb database
        :return: None
        """

        author = database.random_one("users")
        article = database.random_one("articles")
        fake = Faker()
        return Comment(article.get("_id"), fake.paragraph(nb_sentences=2), fake.date_time(),
                       author.get("_id"), author.get("username"), author.get("email"))

        # database.insert("articles", {
        #     "title": fake.sentence(),
        #     "text": fake.paragraph(nb_sentences=10),
        #     "date_created": fake.date_time(),
        #     "author": {
        #       "id": author.get("_id"),
        #       "username": author.get("username"),
        #       "email": author.get("email")
        #     }
        # })

