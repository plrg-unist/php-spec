#!/usr/bin/env python3
"""Frozen fatal status after caught shutdown exit and fresh fatal reporting."""
import argparse
import base64
import hashlib
import json
import os
from pathlib import Path
import subprocess

import source_static_fatal_protocol as fatal
from recorded_worker import Worker
from typed_static_invoke_set_protocol import process

retirement = fatal.retirement
ROOT, inputs, types = retirement.ROOT, retirement.inputs, retirement.types
seq, byte_expr, b64 = retirement.seq, retirement.byte_expr, retirement.b64
STAGES = {'frozen-reset': ('static-native-v19','eval-fatal-caught-reset-zero'),
    'new-visible': ('static-native-v21','eval-fatal-caught-reset-new-uncaught'),
    'new-hidden': ('static-native-v22','eval-fatal-caught-reset-hidden-uncaught')}
PREFIX = r'''dec $stage(pstate) : bool
def $stage(S) = true
  -- if S.TODO = (THROW_SEARCH n) :: ptask_tail*
  -- if $string_bytes($throwable_field(S,n,"message")) = ($ptascii("late"))
def $stage(S) = false -- otherwise
''' + retirement.PREFIX
PREFIX += r'''dec $stderr_item(pevent) : nat
def $stderr_item(STDERR n*) = 1
def $stderr_item(pevent) = 0 -- otherwise
dec $stderr_count(pevent*) : nat
def $stderr_count(eps) = 0
def $stderr_count(pevent :: pevent_tail*) = $($stderr_item(pevent) + $stderr_count(pevent_tail*))
'''


def native_record(sources, suite, case):
    suite = sources / suite
    report = json.loads((suite / 'report.json').read_text())
    row, = [row for row in report['records'] if row['id'] == case]
    assert report['target'] == types.PROFILE
    assert report['runtime_sha256'] == hashlib.sha256(types.PHP.read_bytes()).hexdigest()
    directory = suite / case
    assert json.loads((directory / 'native/process.json').read_text())['exit_status'] == row['exit']
    assert (directory / 'native/stdout').read_bytes() == row['stdout'].encode()
    assert (directory / 'native/stderr').read_bytes() == row['stderr'].encode()
    for name, digest in row['originals'].items():
        assert hashlib.sha256((directory / name).read_bytes()).hexdigest() == digest
    return directory, row


