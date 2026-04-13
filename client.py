import socket
import json

SERVER_HOST = "127.0.0.1"
SERVER_PORT = 9090


def server_request(action, username, password="", data=None):
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect((SERVER_HOST, SERVER_PORT))
            header = {"action": action, "user": username, "password": password}
            if data: header["size"] = len(data)

            s.sendall(json.dumps(header).encode("utf-8"))

            if action == "upload" and data:
                s.sendall(data)
                return s.recv(1024).decode()

            if action == "download":
                size_line = b""
                while not size_line.endswith(b"\n"):
                    chunk = s.recv(1)
                    if not chunk: break
                    size_line += chunk
                size = int(size_line.decode().strip())
                if size == 0: return None
                received = b""
                while len(received) < size:
                    chunk = s.recv(min(4096, size - len(received)))
                    received += chunk
                return received

            return s.recv(1024).decode()
    except:
        return "ERROR"