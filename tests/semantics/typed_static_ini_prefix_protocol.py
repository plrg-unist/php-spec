#!/usr/bin/env python3
"""Raw INI bytes and effective old values through invoke/SET/static conversion."""
import argparse
import base64
import json
import os
from pathlib import Path
import subprocess
import tempfile

import typed_static_invoke_set_protocol as invoke
from recorded_worker import Worker

ROOT = invoke.ROOT
CASES = Path(__file__).with_name('typed_static_ini_prefix_cases.json')
RAW_SEED = invoke.byte_expr(b'seed\0old')
RAW_INNER = invoke.byte_expr(b'inner\0tail')
PROPERTY = invoke.byte_expr(b's\0typed')
REJECTED = invoke.byte_expr(b'\0rejected')
PREFIX = invoke.PREFIX.replace(
    '  -- if S.FILEINCLUDEPATH = ($ptascii("inner"))',
    '  -- if S.FILEINCLUDEPATH = (' + RAW_INNER + ')\n'
    '  -- if $invoke_set_static_outputs(S.EVENTS) = $ptascii("TINZ")').replace(
    'S.RESULT = KNOWN (PSTRING $ptascii("s"))',
    'S.RESULT = KNOWN (PSTRING ' + PROPERTY + ')').replace(
    'def $invoke_set_static_phase(S,n) = false -- otherwise',
    'def $invoke_set_static_phase(S,5) = true\n'
    '  -- if $invoke_set_static_entered(S)\n'
    '  -- if S.TODO = (CONFIG_INVOKE pconfigcall_rejected) :: ptask_rejected_tail*\n'
    '  -- if pconfigcall_rejected.KIND = INTRINSIC_INI_SET\n'
    '  -- if pconfigcall_rejected.SENT = [NAMED_SENT (KNOWN (PSTRING $ptascii("include_path"))), NAMED_SENT (KNOWN (PSTRING ' + REJECTED + '))]\n'
    'def $invoke_set_static_phase(S,n) = false -- otherwise')
outputs = PREFIX.index('dec $invoke_set_static_output_marker')
PREFIX = PREFIX[outputs:] + PREFIX[:outputs]


def assertions(row, checked, path, cwd):
    checks = invoke.common(checked, path, cwd)
    split = checks.index('S_inner_found = $invoke_set_static_seek(S,1,2048)')
    checks[split:split] = invoke.seek('S_reject', 'S', 5) + [
        'S_reject.CURRENT = S.CURRENT', 'S_reject.FRAMES = S.FRAMES',
        'S_reject.TODO = (CONFIG_INVOKE pconfigcall_rejected) :: ptask_rejected_tail*',
        'pconfigcall_rejected.KIND = INTRINSIC_INI_SET',
        'pconfigcall_rejected.SENT = [NAMED_SENT (KNOWN (PSTRING $ptascii("include_path"))), NAMED_SENT (KNOWN (PSTRING ' + REJECTED + '))]',
        'S_reject.FILEINCLUDEPATH = (' + RAW_INNER + ')',
        '$invoke_set_static_outputs(S_reject.EVENTS) = $ptascii("TIN")',
        '$config_invoke_valid(S_reject,pconfigcall_rejected)',
        'S_rejected_found = $drive_steps(S_reject,1)',
        'S_rejected_found.COMPLETION = BUDGET',
        'S_rejected = S_rejected_found[.COMPLETION = NORMAL]',
        'S_rejected.RESULT = KNOWN (PBOOL false)',
        'S_rejected.FILEINCLUDEPATH = S_reject.FILEINCLUDEPATH',
        'S_rejected.CURRENT = S.CURRENT', 'S_rejected.FRAMES = S.FRAMES',
    ] + invoke.valid('S_reject') + invoke.no_directory('S_reject', cwd) + \
        invoke.valid('S_rejected') + invoke.no_directory('S_rejected', cwd)
    checks[checks.index('S_inner_found = $invoke_set_static_seek(S,1,2048)')] = \
        'S_inner_found = $invoke_set_static_seek(S_rejected,1,2048)'
    checks = invoke.abrupt(checks, cwd) if row['abrupt'] else invoke.normal(checks, cwd)
    replaced = []
    for clause in checks:
        clause = clause.replace('.FILEINCLUDEPATH = ($ptascii("seed"))',
                                '.FILEINCLUDEPATH = (' + RAW_SEED + ')')
        clause = clause.replace('.FILEINCLUDEPATH = ($ptascii("inner"))',
                                '.FILEINCLUDEPATH = (' + RAW_INNER + ')')
        clause = clause.replace('S_inner.EVENTS) = $ptascii("TIN")',
                                'S_inner.EVENTS) = $ptascii("TINZ")')
        clause = clause.replace('$ptascii("TINinners|s|outer")',
                                invoke.byte_expr(row['expected_stdout'].encode()))
        clause = clause.replace('$ptascii("TINF")', '$ptascii("TINZF")')
        clause = clause.replace('PSTRING $ptascii("s")', 'PSTRING ' + PROPERTY)
        clause = clause.replace('"line") = PINT 26', '"line") = PINT 27')
        replaced.append(clause)
    replaced += ['$c_string(' + RAW_INNER + ') = $ptascii("inner")',
                 RAW_INNER + ' =/= $ptascii("inner")',
                 '$c_string(' + PROPERTY + ') = $ptascii("s")',
                 PROPERTY + ' =/= $ptascii("s")']
    if not row['abrupt']:
        replaced += ['S_write.RESULT = KNOWN (PSTRING ' + PROPERTY + ')',
                     'S_set.RESULT =/= KNOWN (PSTRING ' + RAW_INNER + ')']
    # The invoke suite retains the malformed-context counterexamples.
    return [clause for clause in replaced if 'S_bad_' not in clause]


