# create_prelearning_structure.py

import os

def create_prelearning_structure():
    base_dir = os.getcwd()  # Current working directory
    experiment_dir = os.path.join(base_dir, 'experiments', '1_prelearning')

    # Define the folder structure
    folders = [
        os.path.join(experiment_dir, 'data'),
        os.path.join(experiment_dir, 'src'),
        os.path.join(experiment_dir, 'src', 'utils'),
        os.path.join(experiment_dir, 'configs'),
        os.path.join(experiment_dir, 'logs')
    ]

    # Define the files to create
    files = [
        os.path.join(experiment_dir, 'src', 'runner.py'),
        os.path.join(experiment_dir, 'src', 'step1_read_documents.py'),
        os.path.join(experiment_dir, 'src', 'step2_preprocess_documents.py'),
        os.path.join(experiment_dir, 'src', 'step3_extract_entities.py'),
        os.path.join(experiment_dir, 'src', 'step4_extract_relationships.py'),
        os.path.join(experiment_dir, 'src', 'step5_update_knowledge_graph.py'),
        os.path.join(experiment_dir, 'src', 'utils', 'helper_functions.py'),
        os.path.join(experiment_dir, 'configs', 'config.yaml'),
        os.path.join(experiment_dir, 'requirements.txt'),
        os.path.join(experiment_dir, 'README.md')
    ]

    # Create folders
    for folder in folders:
        os.makedirs(folder, exist_ok=True)
        print(f"Created folder: {folder}")

    # Create empty files
    for file in files:
        open(file, 'a').close()
        print(f"Created file: {file}")

    print("Folder structure and files created successfully.")

if __name__ == '__main__':
    create_prelearning_structure()