def prepare(out, sources, names):
    out.mkdir()
    frontend = Worker([str(types.PHP), '-n', *types.FLAGS, '-d',
        'extension=' + str(ROOT / '.tools/php-file.so'), str(ROOT / 'frontend/worker.php')], out / 'frontend')
    adapter = None
    try:
        adapter = Worker([str(ROOT / '_build/default/adapter/main.exe'), str(ROOT)], out / 'adapter')
        for name in names:
            directory, native = native_record(sources, *STAGES[name])
            main_path = directory / 'main.php'
            parsed = frontend.request({'op': 'parse', 'source': b64(main_path.read_bytes())})
            assert parsed['accepted'], parsed
            main_ast = parsed['ast']
            main_fixture = adapter.request({'op': 'check', 'ast': main_ast, 'fixture': True})['fixture']
            evaluations = [(node, ancestors) for _, node, ancestors in retirement.nodes(main_ast['program']) if node['node'] == 'Expr_Eval']
            outer, = [node for node, ancestors in evaluations if 'Stmt_Function' not in ancestors]
            inner, = [node for node, ancestors in evaluations if 'Stmt_Function' in ancestors]
            children = []
            for unit, node in [(1,outer),(2,inner)]:
                data = base64.b64decode(node['fields'][0]['fields'][0]['bytes'])
                child = frontend.request({'op': 'parse-eval', 'id': str(unit), 'mode': 'eval', 'profile': 'cli-raw-85', 'source': b64(data)})
                assert child['accepted'], child
                fixture = adapter.request({'op': 'check', 'ast': child['ast'], 'fixture': True})['fixture']
                children.append((data,fixture))
            first, second = children
            checks = ['S_wait1 = $php_file_run(' + main_fixture + ',1800,' + byte_expr(os.fsencode(main_path)) + ',' + byte_expr(os.fsencode(directory)) + ')',
                'S_wait1.COMPLETION = SOURCE_PENDING',
                'S_ready1 = $eval_resume(S_wait1,SOURCE_ACCEPT 1 ' + seq(first[0]) + ' ' + first[1] + ')',
                'S_ready1.COMPLETION = NORMAL',
                'S_wait2 = $drive_steps(S_ready1,1800)', 'S_wait2.COMPLETION = SOURCE_PENDING',
                'S_wait2.EXITSTATUS = 255', *fatal.public('S_wait2'),
                'S_ready2 = $eval_resume(S_wait2,SOURCE_ACCEPT 2 ' + seq(second[0]) + ' ' + second[1] + ')',
                'S_ready2.COMPLETION = NORMAL', *fatal.public('S_ready2')]
            if name == 'frozen-reset':
                checks += ['S_final = $drive_steps(S_ready2,1800)',
                    'S_final.COMPLETION = REQUESTFATAL ($ptascii("Error")) ($ptascii("stop")) 1',
                    'S_final.EXITSTATUS = 0', '$stderr_count(S_final.EVENTS) = 1']
            else:
                checks += [*fatal.reached('S_late','$seek(S_ready2,1800)'),
                    'S_late.TODO = (THROW_SEARCH n_late) :: ptask_late_tail*',
                    '$string_bytes($throwable_field(S_late,n_late,"message")) = ($ptascii("late"))',
                    'S_late.EXITSTATUS = 0', 'S_late.REPORTING = ' + ('0' if name == 'new-hidden' else '30719'),
                    '$test_outputs(S_late.EVENTS) = $ptascii("B|S|alive|Q|N|C|E|")', *fatal.public('S_late'),
                    'S_final = $drive_steps(S_late,1800)',
                    'S_final.COMPLETION = REQUESTFATAL ($ptascii("TypeError")) ($ptascii("late")) z',
                    'S_final.EXITSTATUS = 255', '$stderr_count(S_final.EVENTS) = ' + ('1' if name == 'new-hidden' else '2')]
            checks += ['S_final.SHUTDOWN.PHASE = SHUTDOWN_DONE',
                'S_final.SHUTDOWN.COMPLETION = REQUESTFATAL ($ptascii("Error")) ($ptascii("stop")) 1',
                'S_final.CURRENT = eps', 'S_final.FRAMES = eps', 'S_final.TODO = eps',
                'S_final.EVALCONTEXTS = eps', 'S_final.FILECONTEXTS = eps',
                'S_final.STATICS = [pstaticcell]', '$source_static_origin(S_final,pstaticcell.ORIGIN)',
                'S_final.STORE[pstaticcell.CELL] = DEFINED (POBJECT n_object)',
                '$weakref_find(S_final,S_final.ALLOCATIONS,n_object) = (n_weak)',
                '$weakref_get(S_final,n_weak) = POBJECT n_object', 'n_object <- S_final.DESTRUCTION.CALLED',
                '$test_outputs(S_final.EVENTS) = $ptascii(' + json.dumps(native['stdout']) + ')',
                '$shutdown_freeze(S_final) = S_final', *fatal.public('S_final')]
            target = out / name
            target.mkdir()
            (target / 'protocol.watsup').write_text(PREFIX + '\ndec $main() : bool\ndef $main() = true\n' +
                ''.join('  -- if ' + item + '\n' for item in checks))
            (target / 'assertions.json').write_text(json.dumps(checks, indent=2) + '\n')
    finally:
        if adapter:
            adapter.close()
        frontend.close()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--phase', choices=['fixtures', 'check'], required=True)
    parser.add_argument('--sources', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--stage', action='append', default=[])
    parser.add_argument('--attempt', type=int, default=1)
    args = parser.parse_args()
    names = args.stage or list(STAGES)
    assert args.attempt > 0 and names and len(set(names)) == len(names) and set(names) <= STAGES.keys()
    out, sources = args.output.resolve(), args.sources.resolve()
    paths = [Path(__file__), Path(fatal.__file__), Path(retirement.__file__), ROOT / 'tests/semantics/recorded_worker.py',
        ROOT / 'tests/semantics/_build/default/numeric_runner.exe']
    for name in names:
        suite,case = STAGES[name]
        directory = sources / suite / case
        paths += [sources / suite / 'report.json', sources / suite / 'run.py']
        paths += [*sorted(directory.glob('*.php')),
            *[directory / 'native' / item for item in ['stdout', 'stderr', 'process.json', 'command.json']]]
        if args.phase == 'check':
            paths += [out / name / 'protocol.watsup', out / name / 'assertions.json']
    pins = lambda: dict(inputs.inputs(), **{str(path): hashlib.sha256(path.read_bytes()).hexdigest() for path in paths})
    before = pins()
    label = args.phase if args.attempt == 1 else args.phase + '-' + str(args.attempt)
    report = {'phase': args.phase, 'revision': subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip(),
        'implementation_diff_sha256': hashlib.sha256(subprocess.check_output(['git', 'diff', 'HEAD', '--', 'spec/semantics', 'bin/php-semantics'], cwd=ROOT)).hexdigest(),
        'inputs': before, 'profile': types.PROFILE, 'environment': {'LC_ALL': 'C', 'TZ': 'UTC'},
        'records': [], 'result': 'fail', 'runtime_assertions': 0}
    try:
        if args.phase == 'fixtures':
            prepare(out, sources, names)
            report['result'] = 'pass'
        else:
            modules = [str(ROOT / name) for name in json.loads((ROOT / 'spec/semantics/modules.json').read_text())]
            for name in names:
                directory = out / name
                result = process([str(ROOT / 'tests/semantics/_build/default/numeric_runner.exe'), '--sl', *modules, str(directory / 'protocol.watsup')],
                    directory / label, 90, ROOT)
                passed = result.returncode == 0 and result.stdout == b'true\n' and not result.stderr
                count = len(json.loads((directory / 'assertions.json').read_text()))
                report['records'].append({'id': name, 'pass': passed, 'runtime_assertions': count})
                report['runtime_assertions'] += count if passed else 0
                print(name, passed, flush=True)
                if not passed:
                    break
            report['result'] = 'pass' if len(report['records']) == len(names) and all(row['pass'] for row in report['records']) else 'fail'
    finally:
        report['stable_inputs'] = before == pins()
        if not report['stable_inputs']:
            report['result'] = 'fail'
        (out / (label + '-report.json')).write_text(json.dumps(report, indent=2) + '\n')
    return report['result'] == 'pass'


if __name__ == '__main__':
    raise SystemExit(0 if main() else 1)
