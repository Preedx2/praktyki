from __future__ import annotations

from source.database import Database


class ForbiddenPhrase:
    # Validation schema for 'forbidden_phrases' collection
    validation = {
      "$jsonSchema": {
        "bsonType": "object",
        "title": "forbidden_phrases schema validation",
        "required": ["phrase"],
        "properties": {
          "phrase": {
            "bsonType": "string"
          }
        }
      }
    }

    def __init__(self, phrase: str):
        self.json = {
            "phrase": phrase
        }

    @property
    def phrase(self) -> str:
        return self.json["phrase"]

    @staticmethod
    def create_collection(database: Database) -> None:
        """
        Create new collection of "forbidden_phrases"
        :param database: connected mongodb database
        :return: None
        """
        database.create_collection("forbidden_phrases", ForbiddenPhrase.validation)
