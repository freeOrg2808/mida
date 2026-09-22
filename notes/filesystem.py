import json
import os

FILE_NAME = "notes.json"

class FileSystem:
    @staticmethod
    def save_data(data: dict) -> bool:
        """Receives a dictionary and writes it to the JSON file."""
        try:
            with open(FILE_NAME, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=4, ensure_ascii=False)
            return True
        except Exception:
            return False

    @staticmethod
    def load_data() -> dict:
        """Reads the JSON file and returns its dictionary content, or empty framework."""
        if not os.path.exists(FILE_NAME):
            return {}
        try:
            with open(FILE_NAME, "r", encoding="utf-8") as f:
                return json.load(f)
        except json.JSONDecodeError:
            return {}
