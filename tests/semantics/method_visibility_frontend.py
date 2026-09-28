#!/usr/bin/env python3
"""Check native static method errors stay parseable by the frontend."""
from pathlib import Path
import base64
import hashlib
import json
import subprocess
import tempfile

from recorded_worker import Worker

ROOT = Path(__file__).resolve().parents[2]
CONTROLS = ROOT / 'tests/semantics/method_visibility_frontend_controls.json'


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def run():
    controls = json.loads(CONTROLS.read_text())
    out = Path(tempfile.mkdtemp(prefix='method-visibility-frontend-', dir=ROOT / '.tools'))
    watched = [CONTROLS, Path(__file__), ROOT / 'frontend/worker.php',
               ROOT / 'frontend/encoding.php', ROOT / 'frontend/FileLexer.php',
               ROOT / 'tests/semantics/recorded_worker.py', ROOT / '.tools/php/bin/php',
               ROOT / '.tools/php-file.so']
    native_raw = ROOT / '.tools/nonpublic-native/native.json'
    if native_raw.exists():
        watched.append(native_raw)
    before = {str(path.relative_to(ROOT)): sha(path) for path in watched}
    worker = Worker([str(ROOT / '.tools/php/bin/php'), '-n', '-d',
                     'extension=' + str(ROOT / '.tools/php-file.so'),
                     str(ROOT / 'frontend/worker.php')], out / 'frontend')
    records = []
    try:
        for row in controls:
            if native_raw.exists():
                assert sha(native_raw) == row['native_raw_sha256'], row['id']
            source = out / (row['id'] + '.php')
            source.write_bytes(row['source'].encode())
            assert sha(source) == row['source_sha256'], row['id']
            native = subprocess.run([str(ROOT / '.tools/php/bin/php'),
                                     *row['native_profile'], str(source)],
                                    capture_output=True, timeout=10)
            expected = row['native_stderr_template'].replace('{FILE}', str(source)).encode()
            assert native.returncode == row['native_exit_status'], row['id']
            assert native.stdout == b'' and native.stderr == expected, row['id']
            parsed = worker.request({'op': 'parse', 'source': base64.b64encode(source.read_bytes()).decode()})
            assert parsed['accepted'] and row['expected_frontend_status'] == 'accepted', row['id']
            flags = parsed['ast']['program'][0]['fields'][5][0]['fields'][1]
            assert flags == {'int': str(row['expected_method_flags'])}, row['id']
            records.append({'id': row['id'], 'source_sha256': row['source_sha256'],
                            'native_raw_sha256': row['native_raw_sha256'],
                            'native_status': row['native_status'],
                            'frontend_status': 'accepted', 'method_flags': flags['int']})
        for source, message in [
            ('<?php class A{final abstract int $x;}',
             'Cannot use the final modifier on an abstract class member on line 1'),
            ('<?php class A{final abstract function f(){$x=new class{final abstract int $y;};}}',
             'Cannot use the final modifier on an abstract class member on line 1'),
            ('<?php class A{final abstract function f(); final final function g(){}}',
             'Multiple final modifiers are not allowed on line 1'),
            ('<?php final abstract class A{}',
             'Cannot use the final modifier on an abstract class on line 1'),
        ]:
            parsed = worker.request({'op': 'parse', 'source': base64.b64encode(source.encode()).decode()})
            assert not parsed['accepted'] and parsed['category'] == 'parser_rejection'
            assert base64.b64decode(parsed['message']).decode() == message
    finally:
        worker.close()
    assert all(sha(ROOT / name) == digest for name, digest in before.items())
    report = {'result': 'pass', 'frontend_admission': True, 'controls': len(records),
              'direct_inputs': before, 'records': records, 'raw': str(out)}
    (out / 'report.json').write_text(json.dumps(report, indent=2) + '\n')
    print(out, 'frontend admission pass', len(records))


if __name__ == '__main__':
    run()
