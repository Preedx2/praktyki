import wsgiref.simple_server
from app.app import Application

if __name__ == "__main__":
    server = wsgiref.simple_server.make_server(
        host="localhost",
        port=8000,
        app=Application
    )
    server.serve_forever()

