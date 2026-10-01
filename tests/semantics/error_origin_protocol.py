#!/usr/bin/env python3
"""Source-derived abrupt frame retirement, diagnostics and public resumption."""
import argparse
import base64
import hashlib
import json
from pathlib import Path
import subprocess
import tempfile

from recorded_worker import Worker

ROOT = Path(__file__).resolve().parents[2]
MODULES = [ROOT / name for name in json.loads(
    (ROOT / 'spec/semantics/modules.json').read_text())]
CLASSES = ('<?php class O{function __toString():string{return "s";}}'
           'class P{public string $p="s";}')
ASSIGN = '$p=new P;$r=&$p->p;$r=new O;'
SOURCES = {
    'protected': CLASSES + 'function f(){$p=new P;$r=&$p->p;try{$r=new O;'
                 '}finally{echo "F;";}}try{f();echo "OK;";}'
                 'catch(Throwable $e){echo "C;";}finally{echo "G;";}',
    'current-foreach': CLASSES + 'function f(){foreach([1,2] as &$v){try{' +
                       ASSIGN + '}finally{echo "F;";}}}@f();',
    'saved-foreach': CLASSES + 'function f($arg){try{' + ASSIGN +
                     '}finally{echo "F;";}}function h($arg){foreach([1,2] as &$v)'
                     '{try{f($arg);}finally{echo "G;";}}}@h([7]);',
    'fatal': '<?php\nclass A {}\nfunction f() {\n try {\n'
             '  if (true) { class A {} }\n } finally { echo "BAD;"; }\n'
             '}\ntry { f(); } finally { echo "BAD;"; }\n',
}


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def common():
    checks = [
        'S.COMPLETION = BUDGET', 'S.TODO = [ERROR_UNWIND pcompletion]',
        'S.ORIGIN = eps', 'S.ERRORORIGIN = (porigin_error)', 'S.TRACE =/= eps',
        '$task_nodes(ERROR_UNWIND pcompletion) = eps',
        '$call_task_valid(S, ERROR_UNWIND pcompletion)',
        '$call_task_valid(S[.ERRORORIGIN = eps], ERROR_UNWIND pcompletion)',
        '$call_descriptors_valid(S[.ERRORORIGIN = eps])',
        '~$call_task_valid(S[.ORIGIN = (porigin_error)], ERROR_UNWIND pcompletion)',
        '~$call_descriptors_valid(S[.ORIGIN = (porigin_error)])',
        '~$call_task_valid(S[.TODO = [ERROR_UNWIND pcompletion, RETURN_NULL]], ERROR_UNWIND pcompletion)',
        '~$call_descriptors_valid(S[.TODO = [ERROR_UNWIND pcompletion, RETURN_NULL]])',
    ]
    for bad in ['NORMAL', 'BUDGET', 'SOURCE_PENDING', 'EXITED 7', 'THROWING 0']:
        checks += [
            '~$call_task_valid(S[.TODO = [ERROR_UNWIND (' + bad + ')]], ERROR_UNWIND (' + bad + '))',
            '~$call_descriptors_valid(S[.TODO = [ERROR_UNWIND (' + bad + ')]])',
        ]
    return checks


def completed():
    return [
        'S_done = $drive(S[.COMPLETION = NORMAL], 1000)',
        'S_whole = $drive_steps(S_initial[.COMPLETION = NORMAL], 1000)',
        'S_done = S_whole', 'S_done.COMPLETION = pcompletion',
        'S_done.CURRENT = eps', 'S_done.FRAMES = eps', 'S_done.TODO = eps',
        'S_done.ORIGIN = eps', 'S_done.ITERATORS = eps', 'S_done.SILENCES = eps',
        'S_done.REPORTING = S_initial.REPORTING',
        'S_done.TRACE = S.TRACE', 'S_done.ERRORORIGIN = S.ERRORORIGIN',
        'S_done.EVENTS = eps', 'S_done.RESULT = KNOWN PNULL',
        'S_done.BASE = BASE_VALUE (KNOWN PNULL)', 'S_done.HELD = eps',
        'S_done.CONSTCONTEXT = eps', '$call_descriptors_valid(S_done)',
        '$heap_valid($heap_graph(S_done))',
    ]


