#!/usr/bin/env python3
"""
Production environment checker for Word import functionality.
Run this on your Digital Ocean server to diagnose import issues.
"""

import subprocess
import sys
import os
from pathlib import Path

def check_pandoc():
    """Check if pandoc is available and working"""
    print("🔍 Checking Pandoc Installation...")
    try:
        result = subprocess.run(['pandoc', '--version'], 
                              capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            version_line = result.stdout.split('\n')[0] if result.stdout else "Unknown"
            print(f"✅ Pandoc is available: {version_line}")
            return True
        else:
            print(f"❌ Pandoc command failed: {result.stderr}")
            return False
    except FileNotFoundError:
        print("❌ Pandoc is not installed or not in PATH")
        return False
    except Exception as e:
        print(f"❌ Error checking pandoc: {e}")
        return False

def check_python_docx():
    """Check if python-docx is available"""
    print("\n🔍 Checking Python-DOCX...")
    try:
        from docx import Document
        print("✅ python-docx is available")
        return True
    except ImportError as e:
        print(f"❌ python-docx not available: {e}")
        return False

def check_app_dependencies():
    """Check if all required dependencies are available"""
    print("\n🔍 Checking App Dependencies...")
    required_modules = [
        'flask', 'sqlalchemy', 'werkzeug', 'docx', 're', 'io', 'tempfile'
    ]
    
    missing = []
    for module in required_modules:
        try:
            __import__(module)
            print(f"✅ {module}")
        except ImportError:
            print(f"❌ {module}")
            missing.append(module)
    
    return len(missing) == 0

def check_file_permissions():
    """Check if temporary directories can be created"""
    print("\n🔍 Checking File System Permissions...")
    try:
        import tempfile
        with tempfile.TemporaryDirectory() as temp_dir:
            test_file = os.path.join(temp_dir, 'test.txt')
            with open(test_file, 'w') as f:
                f.write('test')
            print(f"✅ Can create temporary files in: {temp_dir}")
            return True
    except Exception as e:
        print(f"❌ Cannot create temporary files: {e}")
        return False

def main():
    print("🏥 StructuredDocs Import Diagnostic Tool")
    print("=" * 50)
    
    issues = []
    
    # Check all components
    if not check_pandoc():
        issues.append("Pandoc not available - Word imports will use fallback python-docx")
    
    if not check_python_docx():
        issues.append("python-docx not available - Word imports will fail")
    
    if not check_app_dependencies():
        issues.append("Missing required Python modules")
    
    if not check_file_permissions():
        issues.append("Cannot create temporary files")
    
    print("\n" + "=" * 50)
    print("📋 DIAGNOSTIC SUMMARY")
    print("=" * 50)
    
    if not issues:
        print("✅ All systems appear to be working correctly")
        print("\nIf imports are still failing, the issue is likely:")
        print("  • Document format/structure not as expected")
        print("  • Database connection issues") 
        print("  • Application-level errors")
        print("\nCheck the application logs for specific error messages.")
    else:
        print("❌ Issues found:")
        for i, issue in enumerate(issues, 1):
            print(f"  {i}. {issue}")
        
        print("\n🔧 RECOMMENDED ACTIONS:")
        if "Pandoc not available" in str(issues):
            print("  • Install pandoc: apt-get install pandoc (Ubuntu/Debian)")
            print("  • Or ensure pandoc is in PATH")
        
        if "python-docx not available" in str(issues):
            print("  • Install python-docx: pip install python-docx")
        
        if "Missing required Python modules" in str(issues):
            print("  • Install missing modules via pip")
        
        if "Cannot create temporary files" in str(issues):
            print("  • Check disk space and permissions")
            print("  • Ensure /tmp directory is writable")

if __name__ == "__main__":
    main()