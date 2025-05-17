# dummy_webserver.py
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer

class SimpleHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"OK - DoPing is running")

    def do_HEAD(self):
        self.send_response(200)
        self.end_headers()

    def do_POST(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"POST received - but this server does nothing.")

    def log_message(self, format, *args):
        return  # Suppress console logging

def run_server():
    server = HTTPServer(('0.0.0.0', 10000), SimpleHandler)
    server.serve_forever()

def start():
    thread = threading.Thread(target=run_server)
    thread.daemon = True
    thread.start()
