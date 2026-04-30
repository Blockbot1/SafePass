import socket
import json

SERVER_HOST = "192.168.24.129"
SERVER_PORT = 9090


def send_frame(s, data):
    s.sendall(len(data).to_bytes(4, "big") + data)


def server_request(action, username, password="", data=None):
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect((SERVER_HOST, SERVER_PORT))

            header_dict = {"action": action, "user": username, "password": password}
            if data:
                header_dict["size"] = len(data)

            header_json = json.dumps(header_dict).encode("utf-8")
            send_frame(s, header_json)

            if action == "upload" and data:
                send_frame(s, data)
                return s.recv(1024).decode()

            if action == "download":
                # Read the length prefix (e.g. "1234\n")
                size_line = b""
                while not size_line.endswith(b"\n"):
                    size_line += s.recv(1)
                size = int(size_line.strip())
                if size == 0:
                    return None  # No vault on server yet
                # Read exactly `size` bytes of encrypted vault data
                buf = b""
                while len(buf) < size:
                    chunk = s.recv(size - len(buf))
                    if not chunk:
                        break
                    buf += chunk
                return buf  # Returns bytes, not str

            return s.recv(1024).decode()
    except Exception as e:
        print(f"Connection Error: {e}")
        return None