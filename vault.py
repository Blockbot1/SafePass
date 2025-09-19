from dataclasses import dataclass
from typing import List

@dataclass
class VaultEntry:
    site: str
    username: str
    password: str
    notes: str = ""

class Vault:
    def __init__(self):
        self.entries: List[VaultEntry] = []

    def add_entry(self, entry: VaultEntry):
        self.entries.append(entry)

    def remove_entry(self, index: int):
        if 0 <= index < len(self.entries):
            del self.entries[index]

    def get_all_entries(self) -> List[VaultEntry]:
        return self.entries