def checked(row, directory, path):
    frontend = Worker([str(ROOT / '.tools/php/bin/php'), '-n', '-d',
                       'extension=' + str(ROOT / '.tools/php-file.so'),
                       str(ROOT / 'frontend/worker.php')], directory / 'frontend')
    try:
        adapter = Worker([str(ROOT / '_build/default/adapter/main.exe'), str(ROOT)],
                         directory / 'adapter')
        try:
            parsed = frontend.request({'op': 'parse', 'source': invoke.b64(path.read_bytes())})
            assert parsed['accepted'] is True
            packet = adapter.request({'op': 'check', 'ast': parsed['ast'], 'fixture': True})
            assert packet['ok'] is True
        finally:
            adapter.close()
    finally:
        frontend.close()
    checks = assertions(row, packet, path, directory)
    body = 'dec $body() : bool\ndef $body() = true\n'
    return body + ''.join('  -- if ' + clause + '\n' for clause in checks), checks


def source(row, directory, path):
    observed = invoke.process([str(ROOT / '.tools/php/bin/php'), '-n', *invoke.types.FLAGS,
                               str(path)], directory / 'native', 30, directory)
    assert observed.returncode == row['expected_exit_status']
    assert observed.stdout == row['expected_stdout'].encode()
    facts = {'version': 2, 'main': invoke.b64(os.fsencode(path)),
             'cwd': invoke.b64(os.fsencode(directory)), 'include_path': invoke.b64(b'.:'),
             'entries': [], 'chdir_entries': []}
    facts_path = directory / 'snapshot.json'
    facts_path.write_text(json.dumps(facts, sort_keys=True) + '\n')
    result = invoke.process([str(ROOT / 'bin/php-semantics'), str(path), '--file-snapshot',
        str(facts_path), '--steps', '100000', '--timeout', '60'], directory / 'model', 90, directory)
    assert result.returncode == 0 and not result.stderr
    outcome = json.loads(result.stdout)
    assert outcome['frontend'] == 'accepted' and outcome['checked'] == 'program'
    assert outcome['status'] == ('php_error' if row['abrupt'] else 'normal')
    assert outcome['exit_status'] == observed.returncode and outcome['reason'] is None
    assert base64.b64decode(outcome['stdout'], validate=True) == observed.stdout
    assert base64.b64decode(outcome['stderr'], validate=True) == observed.stderr
    if row['abrupt']:
        line = row['predicted_php_error']['line']
        assert observed.stderr.startswith(b'Fatal error: Uncaught Exception: X in ' +
                                         os.fsencode(path) + b':' + str(line).encode() + b'\nStack trace:\n')
        assert observed.stderr.endswith(b'  thrown in ' + os.fsencode(path) +
                                       b' on line ' + str(line).encode() + b'\n')
        assert outcome['diagnostic']['class'] == 'Exception' and outcome['diagnostic']['line'] == line
        assert base64.b64decode(outcome['diagnostic']['message'], validate=True) == b'X'
    else:
        assert not observed.stderr and outcome['diagnostic'] is None
    return {'status': outcome['status'], 'exit_status': outcome['exit_status']}


