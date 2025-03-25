# Configuration for the document classifier

# MIME types configuration
MIME_TYPES = {
    # Text-based non-PDF types
    'TEXT_BASED_NON_PDF': [
        "application/msword",                                                # .doc
        "application/vnd.openxmlformats-officedocument.wordprocessingml.document",  # .docx
        "text/plain",                                                        # .txt
        "application/rtf",                                                   # .rtf
        "text/csv",                                                          # .csv
        "text/html",                                                         # .html
        "application/xml",                                                   # .xml
    ],
    
    # Image-based document types
    'IMAGE_BASED': [
        "image/jpeg",     # .jpg, .jpeg
        "image/png",      # .png
        "image/tiff",     # .tiff
        "image/bmp",      # .bmp
        "image/gif",      # .gif
        "image/webp",     # .webp
    ],
}

# Paths configuration
PATHS = {
    'INPUT_DIR': './Claude/inbound/',
    'OUTPUT_DIR': './Claude/outbound/',
    'CLASSIFIED_DIR': {
        'Text-based PDF': './Claude/outbound/Classified/PDF-Text/',
        'Text-based non-PDF': './Claude/outbound/Classified/Text-Only/',
        'Image-based document': './Claude/outbound/Classified/PDF-Images/',
        'PDF-Text-With-Images': './Claude/outbound/Classified/PDF-Mixed/',
        'Plain-Text-Special-Format': './Claude/outbound/Classified/Text-Special/',
        'Unknown': './Claude/outbound/Classified/PDF-Unknown/',
    },
    'IN_PROCESSING_DIR': './Claude/outbound/In_Processing/',
}

# Logging configuration
LOGGING = {
    'LEVEL': 'INFO',  # DEBUG, INFO, WARNING, ERROR, CRITICAL
    'FORMAT': '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    'FILE': './Claude/logs/document_classifier.log',
}

# Classification rules
CLASSIFICATION_RULES = {
    'TEXT_BASED_PDF': {
        'mime_type': 'application/pdf',
        'has_text_layer': True
    },
    'TEXT_BASED_NON_PDF': {
        'mime_type': MIME_TYPES['TEXT_BASED_NON_PDF']
    },
    'IMAGE_BASED_DOCUMENT': {
        'mime_type': [*MIME_TYPES['IMAGE_BASED'], 'application/pdf'],
        'has_text_layer': False
    }
}