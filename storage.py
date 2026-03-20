from pathlib import Path
from vault import Vault, BaseEntry, PasswordEntry  # Updated imports
from crypto import encrypt, decrypt
import json

VAULT_FILE = Path("safepass.vault")


def save_vault(master_password: str, vault: Vault):
    data = []
    for entry in vault.get_all_entries():
        # Convert entry to dict and add a 'type' field to identify the class
        entry_dict = entry.__dict__.copy()
        entry_dict["type"] = entry.__class__.__name__
        data.append(entry_dict)

    json_bytes = json.dumps(data, ensure_ascii=False, indent=2).encode("utf-8")
    encrypted = encrypt(master_password, json_bytes)
    VAULT_FILE.write_bytes(encrypted)


def load_vault(master_password: str) -> Vault:
    if not VAULT_FILE.exists():
        return Vault()

    encrypted = VAULT_FILE.read_bytes()
    decrypted = decrypt(master_password, encrypted)
    entries_data = json.loads(decrypted.decode("utf-8"))

    vault = Vault()
    for item in entries_data:
        # Determine which class to instantiate based on the saved 'type'
        entry_type = item.pop("type", "PasswordEntry")

        if entry_type == "PasswordEntry":
            vault.add_entry(PasswordEntry(**item))
        else:
            vault.add_entry(BaseEntry(**item))

    return vault