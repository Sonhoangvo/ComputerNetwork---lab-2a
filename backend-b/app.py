import ssl
from http.server import BaseHTTPRequestHandler, HTTPServer

class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        print(f"[Backend B] Request from {self.client_address}")
        self.send_response(200)
        self.send_header("Content-type", "text/plain")
        self.end_headers()
        self.wfile.write(b"Hello from Backend B\n")

server = HTTPServer(("0.0.0.0", 3000), Handler)

# Serve HTTPS so gateway-to-backend traffic is also encrypted.
tls_context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
tls_context.load_cert_chain(certfile="/certs/backend.crt", keyfile="/certs/backend.key")
server.socket = tls_context.wrap_socket(server.socket, server_side=True)

print("Backend B running on HTTPS port 3000")
server.serve_forever()
