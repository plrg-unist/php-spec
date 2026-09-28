#!/usr/bin/env python3
"""Bridge four pinned parse-time modifier errors to checked CompileError results."""
from pathlib import Path
import base64
import hashlib
import json
import os
import subprocess
import sys
import tempfile

import static_types as types
from recorded_worker import Worker

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'tests'))
from corpus import phpt  # noqa: E402


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def run():
    ledger = ROOT / 'tests/phase-discrepancies.json'
    entries = [entry for entry in json.loads(ledger.read_text())
               if entry.get('direction') == 'frontend_accepts_static_rejection']
    assert len(entries) == 4
    before = types.syntax_validation.implementation_fingerprint()
    watched = [ledger, Path(__file__), ROOT / 'frontend/encoding.php', ROOT / 'frontend/worker.php',
               ROOT / 'bin/php-semantics', ROOT / 'tests/semantics/profile.json',
               ROOT / '.tools/php/bin/php', ROOT / '.tools/php-file.so']
    watched += [ROOT / name for name in json.loads((ROOT / 'spec/semantics/modules.json').read_text())]
    direct = {str(path.relative_to(ROOT)): sha(path) for path in watched}
    out = Path(tempfile.mkdtemp(prefix='method-modifier-phase-', dir=ROOT / '.tools'))
    worker = Worker([str(ROOT / '.tools/php/bin/php'), '-n', '-d',
                     'extension=' + str(ROOT / '.tools/php-file.so'),
                     str(ROOT / 'frontend/worker.php')], out / 'frontend')
    records = []
    environment = os.environ.copy()
    environment.update(LC_ALL='C', TZ='UTC')
    try:
        for entry in entries:
            record = phpt(ROOT / entry['id'])
            assert record['sha256'] == entry['sha256'] and record.get('ini', {}) == entry['ini']
            source = base64.b64decode(record['source_b64'])
            parsed = worker.request({'op': 'parse', 'source': record['source_b64']})
            oracle = worker.request({'op': 'oracle', 'source': record['source_b64']})
            assert parsed['accepted'] and not oracle['accepted']
            assert oracle['category'] == entry['oracle_category']
            assert base64.b64decode(oracle['message']).decode() == entry['oracle_message']
            flags = parsed['ast']['program'][0]['fields'][5][0]['fields'][1]
            assert int(flags['int']) & 48 == 48, entry['id']
            path = out / (Path(entry['id']).stem + '.php')
            path.write_bytes(source)
            native = subprocess.run([str(ROOT / '.tools/php/bin/php'), '-n', '-d',
                                     'display_errors=stderr', str(path)],
                                    capture_output=True, env=environment, timeout=15)
            model = subprocess.run([str(ROOT / 'bin/php-semantics'), str(path),
                                    '--steps', '100000', '--timeout', '45'],
                                   capture_output=True, env=environment, timeout=55)
            actual = json.loads(model.stdout)
            assert model.returncode == 0 and model.stderr == b''
            assert actual['status'] == 'static_rejection' and actual['exit_status'] == native.returncode
            assert actual['frontend'] == 'accepted' and actual['checked'] == 'program'
            assert base64.b64decode(actual['stdout']) == native.stdout == b''
            assert base64.b64decode(actual['stderr']) == native.stderr
            assert b'Stack trace:' not in native.stderr and entry['lint_contains'].encode() in native.stderr
            records.append({'id': entry['id'], 'source_sha256': entry['sha256'],
                            'method_flags': int(flags['int']), 'native_category': oracle['category'],
                            'model_status': actual['status'], 'native_exit_status': native.returncode,
                            'stderr_sha256': hashlib.sha256(native.stderr).hexdigest()})
            print(entry['id'], 'phase bridge pass', flush=True)
    finally:
        worker.close()
    assert before == types.syntax_validation.implementation_fingerprint()
    assert all(sha(ROOT / name) == digest for name, digest in direct.items())
    report = {'result': 'pass', 'cases': len(records), 'records': records,
              'fingerprint': before, 'direct_inputs': direct, 'raw': str(out)}
    (out / 'report.json').write_text(json.dumps(report, indent=2) + '\n')
    print(out, 'pass')


if __name__ == '__main__':
    run()
