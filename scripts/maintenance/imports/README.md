# Import maintenance utilities

These scripts are for diagnosing or repairing imported content; they are not
used by normal application requests.

Run Python tools from the repository root as modules, for example:

```bash
python -m scripts.maintenance.imports.fix_image_display_tool
python -m scripts.maintenance.imports.cleanup_import_images_helper --help
```

Some utilities modify topic content, database rows, or image files. Review the
tool's options and back up affected data before applying changes.
