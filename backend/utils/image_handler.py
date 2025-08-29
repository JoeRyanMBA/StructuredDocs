import os
import shutil
import uuid
import re
from pathlib import Path
from urllib.parse import urlparse
from PIL import Image
import mimetypes
from flask import current_app

class ImageHandler:
    """Handles image extraction, storage, and path management for imports"""
    
    SUPPORTED_FORMATS = {'.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff', '.webp'}
    MAX_IMAGE_SIZE = (1920, 1080)  # Max dimensions for optimization
    
    def __init__(self, import_doc_id):
        """Initialize with import document ID for organizing images"""
        self.import_doc_id = import_doc_id
        self.backend_images_dir = Path(current_app.root_path) / 'static' / 'images' / 'imports' / str(import_doc_id)
        self.frontend_images_dir = Path(current_app.root_path).parent / 'frontend' / 'public' / 'images' / 'imports' / str(import_doc_id)
        
        # Ensure directories exist
        self.backend_images_dir.mkdir(parents=True, exist_ok=True)
        self.frontend_images_dir.mkdir(parents=True, exist_ok=True)
    
    def extract_and_store_images(self, temp_media_dir, markdown_content):
        """
        Extract images from temp directory and store them permanently.
        Update markdown content with new image paths.
        
        Args:
            temp_media_dir (str): Temporary directory where pandoc extracted images
            markdown_content (str): Markdown content with temporary image references
            
        Returns:
            tuple: (updated_markdown_content, list_of_stored_images)
        """
        stored_images = []
        updated_content = markdown_content
        
        if not os.path.exists(temp_media_dir):
            current_app.logger.info(f"No temp media directory found at {temp_media_dir}")
            return updated_content, stored_images
        
        # Find all image files in temp directory, including .emf
        image_files = []
        emf_files = []
        for root, dirs, files in os.walk(temp_media_dir):
            for file in files:
                file_path = Path(root) / file
                if file_path.suffix.lower() in self.SUPPORTED_FORMATS:
                    image_files.append(file_path)
                elif file_path.suffix.lower() == '.emf':
                    emf_files.append(file_path)

        # Convert .emf files to .png using libreoffice (headless)
        for emf_path in emf_files:
            try:
                png_path = emf_path.with_suffix('.png')
                # Use libreoffice to convert emf to png
                import subprocess
                result = subprocess.run([
                    'libreoffice', '--headless', '--convert-to', 'png', str(emf_path), '--outdir', str(emf_path.parent)
                ], capture_output=True)
                if result.returncode == 0 and png_path.exists():
                    image_files.append(png_path)
                    current_app.logger.info(f"Converted {emf_path} to {png_path}")
                    # Update markdown references from .emf to .png
                    old_ref = f"media/{emf_path.name}"
                    new_ref = f"media/{png_path.name}"
                    updated_content = updated_content.replace(old_ref, new_ref)
                else:
                    current_app.logger.error(f"Failed to convert {emf_path} to PNG: {result.stderr.decode()}")
            except Exception as e:
                current_app.logger.error(f"Exception during EMF to PNG conversion for {emf_path}: {str(e)}")

        current_app.logger.info(f"Found {len(image_files)} images to process (after EMF conversion)")

        # Process each image
        for temp_image_path in image_files:
            try:
                stored_image_info = self._store_single_image(temp_image_path)
                if stored_image_info:
                    stored_images.append(stored_image_info)
                    # Update markdown content with new image path
                    old_ref = f"media/{temp_image_path.name}"
                    new_ref = f"/images/imports/{self.import_doc_id}/{stored_image_info['filename']}"
                    # Replace various possible reference formats
                    patterns = [
                        f"![.*?]\\({re.escape(old_ref)}\\)",
                        f"![.*?]\\({re.escape(temp_image_path.name)}\\)",
                        f"!\\[.*?\\]\\(.*?{re.escape(temp_image_path.stem)}.*?\\)"
                    ]
                    for pattern in patterns:
                        matches = re.finditer(pattern, updated_content)
                        for match in matches:
                            alt_text = re.search(r'!\[(.*?)\]', match.group()).group(1)
                            new_markdown = f"![{alt_text}]({new_ref})"
                            updated_content = updated_content.replace(match.group(), new_markdown)
            except Exception as e:
                current_app.logger.error(f"Failed to process image {temp_image_path}: {str(e)}")
                continue

        return updated_content, stored_images
    
    def _store_single_image(self, temp_image_path):
        """
        Store a single image file permanently and return metadata.
        
        Args:
            temp_image_path (Path): Path to temporary image file
            
        Returns:
            dict: Image metadata including new filename and paths
        """
        try:
            # Generate unique filename
            original_name = temp_image_path.stem
            extension = temp_image_path.suffix.lower()
            unique_id = str(uuid.uuid4())[:8]
            new_filename = f"{original_name}_{unique_id}{extension}"
            
            # Paths for storing
            backend_path = self.backend_images_dir / new_filename
            frontend_path = self.frontend_images_dir / new_filename
            
            # Optimize and copy image
            self._optimize_image(temp_image_path, backend_path)
            
            # Copy to frontend public directory for serving
            shutil.copy2(backend_path, frontend_path)
            
            # Get image metadata
            with Image.open(backend_path) as img:
                width, height = img.size
                format_type = img.format
            
            file_size = backend_path.stat().st_size
            
            image_info = {
                'filename': new_filename,
                'original_name': temp_image_path.name,
                'backend_path': str(backend_path),
                'frontend_path': str(frontend_path),
                'public_url': f"/images/imports/{self.import_doc_id}/{new_filename}",
                'width': width,
                'height': height,
                'format': format_type,
                'file_size': file_size,
                'mime_type': mimetypes.guess_type(new_filename)[0]
            }
            
            current_app.logger.info(f"Stored image: {new_filename} ({width}x{height}, {file_size} bytes)")
            return image_info
            
        except Exception as e:
            current_app.logger.error(f"Failed to store image {temp_image_path}: {str(e)}")
            return None
    
    def _optimize_image(self, source_path, dest_path):
        """
        Optimize image size and quality while preserving reasonable quality.
        
        Args:
            source_path (Path): Source image path
            dest_path (Path): Destination path for optimized image
        """
        try:
            with Image.open(source_path) as img:
                # Convert RGBA to RGB for JPEG if needed
                if img.mode == 'RGBA' and dest_path.suffix.lower() in ['.jpg', '.jpeg']:
                    background = Image.new('RGB', img.size, (255, 255, 255))
                    background.paste(img, mask=img.split()[-1])
                    img = background
                
                # Resize if too large
                if img.size[0] > self.MAX_IMAGE_SIZE[0] or img.size[1] > self.MAX_IMAGE_SIZE[1]:
                    img.thumbnail(self.MAX_IMAGE_SIZE, Image.Resampling.LANCZOS)
                    current_app.logger.info(f"Resized image to {img.size}")
                
                # Save with optimization
                save_kwargs = {'optimize': True}
                if dest_path.suffix.lower() in ['.jpg', '.jpeg']:
                    save_kwargs['quality'] = 85
                elif dest_path.suffix.lower() == '.png':
                    save_kwargs['compress_level'] = 6
                
                img.save(dest_path, **save_kwargs)
                
        except Exception as e:
            # Fallback: just copy the file if optimization fails
            current_app.logger.warning(f"Image optimization failed for {source_path}, copying as-is: {str(e)}")
            shutil.copy2(source_path, dest_path)
    
    def validate_markdown_images(self, markdown_content):
        """
        Validate that images referenced in markdown exist and are accessible.
        
        Args:
            markdown_content (str): Markdown content to validate
            
        Returns:
            list: List of validation issues found
        """
        issues = []
        
        # Find all image references in markdown
        image_pattern = r'!\[.*?\]\((.*?)\)'
        matches = re.finditer(image_pattern, markdown_content)
        
        for match in matches:
            image_path = match.group(1)
            
            # Skip external URLs
            if image_path.startswith(('http://', 'https://')):
                continue
            
            # Check if local image exists
            if image_path.startswith('/images/imports/'):
                # Check in frontend public directory
                public_path = Path(current_app.root_path).parent / 'frontend' / 'public' / image_path.lstrip('/')
                if not public_path.exists():
                    issues.append({
                        'type': 'missing_image',
                        'path': image_path,
                        'line': markdown_content[:match.start()].count('\n') + 1,
                        'message': f"Referenced image not found: {image_path}"
                    })
            else:
                issues.append({
                    'type': 'external_reference',
                    'path': image_path,
                    'line': markdown_content[:match.start()].count('\n') + 1,
                    'message': f"External image reference (may not be accessible): {image_path}"
                })
        
        return issues
    
    def cleanup_temp_images(self, temp_media_dir):
        """Clean up temporary image directory after processing"""
        try:
            if os.path.exists(temp_media_dir):
                shutil.rmtree(temp_media_dir)
                current_app.logger.info(f"Cleaned up temporary image directory: {temp_media_dir}")
        except Exception as e:
            current_app.logger.warning(f"Failed to cleanup temp directory {temp_media_dir}: {str(e)}")
    
    def get_import_images(self):
        """Get list of all images for this import document"""
        images = []
        if self.frontend_images_dir.exists():
            for image_file in self.frontend_images_dir.glob('*'):
                if image_file.suffix.lower() in self.SUPPORTED_FORMATS:
                    try:
                        with Image.open(image_file) as img:
                            width, height = img.size
                            format_type = img.format
                        
                        images.append({
                            'filename': image_file.name,
                            'public_url': f"/images/imports/{self.import_doc_id}/{image_file.name}",
                            'width': width,
                            'height': height,
                            'format': format_type,
                            'file_size': image_file.stat().st_size
                        })
                    except Exception as e:
                        current_app.logger.error(f"Error reading image metadata for {image_file}: {str(e)}")
        
        return images
