import logging
from datetime import datetime
from notes.filesystem import FileSystem  
from notes.models import BaseNote

# ONLY get the child logger. DO NOT call basicConfig here.
logger = logging.getLogger("notebook_cli.manager")

class NotebookManager:
    def __init__(self):
        self.max_id = 0
        self.notes: list[BaseNote] = []  
        self.load_data()

    def load_data(self) -> bool:
        """Reads the JSON file via FileSystem and restores pure Python objects into memory."""
        logger.debug("Manager: Requesting raw data from FileSystem layer...")
        data = FileSystem.load_data()
        
        if not data:
            logger.warning("No data found or file is empty during loading.")
            return False
            
        self.max_id = data.get("maxid", 0)
        self.notes.clear()
        
        for n in data.get("notes", []):
            success, obj = BaseNote.load_note_data(n)
            
            if success and obj:
                self.notes.append(obj)
                logger.debug(f"Loaded note ID {obj.id} via reference classmethod.")
            else:
                logger.error(f"Failed to load specific note data structure for: {n}")
                return False
                
        logger.info(f"Successfully populated memory with {len(self.notes)} notes references.")
        return True

    def save_data(self) -> bool:
        """Converts all smart objects back to JSON layout and stores them via FileSystem."""
        logger.debug("Manager: Serializing object matrix back to dictionaries...")
        serialized_notes = [note.to_dict() for note in self.notes]
        payload = {"maxid": self.max_id, "notes": serialized_notes}
        
        success = FileSystem.save_data(payload)
        if success:
            logger.info("Database matrix successfully stored via FileSystem layer.")
            return True
        else:
            logger.error("FileSystem write operation failed completely.")
            return False

    def update_note_title(self, note_id: int, new_title: str) -> bool:
        """Finds note reference and updates title attribute using logger."""
        logger.debug(f"Attempting to locate note ID {note_id} for title modification.")
        found = False
        
        for note in self.notes:
            if note.id == note_id:
                note.title = new_title
                note.updated_at = datetime.now().isoformat()
                found = True
                logger.info(f"Note title updated in memory wrapper for ID {note_id}.")
                break
                
        if not found:
            logger.warning(f"Aborted: Target ID {note_id} does not exist in dataset.")
            return False

        return self.save_data()
