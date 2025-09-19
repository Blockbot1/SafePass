import socket
import threading
import json
from pathlib import Path

# Folder to store encrypted vaults
VAULTS_DIR = Path("vault_sync_storage")
VAULTS_DIR.mkdir(exist_ok=True)

HOST = "0.0.0.0"  # Listen on all interfaces
PORT = 9090       # Change if needed

def handle_client(conn, addr):
    try:
        with conn:
            print(f"[+] Connected: {addr}")

            header = conn.recv(4096).decode("utf-8")
            data = json.loads(header)
            action = data.get("action")
            username = data.get("user")

            if not username:
                conn.sendall(b"Missing username")
                return

            user_file = VAULTS_DIR / f"{username}.vault"

            if action == "upload":
                size = int(data.get("size", 0))
                received = b""
                while len(received) < size:
                    chunk = conn.recv(min(4096, size - len(received)))
                    if not chunk:
                        break
                    received += chunk
                user_file.write_bytes(received)
                conn.sendall(b"OK")

            elif action == "download":
                if not user_file.exists():
                    conn.sendall(b"0\n")
                    return
                data = user_file.read_bytes()
                conn.sendall(f"{len(data)}\n".encode("utf-8"))
                conn.sendall(data)

            else:
                conn.sendall(b"Unknown action")

    except Exception as e:
        print(f"[!] Error with {addr}: {e}")

def start_server():
    print(f"[*] Server starting on port {PORT}...")
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server:
        server.bind((HOST, PORT))
        server.listen()

        while True:
            conn, addr = server.accept()
            threading.Thread(target=handle_client, args=(conn, addr), daemon=True).start()

if __name__ == "__main__":
    start_server()
