import socket
import json

SERVER_HOST = "192.168.24.129"
SERVER_PORT = 9090


def send_frame(s, data):
    # Send the length of the data first (4 bytes), then the data
    s.sendall(len(data).to_bytes(4, "big") + data)


def server_request(action, username, password="", data=None):
    try:
        # We use 'with' to create the socket 's'
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect((SERVER_HOST, SERVER_PORT))

            header_dict = {"action": action, "user": username, "password": password}
            if data:
                header_dict["size"] = len(data)

            header_json = json.dumps(header_dict).encode("utf-8")

            # Now 's' is defined, so this will work!
            send_frame(s, header_json)

            if action == "upload" and data:
                send_frame(s, data)
                return s.recv(1024).decode()

            # ... rest of your download/login logic ...
            return s.recv(1024).decode()
    except Exception as e:
        print(f"Connection Error: {e}")
        return "ERROR"