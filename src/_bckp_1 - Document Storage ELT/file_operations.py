
import os
import shutil

def move_file(source, destination):
    """
    Move a file from source to destination.
    
    Args:
        source (str): Path to the source file.
        destination (str): Path to the destination directory.
    """
    shutil.move(source, destination)

def delete_file(filepath):
    """
    Delete a file at the specified filepath.
    
    Args:
        filepath (str): Path to the file to be deleted.
    """
    os.remove(filepath)

def read_file(filepath, mode='r'):
    """
    Read the contents of a file.
    
    Args:
        filepath (str): Path to the file.
        mode (str): Mode to open the file.
        
    Returns:
        str: Contents of the file.
    """
    with open(filepath, mode) as f:
        return f.read()

def write_file(filepath, content, mode='w'):
    """
    Write content to a file.
    
    Args:
        filepath (str): Path to the file.
        content (str): Content to write.
        mode (str): Mode to open the file.
    """
    with open(filepath, mode) as f:
        f.write(content)

def cleanup_old_files(directory, extension):
    """
    Remove old files with a specific extension from a directory.
    
    Args:
        directory (str): Path to the directory.
        extension (str): File extension to target.
    """
    for file in os.listdir(directory):
        if file.endswith(extension):
            delete_file(os.path.join(directory, file))