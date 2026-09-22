import logging
import click
# Import the specific note types and manager
from notes.json_handler import NotebookManager
from notes.models import SimpleNote, BookmarkNote, ListNote

# --- COOL LOGS CONFIGURATION ---
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("notebook_cli.main")

# Create a single instance of the manager to use across commands
manager = NotebookManager()

@click.group()
def cli():
    """Notebook CLI - A professional tool to manage your notes via terminal."""
    pass

# --- 1. COMMAND: LIST ALL NOTES ---
# --- 1. COMMAND: LIST ALL NOTES ---
@cli.command(name="list")
def list_notes():
    """List all notes saved in the system with their specific details."""
    logger.debug("CLI: Requesting list of all notes from NotebookManager.")
    
    if not manager.notes:
        click.echo("Your notebook is currently empty.")
        return
    
    click.echo("\n--- Your Notes ---")
    for note in manager.notes:
        note_id = getattr(note, 'id', 'N/A')
        title = getattr(note, 'title', 'No Title')
        note_type = getattr(note, 'type', 'unknown')
        
        click.echo(f"ID: {note_id} | Title: {title} | Type: [{note_type.upper()}]")
        
        # Display specific content based on the note subclass type
        if isinstance(note, SimpleNote):
            click.echo(f"Text content: {note.text}")
        elif isinstance(note, BookmarkNote):
            click.echo(f"URL: {note.url}")
        elif isinstance(note, ListNote):
            # FIXED: Convert each item to string using str(item) to prevent crashes if numbers exist
            items_str = [str(item) for item in note.list] if note.list else []
            click.echo(f"List Items: {', '.join(items_str) if items_str else 'Empty List'}")
            
        click.echo("-" * 20)

# --- 2. COMMAND: ADD A NEW SIMPLE NOTE ---
# --- 2. COMMAND: ADD A NEW NOTE (SIMPLE, BOOKMARK, OR LIST) ---
@cli.command()
@click.option('--title', '-t', required=True, help='The title of the new note.')
@click.option('--type', 'note_type', type=click.Choice(['simple', 'bookmark', 'list']), default='simple', help='The type of the note.')
@click.option('--content', '-c', default='', help='Text content (for SimpleNote) OR URL (for BookmarkNote) OR comma-separated items (for ListNote).')
def add(title, note_type, content):
    """Add a new note (simple text, bookmark URL, or comma-separated list) to the notebook."""
    logger.debug(f"CLI: Requesting to add a new [{note_type.upper()}] note titled '{title}'")
    
    # Auto-generate a unique incremental ID
    manager.max_id += 1
    new_id = manager.max_id
    
    new_note_obj = None

    # Scenario 1: Creating a BookmarkNote
    if note_type == 'bookmark':
        # The content argument will be treated as the URL
        new_note_obj = BookmarkNote(note_id=new_id, title=title, url=content)
        
    # Scenario 2: Creating a ListNote
    elif note_type == 'list':
        # Split the comma-separated string into a clean Python list
        # Example: "Milk, Bread, Eggs" -> ["Milk", "Bread", "Eggs"]
        items = [item.strip() for item in content.split(',')] if content else []
        new_note_obj = ListNote(note_id=new_id, title=title, items_list=items)
        
    # Scenario 3: Defaulting to a standard SimpleNote
    else:
        new_note_obj = SimpleNote(note_id=new_id, title=title, text=content)
        
    # Append the smart object reference directly to the manager's live notes array
    manager.notes.append(new_note_obj)
    
    # Save the updated data matrix using your manager's build-in method
    success_save = manager.save_data()
    if success_save:
        click.echo(f"Success: [{note_type.upper()}] note '{title}' created with ID: {new_id}.")
    else:
        click.echo("Error: Failed to write the new note object layout to disk.")

# --- 3. COMMAND: DELETE A NOTE BY ID ---
@cli.command()
@click.argument('note_id', type=int)
def delete(note_id):
    """Delete a specific note using its ID."""
    logger.debug(f"CLI: Requesting to delete note ID {note_id}")
    
    note_to_remove = None
    for note in manager.notes:
        if getattr(note, 'id', None) == note_id:
            note_to_remove = note
            break
            
    if note_to_remove:
        manager.notes.remove(note_to_remove)
        success = manager.save_data()
        if success:
            click.echo(f"Success: Note with ID {note_id} has been deleted.")
        else:
            click.echo("Error: Failed to update data file after deletion.")
    else:
        click.echo(f"Error: Note with ID {note_id} was not found in the dataset.")

# --- 4. COMMAND: EDIT TITLE OR TEXT ---
@cli.command()
@click.argument('note_id', type=int)
@click.option('--title', '-t', help='The new title for the note (optional).')
@click.option('--content', '-c', help='The new text content for SimpleNote (optional).')
def edit(note_id, title, content):
    """Edit the title or text content of an existing note."""
    logger.debug(f"CLI: Requesting update for note ID {note_id}")
    
    from datetime import datetime
    found = False
    
    for note in manager.notes:
        if getattr(note, 'id', None) == note_id:
            found = True
            
            # Update title attribute if provided
            if title is not None:
                note.title = title
                
            # Update text content if it's a SimpleNote and content is provided
            if content is not None:
                if isinstance(note, SimpleNote):
                    note.text = content
                else:
                    click.echo("Warning: '--content' can only be updated for SimpleNote types.")
            
            # Update the updatedAt timestamp manually
            note.updated_at = datetime.now().isoformat()
            break
            
    if found:
        manager.save_data()
        click.echo(f"Success: Note {note_id} has been updated.")
    else:
        click.echo(f"Error: Note with ID {note_id} was not found.")

if __name__ == '__main__':
    cli()
