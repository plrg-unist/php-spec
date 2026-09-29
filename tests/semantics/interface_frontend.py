#!/usr/bin/env python3
"""Keep native compile-time readonly method sources in checked syntax."""
from pathlib import Path
import base64
import hashlib
import json
import tempfile

from recorded_worker import Worker

ROOT = Path(__file__).resolve().parents[2]
SOURCES = [
    ('interface', b'<?php interface I { public readonly function f(); }', 3),
    ('class', b'<?php class C { public readonly function f() {} }', 5),
]
MIXED = b'<?php interface I { public readonly function f(); final final function g(); }'


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def run():
    watched = [Path(__file__), ROOT / 'frontend/encoding.php', ROOT / 'frontend/target.php',
               ROOT / 'frontend/worker.php', ROOT / '.tools/php/bin/php', ROOT / '.tools/php-file.so']
    before = {str(path.relative_to(ROOT)): sha(path) for path in watched}
    out = Path(tempfile.mkdtemp(prefix='interface-frontend-', dir=ROOT / '.tools'))
    worker = Worker([str(ROOT / '.tools/php/bin/php'), '-n', '-d',
                     'extension=' + str(ROOT / '.tools/php-file.so'),
                     str(ROOT / 'frontend/worker.php')], out / 'frontend')
    records = []
    try:
        for name, source, members in SOURCES:
            encoded = base64.b64encode(source).decode()
            parsed = worker.request({'op': 'parse', 'source': encoded})
            oracle = worker.request({'op': 'oracle', 'source': encoded})
            assert parsed['accepted'] and not oracle['accepted']
            assert oracle['category'] == 'parser_static_rejection'
            assert base64.b64decode(oracle['message']) == b'Cannot use the readonly modifier on a method'
            method = parsed['ast']['program'][0]['fields'][members][0]
            assert method['node'] == 'Stmt_ClassMethod' and method['fields'][1] == {'int': '65'}
            records.append({'id': name, 'source_sha256': hashlib.sha256(source).hexdigest(),
                            'flags': 65, 'oracle': oracle['category']})
        encoded = base64.b64encode(MIXED).decode()
        parsed = worker.request({'op': 'parse', 'source': encoded})
        oracle = worker.request({'op': 'oracle', 'source': encoded})
        assert not parsed['accepted'] and parsed['category'] == 'parser_rejection'
        assert base64.b64decode(parsed['message']).startswith(b'Multiple final modifiers')
        assert not oracle['accepted'] and oracle['category'] == 'parser_static_rejection'
        records.append({'id': 'mixed_error_rejected', 'source_sha256': hashlib.sha256(MIXED).hexdigest()})
    finally:
        worker.close()
    assert all(sha(ROOT / name) == digest for name, digest in before.items())
    report = {'result': 'pass', 'records': records, 'direct_inputs': before}
    (out / 'report.json').write_text(json.dumps(report, indent=2) + '\n')
    print(out, 'pass', len(records))


if __name__ == '__main__':
    run()
