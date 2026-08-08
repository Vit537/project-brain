"""
File Operations Module
Handles all file system operations (create, delete, move, etc.)
"""
import os
import shutil
from pathlib import Path
from datetime import datetime
from colorama import Fore, Style, init

init(autoreset=True)


class FileOperations:
    def __init__(self):
        # Default locations for quick access
        self.desktop = os.path.join(os.path.expanduser("~"), "Desktop")
        self.documents = os.path.join(os.path.expanduser("~"), "Documents")
        self.downloads = os.path.join(os.path.expanduser("~"), "Downloads")
        self.notes_folder = os.path.join(self.documents, "JARVIS_Notes")
        
        # Create notes folder if it doesn't exist
        os.makedirs(self.notes_folder, exist_ok=True)
        
        print(f"{Fore.GREEN}✓ File operations system ready{Style.RESET_ALL}")
    
    def create_folder(self, folder_name, location):
        """
        Create a new folder
        
        Args:
            folder_name (str): Name of the folder
            location (str): Path where to create the folder
            
        Returns:
            tuple: (success: bool, message: str)
        """
        try:
            # Construct full path
            full_path = os.path.join(location, folder_name)
            
            # Check if already exists
            if os.path.exists(full_path):
                return False, f"Folder '{folder_name}' already exists in {location}"
            
            # Create the folder
            os.makedirs(full_path, exist_ok=True)
            
            print(f"{Fore.GREEN}✓ Created: {full_path}{Style.RESET_ALL}")
            return True, f"Folder '{folder_name}' created successfully in {location}"
            
        except PermissionError:
            return False, f"Permission denied to create folder in {location}"
            
        except Exception as e:
            return False, f"Error creating folder: {str(e)}"
    
    def delete_folder(self, folder_name, location):
        """
        Delete a folder
        
        Args:
            folder_name (str): Name of the folder
            location (str): Path where the folder is located
            
        Returns:
            tuple: (success: bool, message: str)
        """
        try:
            full_path = os.path.join(location, folder_name)
            
            if not os.path.exists(full_path):
                return False, f"Folder '{folder_name}' not found in {location}"
            
            shutil.rmtree(full_path)
            
            print(f"{Fore.GREEN}✓ Deleted: {full_path}{Style.RESET_ALL}")
            return True, f"Folder '{folder_name}' deleted successfully"
            
        except PermissionError:
            return False, f"Permission denied to delete folder"
            
        except Exception as e:
            return False, f"Error deleting folder: {str(e)}"
    
    def create_file(self, file_name, location, content=""):
        """
        Create a new file
        
        Args:
            file_name (str): Name of the file
            location (str): Path where to create the file
            content (str): Initial content for the file
            
        Returns:
            tuple: (success: bool, message: str)
        """
        try:
            full_path = os.path.join(location, file_name)
            
            if os.path.exists(full_path):
                return False, f"File '{file_name}' already exists"
            
            with open(full_path, 'w') as f:
                f.write(content)
            
            print(f"{Fore.GREEN}✓ Created: {full_path}{Style.RESET_ALL}")
            return True, f"File '{file_name}' created successfully"
            
        except Exception as e:
            return False, f"Error creating file: {str(e)}"
    
    def delete_file(self, file_name, location):
        """
        Delete a file
        
        Args:
            file_name (str): Name of the file
            location (str): Path where the file is located
            
        Returns:
            tuple: (success: bool, message: str)
        """
        try:
            full_path = os.path.join(location, file_name)
            
            if not os.path.exists(full_path):
                return False, f"File '{file_name}' not found"
            
            os.remove(full_path)
            
            print(f"{Fore.GREEN}✓ Deleted: {full_path}{Style.RESET_ALL}")
            return True, f"File '{file_name}' deleted successfully"
            
        except Exception as e:
            return False, f"Error deleting file: {str(e)}"

    def move_item(self, name, source, destination):
        """
        Move a file or folder
        
        Args:
            name (str): Name of the item to move
            source (str): Source directory path
            destination (str): Destination directory path
            
        Returns:
            tuple: (success: bool, message: str)
        """
        try:
            src_path = os.path.join(source, name)
            dest_path = os.path.join(destination, name)

            if not os.path.exists(src_path):
                return False, f"'{name}' not found in {source}"

            # Ensure destination exists
            os.makedirs(destination, exist_ok=True)

            shutil.move(src_path, dest_path)
            print(f"{Fore.GREEN}✓ Moved: {src_path} -> {dest_path}{Style.RESET_ALL}")
            return True, f"Moved '{name}' to {destination}"

        except Exception as e:
            return False, f"Error moving item: {str(e)}"

    def copy_item(self, name, source, destination):
        """
        Copy a file or folder
        
        Args:
            name (str): Name of the item to copy
            source (str): Source directory path
            destination (str): Destination directory path
            
        Returns:
            tuple: (success: bool, message: str)
        """
        try:
            src_path = os.path.join(source, name)
            dest_path = os.path.join(destination, name)

            if not os.path.exists(src_path):
                return False, f"'{name}' not found in {source}"

            # Ensure destination exists
            os.makedirs(destination, exist_ok=True)

            if os.path.isdir(src_path):
                if os.path.exists(dest_path):
                    return False, f"Destination already has a folder named '{name}'"
                shutil.copytree(src_path, dest_path)
            else:
                shutil.copy2(src_path, dest_path)

            print(f"{Fore.GREEN}✓ Copied: {src_path} -> {dest_path}{Style.RESET_ALL}")
            return True, f"Copied '{name}' to {destination}"

        except Exception as e:
            return False, f"Error copying item: {str(e)}"

    def search_item(self, name, location, max_results=5):
        """
        Search for files/folders by name in a directory tree
        
        Args:
            name (str): Name to search for (case-insensitive substring)
            location (str): Root path to search
            max_results (int): Limit results to avoid long output
            
        Returns:
            tuple: (success: bool, message: str)
        """
        try:
            matches = []
            name_lower = name.lower()

            for root, dirs, files in os.walk(location):
                for entry in dirs + files:
                    if name_lower in entry.lower():
                        matches.append(os.path.join(root, entry))
                        if len(matches) >= max_results:
                            break
                if len(matches) >= max_results:
                    break

            if not matches:
                return False, f"No matches for '{name}' in {location}"

            # Build readable message
            lines = "\n".join(matches)
            return True, f"Found {len(matches)} match(es):\n{lines}"

        except Exception as e:
            return False, f"Error searching items: {str(e)}"
    
    def write_to_file(self, file_name, location, content, append=False):
        """
        Write content to a file (create if doesn't exist, or append)
        
        Args:
            file_name (str): Name of the file
            location (str): Path where the file is located
            content (str): Content to write
            append (bool): If True, append to existing content
            
        Returns:
            tuple: (success: bool, message: str)
        """
        try:
            full_path = os.path.join(location, file_name)
            mode = 'a' if append else 'w'
            
            with open(full_path, mode, encoding='utf-8') as f:
                f.write(content)
                if append:
                    f.write('\n')  # Add newline after append
            
            action = "Appended to" if append else "Written to"
            print(f"{Fore.GREEN}✓ {action}: {full_path}{Style.RESET_ALL}")
            return True, f"Content {action.lower()} '{file_name}' successfully"
            
        except Exception as e:
            return False, f"Error writing to file: {str(e)}"
    
    def read_file(self, file_name, location):
        """
        Read content from a file
        
        Args:
            file_name (str): Name of the file
            location (str): Path where the file is located
            
        Returns:
            tuple: (success: bool, content or error message: str)
        """
        try:
            full_path = os.path.join(location, file_name)
            
            if not os.path.exists(full_path):
                return False, f"File '{file_name}' not found in {location}"
            
            with open(full_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            print(f"{Fore.GREEN}✓ Read: {full_path}{Style.RESET_ALL}")
            return True, content
            
        except Exception as e:
            return False, f"Error reading file: {str(e)}"
    
    def take_note(self, note_content, note_title=None):
        """
        Take a quick voice note (saved to JARVIS_Notes folder)
        
        Args:
            note_content (str): The note content
            note_title (str): Optional title, defaults to timestamp
            
        Returns:
            tuple: (success: bool, message: str)
        """
        try:
            timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
            
            if note_title:
                # Clean title for filename
                safe_title = "".join(c for c in note_title if c.isalnum() or c in (' ', '_', '-')).strip()
                filename = f"{timestamp}_{safe_title}.txt"
            else:
                filename = f"note_{timestamp}.txt"
            
            full_path = os.path.join(self.notes_folder, filename)
            
            # Format note with timestamp header
            formatted_note = f"Note taken: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
            formatted_note += "="*50 + "\n\n"
            formatted_note += note_content + "\n"
            
            with open(full_path, 'w', encoding='utf-8') as f:
                f.write(formatted_note)
            
            print(f"{Fore.GREEN}✓ Note saved: {full_path}{Style.RESET_ALL}")
            return True, f"Note saved as '{filename}' in Documents/JARVIS_Notes"
            
        except Exception as e:
            return False, f"Error saving note: {str(e)}"
    
    def list_notes(self):
        """
        List all saved notes
        
        Returns:
            tuple: (success: bool, message: str)
        """
        try:
            if not os.path.exists(self.notes_folder):
                return False, "No notes folder found"
            
            notes = [f for f in os.listdir(self.notes_folder) if f.endswith('.txt')]
            
            if not notes:
                return False, "No notes found"
            
            # Sort by date (newest first)
            notes.sort(reverse=True)
            
            message = f"Found {len(notes)} note(s):\n"
            for note in notes[:10]:  # Show max 10
                message += f"- {note}\n"
            
            return True, message
            
        except Exception as e:
            return False, f"Error listing notes: {str(e)}"
    
    def read_latest_note(self):
        """
        Read the most recent note
        
        Returns:
            tuple: (success: bool, content or error message: str)
        """
        try:
            if not os.path.exists(self.notes_folder):
                return False, "No notes folder found"
            
            notes = [f for f in os.listdir(self.notes_folder) if f.endswith('.txt')]
            
            if not notes:
                return False, "No notes found"
            
            # Get newest note
            notes.sort(reverse=True)
            latest = notes[0]
            
            full_path = os.path.join(self.notes_folder, latest)
            with open(full_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            return True, f"Latest note ({latest}):\n{content}"
            
        except Exception as e:
            return False, f"Error reading note: {str(e)}"
    
    def get_quick_location(self, location_name):
        """
        Get full path for common location names
        
        Args:
            location_name (str): Name like 'desktop', 'documents', 'downloads'
            
        Returns:
            str: Full path or original input if not recognized
        """
        location_map = {
            'desktop': self.desktop,
            'documents': self.documents,
            'downloads': self.downloads,
            'notes': self.notes_folder
        }
        
        return location_map.get(location_name.lower(), location_name)
