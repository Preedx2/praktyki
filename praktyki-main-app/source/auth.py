import re
import hashlib
import time
import os
import datetime

import pymongo.collection
import jwt
from cryptography.hazmat.primitives import serialization

from source.database import Database


# TODO make config file for environmental variables
# regex for recognizing email
REGEX_EMAIL = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,7}\b'
HASH_ITERS = 100000     # number of iterations of hashing function - 100000 results in ~ 10 ms delay


def authenticate(token) -> str:
    """
    Decode given token using public key and return associated username.
    Error handling is taken care of in the main Application class
    :param token: token taken from the header of a request
    :return: associated username as a string
    """
    public_key = open(".ssh/id_rsa.pub", "r").read()
    key = serialization.load_ssh_public_key(public_key.encode())
    payload = jwt.decode(token, key=key, algorithms=['RS256', ])
    return payload["username"]


def login(login_str: str, password: str, database: Database) -> str:
    """
    Login existing user into the application.
    :param login_str: either username or email - application automatically recognizes which one
    :param password: password
    :param database: database connection object
    :return: encoded jwt token authenticating user for 8 hours
    """
    if re.fullmatch(REGEX_EMAIL, login_str):
        user = database.search("users", {"email": login_str})
    else:
        user = database.search("users", {"username": login_str})

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

    private_key = open('.ssh/id_rsa', 'r').read()
    key = serialization.load_ssh_private_key(private_key.encode(), password=b'')

    # in token could have used _id, but usernames are unique and human readable so I decided to use them instead
    token = jwt.encode(
        payload={
            "username": user.get("username"),
            "exp": datetime.datetime.now(tz=datetime.timezone.utc) + datetime.timedelta(hours=8)
        },
        key=key,
        algorithm='RS256'
    )

    return token


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

    if database.search("users", {"username": username}):
        raise ValueError("Username already taken")
    if database.search("users", {"email": email}):
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
    user = database.search("users", {"email": email})  # in real life it should be controlled by tokenized emails

    if not user:
        raise ValueError(f"There is no user identified by {email}")

    if not 8 < len(new_password) < 64:
        raise ValueError("Password needs to be between 8 and 64 characters long")

    salt = os.urandom(32)
    hashed_pswd = hashlib.pbkdf2_hmac('sha512', new_password.encode('utf-8'), salt, HASH_ITERS)

    database.find_one_and_update("users", {"_id": user.get("_id")},
                                {"$set": {"password": hashed_pswd, "salt": salt}})
