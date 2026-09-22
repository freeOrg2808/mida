from __future__ import annotations

from datetime import datetime

class BaseNote:
    def __init__(self, note_id: int, title: str, created_at=None, updated_at=None):
        self.id = note_id
        self.title = title
        self.created_at = created_at or datetime.now().isoformat()
        self.updated_at = updated_at or datetime.now().isoformat()

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "title": self.title,
            "createdAt": self.created_at,
            "updatedAt": self.updated_at
        }

    def display(self):
        print(f"[{self.id}] | Title: {self.title}")

    @classmethod
    def load_note_data(cls, data: dict) -> tuple[bool, 'BaseNote']:
        """
        Class factory method that verifies data and hydrates the correct note subclass.
        
        Returns:
            tuple: (bool_success, note_object_reference)
        """
        try:
            note_type = data.get("type")
            
            # Validation check: if required fields are missing, return failure
            if "id" not in data or "title" not in data:
                return False, None

            # Match and build the correct object based on the note type
            if note_type == "simple":
                return True, SimpleNote(data["id"], data["title"], data.get("text", ""), data.get("createdAt"), data.get("updatedAt"))
            elif note_type == "bookmark":
                return True, BookmarkNote(data["id"], data["title"], data.get("url", ""), data.get("createdAt"), data.get("updatedAt"))
            elif note_type == "list":
                return True, ListNote(data["id"], data["title"], data.get("list", []), data.get("createdAt"), data.get("updatedAt"))
            
            return False, None
        except Exception:
            return False, None


class SimpleNote(BaseNote):
    def __init__(self, note_id: int, title: str, text: str, created_at=None, updated_at=None):
        super().__init__(note_id, title, created_at, updated_at)
        self.text = text
        self.type = "simple"

    def to_dict(self) -> dict:
        data = super().to_dict()
        data.update({"type": self.type, "text": self.text})
        return data


class BookmarkNote(BaseNote):
    def __init__(self, note_id: int, title: str, url: str, created_at=None, updated_at=None):
        super().__init__(note_id, title, created_at, updated_at)
        self.url = url
        self.type = "bookmark"

    def to_dict(self) -> dict:
        data = super().to_dict()
        data.update({"type": self.type, "url": self.url})
        return data


class ListNote(BaseNote):
    def __init__(self, note_id: int, title: str, items_list: list, created_at=None, updated_at=None):
        super().__init__(note_id, title, created_at, updated_at)
        self.list = items_list
        self.type = "list"

    def to_dict(self) -> dict:
        data = super().to_dict()
        data.update({"type": self.type, "list": self.list})
        return data
