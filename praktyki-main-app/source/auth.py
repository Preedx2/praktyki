
import datetime

import pymongo.collection
import jwt
from cryptography.hazmat.primitives import serialization

from source.database import Database


class Auth:
    def __init__(self):
        self.public_key = open(".ssh/id_rsa.pub", "r").read()
        self.private_key = open('.ssh/id_rsa', 'r').read()

    def authenticate(self, token) -> str:
        """
        Decode given token using public key and return associated username.
        Error handling is taken care of in the main Application class
        :param token: token taken from the header of a request
        :return: associated username as a string
        """
        key = serialization.load_ssh_public_key(self.public_key.encode())
        payload = jwt.decode(token, key=key, algorithms=['RS256', ])
        return payload["username"]

    def generate_login_token(self, username: str) -> str:
        """

        @param username:
        @return:
        """
        key = serialization.load_ssh_private_key(self.private_key.encode(), password=b'')

        # in token could have used _id, but usernames are unique and human readable so I decided to use them instead
        token = jwt.encode(
            payload={
                "username": username,
                "exp": datetime.datetime.now(tz=datetime.timezone.utc) + datetime.timedelta(hours=8)
            },
            key=key,
            algorithm='RS256'
        )

        return token

