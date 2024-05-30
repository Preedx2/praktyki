from __future__ import annotations
from datetime import datetime

import pymongo.database
from faker import Faker

from source.database import Database


class Article:
    # Validation schema for 'articles' collection
    # currently not working
    validation = {
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

    def __init__(self, title: str, text: str, date_created: datetime, author_id, author_username, author_email):
        self.json = {
            "title": title,
            "text": text,
            "date_created": date_created,
            "author": {
                "id": author_id,
                "username": author_username,
                "email": author_email
            }
        }

    @property
    def title(self) -> str:
        return self.json["title"]

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
    def create_articles_collection(database: pymongo.database.Database) -> None:
        """
        Create new collection of "articles"
        :param database: connected mongodb database
        :return: None
        """
        if database.list_collection_names().count("articles") == 0:
            database.create_collection("articles", validator=Article.validation)

    @staticmethod
    def create_random_article(database: Database) -> Article:
        """
        Adds random article generated with Faker for testing purposes.
        User gets randomly sellected from existing collection of users
        :param database: connected mongodb database
        :return: None
        """

        author = database.random_one("users")
        fake = Faker()
        return Article(fake.sentence(), fake.paragraph(nb_sentences=10), fake.date_time(),
                       author.get("_id"), author.get("username"), author.get("email"))



