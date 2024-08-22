from werkzeug.utils import secure_filename
import os
from flask import current_app as app
import logging
import uuid

def save_image(file):
    filename = secure_filename(file.filename)
    unique_filename = f"{uuid.uuid4().hex}_{filename}"
    upload_folder = app.config['UPLOAD_FOLDER']
    
    # Ensure the upload directory exists
    os.makedirs(upload_folder, exist_ok=True)
    filepath = os.path.join(upload_folder, unique_filename)
    
    # Save the file and log the outcome
    file.save(filepath)
    if os.path.exists(filepath):
        logging.info(f"File saved successfully: {filepath}")
    else:
        logging.error(f"File not found after saving: {filepath}")

    return unique_filename  # return only the unique filename

