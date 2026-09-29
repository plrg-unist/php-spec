#!/usr/bin/env python3
"""Malformed finite file facts leave the live adapter pause untouched."""
import base64
import copy
import hashlib
import importlib.machinery
import json
import os
import subprocess
from pathlib import Path
import tempfile

from recorded_worker import Worker

ROOT = Path(__file__).resolve().parents[2]
CLI = importlib.machinery.SourceFileLoader('php_semantics_include', str(ROOT / 'bin/php-semantics')).load_module()
MAIN = b"<?php echo include 'one.php';"
CHILD = b'<?php return 7;'


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def b64(data):
    return base64.b64encode(data).decode()


def vendor_identity():
    tree = subprocess.check_output(['git', 'rev-parse', 'HEAD:vendor/php-parser-source'],
                                   cwd=ROOT, text=True).strip()
    dirty = subprocess.check_output(['git', 'status', '--porcelain',
                                     '--untracked-files=all', '--', 'vendor/php-parser-source'],
                                    cwd=ROOT, text=True)
    assert not dirty, 'vendored parser changed during campaign'
    return tree

def main():
    out = Path(tempfile.mkdtemp(prefix='include-adapter-protocol-', dir=ROOT / '.tools'))
    print(out, flush=True)
    modules = [ROOT / name for name in json.loads((ROOT / 'spec/semantics/modules.json').read_text())]
    inputs = [*modules, ROOT / 'spec/semantics/modules.json', ROOT / 'bin/php-semantics',
              ROOT / '_build/default/adapter/main.exe', ROOT / 'frontend/worker.php',
              ROOT / 'frontend/FileLexer.php', ROOT / 'frontend/EvalLexer.php',
              ROOT / 'frontend/autoload.php', ROOT / 'frontend/encoding-literal.php',
              ROOT / 'frontend/target.php', ROOT / 'frontend/SourcePrinter.php',
              ROOT / 'frontend/encoding.php', ROOT / 'spec/schema.json',
              ROOT / 'spec/php.watsup', ROOT / 'adapter/main.ml', ROOT / '.tools/php/bin/php',
              ROOT / '.tools/php-file.so', ROOT / 'tests/semantics/profile.json',
              ROOT / 'tests/semantics/recorded_worker.py', ROOT / 'frontend/wire.php', ROOT / 'frontend/wire.py',
              ROOT / 'tests/validate.py', Path(__file__)]
    before = {str(path.relative_to(ROOT)): digest(path) for path in inputs}
    vendor_before = vendor_identity()
    path = out / 'main.php'
    child = out / 'one.php'
    path.write_bytes(MAIN)
    child.write_bytes(CHILD)
    main_path = os.fsencode(path.resolve())
    child_path = os.fsencode(child.resolve())
    entry = {'caller': b64(main_path), 'requested': b64(b'one.php'),
             'status': 'opened', 'resolved': b64(child_path),
             'opened': b64(child_path), 'source': b64(CHILD)}
    snapshot = {'version': 1, 'main': b64(main_path),
                'cwd': b64(os.fsencode(ROOT.resolve())),
                'include_path': b64(b'.:'), 'entries': [entry]}
    frontend = Worker([str(ROOT / '.tools/php/bin/php'), '-n', '-d',
                       'extension=' + str(ROOT / '.tools/php-file.so'),
                       str(ROOT / 'frontend/worker.php')], out / 'frontend')
    adapter = CLI.AdapterSession([str(ROOT / '_build/default/adapter/main.exe'), str(ROOT)])
    checks = 0
    try:
        parsed = frontend.request({'op': 'parse', 'source': b64(MAIN)})
        assert parsed['accepted'], parsed
        initial = adapter.request({'op': 'execute', 'ast': parsed['ast'],
                                   'filename': b64(main_path), 'steps': 300,
                                   'file_snapshot': snapshot}, 30)
        assert initial['ok'] and initial['pending']['mode'] == 'file-resolve', initial
        checks += 1
        resolver = {'id': initial['pending']['id'], **entry}
        forged = copy.deepcopy(resolver)
        forged['opened'] = b64(b'/forged/one.php')
        rejected = adapter.request({'op': 'resume_file_resolve', 'response': forged}, 30)
        assert not rejected['ok'] and rejected['category'] == 'adapter_rejection', rejected
        checks += 1
        opened = adapter.request({'op': 'resume_file_resolve', 'response': resolver}, 30)
        assert opened['ok'] and opened['pending']['mode'] == 'file', opened
        assert opened['pending']['id'] == initial['pending']['id']
        checks += 2
        wrong_phase = adapter.request({'op': 'resume_file_resolve', 'response': resolver}, 30)
        assert not wrong_phase['ok'] and wrong_phase['category'] == 'adapter_rejection', wrong_phase
        checks += 1
        parsed_file = frontend.request({'op': 'parse-file', **opened['pending']})
        assert parsed_file['ok'] and parsed_file['accepted'], parsed_file
        response = {key: value for key, value in parsed_file.items() if key not in {'ok', 'diagnostics'}}
        checks += 1
        forged_file = copy.deepcopy(response)
        forged_file['source'] = b64(b'<?php return 8;')
        bad_parse = adapter.request({'op': 'resume_file_parse', 'response': forged_file}, 30)
        assert not bad_parse['ok'] and bad_parse['category'] == 'adapter_rejection', bad_parse
        checks += 1
        completed = adapter.request({'op': 'resume_file_parse', 'response': response}, 30)
        assert completed['ok'] and 'pending' not in completed, completed
        assert completed['state']['COMPLETION']['tag'] == 'NORMAL'
        checks += 2
        replay = adapter.request({'op': 'resume_file_parse', 'response': response}, 30)
        assert not replay['ok'] and replay['category'] == 'adapter_rejection', replay
        checks += 1
    finally:
        frontend.close()
        adapter.close()
    assert before == {str(path.relative_to(ROOT)): digest(path) for path in inputs}
    assert vendor_before == vendor_identity()
    report = {'result': 'pass', 'assertions': checks, 'inputs': before, 'vendor_parser_tree': vendor_before,
              'main_sha256': digest(path), 'child_sha256': digest(child),
              'snapshot_sha256': hashlib.sha256(json.dumps(snapshot, sort_keys=True).encode()).hexdigest(),
              'scope': 'Live resolve/parse pauses, forged responses, phase separation and one-shot replay.'}
    (out / 'report.json').write_text(json.dumps(report, indent=2) + '\n')
    print('include-adapter-protocol', checks, flush=True)
    return True


if __name__ == '__main__':
    raise SystemExit(0 if main() else 1)
