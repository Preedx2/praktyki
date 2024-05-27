import wsgiref.simple_server
from source.app import Application

if __name__ == "__main__":
    server = wsgiref.simple_server.make_server(
        host="0.0.0.0",
        port=8000,
        app=Application
    )
    print("Server started", flush=True)
    server.serve_forever()

