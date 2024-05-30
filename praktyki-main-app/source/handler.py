import json
import traceback
from datetime import datetime

import jwt.exceptions
from bson import ObjectId

import source.exceptions as ex
from source.collections.users import User
from source.collections.articles import Article
from source.collections.comments import Comment
from source.collections.forbidden_phrases import ForbiddenPhrase
from source.database import Database
from source.utils import HTTP_STATUS, jsonify


# def access_method(func: callable, allowed: list[str], method: str):
#     if method in allowed:
#         return func
#     else:
#         raise ex.MethodNotAllowedException(allowed)


class Handler:

    def __init__(self, database: Database):
        self.database = database

    @staticmethod
    def error_handler(error: Exception) -> (bytes, str):
        """
        Method handling
        @param error:
        @return: tuple of reponse containing error message encoded in bytes
            and status representing HTTP status in string
        """
        response = str(error).encode()
        if isinstance(error, ValueError):
            status = HTTP_STATUS[400]
        elif isinstance(error, jwt.exceptions.ExpiredSignatureError):
            response = b"Your authentication has expired"
            status = HTTP_STATUS[401]
        elif isinstance(error, ex.NotLoggedInException):
            status = HTTP_STATUS[403]
        elif isinstance(error, ex.MethodNotAllowedException):
            status = HTTP_STATUS[405]
        else:
            response = b"An error has occurred"
            status = HTTP_STATUS[500]
        traceback.print_exc()

        return response, status

    def insert_random_article(self) -> (bytes, str):
        """
        Insert random article to the collection
        @return: tuple of byte encoded response, and status in string
        """
        self.database.insert("articles", Article.create_random_article(self.database).json)
        response = b"Inserted random article"
        status = HTTP_STATUS[201]
        return response, status

    def insert_random_comment(self) -> (bytes, str):
        """
        Insert random article to the collection
        @return: tuple of byte encoded response, and status in string
        """
        self.database.insert("comments", Comment.create_random_comment(self.database).json)
        response = b"Inserted random comment"
        status = HTTP_STATUS[201]
        return response, status

    def insert_random_user(self) -> (bytes, str):
        """
        Insert random user to the collection
        @return: tuple of byte encoded response, and status in string
        """
        self.database.insert("users", User.add_random_user().json)
        response = b"Inserted random user"
        status = HTTP_STATUS[201]
        return response, status

    def get_article(self, get_input: dict) -> (bytes, str):
        print(get_input, flush=True)
        article_id = ObjectId(get_input["id"][0])
        if "comms" in get_input:
            comm_nmbr = int(get_input["comms"][0])
        else:
            comm_nmbr = 10

        article = self.database.search_one("articles", {"_id": article_id})
        if article is None:
            return b"{}", HTTP_STATUS[204]

        comments = self.database.search_all("comments", {"article_id": article_id})
        comment_count = len(comments)
        if len(comments) > comm_nmbr:
            comments = comments[:comm_nmbr]
        article["comment_list"] = comments
        article["comment_count"] = comment_count

        response = f"<pre>{jsonify(article)}</pre>".encode()
        status = HTTP_STATUS[200]
        return response, status

    def get_articles(self) -> (bytes, str):
        articles = self.database.list_all("articles")
        for article in articles:
            article["comment_count"] = self.database.count("comments", {"article_id": article.get("_id")})
        response = f"<pre>{jsonify(articles)}</pre>".encode()
        status = HTTP_STATUS[200]
        return response, status

    def get_articles_textless(self) -> (bytes, str):
        articles = self.database.list_all("articles")
        for article in articles:
            del article["text"]
        response = f"<pre>{jsonify(articles)}</pre>".encode()
        status = HTTP_STATUS[200]
        return response, status

    def get_users(self) -> (bytes, str):
        response = f"<pre>{jsonify(self.database.list_all("users"))}</pre>".encode()
        status = HTTP_STATUS[200]
        return response, status

    def add_article(self, username: str, post_input: dict) -> (bytes, str):
        user = self.database.search_one("users", {"username": username})
        art = Article(
            post_input["title"],
            post_input["text"],
            datetime.now(),
            user.get("_id"),
            username,
            user.get("email")
        )
        self.database.insert("articles", art.json)
        response = b"Article added"
        status = HTTP_STATUS[201]
        return response, status

    def add_comment(self, username: str, post_input: dict) -> (bytes, str):
        user = self.database.search_one("users", {"username": username})
        self.database.search_one("articles", {"_id": post_input["article_id"]})
        #TODO check no id error
        comment = Comment(
            ObjectId(post_input["article_id"]),
            post_input["text"],
            datetime.now(),
            user.get("_id"),
            username,
            user.get("email")
        )
        self.database.insert("comments", comment.json)
        response = b"Comment added"
        status = HTTP_STATUS[201]
        return response, status

    def add_forbidden(self, post_input: dict) -> (bytes, str):
        if self.database.search_one("forbidden_phrases", {"phrase": post_input["phrase"]}):
            raise ValueError("Phrase already present in forbidden phrases collection")

        self.database.insert("forbidden_phrases", ForbiddenPhrase(post_input["phrase"]).json)
        response = b"Forbidden phrase added"
        status = HTTP_STATUS[201]
        return response, status

    def login(self, post_input: dict) -> (bytes, str):
        response = User.login(
            post_input["login_str"],
            post_input["password"],
            self.database
        ).encode()
        status = HTTP_STATUS[200]
        return response, status

    def register(self, post_input: dict) -> (bytes, str):
        User.register(
            post_input["username"],
            post_input["email"],
            post_input["password"],
            self.database
        )
        response = b"Registration successful"
        status = HTTP_STATUS[201]
        return response, status

    def reset_password(self, post_input: dict) -> (bytes, str):
        User.reset_password(
            post_input["email"],
            post_input["new_password"],
            self.database
        )
        response = b"Password changed successfully"
        status = HTTP_STATUS[200]
        return response, status
