"""
Flask API Backend for KisanSeva
Connects ML models with React frontend
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import base64
import json
import os
import numpy as np
from io import BytesIO
from PIL import Image
import tensorflow as tf
from test_model import predict as ml_predict
from recommendation_engine import get_farmer_recommendation

# Initialize Flask app
app = Flask(__name__)
CORS(app)

# Configuration
IMG_SIZE = (224, 224)
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB
ALLOWED_EXTENSIONS = {'jpg', 'jpeg', 'png', 'gif'}

def allowed_file(filename):
    """Check if file extension is allowed"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def base64_to_image(base64_str):
    """Convert base64 string to PIL Image"""
    try:
        # Remove data URI prefix if present (e.g., "data:image/jpeg;base64,")
        if ',' in base64_str:
            base64_str = base64_str.split(',')[1]
        
        # Remove any whitespace
        base64_str = base64_str.strip()
        
        # Decode base64 to bytes
        image_data = base64.b64decode(base64_str)
        image = Image.open(BytesIO(image_data))
        return image
    except Exception as e:
        raise ValueError(f"Invalid base64 image: {str(e)}")

def save_temp_image(image, temp_path="temp_image.jpg"):
    """Save image temporarily for model prediction"""
    image.save(temp_path, quality=95)
    return temp_path

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        "status": "healthy",
        "service": "KisanSeva ML Backend",
        "version": "1.0.0"
    }), 200

