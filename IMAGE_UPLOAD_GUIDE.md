# Image Upload Guide

## For Images That Don't Display in WYSIWYG Editor

### Quick Fix Steps:

1. **Open the Topic Editor**
   - Navigate to the topic with missing images
   - Switch to markdown mode to see the image references

2. **Upload Images Manually**
   - Click the 🖼️ Image button in the editor toolbar
   - Upload your image files (must be web formats: .png, .jpg, .gif, .webp)
   - For .emf files: convert them to .png first using an image editor

3. **Replace the Markdown**
   - Delete the old image markdown (e.g., `![](media/image1.png)`)
   - The upload will insert correct markdown (e.g., `![Image](/images/filename.png)`)

4. **Switch to WYSIWYG Mode**
   - Images should now display correctly
   - WYSIWYG editor can render standard markdown image syntax

### Why This Was Needed:

- `media/` paths don't work in web browsers
- `{width="..."}` syntax is Pandoc-specific, not standard markdown
- `.emf` files are not web-compatible formats

### Correct Image Markdown Format:
```markdown
![Alt Text](/images/filename.png)
```

### Avoid These Formats:
```markdown
![](media/image.png){width="6in" height="4in"}  ❌
![](image.emf)                                   ❌
```
