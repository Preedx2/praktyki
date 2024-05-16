import wsgiref.simple_server
from app.app import Application

if __name__ == "__main__":
    server = wsgiref.simple_server.make_server(
        host="localhost",
        port=8000,
        app=Application
    )
    server.serve_forever()

# with open("mongodb-login", 'r') as file:
#     _cluster = file.readline()[:-1]
#     _login = file.readline()[:-1]
#     _password = file.readline()[:-1]
#
# uri = f"mongodb+srv://{_login}:{_password}@{_cluster}.mongodb.net/?retryWrites=true&w=majority&appName=praktyki0"
#
# # Create a new client and connect to the server
# client = MongoClient(uri, server_api=ServerApi('1'))
# # Send a ping to confirm a successful connection
# try:
#     database = client.get_database("sample_mflix")
#     movies = database.get_collection("movies")
#
#     query = {"title": "Back to the Future"}
#     movie = movies.find_one(query)
#
#     print(movie)
#
#     client.close()
# except Exception as e:
#     print(e)
