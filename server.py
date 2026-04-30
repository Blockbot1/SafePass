import socket
import threading
import json
import sqlite3
import hashlib
from pathlib import Path

VAULTS_DIR = Path("vault_sync_storage")
VAULTS_DIR.mkdir(exist_ok=True)
DB_PATH = "users.db"
HOST = "0.0.0.0"
PORT = 9090


def init_db():
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute("CREATE TABLE IF NOT EXISTS users (username TEXT PRIMARY KEY, password_hash TEXT)")


def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()


def handle_client(conn, addr):
    try:
        with conn:
            header_data = conn.recv(4096).decode("utf-8")
            if not header_data: return
            request = json.loads(header_data)
            action = request.get("action")
            username = request.get("user")
            pwd = request.get("password")

            with sqlite3.connect(DB_PATH) as db:
                cursor = db.cursor()

                if action == "register":
                    try:
                        cursor.execute("INSERT INTO users VALUES (?, ?)", (username, hash_password(pwd)))
                        db.commit()
                        # Create empty vault file for new user
                        (VAULTS_DIR / f"{username}.vault").write_bytes(b"")
                        conn.sendall(b"SUCCESS")
                    except sqlite3.IntegrityError:
                        conn.sendall(b"EXISTS")

                elif action == "login":
                    cursor.execute("SELECT password_hash FROM users WHERE username=?", (username,))
                    row = cursor.fetchone()
                    if row and row[0] == hash_password(pwd):
                        conn.sendall(b"SUCCESS")
                    else:
                        conn.sendall(b"FAIL")


                elif action == "upload":

                    try:

                        size = int(request.get("size", 0))

                        received = b""

                        # Use a timeout so the server doesn't hang if the client stops

                        conn.settimeout(5.0)

                        while len(received) < size:

                            chunk = conn.recv(min(4096, size - len(received)))

                            if not chunk: break

                            received += chunk

                        # Ensure the directory exists right before writing test

                        VAULTS_DIR.mkdir(exist_ok=True)

                        save_path = VAULTS_DIR / f"{username}.vault"

                        save_path.write_bytes(received)

                        print(f"Successfully saved vault for {username}")

                        conn.sendall(b"OK")

                    except Exception as e:

                        print(f"Upload write error: {e}")

                        conn.sendall(b"ERROR")

                elif action == "download":
                    user_file = VAULTS_DIR / f"{username}.vault"
                    if not user_file.exists():
                        conn.sendall(b"0\n")
                    else:
                        data = user_file.read_bytes()
                        conn.sendall(f"{len(data)}\n".encode("utf-8"))
                        conn.sendall(data)
    except Exception as e:
        print(f"Error: {e}")


def recv_exact(conn, n):
    buf = b""
    while len(buf) < n:
        chunk = conn.recv(n - len(buf))
        if not chunk: raise ConnectionError("Connection lost")
        buf += chunk
    return buf

def recv_frame(conn):
    # Read the 4-byte header to know how much data is coming
    hdr = recv_exact(conn, 4)
    length = int.from_bytes(hdr, "big")
    return recv_exact(conn, length)

if __name__ == "__main__":
    init_db()
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((HOST, PORT))
    server.listen()
    print(f"Server listening on {HOST}:{PORT}")
    while True:
        c, a = server.accept()
        threading.Thread(target=handle_client, args=(c, a), daemon=True).start()