"""
excel_classifier.py

Contains classification logic for Excel documents:
- .xls
- .xlsx
"""

import logging
import pandas as pd

def classify_excel(filepath: str) -> dict:
    """
    Classifies an Excel document by checking if it contains any data/tables.
    
    Args:
        filepath (str): Path to the Excel file (.xls or .xlsx).
        
    Returns:
        dict: A dictionary with key "Tables" set to "Yes", "No", or "Unknown".
              You can expand this to identify multiple sheets, number of rows, etc.
    """
    classification_results = {
        "Tables": "No"  # Default
    }

    try:
        if filepath.lower().endswith(".xlsx"):
            df = pd.read_excel(filepath, engine='openpyxl')
        elif filepath.lower().endswith(".xls"):
            df = pd.read_excel(filepath, engine='xlrd')
        else:
            # Not recognized by this classifier
            logging.warning(f"Unsupported Excel format: {filepath}")
            classification_results["Tables"] = "Unknown"
            return classification_results

        # If data frame is not empty, we consider it has "tables"
        if not df.empty:
            classification_results["Tables"] = "Yes"

    except Exception as e:
        logging.error(f"Error classifying Excel file: {e}")
        classification_results["Tables"] = "Unknown"

    return classification_results
