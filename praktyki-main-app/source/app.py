import json
from datetime import datetime

import jwt
from bson import ObjectId
from bson.json_util import dumps

import source.auth as auth
from source.collections.users import User
from source.collections.articles import Article
from source.collections.comments import Comment
from source.database import Database


class Application:
    """
    Main class of the application, handles user requests
    """
    def __init__(self, environ, start_response):
        """
        Initiates environment and database connection
        :param environ:
        :param start_response:
        """
        self.environ = environ
        self.start_response = start_response

        self.database = Database()

    def __iter__(self):
        """
        Iterator handles request given from the server.py
        Handles most of the exceptions
        :return: response to the server
        """
        print("Received http request")
        path = self.environ['PATH_INFO']
        method = self.environ['REQUEST_METHOD']

        auth_token = None
        if 'HTTP_AUTH' in self.environ:
            auth_token = self.environ['HTTP_AUTH']

        post_input = {}
        if method == "POST":
            input_obj = self.environ['wsgi.input']
            input_len = int(self.environ['CONTENT_LENGTH'])
            post_input = json.loads(input_obj.read(input_len).decode())

        status = "501 Not Implemented"
        response = b"501 Not Implemented"
        match path:
            case "/test":
                art = Article.create_random_article(self.database)
                print(art.author)
                print(type(art.author.get("id")), flush=True)

            case "/insert_random_user":
                User.add_random_user(self.database)
                response = b"Inserted random user"
                status = "200 OK"
            case "/get_users":
                response = response = f"<pre>{dumps(self.database.list_all("users"), 
                                         sort_keys=True, indent=4, separators=(',', ': '))}</pre>".encode()
                status = "200 OK"
            case "/create_article":
                if method == "POST":
                    if auth_token:
                        user_name = auth.authenticate(auth_token)
                        user = self.database.search_one("users", {"username": user_name})
                        art = Article(
                            post_input["title"],
                            post_input["text"],
                            datetime.now(),
                            user.get("_id"),
                            user_name,
                            user.get("email")
                        )
                        self.database.insert("articles", art.json)
                        response = b"Article added"
                        status = "200 OK"
                    else:
                        response = b"You need to log in before posting an Article"
                        status = "403 Forbidden"
            case "/add_comment":
                if method == "POST":
                    if auth_token:
                        user_name = auth.authenticate(auth_token)
                        user = self.database.search_one("users", {"username": user_name})
                        try:
                            self.database.search_one("articles", {"_id": post_input["article_id"]})
                            comment = Comment(
                                ObjectId(post_input["article_id"]),
                                post_input["text"],
                                datetime.now(),
                                user.get("_id"),
                                user_name,
                                user.get("email")
                            )
                            self.database.insert("comments", comment.json)
                            response = b"Comment added"
                            status = "200 OK"
                        except:
                            response = b"Article id not recognized"
                            status = "400 Bad Request"
                    else:
                        response = b"You need to log in before posting a comment"
                        status = "403 Forbidden"
            case "/insert_random_art":
                self.database.insert("articles", Article.create_random_article(self.database).json)
                response = b"Inserted random article"
                status = "200 OK"
            case "/get_articles_comentless":
                articles = self.database.list_all("articles")
                for article in articles:
                    del article["text"]
                response = f"<pre>{dumps(articles, sort_keys=True, indent=2, separators=(',', ': '))}</pre>".encode()
                status = "200 OK"
            case "/insert_random_comment":
                self.database.insert("comments", Comment.create_random_comment(self.database).json)
                response = b"Inserted random comment"
                status = "200 OK"
            case "/get_articles":
                articles = self.database.list_all("articles")
                for article in articles:
                    article["comment_count"] = self.database.count("comments", {"article_id": article.get("_id")})
                response = f"<pre>{dumps(articles, sort_keys=True, indent=2, separators=(',', ': '))}</pre>".encode()
                status = "200 OK"
            case "/register":
                if method == "POST":
                    try:
                        auth.register(
                                post_input["username"],
                                post_input["email"],
                                post_input["password"],
                                self.database
                            )
                        response = b"Successful registration"
                        status = "200 OK"
                    except Exception as e:
                        print(e)
                        response = f"Error: {e}".encode()
                        status = "400 Bad Request"
                else:
                    response = b"405 Method not allowed"
                    status = "405 Method not allowed"
            case "/login":
                if method == "POST":
                    try:
                        response = auth.login(
                            post_input["login_str"],
                            post_input["password"],
                            self.database
                        ).encode()
                        status = "200 OK"
                    except Exception as e:
                        print(e)
                        response = f"Error of type: {type(e)}".encode()
                        status = "400 Bad Request"
                else:
                    response = b"405 Method not allowed"
                    status = "405 Method not allowed"
            case "/reset_password":
                if method == "POST":
                    try:
                        auth.reset_password(
                            post_input["email"],
                            post_input["new_password"],
                            self.database
                        )
                        response = b"Password changed successfully"
                        status = "200 OK"
                    except Exception as e:
                        print(e)
                        response = f"Error of type: {type(e)}".encode()
                        status = "400 Bad Request"
                else:
                    response = b"405 Method not allowed"
                    status = "405 Method not allowed"
            case "/protected":
                try:
                    name = auth.authenticate(auth_token)
                    response = f"Welcome {name}".encode()
                    status = "200 OK"
                except (jwt.exceptions.ExpiredSignatureError, jwt.exceptions.InvalidSignatureError) as e:
                    response = f"{e}".encode()
                    status = "403 Forbidden"
                except jwt.exceptions.DecodeError:
                    response = b"You need to be authenticated to access this page"
                    status = "403 Forbidden"
            case _:
                response = b"404 Not Found"
                status = "404 Not Found"
        headers = [
            ("Content-Type", "text/html"),
            ("content-Length", str(len(response)))
        ]
        self.start_response(status, headers)

        yield response
