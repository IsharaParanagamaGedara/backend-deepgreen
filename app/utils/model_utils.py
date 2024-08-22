import numpy as np
import tensorflow as tf
from tensorflow.keras.models import load_model
import logging

# Load the model once at the start
model = load_model('best_model1_1.keras')

# Define class names
CLASS_NAMES = [
    'Corn___Common_rust',
    'Corn___Gray_leaf_spot',
    'Corn___Northern_Leaf_Blight',
    'Corn___healthy',
    'Potato___Early_blight',
    'Potato___Late_blight',
    'Potato___healthy',
    'Strawberry___Leaf_scorch',
    'Strawberry___healthy',
    'Unknown___Unexpected_input'
]

def predict_disease(image_path):
    try:
        # Load and preprocess the image
        logging.info(f"Loading and preprocessing image: {image_path}")
        img = tf.image.decode_image(tf.io.read_file(image_path), channels=3)
        img = tf.image.resize(img, [256, 256])
        img_array = tf.expand_dims(img, 0)  # Add batch dimension

        # Make prediction
        logging.info(f"Making prediction for image: {image_path}")
        predictions = model.predict(img_array)
        
        predicted_class_idx = np.argmax(predictions[0])
        predicted_class = CLASS_NAMES[predicted_class_idx]
        confidence_percentage = round(100 * np.max(predictions[0]), 2)
        
        logging.info(f"Prediction: {predicted_class} with confidence {confidence_percentage}%")
        return predicted_class, confidence_percentage
    except Exception as e:
        logging.error(f"Error in prediction: {str(e)}")
        return "Unknown___Unexpected_input", 0.0
