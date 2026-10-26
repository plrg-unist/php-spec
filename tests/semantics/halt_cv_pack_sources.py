#!/usr/bin/env python3
"""Singleton ordinary-CV ARRAY unpack queries of filename-local HALT registration."""
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
POSITIVE_COW = (b"<?php $a=['other']; $s=$a; $a[0]='__COMPILER_HALT_OFFSET__'; "
                b"echo 'S:',$s[0],'|P:',constant(...$a),'|'; __halt_compiler();PAYLOAD")
POSITIVE_NAMED = (b"<?php $a=['__COMPILER_HALT_OFFSET__']; $s=$a; unset($a[0]); "
                  b"$a['name']='__COMPILER_HALT_OFFSET__'; echo 'S:',(isset($s[0])?'0':'X'),'|N:',constant(...$a),'|'; "
                  b"__halt_compiler();PAYLOAD")
ABSENT = (b"<?php\n$a=['__COMPILER_HALT_OFFSET__']; try { constant(...$a); } catch (Error $e) {\n"
          b"    $t=$e->getTrace(); $args=$t[0]['args'];\n"
          b"    echo 'A:',$e->getMessage(),'|',($e->getFile()===__FILE__?'F':'BAD'),':',$e->getLine(),':',$t[0]['function'],':',"
          b"(isset($args[0])?'0':'X'),':',(isset($args['name'])?'N':'X'),':',$args[0];\n"
          b"} echo '|Z';\n")
CHILD = b"<?php\nfunction childQuery(){\n  $a=['__COMPILER_HALT_OFFSET__']; return constant(...$a);\n}\n"
MAIN_CHILD = (b"<?php include 'child.php'; try { childQuery(); } catch (Error $e) { "
              b"echo 'C:',$e->getMessage(),'|',($e->getFile()===__DIR__.'/child.php'?'F':'BAD'),':',$e->getLine(),'|'; } "
              b"$a=['__COMPILER_HALT_OFFSET__']; echo 'M:',constant(...$a),'|'; __halt_compiler();PAYLOAD")
EVAL_MAIN = (b"<?php $a=['__COMPILER_HALT_OFFSET__']; try { eval('return constant(...$a);'); } "
             b"catch (Error $e) { echo 'E:',$e->getMessage(),'|'; } "
             b"echo 'M:',constant(...$a),'|'; __halt_compiler();PAYLOAD")
REPEATED = (b"<?php function q($a){ return constant(...$a); } "
            b"$a=['__COMPILER_HALT_OFFSET__']; echo 'P:',q($a),'|'; "
            b"$a=['name'=>'__COMPILER_HALT_OFFSET__']; echo 'N:',q($a),'|'; "
            b"__halt_compiler();PAYLOAD")
ALIAS = (b"<?php $n='__COMPILER_HALT_OFFSET__'; $a=[&$n]; "
         b"echo 'R:',constant(...$a),'|'; __halt_compiler();PAYLOAD")
CASES = {
    'cv-cow-positional': (POSITIVE_COW, None,
        b'S:other|P:' + str(POSITIVE_COW.index(b'PAYLOAD')).encode() + b'|'),
    'cv-key-rewrite-named': (POSITIVE_NAMED, None,
        b'S:0|N:' + str(POSITIVE_NAMED.index(b'PAYLOAD')).encode() + b'|'),
    'cv-absent-trace': (ABSENT, None,
        b'A:' + ERROR + b'|F:2:constant:0:X:' + NAME + b'|Z'),
    'cv-child-function': (MAIN_CHILD, CHILD,
        b'C:' + ERROR + b'|F:3|M:' + str(MAIN_CHILD.index(b'PAYLOAD')).encode() + b'|'),
    'cv-main-present-eval-absent': (EVAL_MAIN, None,
        b'E:' + ERROR + b'|M:' + str(EVAL_MAIN.index(b'PAYLOAD')).encode() + b'|'),
    'cv-repeated-site': (REPEATED, None,
        b'P:' + str(REPEATED.index(b'PAYLOAD')).encode() + b'|N:' + str(REPEATED.index(b'PAYLOAD')).encode() + b'|'),
    'cv-wrong-key-before-halt': (
        b"<?php $a=['Name'=>'__COMPILER_HALT_OFFSET__']; try { constant(...$a); } catch (Error $e) { echo 'B:',$e->getMessage(),'|'; } echo 'Z'; __halt_compiler();PAYLOAD",
        None, b'B:Unknown named parameter $Name|Z'),
    'cv-duplicate-before-halt': (
        b"<?php $a=['name'=>'__COMPILER_HALT_OFFSET__']; try { constant('__COMPILER_HALT_OFFSET__', ...$a); } catch (Error $e) { echo 'D:',$e->getMessage(),'|'; } echo 'Z'; __halt_compiler();PAYLOAD",
        None, b'D:Named parameter $name overwrites previous argument|Z'),
    'cv-alias-leaf-control': (ALIAS, None,
        b'R:' + str(ALIAS.index(b'PAYLOAD')).encode() + b'|'),
}
UNSUPPORTED = {'cv-alias-leaf-control'}


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
            assert (directory / 'native-stderr').read_bytes() == b''
            command = [str(ROOT / 'bin/php-semantics'), str(directory / 'main.php')]
            if child is not None:
                command += ['--file-snapshot', str(directory / 'snapshot.json')]
            command += ['--steps', '100000', '--timeout', '60']
        result = subprocess.run(command, cwd=directory, env=types.ENV, capture_output=True, timeout=90)
        (directory / (args.phase + '-stdout')).write_bytes(result.stdout)
        (directory / (args.phase + '-stderr')).write_bytes(result.stderr)
        oracle = result.stdout if args.phase == 'native' else (directory / 'native-stdout').read_bytes()
        expected_ok = oracle == expected
        try:
            observed = json.loads(result.stdout) if args.phase == 'model' and result.returncode == 0 else None
        except json.JSONDecodeError:
            observed = None
        if args.phase == 'model' and name in UNSUPPORTED:
            try:
                observed = json.loads(result.stdout)
            except json.JSONDecodeError:
                observed = None
            passed = (expected_ok and result.returncode == 1 and result.stderr == b'' and
                      observed is not None and observed.get('frontend') == 'accepted' and
                      observed.get('checked') == 'program' and observed.get('status') == 'unsupported' and
                      observed.get('reason') == 'halt offset constant query')
        else:
            passed = (expected_ok and result.returncode == 0 and result.stderr == b'' and
                      (args.phase == 'native' or observed is not None and observed.get('frontend') == 'accepted' and
                       observed.get('checked') == 'program' and observed.get('status') == 'normal' and
                       observed.get('exit_status') == 0 and observed.get('stdout') == b64(oracle) and
                       observed.get('stderr') == b64(b'')))
        records.append({'id': name, 'pass': passed, 'command': command, 'cwd': str(directory),
                        'exit': result.returncode, 'source_sha256': digest(directory / 'main.php'),
                        'child_sha256': digest(directory / 'child.php') if child is not None else None,
                        'snapshot_sha256': digest(directory / 'snapshot.json') if child is not None else None,
                        'oracle_stdout_sha256': hashlib.sha256(oracle).hexdigest(),
                        'status': observed.get('status') if observed is not None else None,
                        'category': 'unsupported-control' if name in UNSUPPORTED else 'agreement'})
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
