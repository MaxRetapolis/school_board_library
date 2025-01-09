
import shutil
import logging
import os

def move_file(src, dest):
    """Moves a file from src to dest and handles errors."""
    try:
        shutil.move(src, dest)
        logging.info(f"Moved file from {src} to {dest}")
        print(f"Moved file from {src} to {dest}")
    except Exception as e:
        logging.error(f"Error moving file from {src} to {dest}: {e}")
        print(f"Error moving file from {src} to {dest}: {e}")

def get_file_extension(filepath):
    """Extracts the file extension from a filepath."""
    return os.path.splitext(filepath)[1].lower()