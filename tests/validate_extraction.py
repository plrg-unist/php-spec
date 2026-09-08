#!/usr/bin/env python3
"""Compare every imported PHPT extraction against the pinned runner reader."""
import collections
import json
import subprocess
from corpus import ROOT, config, phpt, sections

# Byte-oriented section boundaries, DONE marker inclusion, and encoding settings.
assert sections(b'--TEST--\nx\n--FILE--\na\v\rb\n===DONE===\nignored\n--EXPECT--\nx\n')['FILE'] == b'a\v\rb\n===DONE===\n'
assert config(b'internal_encoding=CP932\r\nzend.detect_unicode=0\nmbstring.internal_encoding=UTF-8\n') == {
    'internal_encoding': 'CP932', 'zend.detect_unicode': '0', 'mbstring.internal_encoding': 'UTF-8'}
paths = sorted((ROOT / 'vendor/php-src').rglob('*.phpt'))
reference = subprocess.run([str(ROOT / '.tools/php/bin/php'), '-n', str(ROOT / 'tests/phpt-reference.php')],
    input=''.join(json.dumps(str(path)) + '\n' for path in paths).encode(), capture_output=True, check=True)
rows = reference.stdout.splitlines()
assert len(rows) == len(paths), reference.stderr.decode(errors='replace')
counts = collections.Counter()
for path, line in zip(paths, rows):
    expected, actual = json.loads(line), phpt(path)
    for key in ('status', 'source_b64', 'ini_b64'):
        assert expected.get(key) == actual.get(key), (str(path.relative_to(ROOT)), key, expected.get('error'))
    counts[actual['status'] + ':' + actual.get('section', '')] += 1
print(json.dumps({'phpt_files': len(paths), 'runner_extraction_matches': len(paths), 'counts': counts}, sort_keys=True))
