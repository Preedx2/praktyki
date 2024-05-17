import re
import hashlib
import time
import os
import datetime

import pymongo.collection
import jwt
from cryptography.hazmat.primitives import serialization


# regex for recognizing email
REGEX_EMAIL = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,7}\b'
HASH_ITERS = 100000


def authenticate(token) -> str:
    public_key = open(".ssh/id_rsa.pub", "r").read()
    key = serialization.load_ssh_public_key(public_key.encode())
    payload = jwt.decode(token, key=key, algorithms=['RS256', ])
    return payload["username"]


def login(login_str: str, password: str, users: pymongo.collection.Collection) -> str:
    if re.fullmatch(REGEX_EMAIL, login_str):
        user = users.find_one({"email": login_str})
    else:
        user = users.find_one({"username": login_str})

    if not user:
        raise ValueError(f"There is no user identified by {login_str}")

    salt = user.get("salt")
    start = time.time_ns()
    hashed_pswd = hashlib.pbkdf2_hmac('sha512', password.encode('utf-8'), salt, HASH_ITERS)
    end = time.time_ns()
    print(f"Hashing time: {end-start} ns")
    if user.get("password") != hashed_pswd:
        raise ValueError(f"Invalid password")

    users.find_one_and_update({"_id": user.get("_id")},
                              {"$set": {"last_login": datetime.datetime.now()}})

    private_key = open('.ssh/id_rsa', 'r').read()
    key = serialization.load_ssh_private_key(private_key.encode(), password=b'')

    token = jwt.encode(
        payload={
            "username": user.get("username"),
            "exp": datetime.datetime.now(tz=datetime.timezone.utc) + datetime.timedelta(hours=8)
        },
        key=key,
        algorithm='RS256'
    )

    # return {"Successful login": ""}
    return token


def register(username: str, email: str, password: str, users: pymongo.collection.Collection) -> None:
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

    if users.find_one({"username": username}):
        raise ValueError("Username already taken")
    if users.find_one({"email": email}):
        raise ValueError("Email already in use")

    salt = os.urandom(32)
    hashed_pswd = hashlib.pbkdf2_hmac('sha512', password.encode('utf-8'), salt, HASH_ITERS)

    users.insert_one({
        "username": username,
        "email": email,
        "password": hashed_pswd,
        "salt": salt,
        "active": True,
        "date_created": datetime.datetime.now()
    })


def reset_password(email: str, new_password: str, users: pymongo.collection.Collection) -> None:
    user = users.find_one({"email": email})  # in real life it should be controlled by tokenized emails

    if not user:
        raise ValueError(f"There is no user identified by {email}")

    if not 8 < len(new_password) < 64:
        raise ValueError("Password needs to be between 8 and 64 characters long")

    salt = os.urandom(32)
    hashed_pswd = hashlib.pbkdf2_hmac('sha512', new_password.encode('utf-8'), salt, HASH_ITERS)

    users.find_one_and_update({"_id": user.get("_id")},
                              {"$set": {"password": hashed_pswd, "salt": salt}})
