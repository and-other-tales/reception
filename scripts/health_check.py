import http.server
import socketserver
import threading
import logging
import os

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("health_check")

# Get port from environment variable or use default
PORT = int(os.environ.get("PORT", 8080))

class HealthCheckHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/health' or self.path == '/':
            self.send_response(200)
            self.send_header('Content-type', 'text/plain')
            self.end_headers()
            self.wfile.write(b'OK')
        else:
            self.send_response(404)
            self.send_header('Content-type', 'text/plain')
            self.end_headers()
            self.wfile.write(b'Not Found')
    
    def log_message(self, format, *args):
        logger.info("%s - - [%s] %s" % (self.client_address[0], self.log_date_time_string(), format % args))

def start_health_server():
    handler = HealthCheckHandler
    with socketserver.TCPServer(("", PORT), handler) as httpd:
        logger.info(f"Health check server started at port {PORT}")
        httpd.serve_forever()

def run_health_server():
    # Start the health check server in a separate thread
    health_thread = threading.Thread(target=start_health_server, daemon=True)
    health_thread.start()
    return health_thread
