#!/usr/bin/env python3
"""Fixed defined CV queries of filename-local HALT registration."""
import argparse
import base64
import hashlib
import json
import os
from pathlib import Path
import subprocess

import static_types as types

ROOT = Path(__file__).resolve().parents[2]
MAIN_PRESENT = b"<?php $n='__COMPILER_HALT_OFFSET__'; echo 'V:',(defined($n)?'1':'0'),'|L:',(defined('__COMPILER_HALT_OFFSET__')?'1':'0'),'|'; __halt_compiler();PAYLOAD"
CHILD = b"<?php $n='__COMPILER_HALT_OFFSET__'; echo 'I:',(defined($n)?'1':'0'),'|'; __halt_compiler();PAYLOAD"
CASES = {
    'main-present-literal-contrast': (MAIN_PRESENT, None, b'V:1|L:0|'),
    'main-absent': (
        b"<?php $n='__COMPILER_HALT_OFFSET__'; echo 'A:',(defined($n)?'1':'0'),'|';\n",
        None, b'A:0|'),
    'child-present-main-absent': (
        b"<?php include 'child.php'; $n='__COMPILER_HALT_OFFSET__'; echo 'M:',(defined($n)?'1':'0'),'|';\n",
        CHILD, b'I:1|M:0|'),
    'main-present-eval-absent': (
        b"<?php $n='__COMPILER_HALT_OFFSET__'; echo 'E:',eval('return defined($n) ? \"1\" : \"0\";'),'|M:',(defined($n)?'1':'0'),'|'; __halt_compiler();PAYLOAD",
        None, b'E:0|M:1|'),
}


def b64(value):
    return base64.b64encode(value).decode()


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def snapshot(directory):
    main, child = directory / 'main.php', directory / 'child.php'
    child_name = os.fsencode(child)
    entry = {'caller': b64(os.fsencode(main)), 'requested': b64(b'child.php'),
             'cwd': b64(os.fsencode(directory)), 'include_path': b64(b'.:'),
             'status': 'opened', 'resolved': b64(child_name), 'opened': b64(child_name),
             'source': b64(child.read_bytes())}
    (directory / 'snapshot.json').write_text(json.dumps({
        'version': 2, 'main': b64(os.fsencode(main)), 'cwd': b64(os.fsencode(directory)),
        'include_path': b64(b'.:'), 'chdir_entries': [], 'entries': [entry]}, indent=2) + '\n')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--phase', choices=['native', 'model'], required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    out = args.output.resolve()
    out.mkdir(parents=True, exist_ok=True)
    tracked = [ROOT / 'spec/semantics/400-dynamic-constants.watsup', ROOT / 'spec/semantics/modules.json',
               ROOT / 'bin/php-semantics', ROOT / 'frontend/worker.php', ROOT / 'tests/semantics/profile.json',
               ROOT / 'tests/semantics/static_types.py', Path(__file__), ROOT / '.tools/php/bin/php',
               ROOT / '_build/default/adapter/main.exe']
    before = {str(path): digest(path) for path in tracked}
    records = []
    for name, (source, child, expected) in CASES.items():
        directory = out / name
        if args.phase == 'native':
            directory.mkdir()
            (directory / 'main.php').write_bytes(source)
            if child is not None:
                (directory / 'child.php').write_bytes(child)
                snapshot(directory)
            command = [str(types.PHP), '-n', *types.FLAGS, str(directory / 'main.php')]
        else:
            assert (directory / 'main.php').read_bytes() == source
            assert child is None or (directory / 'child.php').read_bytes() == child
            assert (directory / 'native-stdout').read_bytes() == expected
            assert (directory / 'native-stderr').read_bytes() == b''
            command = [str(ROOT / 'bin/php-semantics'), str(directory / 'main.php')]
            if child is not None:
                command += ['--file-snapshot', str(directory / 'snapshot.json')]
            command += ['--steps', '100000', '--timeout', '60']
        result = subprocess.run(command, cwd=directory, env=types.ENV, capture_output=True, timeout=90)
        (directory / (args.phase + '-stdout')).write_bytes(result.stdout)
        (directory / (args.phase + '-stderr')).write_bytes(result.stderr)
        try:
            observed = json.loads(result.stdout) if args.phase == 'model' and result.returncode == 0 else None
        except json.JSONDecodeError:
            observed = None
        passed = (result.returncode == 0 and result.stderr == b'' and
                  (result.stdout == expected if args.phase == 'native' else
                   observed is not None and observed.get('frontend') == 'accepted' and observed.get('checked') == 'program' and
                   observed.get('status') == 'normal' and observed.get('exit_status') == 0 and
                   observed.get('stdout') == b64(expected) and observed.get('stderr') == b64(b'')))
        records.append({'id': name, 'pass': passed, 'command': command, 'cwd': str(directory),
                        'exit': result.returncode, 'source_sha256': digest(directory / 'main.php'),
                        'child_sha256': digest(directory / 'child.php') if child is not None else None,
                        'snapshot_sha256': digest(directory / 'snapshot.json') if child is not None else None,
                        'status': observed.get('status') if observed is not None else None})
        print(name, passed, flush=True)
        if not passed and args.phase == 'native':
            break
    after = {str(path): digest(path) for path in tracked}
    report = {'phase': args.phase, 'result': 'pass' if len(records) == len(CASES) and all(row['pass'] for row in records) else 'fail',
              'revision': subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip(),
              'profile': types.PROFILE, 'environment': {'LC_ALL': 'C', 'TZ': 'UTC'},
              'inputs': before, 'stable_inputs': before == after, 'records': records}
    if not report['stable_inputs']:
        report['result'] = 'fail'
    (out / (args.phase + '-report.json')).write_text(json.dumps(report, indent=2) + '\n')
    return report['result'] == 'pass'


if __name__ == '__main__':
    raise SystemExit(0 if main() else 1)
