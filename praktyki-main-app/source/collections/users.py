from __future__ import annotations
import re
import hashlib
import datetime
import os

import pymongo.database
from faker import Faker

from source.auth import Auth
from source.database import Database
from source.utils import REGEX_EMAIL, HASH_ITERS


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

    def __init__(self, username: str, email: str, password, salt,
                 active, date_created):
        self.json = {
            "username": username,
            "email": email,
            "password": password,
            "salt": salt,
            "active": active,
            "date_created": date_created
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
    def add_random_user() -> User:
        """
        Adds random user  generated with Faker for testing purposes.
        Login for generated user is impossible because of randomly generated and unrelated salt and hashed password
        :return: None
        """

        fake = Faker()
        return User(fake.user_name(), fake.email(), fake.binary(512),
                    fake.binary(32), fake.boolean(), fake.date_time())

    @staticmethod
    def login(login_str: str, password: str, database: Database) -> str:
        """
        Login existing user into the application.
        :param login_str: either username or email - application automatically recognizes which one
        :param password: password
        :param database: database connection object
        :return: encoded jwt token authenticating user for 8 hours
        """
        if re.fullmatch(REGEX_EMAIL, login_str):
            user = database.search_one("users", {"email": login_str})
        else:
            user = database.search_one("users", {"username": login_str})

        if not user:
            raise ValueError(f"There is no user identified by {login_str}")

        salt = user.get("salt")
        # start = time.time_ns()
        hashed_pswd = hashlib.pbkdf2_hmac('sha512', password.encode('utf-8'), salt, HASH_ITERS)
        # end = time.time_ns()
        # print(f"Hashing time: {end-start} ns")
        if user.get("password") != hashed_pswd:
            raise ValueError(f"Invalid password")

        database.find_one_and_update("users", {"_id": user.get("_id")},
                                     {"$set": {"last_login": datetime.datetime.now()}})

        auth = Auth()
        return auth.generate_login_token(user.get("username"))

    @staticmethod
    def register(username: str, email: str, password: str, database: Database) -> None:
        """
        Register new user and insert him to the database. Function also handles validation
        :param username: string between 3 and 64 characters, must be unique and cannot be a valid email address
        :param email: string no longer than 256 characters, must be unique and a valid email address
        :param password: string between 8 and 64 characters
        :param database: database connection object
        :return: None
        """
        if not re.fullmatch(REGEX_EMAIL, email):
            raise ValueError("Improper email format")
        if re.fullmatch(REGEX_EMAIL, username):
            raise ValueError("User name cannot be an email")

        if not 3 < len(username) < 64:
            raise ValueError("Username needs to be between 3 and 64 characters long")
        if not 8 < len(password) < 64:
            raise ValueError("Password needs to be between 8 and 64 characters long")
        if len(email) > 256:
            raise ValueError("Email address cannot exceed 256 characters")

        if database.search_one("users", {"username": username}):
            raise ValueError("Username already taken")
        if database.search_one("users", {"email": email}):
            raise ValueError("Email already in use")

        salt = os.urandom(32)
        hashed_pswd = hashlib.pbkdf2_hmac('sha512', password.encode('utf-8'), salt, HASH_ITERS)

        database.insert("users", {
            "username": username,
            "email": email,
            "password": hashed_pswd,
            "salt": salt,
            "active": True,
            "date_created": datetime.datetime.now()
        })

    @staticmethod
    def reset_password(email: str, new_password: str, database: Database) -> None:
        """
        Function for resetting password of user with specified email address.

        NOTE: in deployment it should be validated with unique token generated on password reset request
        :param email: string with email of an existing user
        :param new_password: string with new user password - can be the same as previous password,
        in that case change will result in generation of new salt and hashed password
        :param database: database connection object
        :return: None
        """
        user = database.search_one("users",
                                   {"email": email})  # in real life it should be controlled by tokenized emails

        if not user:
            raise ValueError(f"There is no user identified by {email}")

        if not 8 < len(new_password) < 64:
            raise ValueError("Password needs to be between 8 and 64 characters long")

        salt = os.urandom(32)
        hashed_pswd = hashlib.pbkdf2_hmac('sha512', new_password.encode('utf-8'), salt, HASH_ITERS)

        database.find_one_and_update("users", {"_id": user.get("_id")},
                                     {"$set": {"password": hashed_pswd, "salt": salt}})
