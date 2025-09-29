## Frontend UI Changes - Import Page

### Before (Original)
```
Import Content
┌─────────────────────────────────────────────┐
│ Import Type                                 │
│ ┌─────────────────┐ ┌─────────────────────┐ │
│ │ 📑              │ │ 🗂️                  │ │
│ │ Individual      │ │ Collection          │ │
│ │ Topics          │ │ (Document)          │ │
│ │ ✓ Selected      │ │                     │ │
│ └─────────────────┘ └─────────────────────┘ │
└─────────────────────────────────────────────┘

Format: [Word (.docx) ▼]
File: [Choose File] No file chosen
[📥 Start Import]
```

### After (With Hierarchy Option)
```
Import Content
┌─────────────────────────────────────────────┐
│ Import Type                                 │
│ ┌─────────────────┐ ┌─────────────────────┐ │
│ │ 📑              │ │ 🗂️                  │ │
│ │ Individual      │ │ Collection          │ │
│ │ Topics          │ │ (Document)          │ │
│ │ ✓ Selected      │ │                     │ │
│ └─────────────────┘ └─────────────────────┘ │
└─────────────────────────────────────────────┘

┌─────────────────────────────────────────────┐
│ Import Options                              │
│                                             │
│ ☑️ Preserve Document Hierarchy              │
│    Automatically create a collection with   │
│    topics organized by heading levels       │
│    (H1, H2, H3). Perfect for structured    │
│    documents where you want to maintain     │
│    the original organization.               │
└─────────────────────────────────────────────┘

Format: [Word (.docx) ▼]
File: [Choose File] employee_handbook.docx
[📥 Start Import]
```

### Result Flow

**Without Hierarchy (Unchecked)**:
Import → Import Review Page → Individual Topics

**With Hierarchy (Checked)**:
Import → Organize Page → Collection with Hierarchical Topics

### Key UI Elements Added

1. **Advanced Options Section**: Only appears for "Individual Topics"
2. **Checkbox**: "Preserve Document Hierarchy" with clear explanation
3. **Conditional Display**: Checkbox hidden for collection imports (redundant)
4. **Visual Feedback**: Check/uncheck state clearly visible
5. **Help Text**: Explains exactly what the feature does