# Skill: Debug PDF Export & Publication Issues

This skill guides you through diagnosing and fixing problems in PDF generation, publication export, and knowledge base rendering.

## When to Use

- PDF export fails or produces corrupt files
- Content cut off or misaligned in exported PDF
- Publications not saving or loading correctly
- HTML export missing styles or images
- Mobile knowledge base not displaying properly
- ReportLab rendering errors during PDF generation

## Quick Diagnosis

### Check PDF Service Status
PDF generation is handled by:
- Route: `backend/routes/publications.py` (likely)
- Generator: `backend/services/pdf_generator.py`
- Config: `backend/pdf_config.py` (ReportLab settings, styling rules)

```bash
python -c "
from backend.services.pdf_generator import generate_pdf
# Check if service is importable and callable
print('PDF generator available')
"
```

### Verify ReportLab Installation
```bash
python -c "from reportlab.lib.pagesizes import letter; print('ReportLab OK')"
# If error: pip install reportlab
```

### Enable Debug Logging
Set environment variable: `FLASK_DEBUG=1`
Monitor logs for:
- HTML parsing/sanitization errors
- ReportLab rendering failures
- Image loading problems
- Font/styling issues

## Diagnosis Workflow

### 1. Understand Publication vs. Export Flow
**Publication (Snapshots):**
- Topics ordered and grouped into a Publication
- Snapshot captured at publication time
- Can be exported as PDF, HTML, or mobile site

**Export Formats:**
- PDF: ReportLab rendering with custom CSS/styling
- HTML: Self-contained HTML with embedded styles/images
- Mobile: Optimized for mobile viewers

### 2. Check HTML Sanitization
Before PDF rendering, HTML is sanitized for ReportLab compatibility:
- File: `backend/pdf_config.py` (likely contains sanitization rules)
- Issue: Invalid HTML tags or attributes cause rendering failures
- Solution: Ensure content uses valid, supported HTML subset

Common ReportLab limitations:
- No `<div>` or block-level styling (use tables/paragraphs instead)
- Limited CSS support (inline styles preferred)
- No JavaScript
- Font embeds must be present

### 3. Test PDF Generation in Isolation
```bash
# From repo root:
python -c "
from backend.app import create_app
from backend.services.pdf_generator import generate_pdf

app = create_app()
with app.app_context():
    sample_html = '''
    <html>
    <body>
    <h1>Test</h1>
    <p>This is a test.</p>
    </body>
    </html>
    '''
    try:
        pdf_bytes = generate_pdf(sample_html)
        print(f'PDF generated: {len(pdf_bytes)} bytes')
    except Exception as e:
        print(f'Error: {e}')
"
```

### 4. Verify Image Handling in Exports
Images in publications must:
- Be accessible from the backend (S3 or local storage)
- Have valid URLs in the content
- Be embedded or linked correctly for format (PDF embeds, HTML links)

**Check file:** `backend/services/pdf_generator.py` for image loading logic

### 5. Check Font Configuration
ReportLab requires fonts to be properly configured:
- Default fonts (Helvetica, Times, Courier) usually available
- Custom fonts must be registered in `backend/pdf_config.py`
- Missing fonts cause rendering errors

**See:** `backend/pdf_config.py` for font setup

### 6. Test Export Endpoint
```bash
# 1. Create or get a Publication ID
# 2. Export as PDF
curl -X GET "http://localhost:8080/api/publications/<id>/export?format=pdf" \
  -H "Authorization: Bearer <JWT>" \
  -o export.pdf

# 3. Check file size and open in PDF viewer
# 4. Look for truncation, misalignment, or missing content

# 5. Export as HTML
curl -X GET "http://localhost:8080/api/publications/<id>/export?format=html" \
  -H "Authorization: Bearer <JWT>" \
  -o export.html
```

## Common Issues & Fixes

| Symptom | Likely Cause | Fix |
|---------|--------------|-----|
| "ReportLab error" in PDF export | Invalid HTML or unsupported styling | Check HTML sanitization, simplify CSS |
| PDF truncated or missing pages | Content too large or encoding error | Check page limits, test with smaller publication |
| Images missing from PDF | Images not accessible or wrong URLs | Verify S3 access, check image URL rewriting |
| Styling not applied in PDF | CSS not supported by ReportLab | Use inline styles, avoid advanced CSS |
| "Font not found" error | Custom fonts not registered | Check `backend/pdf_config.py` font setup |
| HTML export has broken links | Relative links not rewritten | Check link rewriting logic in export handler |
| Mobile site missing images | Image URLs not rewritten for mobile | Check mobile export route/service |

## Files to Check

| File | Purpose |
|------|---------|
| `backend/routes/publications.py` | Publication and export endpoints |
| `backend/services/pdf_generator.py` | PDF generation logic and ReportLab calls |
| `backend/pdf_config.py` | ReportLab configuration, font setup, HTML sanitization rules |
| `backend/models.py` | `Publication`, `Topic`, `Snapshot` schema |
| `frontend/src/api/publications.js` (or similar) | Export API wrappers |
| `frontend/src/pages/Publications.vue` (or similar) | Publication UI and export buttons |

## Debug Tips

1. **Test HTML in ReportLab directly:**
   ```bash
   python -c "
   from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
   from reportlab.lib.styles import getSampleStyleSheet
   styles = getSampleStyleSheet()
   # Create sample PDF to test ReportLab works
   doc = SimpleDocTemplate('/tmp/test.pdf')
   doc.build([Paragraph('Test', styles['Heading1'])])
   print('ReportLab PDF created: /tmp/test.pdf')
   "
   ```

2. **Extract and inspect exported HTML:**
   - Export as HTML
   - Open in browser to check styling
   - Compare with source content

3. **Check database for Publication/Topic data:**
   ```bash
   python -c "
   from backend.app import create_app
   from backend.models import Publication
   app = create_app()
   with app.app_context():
       pub = Publication.query.first()
       print(f'ID: {pub.id}, Topics: {len(pub.topics)}')
   "
   ```

4. **Enable verbose ReportLab logging:**
   - Check ReportLab docs for debug flags
   - Monitor for font/image loading messages

5. **Test with small publication first:**
   - Create publication with 1-2 topics
   - Export and verify format
   - Gradually increase size

## ReportLab HTML Compatibility

Supported tags (subset):
- Paragraphs: `<p>`, `<br>`
- Headings: `<h1>` through `<h6>`
- Emphasis: `<b>`, `<i>`, `<u>`, `<strong>`, `<em>`
- Lists: `<ul>`, `<ol>`, `<li>` (limited nesting)
- Tables: `<table>`, `<tr>`, `<td>`, `<th>`
- Images: `<img>` (with `src` attribute)
- Line breaks: `<br/>`

**Avoid:**
- `<div>`, `<span>` (use `<p>` instead)
- Complex CSS (use inline `style` attributes)
- Absolute positioning
- JavaScript or dynamic content

## Migration Considerations

If modifying PDF/export behavior:
1. Test with real publications from production data
2. Verify backward compatibility (existing exports should still work)
3. Add admin setting or feature flag for new styles
4. Document HTML/CSS restrictions for content authors
5. Include regression tests for export formats

**Read:** [.github/instructions/migrations.instructions.md](../../.github/instructions/migrations.instructions.md)

## Related Topics

- [docs/README.md](../../docs/README.md) — General documentation hub
- ReportLab docs: http://www.reportlab.com/ (external)
