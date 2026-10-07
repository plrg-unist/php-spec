#!/usr/bin/env python3
"""Exact genuine clone callback, declaration and terminal-unwind originals."""
import argparse
import base64
import hashlib
import json
import os
from pathlib import Path
import tempfile

import typed_static_ini_prefix_protocol as cross

ROOT = Path(__file__).resolve().parents[2]
ROWS = json.loads(Path(__file__).with_name('readonly_clone_cases.json').read_text())['cases']
CASES = {row['id']: row['source'].encode() for row in ROWS}
EXPECTED = {row['id']: row['expected_stdout'] for row in ROWS}


def snapshot(freeze_path):
    modules = json.loads((ROOT/'spec/semantics/modules.json').read_text())
    watched = [*modules, 'spec/semantics/modules.json', 'frontend/encoding.php',
               'frontend/worker.php', 'tests/semantics/readonly_clone_cases.json',
               'tests/semantics/readonly_clone_sources.py',
               'tests/semantics/readonly_clone_protocol.py', 'tests/semantics/profile.json',
               'tests/semantics/static_types.py', 'tests/semantics/recorded_worker.py',
               'tests/semantics/typed_static_ini_prefix_protocol.py',
               'tests/semantics/typed_static_invoke_set_protocol.py',
               'bin/php-semantics', '.tools/php/bin/php', '.tools/php-file.so',
               '.tools/cprefix-compiler/compiler', '_build/default/adapter/main.exe',
               'tests/semantics/_build/default/numeric_runner.exe']
    result = {'ordered_modules': modules,
              'watched': {name: {'sha256': hashlib.sha256((ROOT/name).read_bytes()).hexdigest(),
                                 'mode': oct((ROOT/name).stat().st_mode & 0o7777)}
                          for name in watched}}
    if freeze_path:
        result['freeze'] = cross.snapshot(freeze_path)
    return result


def source(row, directory, path):
    native = cross.invoke.process([str(ROOT/'.tools/php/bin/php'), '-n',
        *cross.invoke.types.FLAGS, str(path)], directory/'native', 30, directory)
    assert native.returncode == row['expected_exit_status']
    assert native.stdout == row['expected_stdout'].encode()
    if row['kind'] == 'compiler':
        message = row['expected_compile_message'].encode(); line = row['expected_compile_line']
        stderr = (b'Fatal error: '+message+b' in '+os.fsencode(path)+b' on line '+
                  str(line).encode()+b'\nStack trace:\n#0 {main}\n')
    else:
        stderr = row['expected_stderr'].encode()
    assert native.stderr == stderr
    facts = {'version': 2, 'main': cross.invoke.b64(os.fsencode(path)),
             'cwd': cross.invoke.b64(os.fsencode(directory)),
             'include_path': cross.invoke.b64(b'.:'), 'entries': [], 'chdir_entries': []}
    snapshot = directory/'snapshot.json'; snapshot.write_text(json.dumps(facts)+'\n')
    model = cross.invoke.process([str(ROOT/'bin/php-semantics'), str(path), '--file-snapshot',
        str(snapshot), '--steps', '100000', '--timeout', '60'], directory/'model', 90, directory)
    assert model.returncode == 0 and not model.stderr
    value = json.loads(model.stdout)
    assert value['frontend'] == 'accepted' and value['checked'] == 'program'
    assert value['reason'] is None and value['exit_status'] == native.returncode
    assert base64.b64decode(value['stdout'], validate=True) == native.stdout
    assert base64.b64decode(value['stderr'], validate=True) == native.stderr
    if row['kind'] == 'compiler':
        assert value['status'] == row.get('expected_model_status', 'static_rejection')
        assert value['diagnostic']['class'] == 'CompileError' and value['diagnostic']['line'] == line
        assert base64.b64decode(value['diagnostic']['message'], validate=True) == message
    else:
        assert value['status'] == row.get('expected_model_status', 'normal') and value['diagnostic'] is None
    return {'status': value['status'], 'exit_status': value['exit_status']}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--kind', choices=['normal', 'compiler', 'exit'], default='normal')
    parser.add_argument('--select', help='Comma-separated exact IDs; overrides --kind')
    parser.add_argument('--freeze', type=Path)
    args = parser.parse_args()
    names = args.select.split(',') if args.select else [r['id'] for r in ROWS if r['kind'] == args.kind]
    assert names and len(names) == len(set(names)) and all(name in CASES for name in names)
    os.environ.update(LC_ALL='C', TZ='UTC', GIT_OPTIONAL_LOCKS='0')
    before = snapshot(args.freeze)
    out = Path(tempfile.mkdtemp(prefix='readonly-clone-source-', dir=ROOT/'.tools')).resolve()
    report = {'passed': False, 'before': before, 'profile': cross.invoke.types.PROFILE,
              'selected': names, 'jobs': 1, 'records': []}
    print(out, flush=True)
    try:
        for name in names:
            row = next(r for r in ROWS if r['id'] == name)
            directory = out/name; directory.mkdir()
            path = directory/'source.php'; path.write_bytes(CASES[name])
            assert hashlib.sha256(path.read_bytes()).hexdigest() == row['source_sha256']
            record = {'case': name, 'source_sha256': row['source_sha256'], 'completed': False}
            report['records'].append(record)
            record['outcome'] = source(row, directory, path)
            record['completed'] = True
            print(name, record['outcome']['status'], flush=True)
        report['passed'] = True
    except BaseException as error:
        report['failure'] = {'type': type(error).__name__, 'message': str(error)}
        raise
    finally:
        report['after'] = snapshot(args.freeze)
        report['passed'] = report['passed'] and report['before'] == report['after']
        (out/'report.json').write_text(json.dumps(report, indent=2)+'\n')
        print(out/'report.json', report['passed'], flush=True)
    assert report['passed']


if __name__ == '__main__':
    main()
