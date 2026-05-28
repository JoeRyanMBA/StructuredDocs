---
description: "Debug the StructuredDocs import pipeline. Use when Word, HTML, or Markdown imports fail, staging data is wrong, images are missing, pandoc conversion breaks, or imported hierarchy parsing needs investigation."
name: "Debug Import Flow"
argument-hint: "Describe the import failure, symptoms, file type, and any logs or endpoints involved"
agent: "backend-specialist"
---
Debug the StructuredDocs import problem described in this chat input.

Focus areas:
- Start with the narrowest failing behavior and trace the controlling path in `backend/routes/import_handler.py`.
- Check whether the issue is in upload handling, pandoc conversion, extracted media processing, image storage, markdown rewriting, staging models, hierarchy parsing, or commit from staging into topics.
- Use the existing import models and serializers to inspect where data becomes incorrect.
- If images are involved, verify whether storage is configured for local fallback or S3-compatible storage before changing logic.
- If the failure is reviewer- or publication-adjacent rather than import-core, step to the directly responsible route or model instead of widening scope.
- Prefer the smallest code change that proves or fixes the issue, then run the narrowest validation available.

Useful repo references:
- [backend/routes/import_handler.py](../../backend/routes/import_handler.py)
- [import-guide.md](../../docs/import-guide.md)
- [README.md](../../README.md)
