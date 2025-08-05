#!/bin/bash
# PDF Format Testing Script
# Test different PDF formatting configurations

BASE_URL="http://localhost:5050"
PUB_ID=${1:-1}

echo "📄 Testing PDF formats for publication $PUB_ID"
echo "================================================"

# Array of formats to test
FORMATS=("default" "corporate" "academic" "compact" "organization")

for format in "${formats[@]}"; do
    echo ""
    echo "📄 Testing format: $format"
    
    # Generate filename
    filename="test_publication_${PUB_ID}_${format}.pdf"
    
    # Make request
    curl -s -o "$filename" \
         -w "   Status: %{http_code}, Size: %{size_download} bytes\n" \
         "${BASE_URL}/api/publications/${PUB_ID}/export/pdf?format=${format}"
    
    # Check if file was created successfully
    if [ -f "$filename" ] && [ -s "$filename" ]; then
        file_size=$(stat -f%z "$filename" 2>/dev/null || stat -c%s "$filename" 2>/dev/null)
        echo "   ✅ Success: $filename ($file_size bytes)"
    else
        echo "   ❌ Failed to generate PDF"
        rm -f "$filename"  # Remove empty file
    fi
done

echo ""
echo "📁 PDF files saved in current directory"
echo ""
echo "💡 Usage: $0 [publication_id]"
echo "   Example: $0 3"
