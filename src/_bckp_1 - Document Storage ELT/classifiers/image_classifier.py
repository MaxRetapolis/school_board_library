"""
image_classifier.py

Contains classification logic for image documents:
- .jpg / .jpeg
- .png
- .tif / .tiff (optionally detect multipage TIFF)
"""

import logging
from PIL import Image

def classify_image(filepath: str) -> dict:
    """
    Classifies an image document by checking its format, size, color mode, etc.
    
    Args:
        filepath (str): Path to the image file.
        
    Returns:
        dict: A dictionary with keys "Format", "Size", "Mode" (all as strings).
              Additional keys like "Multipage" for TIFF can be added.
    """
    classification_results = {
        "Format": "Unknown",
        "Size": "Unknown",
        "Mode": "Unknown"
    }

    try:
        with Image.open(filepath) as img:
            # Basic properties
            classification_results["Format"] = img.format or "Unknown"
            width, height = img.size
            classification_results["Size"] = f"{width}x{height}"
            classification_results["Mode"] = img.mode or "Unknown"

            # If it's a TIFF, check if it has multiple frames
            if img.format == "TIFF":
                if getattr(img, "n_frames", 1) > 1:
                    classification_results["Multipage"] = "Yes"
                else:
                    classification_results["Multipage"] = "No"

    except Exception as e:
        logging.error(f"Error classifying image: {e}")
        # If there's an error, we can default to Unknown
        classification_results["Format"] = "Unknown"
        classification_results["Size"] = "Unknown"
        classification_results["Mode"] = "Unknown"

    return classification_results