def snapshot(freeze_path):
    identity = {key: subprocess.check_output(['git', *argv], cwd=ROOT, text=True).strip()
                for key, argv in [('head', ['rev-parse', 'HEAD']),
                                  ('status', ['status', '--porcelain', '--untracked-files=no'])]}
    result = {'identity': identity,
              'ordered_modules': json.loads((ROOT / 'spec/semantics/modules.json').read_text())}
    if freeze_path:
        freeze = json.loads(freeze_path.read_text())
        assert identity == {'head': freeze['head'], 'status': ''}
        assert result['ordered_modules'] == freeze['ordered_modules']
        result['watched'] = {name: {'sha256': invoke.sha(ROOT / name),
                                   'mode': oct((ROOT / name).stat().st_mode & 0o7777)}
                             for name in freeze['watched']}
        assert result['watched'] == freeze['watched']
        result['freeze_sha256'] = invoke.sha(freeze_path)
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('mode', choices=['prepare', 'source', 'finite'])
    parser.add_argument('--freeze', type=Path)
    args = parser.parse_args()
    assert args.mode == 'prepare' or args.freeze
    os.environ.update(LC_ALL='C', TZ='UTC', GIT_OPTIONAL_LOCKS='0')
    before = snapshot(args.freeze)
    out = Path(tempfile.mkdtemp(prefix='typed-static-ini-prefix-' + args.mode + '-', dir=ROOT / '.tools'))
    report = {'mode': args.mode, 'profile': invoke.types.PROFILE, 'before': before,
              'passed': False, 'records': [], 'state_assertions_evaluated': 0,
              'unused_body_assertions': 0}
    print(out, flush=True)
    try:
        for row in json.loads(CASES.read_text())['cases']:
            record = {'case': row['case'], 'completed': False}
            report['records'].append(record)
            directory = out / row['case']; directory.mkdir()
            path = directory / 'main.php'; path.write_text(row['source'])
            assert invoke.sha(path) == row['source_sha256']
            record['source_sha256'] = invoke.sha(path)
            if args.mode == 'source':
                record['outcome'] = source(row, directory, path)
            else:
                body, checks = checked(row, directory, path)
                (directory / 'assertions.json').write_text(json.dumps(checks, indent=2) + '\n')
                fixture = directory / 'protocol.watsup'
                fixture.write_text(PREFIX + body + '\ndec $main() : bool\ndef $main() = ' +
                                   ('true' if args.mode == 'prepare' else '$body()') + '\n')
                invoke.numeric(fixture, directory)
                record['body_assertions'] = len(checks)
                report['unused_body_assertions' if args.mode == 'prepare' else
                       'state_assertions_evaluated'] += len(checks)
            assert snapshot(args.freeze) == before
            record['completed'] = True
            print(row['case'], args.mode, 'pass', flush=True)
        report['passed'] = True
    except BaseException as error:
        report['failure'] = {'type': type(error).__name__, 'message': str(error)}
        raise
    finally:
        report['after'] = snapshot(args.freeze)
        report['passed'] = report['passed'] and report['after'] == before
        report['raw_files'] = {str(p.relative_to(ROOT)): {'sha256': invoke.sha(p),
            'bytes': p.stat().st_size, 'mode': oct(p.stat().st_mode & 0o7777)}
            for p in sorted(out.rglob('*')) if p.is_file()}
        receipt = out / 'report.json'
        receipt.write_text(json.dumps(report, indent=2, sort_keys=True) + '\n')
        print(receipt, invoke.sha(receipt), 'pass', report['passed'], flush=True)
    assert report['passed']


if __name__ == '__main__':
    main()
