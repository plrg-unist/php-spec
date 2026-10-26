#!/usr/bin/env python3
"""Reference-backed singleton ARRAY unpack at a fixed HALT constant call."""
import argparse
import base64
import hashlib
import json
import os
from pathlib import Path
import subprocess

import static_types as types

ROOT = Path(__file__).resolve().parents[2]
NAME = b'__COMPILER_HALT_OFFSET__'
ERROR = b'Undefined constant "' + NAME + b'"'
WRITE = (b"<?php $n='other'; $a=[&$n]; $n='__COMPILER_HALT_OFFSET__'; "
         b"echo 'P:',constant(...$a),'|'; __halt_compiler();PAYLOAD")
REBOUND = (b"<?php $n='__COMPILER_HALT_OFFSET__'; $a=[&$n]; $other='other'; $n =& $other; "
           b"echo 'N:',$n,'|R:',constant(...$a),'|'; __halt_compiler();PAYLOAD")
NAMED = (b"<?php $n='other'; $a=['name'=>&$n]; $n='__COMPILER_HALT_OFFSET__'; "
         b"echo 'N:',constant(...$a),'|'; __halt_compiler();PAYLOAD")
ABSENT = (b"<?php\n$n='__COMPILER_HALT_OFFSET__'; $a=[&$n]; unset($n);\n"
          b"try { constant(...$a); } catch (Error $e) {\n"
          b"  $t=$e->getTrace(); echo 'A:',$e->getMessage(),'|F:',($e->getFile()===__FILE__?'1':'0'),':',$e->getLine(),"
          b"'|T:',$t[0]['function'],':',$t[0]['args'][0];\n"
          b"} echo '|Z';\n")
REPEATED = (b"<?php function q($a){return constant(...$a);} $n='__COMPILER_HALT_OFFSET__'; $a=[&$n]; "
            b"echo 'P:',q($a),'|'; $n='other'; unset($a[0]); $a['name']=&$n; "
            b"$n='__COMPILER_HALT_OFFSET__'; echo 'N:',q($a),'|'; __halt_compiler();PAYLOAD")
CHILD = (b"<?php\nfunction childQuery(){\n"
         b"  $n='__COMPILER_HALT_OFFSET__'; $a=[&$n]; return constant(...$a);\n"
         b"}\n")
MAIN_CHILD = (b"<?php include 'child.php'; try { childQuery(); } catch (Error $e) { "
              b"echo 'C:',$e->getMessage(),'|F:',($e->getFile()===__DIR__.'/child.php'?'1':'0'),':',$e->getLine(),'|'; } "
              b"$n='__COMPILER_HALT_OFFSET__'; $a=[&$n]; echo 'M:',constant(...$a),'|'; __halt_compiler();PAYLOAD")
