# dummy_webserver.py
import os
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer

class SimpleHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"OK - DoPing is running")

def run_server():
    PORT = int(os.environ.get("PORT", 10000))  # Use Render's PORT if set
    server = HTTPServer(('0.0.0.0', PORT), SimpleHandler)
    server.serve_forever()

def start():
    thread = threading.Thread(target=run_server)
    thread.daemon = True
    thread.start()