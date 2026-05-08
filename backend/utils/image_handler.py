import os
import shutil
import uuid
import re
from pathlib import Path
from urllib.parse import urlparse
from PIL import Image
import mimetypes
from flask import current_app
from backend.utils.storage import get_storage_backend

class ImageHandler:
    """Handles image extraction, storage, and path management for imports"""
    
    SUPPORTED_FORMATS = {'.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff', '.webp'}
    VECTOR_FORMATS = {'.emf', '.wmf'}
    MAX_IMAGE_SIZE = (1920, 1080)  # Max dimensions for optimization
    
    def __init__(self, import_doc_id):
        """Initialize with import document ID for organizing images"""
        self.import_doc_id = import_doc_id
        
        # Get storage backend (object storage or local)
        try:
            self.storage = get_storage_backend()
            storage_type = type(self.storage).__name__
            current_app.logger.info(f"🗂️ Using storage backend: {storage_type}")
        except ImportError as ie:
            current_app.logger.error(f"❌ Storage backend ImportError: {ie} - falling back to local")
            # Fallback to legacy local storage
            from backend.utils.storage import LocalStorage
            storage_root = os.environ.get('IMAGE_STORAGE_ROOT', '/app/backend/static/images')
            self.storage = LocalStorage(storage_root)
            current_app.logger.info(f"🗂️ Fallback to local storage: {storage_root}")
        except Exception as e:
            current_app.logger.error(f"❌ Failed to initialize storage backend: {e} - falling back to local")
            # Fallback to legacy local storage
            from backend.utils.storage import LocalStorage
            storage_root = os.environ.get('IMAGE_STORAGE_ROOT', '/app/backend/static/images')
            self.storage = LocalStorage(storage_root)
            current_app.logger.info(f"🗂️ Fallback to local storage: {storage_root}")
        
        # Keep legacy paths for backward compatibility
        configured_root = (os.environ.get('IMAGE_STORAGE_ROOT') or '').strip()
        candidate_roots = []
        if configured_root:
            candidate_roots.append(Path(configured_root))
        candidate_roots.append(Path('/app/data/images'))
        candidate_roots.append(Path(current_app.root_path) / 'static' / 'images')

        selected_root = None
        for root in candidate_roots:
            try:
                root.mkdir(parents=True, exist_ok=True)
                test_file = root / '.write_test'
                test_file.write_text('test')
                test_file.unlink()
                selected_root = root
                break
            except Exception:
                continue

        if selected_root is None:
            selected_root = Path(current_app.root_path) / 'static' / 'images'

        self.backend_images_root = selected_root
        self.backend_images_dir = self.backend_images_root / 'imports' / str(import_doc_id)
        self.frontend_images_dir = Path(current_app.root_path).parent / 'frontend' / 'public' / 'images' / 'imports' / str(import_doc_id)
        
        # Ensure directories exist (for local fallback)
        try:
            self.backend_images_dir.mkdir(parents=True, exist_ok=True)
            current_app.logger.info(f"📁 Created/verified backend images directory: {self.backend_images_dir}")
            
            # Test write permission
            test_file = self.backend_images_dir / '.write_test'
            test_file.write_text('test')
            test_file.unlink()
            current_app.logger.info(f"✅ Backend directory is writable")
        except PermissionError as e:
            current_app.logger.error(f"❌ PERMISSION DENIED: Cannot write to backend images directory: {e}")
            current_app.logger.error(f"   Path: {self.backend_images_dir}")
            current_app.logger.error(f"   This will cause images to fail to save!")
        except Exception as e:
            current_app.logger.error(f"❌ Failed to create backend images directory: {e}")
            
        try:
            self.frontend_images_dir.mkdir(parents=True, exist_ok=True)
            current_app.logger.info(f"📁 Created/verified frontend images directory: {self.frontend_images_dir}")
        except Exception as e:
            current_app.logger.error(f"❌ Failed to create frontend images directory: {e}")
    
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
            current_app.logger.warning(f"⚠️  No temp media directory found at {temp_media_dir} - Pandoc may not have extracted any images. This is OK if the document has no images.")
            return updated_content, stored_images
        
        current_app.logger.info(f"📁 Checking temp media directory: {temp_media_dir}")
        
        # Pre-flight checks
        try:
            # Ensure backend images directory exists first
            self.backend_images_dir.mkdir(parents=True, exist_ok=True)
            current_app.logger.info(f"✅ Ensured backend images directory exists: {self.backend_images_dir}")
            
            # Check disk space
            import shutil as shutil_util
            stat = shutil_util.disk_usage(str(self.backend_images_dir.parent))
            free_gb = stat.free / (1024**3)
            current_app.logger.info(f"💾 Disk space available: {free_gb:.2f} GB")
            if free_gb < 0.1:
                current_app.logger.error(f"❌ CRITICAL: Low disk space ({free_gb:.2f} GB), image storage may fail")
            
            # Check write permissions
            test_file = self.backend_images_dir / '.write_test'
            test_file.touch()
            test_file.unlink()
            current_app.logger.info(f"✅ Write permissions verified for {self.backend_images_dir}")
        except Exception as e:
            current_app.logger.error(f"❌ Pre-flight check failed: {str(e)}")
        
        # Find all image files in temp directory, including vector formats
        image_files = []
        vector_files = []
        all_files_found = []
        
        for root, dirs, files in os.walk(temp_media_dir):
            current_app.logger.info(f"📂 Scanning directory: {root} (found {len(files)} files)")
            for file in files:
                all_files_found.append(file)
                file_path = Path(root) / file
                if file_path.suffix.lower() in self.SUPPORTED_FORMATS:
                    image_files.append(file_path)
                    current_app.logger.info(f"✅ Found supported image: {file}")
                elif file_path.suffix.lower() in self.VECTOR_FORMATS:
                    vector_files.append(file_path)
                    current_app.logger.info(f"🔄 Found vector image (will convert): {file}")
                else:
                    current_app.logger.info(f"⚠️  Found unsupported file: {file} (type: {file_path.suffix})")
        
        if not image_files and not vector_files:
            current_app.logger.warning(f"⚠️  No images found in temp directory. All files found: {all_files_found}")

        # Convert vector files to .png when possible so they can be stored and displayed.
        for vector_path in vector_files:
            png_path = self._convert_vector_to_png(vector_path)
            if png_path is None:
                continue
            image_files.append(png_path)
            current_app.logger.info(f"Converted {vector_path} to {png_path}")
            old_ref = f"media/{vector_path.name}"
            new_ref = f"media/{png_path.name}"
            updated_content = updated_content.replace(old_ref, new_ref)

        current_app.logger.info(f"🔍 Found {len(image_files)} images to process (after EMF conversion)")
        success_count = 0
        failed_count = 0

        # Process each image
        for temp_image_path in image_files:
            try:
                stored_image_info = self._store_single_image(temp_image_path)
                if stored_image_info:
                    stored_images.append(stored_image_info)
                    success_count += 1
                    # Update markdown content with new image path
                    old_ref = f"media/{temp_image_path.name}"
                    new_ref = stored_image_info.get('public_url') or f"/images/imports/{self.import_doc_id}/{stored_image_info['filename']}"
                    # Replace various possible reference formats.
                    # The optional (?:\{[^}]*\})? suffix strips Pandoc-style size attributes
                    # like {width="4.0in" height="2.0in"} that pandoc adds to image references.
                    pandoc_attrs = r'(?:\{[^}]*\})?'
                    patterns = [
                        rf"!\[.*?\]\({re.escape(old_ref)}\){pandoc_attrs}",
                        rf"!\[.*?\]\({re.escape(temp_image_path.name)}\){pandoc_attrs}",
                        rf"!\[.*?\]\(.*?{re.escape(temp_image_path.stem)}.*?\){pandoc_attrs}"
                    ]
                    for pattern in patterns:
                        matches = re.finditer(pattern, updated_content)
                        for match in matches:
                            alt_text = re.search(r'!\[(.*?)\]', match.group()).group(1)
                            new_markdown = f"![{alt_text}]({new_ref})"
                            updated_content = updated_content.replace(match.group(), new_markdown)
                else:
                    failed_count += 1
                    current_app.logger.warning(f"⚠️  Image storage returned None: {temp_image_path.name}")
            except Exception as e:
                failed_count += 1
                current_app.logger.error(f"Failed to process image {temp_image_path}: {str(e)}", exc_info=True)
                continue

        current_app.logger.info(f"📊 Image extraction summary: {success_count} succeeded, {failed_count} failed out of {len(image_files)} total")
        
        return updated_content, stored_images

    def _convert_vector_to_png(self, vector_path: Path):
        """Convert a vector image (EMF/WMF) to PNG via LibreOffice/soffice."""
        png_path = vector_path.with_suffix('.png')
        converter_cmds = ('libreoffice', 'soffice')

        for cmd in converter_cmds:
            try:
                import subprocess
                result = subprocess.run(
                    [cmd, '--headless', '--convert-to', 'png', str(vector_path), '--outdir', str(vector_path.parent)],
                    capture_output=True,
                    timeout=45
                )
                if result.returncode == 0 and png_path.exists():
                    return png_path
                stderr = (result.stderr or b'').decode(errors='ignore').strip()
                if stderr:
                    current_app.logger.warning(f"{cmd} could not convert {vector_path.name}: {stderr}")
            except subprocess.TimeoutExpired:
                current_app.logger.error(f"Vector conversion timeout for {vector_path.name} using {cmd}")
            except FileNotFoundError:
                # Try next converter command name.
                continue
            except Exception as e:
                current_app.logger.error(f"Exception converting {vector_path.name} using {cmd}: {e}")

        current_app.logger.error(f"Failed to convert vector image to PNG: {vector_path.name}")
        return None
    
    def _store_single_image(self, temp_image_path):
        """
        Store a single image file permanently to object storage or local storage and return metadata.
        
        Args:
            temp_image_path (Path): Path to temporary image file
            
        Returns:
            dict: Image metadata including new filename and paths, or None if storage failed
        """
        try:
            # Generate unique filename
            original_name = temp_image_path.stem
            extension = temp_image_path.suffix.lower()
            unique_id = str(uuid.uuid4())[:8]
            new_filename = f"{original_name}_{unique_id}{extension}"
            
            current_app.logger.info(f"💾 Storing image: {temp_image_path.name} -> {new_filename}")
            
            # Storage path for remote object storage or local disk.
            # For remote storage: full path "images/imports/{doc_id}/{filename}"
            # For Local: relative to IMAGE_STORAGE_ROOT which is already .../images, so use "imports/{doc_id}/{filename}"
            is_local_storage = type(self.storage).__name__ == 'LocalStorage'
            storage_path = f"imports/{self.import_doc_id}/{new_filename}" if is_local_storage else f"images/imports/{self.import_doc_id}/{new_filename}"
            
            # Optimize image in-memory
            try:
                with Image.open(temp_image_path) as img:
                    # Get original dimensions
                    width, height = img.size
                    format_type = img.format
                    
                    # Optimize if needed
                    if width > self.MAX_IMAGE_SIZE[0] or height > self.MAX_IMAGE_SIZE[1]:
                        img.thumbnail(self.MAX_IMAGE_SIZE, Image.Resampling.LANCZOS)
                        width, height = img.size
                        current_app.logger.info(f"   🔽 Resized to {width}x{height}")
                    
                    # Convert to RGB if needed (for JPEG compatibility)
                    if img.mode in ('RGBA', 'LA', 'P'):
                        rgb_img = Image.new('RGB', img.size, (255, 255, 255))
                        if img.mode == 'P':
                            img = img.convert('RGBA')
                        rgb_img.paste(img, mask=img.split()[-1] if img.mode in ('RGBA', 'LA') else None)
                        img = rgb_img
                    
                    # Save to bytes
                    import io
                    img_bytes = io.BytesIO()
                    save_format = format_type if format_type in ('JPEG', 'PNG', 'GIF', 'WEBP') else 'PNG'
                    img.save(img_bytes, format=save_format, optimize=True, quality=85)
                    img_data = img_bytes.getvalue()
                    
            except Exception as img_err:
                current_app.logger.error(f"   ❌ Failed to optimize image: {img_err}")
                # Fall back to raw file data
                img_data = temp_image_path.read_bytes()
                with Image.open(temp_image_path) as img:
                    width, height = img.size
                    format_type = img.format
            
            # Determine content type
            content_type = mimetypes.guess_type(new_filename)[0] or 'image/jpeg'
            
            # Save to storage backend
            try:
                public_url = self.storage.save_file(img_data, storage_path, content_type)
                current_app.logger.info(f"   ✅ Saved to storage: {public_url}")
            except Exception as save_err:
                current_app.logger.error(f"   ❌ Failed to save to storage: {save_err}")
                return None
            
            # Create image info
            # For local storage, keep the canonical web path at /images/imports/... so
            # gallery/publication consumers do not depend on storage-internal paths.
            frontend_path = public_url if not is_local_storage else f"/images/imports/{self.import_doc_id}/{new_filename}"
            canonical_public_url = frontend_path if is_local_storage else public_url
            
            image_info = {
                'filename': new_filename,
                'original_name': temp_image_path.name,
                'backend_path': storage_path,
                'frontend_path': frontend_path,
                'public_url': canonical_public_url,
                'width': width,
                'height': height,
                'format': format_type,
                'file_size': len(img_data),
                'mime_type': content_type
            }
            
            current_app.logger.info(f"✅ Stored image: {new_filename} ({width}x{height}, {len(img_data)} bytes)")
            return image_info
            
        except Exception as e:
            current_app.logger.error(f"❌ CRITICAL: Failed to store image {temp_image_path}: {str(e)}", exc_info=True)
            return None
    
    def _optimize_image(self, source_path, dest_path):
        """
        Optimize image size and quality while preserving reasonable quality.
        Returns True if successful, False if failed.
        
        Args:
            source_path (Path): Source image path
            dest_path (Path): Destination path for optimized image
            
        Returns:
            bool: True if successful, False if failed
        """
        try:
            current_app.logger.info(f"   🖼️  Opening image: {source_path}")
            
            # Get source file size for validation
            source_size = source_path.stat().st_size
            if source_size == 0:
                current_app.logger.error(f"   ❌ Source file is empty: {source_path}")
                return False
            
            with Image.open(source_path) as img:
                # Convert RGBA to RGB for JPEG if needed
                if img.mode == 'RGBA' and dest_path.suffix.lower() in ['.jpg', '.jpeg']:
                    background = Image.new('RGB', img.size, (255, 255, 255))
                    background.paste(img, mask=img.split()[-1])
                    img = background
                
                # Resize if too large
                if img.size[0] > self.MAX_IMAGE_SIZE[0] or img.size[1] > self.MAX_IMAGE_SIZE[1]:
                    img.thumbnail(self.MAX_IMAGE_SIZE, Image.Resampling.LANCZOS)
                    current_app.logger.info(f"   📐 Resized image to {img.size}")
                
                # Save with optimization
                save_kwargs = {'optimize': True}
                if dest_path.suffix.lower() in ['.jpg', '.jpeg']:
                    save_kwargs['quality'] = 85
                elif dest_path.suffix.lower() == '.png':
                    save_kwargs['compress_level'] = 6
                
                current_app.logger.info(f"   💾 Saving optimized image to: {dest_path}")
                img.save(dest_path, **save_kwargs)
                current_app.logger.info(f"   ✅ Successfully saved optimized image")
                
                # Verify file was written and has content
                if not dest_path.exists():
                    current_app.logger.error(f"   ❌ File was not created after save: {dest_path}")
                    return False
                
                saved_size = dest_path.stat().st_size
                if saved_size == 0:
                    current_app.logger.error(f"   ❌ File is zero-sized after save: {dest_path}")
                    current_app.logger.error(f"      Source file size: {source_size} bytes")
                    # Remove the empty file
                    try:
                        dest_path.unlink()
                    except:
                        pass
                    return False
                
                current_app.logger.info(f"   ✅ File verified: {saved_size} bytes")
                return True
                
        except PermissionError as e:
            current_app.logger.error(f"   ❌ PERMISSION DENIED writing to {dest_path}: {e}")
            # Try fallback copy
            try:
                shutil.copy2(source_path, dest_path)
                current_app.logger.warning(f"   ⚠️  Fallback: Copied image without optimization")
                
                # Verify fallback copy
                if not dest_path.exists() or dest_path.stat().st_size == 0:
                    current_app.logger.error(f"   ❌ Fallback copy failed - file missing or empty")
                    return False
                
                return True
            except Exception as copy_err:
                current_app.logger.error(f"   ❌ Fallback copy also failed: {copy_err}")
                return False
        except Exception as e:
            # Fallback: just copy the file if optimization fails
            current_app.logger.warning(f"   ⚠️  Image optimization failed for {source_path}: {str(e)}")
            try:
                shutil.copy2(source_path, dest_path)
                current_app.logger.info(f"   ✅ Fallback: Successfully copied image without optimization")
                
                # Verify fallback copy
                if not dest_path.exists() or dest_path.stat().st_size == 0:
                    current_app.logger.error(f"   ❌ Fallback copy failed - file missing or empty")
                    return False
                
                return True
            except Exception as copy_err:
                current_app.logger.error(f"   ❌ Fallback copy also failed: {copy_err}")
                return False
                if dest_path.exists():
                    return True
                else:
                    current_app.logger.error(f"   ❌ Fallback copy created no file at {dest_path}")
                    return False
            except Exception as copy_err:
                current_app.logger.error(f"   ❌ Fallback copy also failed: {copy_err}")
                return False
    
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
