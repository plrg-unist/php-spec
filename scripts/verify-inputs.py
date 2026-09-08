#!/usr/bin/env python3
"""Verify the pinned import bytes, modes and contained symlinks."""
import hashlib
import json
from pathlib import Path
import sys

root = Path(__file__).resolve().parent.parent
count = 0
for line in (root / 'dependencies/files.jsonl').read_text().splitlines():
    entry = json.loads(line)
    path = root / entry['path']
    if 'symlink' in entry:
        valid = path.is_symlink() and str(path.readlink()) == entry['symlink']
        valid = valid and path.resolve().is_relative_to(root) and path.exists()
    else:
        valid = path.is_file() and not path.is_symlink()
        if valid:
            valid = (hashlib.sha256(path.read_bytes()).hexdigest() == entry['sha256']
                     and bool(path.stat().st_mode & 0o111) == entry['executable'])
    if not valid:
        sys.exit(f'Input verification failed: {entry["path"]}')
    count += 1
print(f'Verified {count} pinned import files/links')
