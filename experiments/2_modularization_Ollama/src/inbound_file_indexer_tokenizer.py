import os
import json
import logging
from datetime import datetime
from tokenizer import tokenize, count_words, count_lines, count_chars, initialize_logging, read_file

def main():
    initialize_logging()
    logging.info("Starting inbound file indexing and tokenization process")
    
    inbound_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "inbound_documents")
    output_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "index")
    os.makedirs(output_dir, exist_ok=True)
    output_file = os.path.join(output_dir, "tokenized_inbound_document_index.json")
    
    documents_stats = []
    for root, _, files in os.walk(inbound_dir):
        for file in files:
            if file.endswith('.txt'):
                file_path = os.path.join(root, file)
                logging.info(f"Processing file: {file_path}")
                content = read_file(file_path)
                if content:
                    tokens = tokenize(content)
                    num_words = count_words(content)
                    num_lines = count_lines(content)
                    num_chars = count_chars(content)
                    doc_stats = {
                        "file_location": file_path,
                        "file_name": file,
                        "tokens_count": len(tokens),
                        "words_count": num_words,
                        "lines_count": num_lines,
                        "characters_count": num_chars
                    }
                    documents_stats.append(doc_stats)
                else:
                    logging.error(f"Failed to read content from file: {file_path}")
    
    try:
        with open(output_file, 'w', encoding='utf-8') as json_file:
            json.dump(documents_stats, json_file, indent=4)
        logging.info(f"Tokenized document index saved to {output_file}")
        print(f"Tokenized document index saved to {output_file}")
    except Exception as e:
        logging.error(f"Failed to save tokenized document index: {e}")
        print(f"Failed to save tokenized document index: {e}")

if __name__ == "__main__":
    main()
