from http.server import BaseHTTPRequestHandler, HTTPServer

class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        print(f"[Backend B] Request from {self.client_address}")
        self.send_response(200)
        self.send_header("Content-type", "text/plain")
        self.end_headers()
        self.wfile.write(b"Hello from Backend B\n")

server = HTTPServer(("0.0.0.0", 3000), Handler)
print("Backend B running on port 3000")
server.serve_forever()
