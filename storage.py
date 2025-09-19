from pathlib import Path
from vault import Vault, VaultEntry
from crypto import encrypt, decrypt
import json

VAULT_FILE = Path("safepass.vault")

def save_vault(master_password: str, vault: Vault):
    # Convert entries to list of dictionaries
    data = [entry.__dict__ for entry in vault.get_all_entries()]
    json_bytes = json.dumps(data, ensure_ascii=False, indent=2).encode("utf-8")
    encrypted = encrypt(master_password, json_bytes)
    VAULT_FILE.write_bytes(encrypted)

def load_vault(master_password: str) -> Vault:
    if not VAULT_FILE.exists():
        return Vault()  # Empty vault if no file yet

    encrypted = VAULT_FILE.read_bytes()
    decrypted = decrypt(master_password, encrypted)
    entries_data = json.loads(decrypted.decode("utf-8"))

    vault = Vault()
    for item in entries_data:
        vault.add_entry(VaultEntry(**item))
    return vault