import socket
import json
from pathlib import Path

SERVER_HOST = "127.0.0.1"
SERVER_PORT = 9090
VAULT_FILE = Path("safepass.vault")

def upload_vault(username: str):
    if not VAULT_FILE.exists():
        print("Vault file not found.")
        return

    data = VAULT_FILE.read_bytes()
    header = {
        "action": "upload",
        "user": username,
        "size": len(data)
    }

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((SERVER_HOST, SERVER_PORT))
        s.sendall(json.dumps(header).encode("utf-8"))
        s.sendall(data)
        response = s.recv(1024)
        print("Server response:", response.decode())

def download_vault(username: str):
    header = {
        "action": "download",
        "user": username
    }

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((SERVER_HOST, SERVER_PORT))
        s.sendall(json.dumps(header).encode("utf-8"))

        size_line = b""
        while not size_line.endswith(b"\n"):
            chunk = s.recv(1)
            if not chunk:
                print("Connection closed unexpectedly.")
                return
            size_line += chunk

        size = int(size_line.decode("utf-8").strip())
        if size == 0:
            print("No vault file found on server.")
            return

        received = b""
        while len(received) < size:
            chunk = s.recv(min(4096, size - len(received)))
            if not chunk:
                break
            received += chunk

        VAULT_FILE.write_bytes(received)
        print(f"Downloaded {len(received)} bytes.")


