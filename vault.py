from dataclasses import dataclass, asdict
from typing import List

@dataclass
class BaseEntry:
    """
    Parent Class (Base): Demonstrates Inheritance.
    Contains common fields used by any type of secret item.
    """
    site: str
    notes: str = ""

    def get_summary(self) -> str:
        """A base method that can be overridden (Polymorphism)."""
        return f"Entry for {self.site}"

@dataclass
class PasswordEntry(BaseEntry):
    """
    Child Class: Inherits from BaseEntry.
    Adds specific fields for password management.
    """
    username: str = ""
    password: str = ""

    def get_summary(self) -> str:
        """Overriding the base method (Polymorphism)."""
        return f"Account: {self.username} @ {self.site}"

class Vault:
    """
    Manager Class: Demonstrates Encapsulation.
    Handles the collection of entry objects.
    """
    def __init__(self):
        # This list can now hold any object that inherits from BaseEntry
        self.entries: List[BaseEntry] = []

    def add_entry(self, entry: BaseEntry):
        self.entries.append(entry)

    def remove_entry(self, index: int):
        if 0 <= index < len(self.entries):
            del self.entries[index]

    def get_all_entries(self) -> List[BaseEntry]:
        return self.entries