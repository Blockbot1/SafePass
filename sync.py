import socket

SERVER_HOST = "127.0.0.1"  # Change to your server IP if needed
SERVER_PORT = 5000
BUFFER_SIZE = 4096
COMMAND_UPLOAD = "UPLOAD"
COMMAND_DOWNLOAD = "DOWNLOAD"

def upload_vault(file_path: str):
    try:
        with open(file_path, "rb") as f:
            data = f.read()

        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect((SERVER_HOST, SERVER_PORT))
            s.sendall(COMMAND_UPLOAD.encode())
            ack = s.recv(BUFFER_SIZE)

            if ack != b"READY":
                print("Server did not acknowledge upload")
                return

            s.sendall(data)
            print("Vault uploaded successfully.")
    except Exception as e:
        print("Upload failed:", e)

def download_vault(file_path: str):
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect((SERVER_HOST, SERVER_PORT))
            s.sendall(COMMAND_DOWNLOAD.encode())
            s.shutdown(socket.SHUT_WR)

            with open(file_path, "wb") as f:
                while True:
                    chunk = s.recv(BUFFER_SIZE)
                    if not chunk:
                        break
                    f.write(chunk)

            print("Vault downloaded successfully.")
    except Exception as e:
        print("Download failed:", e)
