import time

from pymongo import MongoClient
from pymongo.server_api import ServerApi


class Censor:
    def __init__(self):
        with open("mongodb-login", 'r') as file:
            _cluster = file.readline()[:-1]
            _login = file.readline()[:-1]
            _password = file.readline()[:-1]

        uri = f"mongodb+srv://{_login}:{_password}@{_cluster}.mongodb.net/?retryWrites=true&w=majority&appName=praktyki0"
        client = MongoClient(uri, server_api=ServerApi('1'))
        database = client.get_database("praktyki_app_db")
        self.comments = database["comments"]

        self.pipeline = [
            {"$match": {"operationType": "insert"}},
        ]

        self.phrases = ["kupa", "dupa"]

    def __del__(self):
        if hasattr(self, 'client'):
            self.client.close()

    def process_text(self, comment) -> None:

        replacement = "[REDACTED]"
        new_text = comment.get("text")
        for phrase in self.phrases:
            if phrase in new_text:
                new_text = new_text.replace(phrase, replacement)
                print(f"Replaced forbidden phrase {phrase} in comment {comment.get("_id")}", flush=True)
        self.comments.update_one({'_id': comment.get("_id")},
                                 {"$set": {"text": new_text}})

    def listen(self):
        with self.comments.watch(self.pipeline) as stream:
            print("Listening for inserts in comments collection...", flush=True)
            for change in stream:
                self.process_text(change.get("fullDocument"))


if __name__ == "__main__":
    censor = Censor()
    try:
        while True:
            censor.listen()
    except KeyboardInterrupt:
        print("Listener has been manually shutdown")


