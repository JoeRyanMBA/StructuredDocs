#!/bin/bash

echo "===== Word Import Diagnostics ====="
echo ""
echo "1. Checking Pandoc installation:"
which pandoc || echo "❌ Pandoc not found in PATH"
pandoc --version 2>&1 | head -5 || echo "❌ Cannot run pandoc --version"
echo ""

echo "2. Checking Python environment:"
python --version
echo ""

echo "3. Checking file /tmp permissions:"
ls -ld /tmp
touch /tmp/test_write_$$ && echo "✅ Can write to /tmp" && rm /tmp/test_write_$$ || echo "❌ Cannot write to /tmp"
echo ""

echo "4. Checking backend logs for Pandoc errors:"
echo "Last 50 lines containing 'PANDOC':"
grep -i "pandoc" /var/log/*.log 2>/dev/null | tail -50 || echo "No system logs found"
echo ""

echo "5. To see real-time application logs:"
echo "   - For Docker: docker logs -f <container_name>"
echo "   - For hosted environments: view runtime logs in the provider dashboard"
echo ""

echo "6. Test Pandoc manually with a sample .docx:"
echo "   If you have a test.docx file, run:"
echo "   pandoc test.docx --from docx --to markdown -o test.md"
echo ""
