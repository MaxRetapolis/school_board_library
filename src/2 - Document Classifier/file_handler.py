import os
import shutil
from typing import Optional
from logging_setup import get_logger
from config import DEFAULT_FOLDERS, ROOT_FOLDER

logger = get_logger(__name__)

class FileHandler:
    def __init__(self, root_folder: str = ROOT_FOLDER):
        self.root_folder = root_folder
        self._ensure_folder_structure()
    
    def _ensure_folder_structure(self) -> None:
        """Creates the necessary folder structure if it doesn't exist."""
        for folder in DEFAULT_FOLDERS.values():
            full_path = os.path.join(self.root_folder, folder)
            if not os.path.exists(full_path):
                os.makedirs(full_path)
                logger.info(f"Created folder: {full_path}")
    
    def move_file(self, file_path: str, destination: str, new_name: Optional[str] = None) -> str:
        """
        Moves a file to the specified destination folder.
        Returns the new file path.
        """
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Source file not found: {file_path}")
            
        dest_folder = os.path.join(self.root_folder, DEFAULT_FOLDERS[destination])
        new_file_name = new_name if new_name else os.path.basename(file_path)
        new_path = os.path.join(dest_folder, new_file_name)
        
        try:
            shutil.move(file_path, new_path)
            logger.info(f"Moved file from {file_path} to {new_path}")
            return new_path
        except Exception as e:
            logger.error(f"Failed to move file {file_path}: {e}")
            raise 