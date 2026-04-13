from pathlib import Path
from vault import Vault, BaseEntry, PasswordEntry
from crypto import encrypt, decrypt
import json

def get_user_path(username: str) -> Path:
    return Path(f"{username}.vault")

def save_vault(username: str, master_password: str, vault: Vault):
    data = []
    for entry in vault.get_all_entries():
        entry_dict = entry.__dict__.copy()
        entry_dict["type"] = entry.__class__.__name__
        data.append(entry_dict)

    json_bytes = json.dumps(data, ensure_ascii=False, indent=2).encode("utf-8")
    encrypted = encrypt(master_password, json_bytes)
    get_user_path(username).write_bytes(encrypted)

def save_vault_raw(username: str, data: bytes):
    """Saves encrypted bytes directly (used during sync)."""
    get_user_path(username).write_bytes(data)

def load_vault(username: str, master_password: str) -> Vault:
    user_file = get_user_path(username)
    if not user_file.exists() or user_file.stat().st_size == 0:
        return Vault()

    try:
        encrypted = user_file.read_bytes()
        decrypted = decrypt(master_password, encrypted)
        entries_data = json.loads(decrypted.decode("utf-8"))

        vault = Vault()
        for item in entries_data:
            entry_type = item.pop("type", "PasswordEntry")
            if entry_type == "PasswordEntry":
                vault.add_entry(PasswordEntry(**item))
            else:
                vault.add_entry(BaseEntry(**item))
        return vault
    except Exception:
        # If decryption fails (wrong password), the app handles the error
        raise Exception("Decryption failed")