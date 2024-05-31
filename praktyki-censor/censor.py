from pymongo import MongoClient
from pymongo.server_api import ServerApi


DEVELOPMENT = True


class Censor:
    def __init__(self):
        with open("mongodb-login", 'r') as file:
            _cluster = file.readline()[:-1]
            _login = file.readline()[:-1]
            _password = file.readline()[:-1]

        uri = f"mongodb+srv://{_login}:{_password}@{_cluster}.mongodb.net/?retryWrites=true&w=majority&appName=praktyki0"
        self.client = MongoClient(uri, server_api=ServerApi('1'))
        self.database = self.client.get_database("praktyki_app_db")
        self.comments = self.database["comments"]

        self.pipeline = [
            {"$match": {"operationType": {'$in': ['insert', 'update']}}},
        ]

        self.replacement = "[REDACTED]"
        self.phrases = self.load_phrases()

    def __del__(self):
        if hasattr(self, 'client'):
            self.client.close()

    def load_phrases(self) -> list[str]:
        collection = self.database.get_collection("forbidden_phrases")
        phrases = [x.get("phrase") for x in collection.find({})]
        for phrase in phrases:
            if phrase in self.replacement:
                raise RuntimeError(f"Forbidden phrase {phrase} found in replacement phrase {self.replacement}."
                                   f"Cannot load phrase list because of risk of cascade")

        if DEVELOPMENT:
            print(phrases, flush=True)

        return phrases

    def process_text(self, text, comment_id):
        self.phrases = self.load_phrases()
        changes = False
        new_text = text
        for phrase in self.phrases:
            if phrase in new_text:
                new_text = new_text.replace(phrase, self.replacement)
                changes = True
                print(f"Replaced forbidden phrase {phrase} in comment {comment_id}", flush=True)
        if changes:
            self.comments.update_one({'_id': comment_id}, {"$set": {"text": new_text}})

    def listen(self):
        with self.comments.watch(self.pipeline) as stream:
            print("Listening for inserts in comments collection...", flush=True)
            for change in stream:
                if change.get("operationType") == 'insert':
                    text = change.get("fullDocument").get("text")
                    comment_id = change.get("fullDocument").get("_id")
                else:
                    text = change.get("updateDescription").get("updatedFields").get("text")
                    comment_id = change.get("documentKey").get("_id")

                self.process_text(text, comment_id)


if __name__ == "__main__":
    try:
        censor = Censor()
        while True:
            censor.listen()
    except KeyboardInterrupt:
        print("Listener has been manually shutdown")
    except RuntimeError as e:
        print(e)
