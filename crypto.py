import os #Allows access to os features (Used for generating random numbers used in the encryption
import json
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC #Imports the key derivation function that uses the salt and password to generate the encryption
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

KDF_ITERATIONS = 200_000
KEY_LENGTH = 32

def derive_key(master_password: str, salt: bytes) -> bytes:
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=KEY_LENGTH,
        salt=salt,
        iterations=KDF_ITERATIONS,
    )
    return kdf.derive(master_password.encode("utf-8"))

def encrypt(master_password: str, plaintext: bytes) -> bytes:
    salt = os.urandom(16)
    nonce = os.urandom(12)
    key = derive_key(master_password, salt)
    aes = AESGCM(key)
    ciphertext = aes.encrypt(nonce, plaintext, associated_data=None)

    blob = {
        "salt": salt.hex(),
        "nonce": nonce.hex(),
        "ciphertext": ciphertext.hex(),
        "kdf": {"iterations": KDF_ITERATIONS}
    }
    return json.dumps(blob).encode("utf-8")

def decrypt(master_password: str, blob_bytes: bytes) -> bytes:
    blob = json.loads(blob_bytes.decode("utf-8"))
    salt = bytes.fromhex(blob["salt"])
    nonce = bytes.fromhex(blob["nonce"])
    ciphertext = bytes.fromhex(blob["ciphertext"])

    key = derive_key(master_password, salt)
    aes = AESGCM(key)
    return aes.decrypt(nonce, ciphertext, associated_data=None)