# School Board Library Copilot: Document Pipeline - Initial Processing

This document describes the initial processing logic for the School Board Library Copilot's document pipeline.

## Part 1: Core Concepts and Document Class

### 1. Document:

A `Document` represents a single file that enters the system. Each document has core attributes:

*   **`filepath`:** The full path to the document's location in the file system.
*   **`filename`:** The name of the file (including the extension).
*   **`extension`:** The file extension (e.g., ".pdf", ".docx").
*   **`size`:** The file size in bytes.
*   **`creation_date`:** The date and time the file was created (obtained from the file system).
*   **`status`:** The current processing status of the document. This status should align with the folder the document is in (e.g., "New_Document", "In_Processing", "Duplicates", "Processed", "Errors").
*   **`document_id`:** A unique identifier assigned to each document upon entering the system. It starts with 1 (or the maximum ID in the existing index) and increments sequentially.
*   **`metadata`:** A flexible container (e.g., a dictionary) to hold any additional information extracted or derived from the document.

### 2. Document Status:

The `status` of a document reflects its current state and will correspond to the folder it resides in:

*   `New_Document`: The document has just arrived in the system and hasn't been processed yet.
*   `In_Processing`: The document is currently undergoing processing (extraction, transformation, etc.).
*   `Duplicates`: The document is considered a duplicate of an already processed document.
*   `Processed`: The document has been successfully processed.
*   `Errors`: An error occurred during the processing of the document.

## Part 2: Document Index, Temporary Indexes, and Logging

### 1. Document Index:

*   The `Document Index` is a crucial data structure that keeps track of all documents in the system.
*   It is stored as a JSON file (`documents_index.json`).
*   The index is a dictionary where:
    *   **Keys:** are the unique `document_id`s.
    *   **Values:** are dictionaries containing the document's metadata as described in Part 1, including `filepath`, `filename`, `extension`, `size`, `creation_date`, `status`, and `metadata`.

### 2. Temporary Indexes:

*   `Temporary Indexes` will be created for each of the key folders: `New_Documents`, `In_Processing`, `Duplicates`, `Processed`, and `Errors`.
*   These indexes will be dictionaries with the same structure as the main `Document Index`.
*   They will be used to track the documents found in each folder *during the current run* of the script.
*   These temporary indexes will be compared with the main index to determine the necessary actions for each document.

### 3. Logging:

*   A log file will be used to record key events and actions for observability.
*   The following information will be logged:
    *   Summary of the main `Document Index` after it's loaded.
    *   Summary of each temporary index after it's created.
    *   Details of the comparison between temporary indexes and the main index.
    *   Actions taken for each document (e.g., moved to `Processed`, moved to `In_Processing`, error encountered, assigned `document_id`).
    *   Any errors encountered during the process.

## Part 3: Detailed Processing Logic (Periodic Script)

**Configuration:**

*   **`FOLDER_LIST`:** A list of folder names: `["New_Documents", "In_Processing", "Duplicates", "Processed", "Errors"]`. This list is configurable and can be extended in the future.

**Step 1: Initialization and Load Main Index**

1.  **Logging:** Start logging (e.g., "Script started").
2.  **Check for Existing Index and Determine `next_document_id`:**
    *   Check if the `documents_index.json` file exists.
    *   **If the index exists:**
        *   Load the `Document Index` from the `documents_index.json` file into memory.
        *   Find the maximum `document_id` in the loaded index.
        *   Set `next_document_id` to `maximum_document_id + 1`.
    *   **If the index does not exist:**
        *   Create an empty dictionary to represent a new `Document Index`.
        *   Set `next_document_id` to 1.
3.  **Logging:** Log a summary of the loaded `Document Index` (e.g., "Loaded index with X documents, next document ID: Y").
4.  **Create Folders:** Create the folders defined in `FOLDER_LIST` if they don't exist.

**Step 2: Create Temporary Indexes for Each Folder**

