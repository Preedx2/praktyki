import wsgiref.simple_server
from source.app import Application

if __name__ == "__main__":
    server = wsgiref.simple_server.make_server(
        host="0.0.0.0",     # KURWAAAAA
        port=8000,
        app=Application
    )
    print("Starting server...")
    server.serve_forever()