UNSUPPORTED = 'S.TODO = [ERROR_UNWIND (UNSUPPORTED "user object string conversion")]'
FATAL = 'S.TODO = [ERROR_UNWIND (FATAL preqbytes_message 5)]'
STAGES = []
for name, source, stage, checks in [
    ('protected-callee', 'protected', UNSUPPORTED + ' /\\ S.CURRENT =/= eps', [
        'S.CURRENT = (pcallcontext)', 'pcallcontext.NAME = $ptascii("f")',
        'S.TRACE = $eval_exception_trace(S[.ORIGIN = S.ERRORORIGIN])',
        'S.TRACE = [ptraceframe]', 'ptraceframe.FUNCTION = $ptascii("f")',
        'ptraceframe.FILE = $call_sourcefile(S.FILES, pcallcontext.FUNCTION)',
        'ptraceframe.LINE = 1', 'ptraceframe.ARGS = eps',
    ]),
    ('restored-protected-caller', 'protected', UNSUPPORTED + ' /\\ S.CURRENT = eps', [
        'S.FRAMES = eps', 'S.TRACE = [ptraceframe]',
        'ptraceframe.FUNCTION = $ptascii("f")', 'ptraceframe.LINE = 1',
    ]),
    ('suppressed-current-foreach', 'current-foreach', UNSUPPORTED, [
        'S.ITERATORS = eps', 'S.SILENCES = eps',
        'S.REPORTING = $long_and(S_initial.REPORTING, 4437)',
        'S.FRAMES = [pframe]', 'pframe.SILENCES =/= eps',
    ]),
    ('saved-outer-foreach', 'saved-foreach', UNSUPPORTED + ' -- if S.CURRENT = (pcallcontext) -- if pcallcontext.NAME = $ptascii("f")', [
        '|S.ITERATORS| = 1', 'S.REPORTING = $long_and(S_initial.REPORTING, 4437)',
        'S.TRACE = [ptraceframe_f, ptraceframe_h]',
        'ptraceframe_f.FUNCTION = $ptascii("f")',
        'ptraceframe_h.FUNCTION = $ptascii("h")',
        'ptraceframe_f.ARGS = [(KINT 0, PARRAY n_arg)]',
        'ptraceframe_h.ARGS = [(KINT 0, PARRAY n_arg)]',
        'S_next = $drive(S[.COMPLETION = NORMAL], 1)',
        'S_next.TODO = [ERROR_UNWIND pcompletion]', 'S_next.ORIGIN = eps',
        'S_next.CURRENT = (pcallcontext_h)', 'pcallcontext_h.NAME = $ptascii("h")',
        'S_next.ITERATORS = eps', 'S_next.SILENCES = eps',
        'S_next.REPORTING = S.REPORTING',
        'S_next.TRACE = S.TRACE', 'S_next.ERRORORIGIN = S.ERRORORIGIN',
        '$call_descriptors_valid(S_next)', '$heap_valid($heap_graph(S_next))',
    ]),
    ('fatal-protected-callee', 'fatal', FATAL + ' -- if S.CURRENT =/= eps', [
        'S.CURRENT = (pcallcontext)', 'pcallcontext.NAME = $ptascii("f")',
        'S.TRACE = $eval_exception_trace(S[.ORIGIN = S.ERRORORIGIN])',
        'S.TRACE = [ptraceframe]', 'ptraceframe.FUNCTION = $ptascii("f")',
        'ptraceframe.LINE = 8',
    ]),
    ('fatal-restored-protected-caller', 'fatal', FATAL + ' -- if S.CURRENT = eps', [
        'S.FRAMES = eps', 'S.TRACE = [ptraceframe]',
        'ptraceframe.FUNCTION = $ptascii("f")', 'ptraceframe.LINE = 8',
    ]),
]:
    tail = [
        '$($heap_count(HARRAY n_arg, $trace_roots(S_done.TRACE)) = 2)',
        '$($heap_count(HARRAY n_arg, $pools_nodes(S_done.POOLS)) = 1)',
        '$($heap_owners($heap_graph(S_done), HARRAY n_arg) = 3)',
    ] if name == 'saved-outer-foreach' else []
    guards = common()
    if name == 'saved-outer-foreach':
        guards = [check for check in guards if '$call_descriptors_valid' not in check]
    STAGES.append((name, source, stage, guards + checks + completed() + tail))


