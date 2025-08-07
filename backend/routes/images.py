# backend/routes/images.py

import os
import uuid
from flask import Blueprint, request, jsonify, current_app, send_from_directory
from werkzeug.utils import secure_filename
from datetime import datetime

images_bp = Blueprint('images', __name__, url_prefix='/api/images')

# Allowed file extensions for image uploads
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'bmp', 'webp', 'svg'}

def allowed_file(filename):
    """Check if file has an allowed extension"""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@images_bp.route('', methods=['GET'])
def get_images():
    """Get all available images from the static/images directory"""
    try:
        images_data = []
        
        # Check if static images directory exists
        static_images_dir = os.path.join(current_app.config['STATIC_FOLDER'], 'images')
        
        if not os.path.exists(static_images_dir):
            return jsonify(images_data), 200
        
        # Scan directory for image files
        for filename in os.listdir(static_images_dir):
            if allowed_file(filename):
                file_path = os.path.join(static_images_dir, filename)
                if os.path.isfile(file_path):
                    file_size = os.path.getsize(file_path)
                    created_time = os.path.getctime(file_path)
                    
                    images_data.append({
                        'id': hash(filename) % 1000000,  # Simple ID from filename hash
                        'filename': filename,
                        'file_path': f"/images/{filename}",
                        'public_url': f"/images/{filename}",
                        'alt_text': filename,
                        'size': file_size,
                        'created_at': datetime.fromtimestamp(created_time).isoformat()
                    })
        
        return jsonify(images_data), 200
        
    except Exception as e:
        current_app.logger.error(f"Error fetching images: {str(e)}")
        return jsonify({'error': 'Failed to fetch images'}), 500

@images_bp.route('/upload', methods=['POST'])
def upload_image():
    """Upload a new image"""
    try:
        # Check if the post request has the file part
        if 'image' not in request.files:
            return jsonify({'error': 'No file provided'}), 400
        
        file = request.files['image']
        
        # If user does not select file, browser also
        # submits an empty part without filename
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        if file and allowed_file(file.filename):
            # Generate a unique filename
            original_filename = secure_filename(file.filename)
            name, ext = os.path.splitext(original_filename)
            unique_filename = f"{name}_{uuid.uuid4().hex[:8]}{ext}"
            
            # Ensure static images directory exists
            static_images_dir = os.path.join(current_app.config['STATIC_FOLDER'], 'images')
            os.makedirs(static_images_dir, exist_ok=True)
            
            # Save the file
            file_path = os.path.join(static_images_dir, unique_filename)
            file.save(file_path)
            
            # Get file size
            file_size = os.path.getsize(file_path)
            
            # Create public URL
            public_url = f"/images/{unique_filename}"
            
            # Return the image data
            return jsonify({
                'id': hash(unique_filename) % 1000000,
                'filename': unique_filename,
                'file_path': public_url,
                'public_url': public_url,
                'alt_text': original_filename,
                'size': file_size,
                'created_at': datetime.utcnow().isoformat()
            }), 201
            
        else:
            return jsonify({'error': 'Invalid file type. Allowed types: ' + ', '.join(ALLOWED_EXTENSIONS)}), 400
            
    except Exception as e:
        current_app.logger.error(f"Error uploading image: {str(e)}")
        return jsonify({'error': 'Failed to upload image'}), 500

@images_bp.route('/<int:image_id>', methods=['DELETE'])
def delete_image(image_id):
    """Delete an image (simplified - by filename hash)"""
    try:
        # This is a simplified approach - in production you'd want a proper database
        static_images_dir = os.path.join(current_app.config['STATIC_FOLDER'], 'images')
        
        # Find file by ID (hash)
        for filename in os.listdir(static_images_dir):
            if hash(filename) % 1000000 == image_id:
                file_path = os.path.join(static_images_dir, filename)
                if os.path.exists(file_path):
                    os.remove(file_path)
                    return jsonify({'message': 'Image deleted successfully'}), 200
        
        return jsonify({'error': 'Image not found'}), 404
        
    except Exception as e:
        current_app.logger.error(f"Error deleting image: {str(e)}")
        return jsonify({'error': 'Failed to delete image'}), 500