CASES = {
    'alias-live-write': (WRITE, None, b'P:' + str(WRITE.index(b'PAYLOAD')).encode() + b'|'),
    'alias-retained-cell': (REBOUND, None, b'N:other|R:' + str(REBOUND.index(b'PAYLOAD')).encode() + b'|'),
    'alias-named-write': (NAMED, None, b'N:' + str(NAMED.index(b'PAYLOAD')).encode() + b'|'),
    'alias-absent-trace': (ABSENT, None,
                           b'A:' + ERROR + b'|F:1:3|T:constant:' + NAME + b'|Z'),
    'alias-repeated-site': (REPEATED, None,
                            b'P:' + str(REPEATED.index(b'PAYLOAD')).encode() +
                            b'|N:' + str(REPEATED.index(b'PAYLOAD')).encode() + b'|'),
    'alias-child-file': (MAIN_CHILD, CHILD,
                         b'C:' + ERROR + b'|F:1:3|M:' +
                         str(MAIN_CHILD.index(b'PAYLOAD')).encode() + b'|'),
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


def freeze(out):
    out.mkdir(parents=True, exist_ok=False)
    records = []
    for name, (source, child, expected) in CASES.items():
        directory = out / name
        directory.mkdir()
        (directory / 'main.php').write_bytes(source)
        if child is not None:
            (directory / 'child.php').write_bytes(child)
            snapshot(directory)
        records.append({'id': name, 'main_sha256': digest(directory / 'main.php'),
                        'child_sha256': digest(directory / 'child.php') if child is not None else None,
                        'snapshot_sha256': digest(directory / 'snapshot.json') if child is not None else None,
                        'expected_stdout': b64(expected)})
    (out / 'freeze.json').write_text(json.dumps({
        'base': subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip(),
        'script_sha256': digest(Path(__file__)), 'cases': records}, indent=2) + '\n')


def run(out, phase, expected_status):
    freeze_record = json.loads((out / 'freeze.json').read_text())
    assert digest(Path(__file__)) == freeze_record['script_sha256']
    tracked = [ROOT / 'spec/semantics/400-dynamic-constants.watsup', ROOT / 'spec/semantics/modules.json',
               ROOT / 'bin/php-semantics', ROOT / 'frontend/worker.php', ROOT / 'tests/semantics/profile.json',
               ROOT / 'tests/semantics/static_types.py', Path(__file__), types.PHP,
               ROOT / '_build/default/adapter/main.exe']
    before = {str(path): digest(path) for path in tracked}
    records = []
    for frozen in freeze_record['cases']:
        name = frozen['id']
        source, child, expected = CASES[name]
        directory = out / name
        assert (directory / 'main.php').read_bytes() == source
        assert digest(directory / 'main.php') == frozen['main_sha256']
        if child is not None:
            assert (directory / 'child.php').read_bytes() == child
            assert digest(directory / 'child.php') == frozen['child_sha256']
            assert digest(directory / 'snapshot.json') == frozen['snapshot_sha256']
        assert b64(expected) == frozen['expected_stdout']
        if phase == 'native':
            command = [str(types.PHP), '-n', *types.FLAGS, str(directory / 'main.php')]
        else:
            assert (directory / 'native-stdout').read_bytes() == expected
            assert (directory / 'native-stderr').read_bytes() == b''
            command = [str(ROOT / 'bin/php-semantics'), str(directory / 'main.php')]
            if child is not None:
                command += ['--file-snapshot', str(directory / 'snapshot.json')]
            command += ['--steps', '100000', '--timeout', '60']
        result = subprocess.run(command, cwd=directory, env=types.ENV, capture_output=True, timeout=90)
        (directory / (phase + '-stdout')).write_bytes(result.stdout)
        (directory / (phase + '-stderr')).write_bytes(result.stderr)
        try:
            observed = json.loads(result.stdout) if phase == 'model' else None
        except json.JSONDecodeError:
            observed = None
        if phase == 'native':
            passed = result.returncode == 0 and result.stderr == b'' and result.stdout == expected
        elif expected_status == 'unsupported':
            passed = (result.returncode == 1 and result.stderr == b'' and observed is not None and
                      observed.get('frontend') == 'accepted' and observed.get('checked') == 'program' and
                      observed.get('status') == 'unsupported' and observed.get('reason') == 'halt offset constant query')
        else:
            passed = (result.returncode == 0 and result.stderr == b'' and observed is not None and
                      observed.get('frontend') == 'accepted' and observed.get('checked') == 'program' and
                      observed.get('status') == 'normal' and observed.get('exit_status') == 0 and
                      observed.get('stdout') == b64(expected) and observed.get('stderr') == b64(b''))
        records.append({'id': name, 'pass': passed, 'command': command, 'cwd': str(directory),
                        'exit': result.returncode, 'status': observed.get('status') if observed is not None else None,
                        'stdout_sha256': hashlib.sha256(result.stdout).hexdigest(),
                        'stderr_sha256': hashlib.sha256(result.stderr).hexdigest()})
        print(name, passed, flush=True)
    after = {str(path): digest(path) for path in tracked}
    report = {'phase': phase, 'expected_status': expected_status, 'result': 'pass' if all(r['pass'] for r in records) else 'fail',
              'revision': subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip(),
              'profile': types.PROFILE, 'environment': {'LC_ALL': 'C', 'TZ': 'UTC'},
              'freeze_sha256': digest(out / 'freeze.json'), 'inputs': before,
              'stable_inputs': before == after, 'records': records}
    if not report['stable_inputs']:
        report['result'] = 'fail'
    (out / (phase + '-' + (expected_status or 'exact') + '-report.json')).write_text(json.dumps(report, indent=2) + '\n')
    return report['result'] == 'pass'


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--phase', choices=['freeze', 'native', 'model'], required=True)
    parser.add_argument('--expected-status', choices=['unsupported', 'normal'])
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    out = args.output.resolve()
    if args.phase == 'freeze':
        freeze(out)
        return True
    if args.phase == 'model' and args.expected_status is None:
        parser.error('--expected-status is required for model')
    return run(out, args.phase, args.expected_status)


if __name__ == '__main__':
    raise SystemExit(0 if main() else 1)
