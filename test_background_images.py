#!/usr/bin/env python3
"""
PDF Background Image Testing Script
Test the new background image feature for PDF title pages
"""

import requests
import sys
import os

BASE_URL = "http://localhost:5050"

def test_background_images(publication_id=3):
    """Test PDF generation with background images"""
    
    print("🖼️  PDF Background Image Testing")
    print("=" * 40)
    
    # Test cases
    test_cases = [
        {
            'name': 'Default without background',
            'params': {'format': 'default'},
            'filename': f'test_bg_none_{publication_id}.pdf'
        },
        {
            'name': 'Corporate with background (non-existent)',
            'params': {'format': 'corporate', 'background_image': 'sample.png'},
            'filename': f'test_bg_missing_{publication_id}.pdf'
        },
        {
            'name': 'Academic format ready for background',
            'params': {'format': 'academic'},
            'filename': f'test_bg_ready_{publication_id}.pdf'
        }
    ]
    
    results = {}
    
    for test_case in test_cases:
        print(f"\n📄 Testing: {test_case['name']}")
        
        # Build URL with parameters
        url = f"{BASE_URL}/api/publications/{publication_id}/export/pdf"
        if test_case['params']:
            params = '&'.join([f"{k}={v}" for k, v in test_case['params'].items()])
            url += f"?{params}"
        
        try:
            response = requests.get(url, timeout=30)
            
            if response.status_code == 200:
                # Save PDF file
                filename = test_case['filename']
                with open(filename, 'wb') as f:
                    f.write(response.content)
                
                file_size = len(response.content)
                results[test_case['name']] = {
                    'status': 'success',
                    'file_size': file_size,
                    'filename': filename
                }
                print(f"   ✅ Success: {filename} ({file_size:,} bytes)")
                
            else:
                results[test_case['name']] = {
                    'status': 'error',
                    'error': f"HTTP {response.status_code}"
                }
                print(f"   ❌ Error {response.status_code}")
                
        except Exception as e:
            results[test_case['name']] = {
                'status': 'error',
                'error': str(e)
            }
            print(f"   ❌ Exception: {e}")
    
    # Summary
    print(f"\n📊 BACKGROUND IMAGE TEST SUMMARY")
    print("=" * 35)
    
    success_count = sum(1 for r in results.values() if r['status'] == 'success')
    total_count = len(results)
    
    print(f"✅ Successful: {success_count}/{total_count}")
    
    if success_count > 0:
        print(f"\n📁 Generated files:")
        for name, result in results.items():
            if result['status'] == 'success':
                print(f"   • {result['filename']} ({result['file_size']:,} bytes)")
        
        print(f"\n💡 To test with actual background images:")
        print(f"   1. Add image files to: backend/static/backgrounds/")
        print(f"   2. Use URL: {BASE_URL}/api/publications/{publication_id}/export/pdf?background_image=yourimage.png")
        print(f"   3. Supported formats: PNG, JPG, JPEG, GIF, BMP")
    
    return success_count == total_count

def create_sample_image():
    """Create a sample background image for testing"""
    try:
        from PIL import Image, ImageDraw, ImageFont
        
        # Create a simple background image
        width, height = 2550, 3300  # Letter size at 300 DPI
        
        # Create image with light gradient background
        img = Image.new('RGB', (width, height), color='white')
        draw = ImageDraw.Draw(img)
        
        # Add a subtle gradient effect
        for y in range(height):
            alpha = int(255 * (1 - y / height * 0.1))  # Very subtle gradient
            color = (240, 248, 255, alpha)  # Light blue
            draw.line([(0, y), (width, y)], fill=color[:3])
        
        # Add a subtle watermark text
        try:
            # Try to use a system font
            font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 200)
        except:
            font = ImageFont.load_default()
        
        # Add very light watermark
        watermark_text = "SAMPLE"
        bbox = draw.textbbox((0, 0), watermark_text, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
        
        # Center the watermark
        x = (width - text_width) // 2
        y = (height - text_height) // 2
        
        # Draw with very light gray
        draw.text((x, y), watermark_text, fill=(230, 230, 230), font=font)
        
        # Save the sample image
        backgrounds_dir = "/workspaces/StructuredDocs/backend/static/backgrounds"
        sample_path = os.path.join(backgrounds_dir, "sample.png")
        img.save(sample_path, "PNG")
        
        print(f"✅ Created sample background image: {sample_path}")
        return sample_path
        
    except ImportError:
        print("💡 PIL/Pillow not available - install it to create sample images")
        print("   Run: pip install Pillow")
        return None
    except Exception as e:
        print(f"❌ Error creating sample image: {e}")
        return None

def main():
    """Main function"""
    pub_id = int(sys.argv[1]) if len(sys.argv) > 1 else 3
    
    print("🖼️  PDF Background Image Feature Test")
    print("====================================")
    
    # Create a sample background image if possible
    sample_image = create_sample_image()
    
    # Test background image functionality
    success = test_background_images(pub_id)
    
    if sample_image and os.path.exists(sample_image):
        print(f"\n🎨 Sample image created! Test it with:")
        print(f"   curl \"{BASE_URL}/api/publications/{pub_id}/export/pdf?background_image=sample.png\" -o test_with_background.pdf")
    
    if success:
        print(f"\n✅ Background image feature tests PASSED")
        sys.exit(0)
    else:
        print(f"\n❌ Some tests FAILED")
        sys.exit(1)

if __name__ == "__main__":
    main()
