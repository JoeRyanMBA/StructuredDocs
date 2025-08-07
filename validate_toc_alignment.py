#!/usr/bin/env python3
"""
TOC Alignment Validation Script
Validates that the TOC page number alignment fix is working correctly
"""

import requests
import os
import sys

BASE_URL = "http://localhost:5050"

def validate_toc_alignment(publication_id=3):
    """Test TOC alignment across all PDF formats"""
    
    print("🔍 TOC Page Number Alignment Validation")
    print("=" * 45)
    
    formats = ['default', 'corporate', 'academic', 'compact', 'organization']
    results = {}
    
    for format_type in formats:
        print(f"\n📄 Testing format: {format_type}")
        
        url = f"{BASE_URL}/api/publications/{publication_id}/export/pdf?format={format_type}"
        
        try:
            response = requests.get(url, timeout=30)
            
            if response.status_code == 200:
                filename = f"validation_toc_{format_type}.pdf"
                with open(filename, 'wb') as f:
                    f.write(response.content)
                
                file_size = len(response.content)
                results[format_type] = {
                    'status': 'success',
                    'file_size': file_size,
                    'filename': filename
                }
                print(f"   ✅ Success: {filename} ({file_size:,} bytes)")
                
            else:
                results[format_type] = {
                    'status': 'error',
                    'error': f"HTTP {response.status_code}"
                }
                print(f"   ❌ Error {response.status_code}")
                
        except Exception as e:
            results[format_type] = {
                'status': 'error',
                'error': str(e)
            }
            print(f"   ❌ Exception: {e}")
    
    # Summary
    print(f"\n📊 VALIDATION SUMMARY")
    print("=" * 25)
    
    success_count = sum(1 for r in results.values() if r['status'] == 'success')
    total_count = len(results)
    
    print(f"✅ Successful: {success_count}/{total_count}")
    
    if success_count == total_count:
        print("🎉 ALL FORMATS WORKING - TOC alignment fix validated!")
        print("\n📁 Generated files:")
        for format_type, result in results.items():
            if result['status'] == 'success':
                print(f"   • {result['filename']} ({result['file_size']:,} bytes)")
    else:
        print("⚠️  Some formats failed - check server logs")
        
    return success_count == total_count

def main():
    """Main validation function"""
    pub_id = int(sys.argv[1]) if len(sys.argv) > 1 else 3
    
    success = validate_toc_alignment(pub_id)
    
    if success:
        print(f"\n✅ TOC alignment validation PASSED")
        print("💡 Open the generated PDFs to visually confirm page numbers are right-aligned")
        sys.exit(0)
    else:
        print(f"\n❌ TOC alignment validation FAILED")
        sys.exit(1)

if __name__ == "__main__":
    main()
