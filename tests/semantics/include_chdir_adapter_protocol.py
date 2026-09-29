#!/usr/bin/env python3
"""Authenticate finite chdir facts and reject stale or forged responses."""
import base64
import hashlib
import json
import os
from pathlib import Path
import subprocess
import tempfile

from recorded_worker import Worker

ROOT = Path(__file__).resolve().parents[2]


def b64(data):
    return base64.b64encode(data).decode()


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def vendor_identity():
    tree = subprocess.check_output(['git', 'rev-parse', 'HEAD:vendor/php-parser-source'],
                                   cwd=ROOT, text=True).strip()
    dirty = subprocess.check_output(['git', 'status', '--porcelain',
                                     '--untracked-files=all', '--', 'vendor/php-parser-source'],
                                    cwd=ROOT, text=True)
    assert not dirty, 'vendored parser changed during campaign'
    return tree


def expect_rejected(worker, packet):
    try:
        worker.request(packet)
    except AssertionError as error:
        assert "'ok': False" in str(error), error
    else:
        raise AssertionError('forged provider packet was accepted')


def main():
    out = Path(tempfile.mkdtemp(prefix='include-chdir-adapter-', dir=ROOT / '.tools'))
    print(out, flush=True)
    modules = [ROOT / name for name in json.loads((ROOT / 'spec/semantics/modules.json').read_text())]
    inputs = [*modules, ROOT / 'spec/semantics/modules.json', ROOT / '_build/default/adapter/main.exe',
              ROOT / 'frontend/worker.php', ROOT / 'frontend/FileLexer.php', ROOT / 'frontend/EvalLexer.php',
              ROOT / 'frontend/autoload.php', ROOT / 'frontend/encoding-literal.php', ROOT / 'frontend/target.php',
              ROOT / 'frontend/SourcePrinter.php', ROOT / 'frontend/encoding.php', ROOT / 'frontend/wire.php',
              ROOT / 'frontend/wire.py', ROOT / 'spec/schema.json', ROOT / 'spec/php.watsup',
              ROOT / 'adapter/main.ml', ROOT / '.tools/php/bin/php', ROOT / '.tools/php-file.so',
              ROOT / 'tests/semantics/recorded_worker.py', Path(__file__)]
    before = {str(path.relative_to(ROOT)): digest(path) for path in inputs}
    vendor_before = vendor_identity()
    main_path = out / 'main.php'
    sub = out / 'sub'
    sub.mkdir()
    source = b"<?php chdir('__SUB__');".replace(b'__SUB__', os.fsencode(sub.resolve()))
    main_path.write_bytes(source)
    cwd = os.fsencode(ROOT.resolve())
    requested = os.fsencode(sub.resolve())
    success = {'cwd': b64(cwd), 'requested': b64(requested), 'status': 'success',
               'next_cwd': b64(requested)}
    failure = {'cwd': b64(cwd), 'requested': b64(b'missing'), 'status': 'failure',
               'stream_error': b64(b'No such file or directory'), 'errno': 2}
    snapshot = {'version': 2, 'main': b64(os.fsencode(main_path.resolve())),
                'cwd': b64(cwd), 'include_path': b64(b'.:'), 'entries': [],
                'chdir_entries': [success, failure]}
    frontend = Worker([str(ROOT / '.tools/php/bin/php'), '-n', '-d',
                       'extension=' + str(ROOT / '.tools/php-file.so'),
                       str(ROOT / 'frontend/worker.php')], out / 'frontend')
    adapter = Worker([str(ROOT / '_build/default/adapter/main.exe'), str(ROOT)], out / 'adapter')
    checks = 0
    try:
        parsed = frontend.request({'op': 'parse', 'source': b64(source)})
        assert parsed['accepted'], parsed
        execution = {'op': 'execute', 'ast': parsed['ast'], 'filename': snapshot['main'],
                     'steps': 300, 'file_snapshot': snapshot}
        missing = {key: value for key, value in snapshot.items() if key != 'chdir_entries'}
        expect_rejected(adapter, {**execution, 'file_snapshot': missing})
        checks += 1
        duplicate = {**snapshot, 'chdir_entries': [success, success]}
        expect_rejected(adapter, {**execution, 'file_snapshot': duplicate})
        checks += 1
        for malformed in (b'relative', b'/with\0nul'):
            bad_success = {**success, 'next_cwd': b64(malformed)}
            bad_snapshot = {**snapshot, 'chdir_entries': [bad_success, failure]}
            expect_rejected(adapter, {**execution, 'file_snapshot': bad_snapshot})
            checks += 1
        start = adapter.request(execution)
        assert start['ok'] and start['pending']['mode'] == 'chdir', start
        pending = start['pending']
        assert pending['id'] == '0' and pending['cwd'] == b64(cwd) and pending['requested'] == b64(requested)
        checks += 2
        valid = {'id': pending['id'], 'site': pending['site'], **success}
        for forged in [
            {**valid, 'id': '1'},
            {**valid, 'site': {'tag': 'PORIGIN', 'args': ['999', []]}},
            {**valid, 'cwd': b64(b'/forged')},
            {**valid, 'requested': b64(b'forged')},
            {**valid, 'next_cwd': b64(b'/forged')},
            {key: value for key, value in valid.items() if key != 'next_cwd'},
            {**valid, 'extra': 1},
            {'id': pending['id'], 'site': pending['site'], **failure},
        ]:
            expect_rejected(adapter, {'op': 'resume_chdir', 'response': forged})
            checks += 1
        checked = adapter.request({'op': 'check_chdir', 'snapshot': snapshot,
                                   'pending': {key: value for key, value in pending.items() if key != 'mode'},
                                   'response': valid})
        assert checked['ok']
        checks += 1
        done = adapter.request({'op': 'resume_chdir', 'response': valid})
        assert done['ok'] and 'pending' not in done
        assert done['state']['FILECWD'] == [str(byte) for byte in requested]
        assert done['state']['DIRCONTEXT'] is None and done['state']['DIRSEQ'] == '1'
        checks += 3
        expect_rejected(adapter, {'op': 'resume_chdir', 'response': valid})
        checks += 1
    finally:
        frontend.close()
        adapter.close()
    after = {str(path.relative_to(ROOT)): digest(path) for path in inputs}
    vendor_after = vendor_identity()
    report = {'passed': True, 'checks': checks, 'source_sha256': digest(main_path),
              'snapshot_sha256': hashlib.sha256(json.dumps(snapshot, sort_keys=True).encode()).hexdigest(),
              'inputs': before, 'vendor_tree': vendor_before,
              'input_changes': [key for key in before if before[key] != after[key]]}
    (out / 'report.json').write_text(json.dumps(report, indent=2, sort_keys=True) + '\n')
    assert not report['input_changes']
    assert vendor_before == vendor_after
    print('checks', checks, flush=True)


if __name__ == '__main__':
    main()
