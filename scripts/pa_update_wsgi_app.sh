#!/usr/bin/env bash
#!/usr/bin/env bash
# Legacy placeholder script.

set -euo pipefail

echo "This helper no longer performs any actions. Consult the deployment documentation instead."
        if line.startswith('#!') or line.strip().startswith('"""') or line.strip().startswith("'''") or not line.strip() or line.strip().startswith('#'):
            insert_idx = i + 1
            continue
        insert_idx = i + 1
        break
    lines.insert(insert_idx, f"from {mod} import {func}")
    src = "\n".join(lines)

# 3) Normalize application assignment to use target factory
patterns = [
    r"application\s*=\s*create_app\(\)",
    r"application\s*=\s*[A-Za-z_][A-Za-z0-9_]*\(\)",
    r"application\s*=\s*[A-Za-z_][A-Za-z0-9_]*",
]
replaced = False
for pat in patterns:
    new_src, n = re.subn(pat, f"application = {func}()", src, count=1)
    if n:
        src = new_src
        replaced = True
        break

if not replaced:
    src += f"\n\n# Injected by pa_update_wsgi_app.sh\napplication = {func}()\n"

open(path, 'w', encoding='utf-8').write(src)
print("Patched:", path)
PY

echo "Done patching WSGI file."
REMOTE

echo "Tip: run ./scripts/pa_reload.sh to apply changes."
