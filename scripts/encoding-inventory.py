#!/usr/bin/env python3
"""Record Zend's bundled mbstring lexer-compatibility flags, not a charset guess."""
import json
from pathlib import Path
import re
root = Path(__file__).resolve().parents[1]
unsafe = []
for path in sorted((root / 'vendor/php-src/ext/mbstring/libmbfl').rglob('*.c')):
    for match in re.finditer(r'const mbfl_encoding \w+\s*=\s*\{(.*?)\};', path.read_text(), re.S):
        fields = match.group(1).split(',')
        if len(fields) > 5 and 'MBFL_ENCTYPE_GL_UNSAFE' in fields[5]:
            name = re.fullmatch(r'\s*"([^"]+)"\s*', fields[1]).group(1)
            unsafe.append({'name': name, 'source': str(path.relative_to(root)), 'line': path.read_text()[:match.start()].count('\n') + 1})
(root / 'spec/lexer-encodings.json').write_text(json.dumps(unsafe, indent=2) + '\n')
print(f'{len(unsafe)} lexer-unsafe encodings from pinned mbfl flags')