def main(match, elaborate_only=False):
    stages = [row for row in STAGES if match in row[0]]
    assert stages
    out = Path(tempfile.mkdtemp(prefix='error-origin-protocol-', dir=ROOT / '.tools'))
    print(out, flush=True)
    inputs = [*MODULES, ROOT / 'spec/semantics/modules.json', Path(__file__),
              ROOT / 'tests/semantics/recorded_worker.py', ROOT / 'tests/semantics/profile.json',
              ROOT / 'frontend/worker.php', ROOT / 'frontend/wire.php',
              ROOT / '.tools/php/bin/php', ROOT / '.tools/php-file.so',
              ROOT / 'tests/semantics/_build/default/numeric_runner.exe',
              ROOT / '_build/default/adapter/main.exe']
    before = {str(path.relative_to(ROOT)): sha(path) for path in inputs}
    (out / 'inputs.json').write_text(json.dumps(before, indent=2) + '\n')
    profile = json.loads((ROOT / 'tests/semantics/profile.json').read_text())
    flags = [part for key, value in profile.items() for part in ('-d', key + '=' + value)]
    frontend = Worker([str(ROOT / '.tools/php/bin/php'), '-n', *flags, '-d',
                       'extension=' + str(ROOT / '.tools/php-file.so'),
                       str(ROOT / 'frontend/worker.php')], out / 'frontend')
    adapter = Worker([str(ROOT / '_build/default/adapter/main.exe'), str(ROOT)], out / 'adapter')
    try:
        fixtures = {}
        for source_id in sorted({row[1] for row in stages}):
            source = out / (source_id + '.php')
            source.write_bytes(SOURCES[source_id].encode())
            parsed = frontend.request({'op': 'parse', 'source': base64.b64encode(source.read_bytes()).decode()})
            assert parsed['accepted']
            checked = adapter.request({'op': 'check', 'ast': parsed['ast'], 'fixture': True})
            assert checked['ok']
            fixtures[source_id] = ('$php_run(' + checked['fixture'] + ', 0, ' +
                                   json.dumps(base64.b64encode(str(source).encode()).decode()) + ')')
    finally:
        frontend.close()
        adapter.close()
    records = []
    for name, source_id, stage, checks in stages:
        directory = out / name
        directory.mkdir()
        fixture = directory / 'protocol.watsup'
        fixture.write_text(
            'dec $stage(pstate) : bool\n'
            f'def $stage(S) = true -- if {stage}\n'
            'def $stage(S) = false -- otherwise\n'
            'dec $seek(pstate, nat) : pstate\n'
            'def $seek(S, n) = S -- if $stage(S)\n'
            'def $seek(S, n) = $seek($drive_steps(S[.COMPLETION = NORMAL], 1), '
            '$nabs($(n - 1))) -- if ~$stage(S) -- if $(n > 0)\n'
            'dec $main() : bool\ndef $main() = true\n'
            f'  -- if S_initial = {fixtures[source_id]}\n'
            '  -- if S = $seek(S_initial[.COMPLETION = NORMAL], 500)\n'
            f'  -- if {stage}\n'
            '  -- if $call_descriptors_valid(S)\n'
            '  -- if $heap_valid($heap_graph(S))\n'
            + ''.join('  -- if ' + check + '\n' for check in checks))
        executed_fixture = fixture
        if elaborate_only:
            executed_fixture = directory / 'elaboration.watsup'
            executed_fixture.write_text(fixture.read_text().replace('$main()', '$checked_main()')
                                        + '\ndec $main() : bool\ndef $main() = true\n')
        command = [str(ROOT / 'tests/semantics/_build/default/numeric_runner.exe'),
                   *map(str, MODULES), str(executed_fixture)]
        (directory / 'command.json').write_text(json.dumps(command) + '\n')
        timed_out = False
        try:
            result = subprocess.run(command, capture_output=True, timeout=300)
            stdout, stderr, exit_status = result.stdout, result.stderr, result.returncode
        except subprocess.TimeoutExpired as error:
            stdout, stderr, exit_status = error.stdout or b'', error.stderr or b'', None
            timed_out = True
        (directory / 'stdout').write_bytes(stdout)
        (directory / 'stderr').write_bytes(stderr)
        (directory / 'status.json').write_text(json.dumps(
            {'exit_status': exit_status, 'timed_out': timed_out, 'timeout_seconds': 300}) + '\n')
        passed = not timed_out and exit_status == 0 and stdout == b'true\n' and not stderr
        records.append({'id': name, 'source_id': source_id,
                        'source_sha256': sha(out / (source_id + '.php')),
                        'fixture_sha256': sha(fixture),
                        'executed_fixture_sha256': sha(executed_fixture),
                        'assertions': 0 if elaborate_only else len(checks) + 5,
                        'stdout_sha256': sha(directory / 'stdout'),
                        'stderr_sha256': sha(directory / 'stderr'),
                        'exit_status': exit_status, 'timed_out': timed_out, 'pass': passed})
        print(name, passed, flush=True)
        if not passed:
            print('fixture timed out after 300s' if timed_out else stderr.decode()[-1500:], flush=True)
            break
    stable = before == {str(path.relative_to(ROOT)): sha(path) for path in inputs}
    result = ('timeout' if any(row['timed_out'] for row in records) else
              'pass' if stable and all(row['pass'] for row in records) else 'fail')
    report = {'result': result,
              'stable': stable, 'inputs': before, 'records': records, 'raw': str(out),
              'selection': [row[0] for row in stages],
              'mode': 'generated_fixture_elaboration' if elaborate_only else 'source_lifecycle',
              'scope': ('Generated full fixture bodies are checked; only a constant main is executed.' if elaborate_only else
                        'Source-derived model boundary and fatal lifecycle; Unsupported assertions are not native agreements.')}
    (out / 'report.json').write_text(json.dumps(report, indent=2) + '\n')
    print(out, report['result'])
    return report['result'] == 'pass'


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--match', default='')
    parser.add_argument('--elaborate-only', action='store_true')
    args = parser.parse_args()
    raise SystemExit(0 if main(args.match, args.elaborate_only) else 1)
