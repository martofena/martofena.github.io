from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import urlparse
import http.client
import json

CKAN_HOST = "ckan.fdm.uni-greifswald.de"
CKAN_API_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJqdGkiOiJfWGJkNTJvdDgyMXFCVUl6ZXN1MzRrMzViRlZudXdEZlJ2eU5OcWJQNXFjIiwiaWF0IjoxNzcwNDcyOTQ5fQ.rlcQ5Q46kLps6T8zqYofX46A-aAenIid_e5LWg3UZQQ"


class CkanProxyHandler(BaseHTTPRequestHandler):

    # ------------------------------------------------------
    # GET -> CKAN JSON API (unchanged)
    # ------------------------------------------------------

    def do_GET(self):
        parsed = urlparse(self.path)

        if not parsed.path.startswith("/api/ckan"):
            self.send_error(404, "Not found")
            return

        # Map to CKAN action API
        ckan_path = parsed.path.replace("/api/ckan", "/api/3/action", 1)
        full_path = f"{ckan_path}?{parsed.query}" if parsed.query else ckan_path

        print("Forwarding to:", full_path)

        try:
            # 🔥 IMPORTANT FIX: HTTPSConnection
            conn = http.client.HTTPSConnection(CKAN_HOST, timeout=20)

            headers = {
                "Authorization": CKAN_API_KEY,
                "Accept": "application/json"
            }

            conn.request("GET", full_path, headers=headers)
            resp = conn.getresponse()
            data = resp.read()

            print("CKAN response status:", resp.status)

            self.send_response(resp.status)
            self.send_header("Content-Type", "application/json")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()

            self.wfile.write(data)
            conn.close()

        except Exception as e:
            print("Proxy error:", e)
            self.send_error(500, str(e))


def run():
    server = HTTPServer(("0.0.0.0", 8001), CkanProxyHandler)
    print("CKAN proxy running on http://localhost:8001/api/ckan")
    server.serve_forever()


if __name__ == "__main__":
    run()