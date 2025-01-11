import socket
import json

LOGSTASH_HOST = "localhost"
LOGSTASH_PORT = 5000

log_message = {
    "message": "Test log from Python",
    "service": "backend",
    "module": "test"
}

try:
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((LOGSTASH_HOST, LOGSTASH_PORT))
    sock.sendall((json.dumps(log_message) + "\n").encode("utf-8"))
    print("Message sent to Logstash")
    sock.close()
except Exception as e:
    print(f"Error: {e}")
