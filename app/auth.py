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


def login(login_str: str, password: str, users: pymongo.collection.Collection):
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

    private_key = open('.ssh/id_rsa', 'r').read()
    key = serialization.load_ssh_private_key(private_key.encode(), password=b'')

    token = jwt.encode(
        payload=a,
        key=key,
        algorithm='RS256'

    )

    return {"Successful login": ""}


def register(username: str, email: str, password: str, users: pymongo.collection.Collection):
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
        "active": True,     # TODO change after email confirmation
        "date_created": datetime.datetime.now()
    })

