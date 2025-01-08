
import os
import json
import yaml

def load_config():
    with open("C:/school_board_library/configs/config.yaml", 'r') as file:
        return yaml.safe_load(file)

def run():
    config = load_config()
    raw_documents = config['paths']['raw_documents']
    data_folder = config['paths']['data_folder']

    # Read the directory and list files
    files = os.listdir(raw_documents)
    available_files = [f for f in files if os.path.isfile(os.path.join(raw_documents, f))]

    # Save the list to 1_available_files.json
    with open(os.path.join(data_folder, '1_available_files.json'), 'w') as json_file:
        json.dump(available_files, json_file, indent=4)