@app.route('/api/analyze', methods=['POST'])
def analyze_image():
    """
    Analyze crop leaf image
    Expects JSON with base64 encoded image
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({
                "status": "error",
                "message": "No JSON data provided"
            }), 400
        
        if 'image' not in data:
            return jsonify({
                "status": "error",
                "message": "No image provided. Send JSON with 'image' field containing base64 data."
            }), 400
        
        base64_image = data['image']
        if not base64_image or not isinstance(base64_image, str):
            return jsonify({
                "status": "error",
                "message": "Image must be a non-empty string"
            }), 400
        
        language = data.get('language', 'hindi').lower()
        
        # Validate language
        if language not in ['hindi', 'marathi']:
            language = 'hindi'
        
        # Convert base64 to image
        image = base64_to_image(base64_image)
        
        # Resize image to model input size
        image = image.resize(IMG_SIZE, Image.Resampling.LANCZOS)
        
        # Save temporarily
        temp_path = save_temp_image(image)
        
        # Run ML prediction
        ml_result = ml_predict(temp_path)
        
        # Extract crop and disease info
        crop = ml_result.get("Crop", "Unknown")
        disease = ml_result.get("Disease", "Unknown")
        confidence = ml_result.get("Confidence", 0)
        
        # Handle uncertain predictions
        if "Status" in ml_result:
            # Uncertain crop or disease
            os.remove(temp_path) if os.path.exists(temp_path) else None
            return jsonify({
                "status": "uncertain",
                "message": ml_result.get("Status"),
                "suggestions": ml_result.get("Suggestions", {})
            }), 200
        
        # Get farmer-friendly recommendations
        recommendations = get_farmer_recommendation(
            crop=crop,
            disease=disease,
            confidence=confidence,
            language=language
        )
        
        # Determine health status based on confidence and disease
        if disease.lower() in ["healthy", "unknown", "unidentified"]:
            status = "Healthy"
        elif confidence >= 0.8:
            status = "Action"
        elif confidence >= 0.6:
            status = "Monitor"
        else:
            status = "Monitor"
        
        # Format response for frontend
        response = {
            "status": "success",
            "cropName": crop,
            "diseaseName": disease,
            "confidence": "High" if confidence >= 0.8 else ("Medium" if confidence >= 0.6 else "Low"),
            "confidenceScore": round(float(confidence), 2),
            "healthStatus": status,
            "recommendations": recommendations,
            "language": language
        }
        
        # Clean up temp file
        if os.path.exists(temp_path):
            os.remove(temp_path)
        
        return jsonify(response), 200
        
    except ValueError as e:
        return jsonify({
            "status": "error",
            "message": f"Image error: {str(e)}"
        }), 400
    except Exception as e:
        print(f"Error in /api/analyze: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({
            "status": "error",
            "message": f"Analysis failed: {str(e)}"
        }), 500

@app.route('/api/analyze-url', methods=['POST'])
def analyze_url():
    """
    Alternative endpoint for analyzing images from file upload
    """
    try:
        if 'image' not in request.files:
            return jsonify({
                "status": "error",
                "message": "No image file provided"
            }), 400
        
        file = request.files['image']
        language = request.form.get('language', 'hindi').lower()
        
        if file.filename == '':
            return jsonify({
                "status": "error",
                "message": "No file selected"
            }), 400
        
        if not allowed_file(file.filename):
            return jsonify({
                "status": "error",
                "message": "Invalid file type. Allowed: jpg, jpeg, png, gif"
            }), 400
        
        # Check file size
        file.seek(0, os.SEEK_END)
        if file.tell() > MAX_FILE_SIZE:
            return jsonify({
                "status": "error",
                "message": "File too large. Max 10MB"
            }), 400
        
        file.seek(0)
        
        # Open image
        image = Image.open(file.stream)
        
        # Resize to model input size
        image = image.resize(IMG_SIZE, Image.Resampling.LANCZOS)
        
        # Save temporarily
        temp_path = f"temp_{file.filename}"
        image.save(temp_path)
        
        # Run ML prediction
        ml_result = ml_predict(temp_path)
        
        # Extract results
        crop = ml_result.get("Crop", "Unknown")
        disease = ml_result.get("Disease", "Unknown")
        confidence = ml_result.get("Confidence", 0)
        
        if "Status" in ml_result:
            return jsonify({
                "status": "uncertain",
                "message": ml_result.get("Status"),
                "suggestions": ml_result.get("Suggestions", {})
            }), 200
        
        # Get recommendations
        recommendations = get_farmer_recommendation(
            crop=crop,
            disease=disease,
            confidence=confidence,
            language=language
        )
        
        # Determine status
        if disease.lower() in ["healthy", "unknown", "unidentified"]:
            status = "Healthy"
        elif confidence >= 0.8:
            status = "Action"
        elif confidence >= 0.6:
            status = "Monitor"
        else:
            status = "Monitor"
        
        response = {
            "status": "success",
            "cropName": crop,
            "diseaseName": disease,
            "confidence": "High" if confidence >= 0.8 else ("Medium" if confidence >= 0.6 else "Low"),
            "confidenceScore": round(float(confidence), 2),
            "healthStatus": status,
            "recommendations": recommendations,
            "language": language
        }
        
        # Clean up
        if os.path.exists(temp_path):
            os.remove(temp_path)
        
        return jsonify(response), 200
        
    except Exception as e:
        print(f"Error in /api/analyze-url: {str(e)}")
        return jsonify({
            "status": "error",
            "message": f"Analysis failed: {str(e)}"
        }), 500

@app.route('/api/models-info', methods=['GET'])
def models_info():
    """Get information about loaded models"""
    return jsonify({
        "status": "success",
        "models": {
            "crop_classifier": "crop_classifier.h5",
            "rice_disease": "rice_disease_model.h5",
            "wheat_disease": "wheat_disease_model.h5"
        },
        "input_size": IMG_SIZE,
        "supported_languages": ["hindi", "marathi"]
    }), 200

if __name__ == '__main__':
    # Set TensorFlow to use less memory
    tf.config.set_visible_devices([], 'GPU')  # Use CPU for deployment
    
    # Run Flask server
    print("🚀 Starting KisanSeva ML Backend...")
    print("📊 Available endpoints:")
    print("  - POST /api/analyze (base64 image)")
    print("  - POST /api/analyze-url (file upload)")
    print("  - GET /health")
    print("  - GET /api/models-info")
    
    app.run(
        host='0.0.0.0',
        port=5000,
        debug=False,
        threaded=True
    )