1.  **Iterate through `FOLDER_LIST`:**
    *   For each `folder_name` in `FOLDER_LIST`:
        *   Create an empty dictionary for the folder's temporary index (e.g., `new_documents_temp_index`, `in_processing_temp_index`, etc.).
        *   Iterate through the corresponding folder:
            *   For each item (check if it's a file):
                *   Create a `Document` object.
                *   Generate a temporary `document_id` (only needs to be unique within this temporary index).
                *   Add the document's metadata to the folder's temporary index, using the temporary `document_id` as the key.
        *   **Logging:** Log a summary of the temporary index (e.g., "Found X documents in New_Documents").

**Step 3: Compare Indexes, Identify Edge Cases, and Determine Actions**

1.  **Compare `New_Documents` Temporary Index with Main Index:**
    *   For each document in the `New_Documents` temporary index:
        *   Check if a document with the same `filename`, `size`, and `creation_date` exists in the main `Document Index`.
        *   **If a match is found in the main index:**
            *   Check the `status` of the matched document in the main index:
                *   **If the status is "In_Processing" or "Duplicates" or "Processed":**
                    *   Treat the document as a duplicate.
                    *   **Action:**
                        *   Update the document's `status` in the main index to "Duplicates".
                        *   Move the document from `New_Documents` to `Duplicates`.
                        *   Update the document's `filepath` in the main index.
                        *   **Logging:** Log the action taken (e.g., "Moved duplicate document X from New_Documents to Duplicates").
                *   **If the status is "Errors":**
                    *   Treat the document as a new document.
                    *   **Action:**
                        *   Call the `Handle_New_Document` function, passing `next_document_id` as an argument: `Handle_New_Document(document, main_index, next_document_id)`.
                        *   Increment `next_document_id` by 1.
                        *   **Logging:** Log the action taken (e.g., "Retrying processing of document X previously in Errors, moved from New_Documents to In_Processing, assigned ID: Y").
        *   **If no match is found in the main index:**
            *   This is a new document.
            *   **Action:**
                *   Call the `Handle_New_Document` function, passing `next_document_id` as an argument: `Handle_New_Document(document, main_index, next_document_id)`.
                *   Increment `next_document_id` by 1.
                *   **Logging:** Log the action taken (e.g., "Moved new document X from New_Documents to In_Processing, assigned ID: Y").

2.  **Analyze Other Temporary Indexes (`In_Processing`, `Duplicates`, `Processed`, `Errors`):**
    *   For each folder in `["Duplicates", "Processed", "Errors"]`:
        *   For each document in the temporary index:
            *   Check if a document with the same `filename`, `size`, and `creation_date` exists in the main `Document Index`.
            *   **If no match is found in the main index:**
                *   This is an anomaly: a document is in one of these folders but not in the main index. It might have been manually moved there.
                *   **Action:**
                    *   Assign the current value of `next_document_id` as the document's `document_id`.
                    *   Increment `next_document_id` by 1.
                    *   Set the document's `status` to the corresponding folder name (e.g., if found in "Processed", set status to "Processed").
                    *   Add the document's metadata to the main index, using the new `document_id` as the key.
                    *   Update the document's `filepath` in the main index.
                    *   **Logging:** Log the anomaly and the action taken (e.g., "Found document X in Processed that was not in the main index. Added to index with ID: Y").
            *   **If a match is found in the main index:**
                *   No action needed - this is expected.
                *   **Logging:** Consider logging this as a confirmation for auditing purposes.
    *   For `In_Processing` temporary index:
        *   For each document in the temporary index:
            *   Check if a document with the same `filename`, `size`, and `creation_date` exists in the main `Document Index`.
            *   **If no match is found in the main index:**
                *   This is an anomaly: a document is in `In_Processing` but not in the main index. It might have been manually moved there.
                *   **Action:**
                    *   Assign the current value of `next_document_id` as the document's `document_id`.
                    *   Increment `next_document_id` by 1.
                    *   Set the document's `status` to "In_Processing".
                    *   Add the document's metadata to the main index, using the new `document_id` as the key.
                    *   Update the document's `filepath` in the main index.
                    *   **Logging:** Log the anomaly and the action taken (e.g., "Found document X in In_Processing that was not in the main index. Added to index with ID: Y").
            *   **If a match is found in the main index:**
                *   No action needed - this is expected.
                *   **Logging:** Consider logging this as a confirmation for auditing purposes.
    *   After each folder is processed - update the main index and save it.

**Step 4: Save the Main Index**

1.  Save the updated `Document Index` back to the `documents_index.json` file.
2.  **Logging:** Log that the index has been saved (e.g., "Index saved successfully").

**Function: `Handle_New_Document(document, main_index, document_id)`**

This function encapsulates the logic for processing a new document.

1.  **Set the document's `document_id` to the passed `document_id`.**
2.  **Set the document's `status` to "In_Processing".**
3.  **Move the document from its current folder to the `In_Processing` folder.**
4.  **Add the document's metadata to the `main_index`, using the `document_id` as the key.**
5.  **Update the document's `filepath` in the main index.**

## Part 4: Future Considerations (Beyond Initial Script)

*   **Error Handling:** Implement more robust error handling for file operations, index loading/saving, and logging.
*   **Scheduling:** Use a task scheduler to run the script periodically.
*   **Scalability:** Consider a database for the index if the number of documents becomes very large.
*   **Similar Document Indexing:** Develop this capability later to find similar documents based on content, even if they have different filenames, sizes, or creation dates.