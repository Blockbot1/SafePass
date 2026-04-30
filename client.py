import socket
import json

SERVER_HOST = "192.168.24.129"
SERVER_PORT = 9090


def send_frame(s, data):
    # Send the length of the data first (4 bytes), then the data
    s.sendall(len(data).to_bytes(4, "big") + data)

def server_request(action, username, password="", data=None):
    # ... setup socket ...
    header = json.dumps({"action": action, "user": username, "password": password}).encode()
    send_frame(s, header) # Use a frame for the header

    if action == "upload" and data:
        send_frame(s, data) # Use a frame for the vault data
    # ...