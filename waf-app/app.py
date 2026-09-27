from flask import Flask, request, Response
import requests
import re
import redis

app = Flask(__name__)

BACKEND_URL = "http://backend-app:5000"
r = redis.Redis(host='redis', port=6379, decode_responses=True)

MALICIOUS_PATTERNS = [
    r"\.\./",
    r"etc/passwd",
    r"<script>",
    r"union.*select",
    r"drop.*table",
]

BAN_DURATION_SECONDS = 300

@app.route('/', defaults={'path': ''}, methods=['GET', 'POST'])
@app.route('/<path:path>', methods=['GET', 'POST'])
def gatekeeper(path):
    client_ip = request.headers.get('X-Forwarded-For', request.remote_addr)

    if r.get(f"banned:{client_ip}"):
        return Response("Your IP is banned by Sentinel WAF", status=403)

    full_url = request.url
    query = request.query_string.decode()

    for pattern in MALICIOUS_PATTERNS:
        if re.search(pattern, full_url, re.IGNORECASE) or re.search(pattern, query, re.IGNORECASE):
            r.setex(f"banned:{client_ip}", BAN_DURATION_SECONDS, "1")
            return Response("Blocked by Sentinel WAF - IP now banned", status=403)

    try:
        resp = requests.request(
            method=request.method,
            url=f"{BACKEND_URL}/{path}",
            params=request.args,
            data=request.get_data(),
            headers={k: v for k, v in request.headers if k.lower() != 'host'}
        )
        return Response(resp.content, status=resp.status_code)
    except Exception as e:
        return Response(f"Backend unreachable: {e}", status=502)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
