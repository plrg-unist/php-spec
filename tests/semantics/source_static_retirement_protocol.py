#!/usr/bin/env python3
"""Source-owned statics at genuine parser, end and copied-return frontiers."""
import argparse
import base64
import hashlib
import json
import os
from pathlib import Path
import subprocess

import file_compile_notice_sources as inputs
import static_types as types
from recorded_worker import Worker
from typed_static_invoke_set_protocol import process

ROOT = inputs.ROOT
b64 = lambda data: base64.b64encode(data).decode()
seq = lambda data: '(' + str(list(data)) + ')'
byte_expr = lambda data: '$base64(' + json.dumps(b64(data)) + ')'
STAGES = {
    'eval-static': ('static-native-v1', 'eval-main-fresh', 'static'),
    'eval-end': ('static-native-v1', 'eval-main-fresh', 'end'),
    'file-end': ('static-native-v1', 'file-main-fresh', 'end'),
    'eval-return': ('static-native-v3', 'eval-returned-static-unset', 'return'),
    'file-return': ('static-native-v3', 'file-returned-static-unset', 'return'),
    'retained-function': ('static-native-v5', 'eval-retained-cell', 'retained'),
    'caller-boundary': ('static-native-v5', 'eval-retained-cell', 'caller'),
    **{'callable-' + kind: ('static-native-v4', 'eval-callable-' + kind, 'callable')
       for kind in ['function', 'method', 'closure', 'hook']},
}
PREFIX = r'''dec $seek(pstate,nat) : pstate
def $seek(S,n) = S -- if $stage(S)
def $seek(S,n) = $seek($drive_steps(S[.COMPLETION = NORMAL],1),$nabs($(n - 1)))
  -- if ~$stage(S) -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET -- if $(n > 0)
def $seek(S,n) = S -- otherwise
dec $one(pstate) : pstate
def $one(S) = S_next -- PhpStep: S ~> S_next
dec $test_output(pevent) : nat*
def $test_output(OUTPUT n*) = n*
def $test_output(pevent) = eps -- otherwise
dec $test_outputs(pevent*) : nat*
def $test_outputs(eps) = eps
def $test_outputs(pevent :: pevent_tail*) = $test_output(pevent) ++ $test_outputs(pevent_tail*)
dec $test_clean_event(pevent) : bool
def $test_clean_event(OUTPUT n*) = true
def $test_clean_event(pevent) = false -- otherwise
dec $test_clean_events(pevent*) : bool
def $test_clean_events(eps) = true
def $test_clean_events(pevent :: pevent_tail*) = ($test_clean_event(pevent) /\ $test_clean_events(pevent_tail*))
'''


def nodes(value, path=(), ancestors=()):
    if isinstance(value, list):
        for index, item in enumerate(value):
            yield from nodes(item, path + ('PCINDEX ' + str(index),), ancestors)
    elif isinstance(value, dict) and 'node' in value:
        yield path, value, ancestors
        for index, item in enumerate(value['fields']):
            yield from nodes(item, path + ('PCFIELD ' + str(index),), ancestors + (value['node'],))


def native_record(sources, suite, case):
    report = json.loads((sources / suite / 'report.json').read_text())
    rows = report.get('records', report.get('rows'))
    row, = [row for row in rows if row.get('id', row.get('name')) == case]
    assert report.get('profile', report.get('target')) == types.PROFILE
    assert report['runtime_sha256'] == hashlib.sha256(types.PHP.read_bytes()).hexdigest()
    directory = sources / suite / case
    assert json.loads((directory / 'native/process.json').read_text())['exit_status'] == row['exit'] == 0
    assert (directory / 'native/stdout').read_bytes() == row['stdout'].encode()
    assert (directory / 'native/stderr').read_bytes() == row['stderr'].encode() == b''
    expected = row.get('originals', {'main.php': row.get('main_sha256', row.get('original_sha256'))})
    for name, digest in expected.items():
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
            suite, case, kind = STAGES[name]
            directory, native = native_record(sources, suite, case)
            main_path = directory / 'main.php'
            parsed = frontend.request({'op': 'parse', 'source': b64(main_path.read_bytes())})
            assert parsed['accepted'], parsed
            main_ast = parsed['ast']
            main_fixture = adapter.request({'op': 'check', 'ast': main_ast, 'fixture': True})['fixture']
            is_file = case.startswith('file-')
            if is_file:
                child_path = directory / 'unit.php'
                child_bytes = child_path.read_bytes()
                request = {'op': 'parse-file', 'id': '1', 'mode': 'file', 'profile': 'cli-raw-85',
                    'requested': b64(os.fsencode(child_path)), 'resolved': b64(os.fsencode(child_path)),
                    'opened': b64(os.fsencode(child_path)), 'source': b64(child_bytes)}
            else:
                evaluations = [node for _, node, _ in nodes(main_ast['program']) if node['node'] == 'Expr_Eval']
                assert evaluations and evaluations[0]['fields'][0]['node'] == 'Scalar_String'
                child_bytes = base64.b64decode(evaluations[0]['fields'][0]['fields'][0]['bytes'])
                request = {'op': 'parse-eval', 'id': '1', 'mode': 'eval', 'profile': 'cli-raw-85', 'source': b64(child_bytes)}
            parsed = frontend.request(request)
            assert parsed['accepted'], parsed
            child_ast = parsed['ast']
            child_fixture = adapter.request({'op': 'check', 'ast': child_ast, 'fixture': True})['fixture']
            setup = ['S_wait = $php_file_run(' + main_fixture + ',1200,' + byte_expr(os.fsencode(main_path)) + ',' + byte_expr(os.fsencode(directory)) + ')',
                     'S_wait.COMPLETION = SOURCE_PENDING']
            if is_file:
                setup += ['S_wait.FILECONTEXTS = [pfilecontext_wait]',
                    'S_parse = $file_open_resume(S_wait,FILE_OPENED pfilecontext_wait.NONCE pfilecontext_wait.CALLER pfilecontext_wait.REQUESTED ' + seq(os.fsencode(child_path)) + ' ' + seq(os.fsencode(child_path)) + ' ' + seq(child_bytes) + ')',
                    'S_parse.COMPLETION = SOURCE_PENDING',
                    'S_ready = $file_parse_resume(S_parse,SOURCE_ACCEPT 1 ' + seq(child_bytes) + ' ' + child_fixture + ')']
                marker = 'FILE_END 1'
                context = ['S.FILECONTEXTS = [pfilecontext]', 'pfilecontext.UNIT = (1)',
                    'pfilecontext.PHASE = FILE_UNIT_RUN', 'pfilecontext.OWNER = 0']
            else:
                setup += ['S_ready = $eval_resume(S_wait,SOURCE_ACCEPT 1 ' + seq(child_bytes) + ' ' + child_fixture + ')']
                marker = 'EVAL_END 1'
                context = ['S.EVALCONTEXTS = [pevalcontext]', 'pevalcontext.UNIT = 1',
                    'pevalcontext.PHASE = UNIT_RUN', 'pevalcontext.OWNER = 0']
            stage = {'static': ['S.TODO = (STATIC_INIT porigin) :: ptask_tail*', 'porigin = PORIGIN 1 pcpath'],
                     'caller': ['S.TODO = (STATIC_INIT porigin) :: ptask_tail*', 'porigin = PORIGIN 1 pcpath',
                         'S.CURRENT = (pcallcontext)', 'pcallcontext.FUNCTION = PORIGIN 1 pcpath_function'],
                     'end': ['S.TODO = (' + marker + ') :: ptask_tail*'],
                     'callable': ['S.TODO = (' + marker + ') :: ptask_tail*'],
                     'retained': ['S.TODO = (' + marker + ') :: ptask_tail*'],
                     'return': ['S.TODO = (RETURN_UNWIND (KNOWN (POBJECT n_object)) (PORIGIN 1 pcpath_return)) :: (' + marker + ') :: ptask_tail*']}[kind]
            checks = [*context, '$call_descriptors_valid(S)', '$declaration_entry_check(S) = S',
                      '$heap_valid($heap_graph(S))']
            if kind != 'caller':
                checks += ['$source_static_running(S,1)', '$source_static_caller(S,1)']
            if kind == 'static':
                checks += ['$source_static_origin(S,porigin)', '$static_task_valid(S,porigin,false)',
                    '~$source_static_origin(S[.EVALBINDINGS = eps],porigin)',
                    '~$static_task_valid(S[.EVALCONTEXTS = [pevalcontext[.OWNER = 1]]],porigin,false)',
                    '~$call_descriptors_valid(S[.EVALCONTEXTS = [pevalcontext[.OWNER = 1]]])',
                    '~$call_descriptors_valid(S[.TODO = [STATIC_INIT porigin]])',
                    '~$source_static_origin(S,PORIGIN 99 pcpath)',
                    'S_finished = $drive_steps(S,1200)', 'S_finished.COMPLETION = SOURCE_PENDING',
                    'S_finished.STATICS = eps', '$call_descriptors_valid(S_finished)',
                    '$eval_response_valid(S_finished,SOURCE_ACCEPT 2 ' + seq(child_bytes) + ' ' + child_fixture + ')']
            elif kind == 'caller':
                checks += ['~$source_static_origin(S,porigin)', '$static_task_valid(S,porigin,false)',
                    '~$source_static_caller(S,1)', '~$source_static_running(S,1)']
                for path, node, ancestors in nodes(child_ast['program']):
                    if node['node'] == 'StaticVar' and 'Stmt_Function' not in ancestors:
                        origin = 'PORIGIN 1 ([' + ','.join(path) + '])'
                        checks += ['$source_static_origin(S,' + origin + ')',
                            '~$static_task_valid(S[.ORIGIN = (' + origin + ')],' + origin + ',false)']
            elif kind == 'retained':
                checks += ['S.STATICS = [pstaticcell_function,pstaticcell_source]',
                    '~$source_static_origin(S,pstaticcell_function.ORIGIN)',
                    '$source_static_origin(S,pstaticcell_source.ORIGIN)',
                    '$source_static_next(S,1) = (pstaticcell_source.ORIGIN)',
                    '~$static_task_valid(S[.ORIGIN = (pstaticcell_function.ORIGIN)],pstaticcell_function.ORIGIN,false)',
                    '~$call_descriptors_valid(S[.ORIGIN = (pstaticcell_function.ORIGIN)][.TODO = (STATIC_INIT pstaticcell_function.ORIGIN) :: S.TODO])',
                    'S_next = $one(S)', 'S_next.STATICS = [pstaticcell_function]', 'S_next.TODO = S.TODO',
                    'S_next.EVALCONTEXTS = S.EVALCONTEXTS', '$call_descriptors_valid(S_next)',
                    '$declaration_entry_check(S_next) = S_next', 'S_retired = $one(S_next)',
                    'S_retired.EVALCONTEXTS = eps', '~$source_static_running(S_retired,1)',
                    '$source_static_origin(S_retired,pstaticcell_source.ORIGIN)',
                    '~$static_task_valid(S_retired[.ORIGIN = (pstaticcell_source.ORIGIN)],pstaticcell_source.ORIGIN,false)',
                    '$call_descriptors_valid(S_retired)', 'S_finished = $drive_steps(S_retired,1200)',
                    'S_finished.COMPLETION = NORMAL', 'S_finished.STATICS = [pstaticcell_function]',
                    '$call_descriptors_valid(S_finished)',
                    '$test_outputs(S_finished.EVENTS) = ' + seq(native['stdout'].encode()),
                    '$test_clean_events(S_finished.EVENTS)']
            else:
                checks += ['S.STATICS = [pstaticcell]', '$source_static_origin(S,pstaticcell.ORIGIN)',
                    '$source_static_next(S,1) = (pstaticcell.ORIGIN)',
                    'S_next = $one(S)', 'S_next.STATICS = eps', 'S_next.TODO = S.TODO',
                    'S_next.EVALCONTEXTS = S.EVALCONTEXTS', 'S_next.FILECONTEXTS = S.FILECONTEXTS',
                    'S_next.EVENTS = S.EVENTS', '$call_descriptors_valid(S_next)',
                    '$declaration_entry_check(S_next) = S_next']
                if kind == 'end':
                    checks += ['S_retired = $one(S_next)', '$source_static_next(S_retired,1) = eps',
                        '~$source_static_running(S_retired,1)', '$call_descriptors_valid(S_retired)',
                        'S_pending = $drive_steps(S_retired,1200)', 'S_pending.COMPLETION = SOURCE_PENDING',
                        'S_pending.STATICS = eps', '$call_descriptors_valid(S_pending)']
                    if not is_file:
                        checks += ['$eval_response_valid(S_pending,SOURCE_ACCEPT 2 ' + seq(child_bytes) + ' ' + child_fixture + ')',
                            '~$eval_response_valid(S_pending,SOURCE_ACCEPT 3 ' + seq(child_bytes) + ' ' + child_fixture + ')',
                            'S_bound = $eval_resume(S_pending,SOURCE_ACCEPT 2 ' + seq(child_bytes) + ' ' + child_fixture + ')',
                            'S_bound.COMPLETION = NORMAL', 'S_finished = $drive_steps(S_bound,1200)',
                            'S_finished.COMPLETION = NORMAL', 'S_finished.STATICS = eps',
                            '$test_outputs(S_finished.EVENTS) = ' + seq(native['stdout'].encode()),
                            '$test_clean_events(S_finished.EVENTS)']
                    checks += ['$read_name(S_pending[.COMPLETION = NORMAL],$ptascii("x"),1).RESULT = KNOWN (PINT 2)',
                               '$read_name(S_pending[.COMPLETION = NORMAL],$ptascii("old"),1).RESULT = KNOWN (PINT 90)']
                elif kind == 'return':
                    checks += ['S_next.TODO = (RETURN_UNWIND (KNOWN (POBJECT n_object)) (PORIGIN 1 pcpath_return)) :: (' + marker + ') :: ptask_tail*',
                        'S_finished = $drive_steps(S_next,1200)', 'S_finished.COMPLETION = NORMAL',
                        'S_finished.STATICS = eps', '$call_descriptors_valid(S_finished)',
                        '$test_outputs(S_finished.EVENTS) = ' + seq(native['stdout'].encode()),
                        '$test_clean_events(S_finished.EVENTS)']
                else:
                    callable_nodes = {'Stmt_Function', 'Stmt_ClassMethod', 'Expr_Closure', 'Expr_ArrowFunction', 'PropertyHook'}
                    static_paths = [path for path, node, ancestors in nodes(child_ast['program'])
                        if node['node'] == 'StaticVar' and callable_nodes.intersection(ancestors)]
                    assert static_paths
                    for path in static_paths:
                        origin = 'PORIGIN 1 ([' + ','.join(path) + '])'
                        checks += ['$static_descriptor(S,' + origin + ') =/= eps',
                            '~$source_static_origin(S,' + origin + ')',
                            '$source_static_candidate(S,1,CODESTATIC ([' + ','.join(path) + ']) eps 1 1 true) = eps',
                            '~$static_task_valid(S[.ORIGIN = (' + origin + ')],' + origin + ',false)',
                            '~$call_descriptors_valid(S[.ORIGIN = (' + origin + ')][.TODO = (STATIC_INIT (' + origin + ')) :: S.TODO])']
            assertions = setup + ['S_ready.COMPLETION = NORMAL', 'S_found = $seek(S_ready,600)',
                r'S_found.COMPLETION = NORMAL \/ S_found.COMPLETION = BUDGET', 'S = S_found[.COMPLETION = NORMAL]', *stage, *checks]
            target = out / name
            target.mkdir()
            text = 'dec $stage(pstate) : bool\ndef $stage(S) = true\n' + ''.join('  -- if ' + item + '\n' for item in stage)
            text += 'def $stage(S) = false -- otherwise\n' + PREFIX
            text += '\ndec $main() : bool\ndef $main() = true\n' + ''.join('  -- if ' + item + '\n' for item in assertions)
            (target / 'protocol.watsup').write_text(text)
            (target / 'assertions.json').write_text(json.dumps(assertions, indent=2) + '\n')
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
    assert args.attempt > 0
    names = args.stage or list(STAGES)
    assert names and len(set(names)) == len(names) and set(names) <= STAGES.keys()
    out, sources = args.output.resolve(), args.sources.resolve()
    paths = [Path(__file__), ROOT / 'tests/semantics/recorded_worker.py', ROOT / 'tests/semantics/_build/default/numeric_runner.exe']
    for name in names:
        suite, case, _ = STAGES[name]
        paths += [sources / suite / 'report.json', *sorted((sources / suite / case).glob('*.php')),
                  *[sources / suite / case / 'native' / name for name in ['stdout', 'stderr', 'process.json', 'command.json']]]
        if args.phase == 'check':
            paths += [out / name / 'protocol.watsup', out / name / 'assertions.json']
    pins = lambda: dict(inputs.inputs(), **{str(path): hashlib.sha256(path.read_bytes()).hexdigest() for path in paths})
    before = pins()
    label = args.phase if args.attempt == 1 else args.phase + '-' + str(args.attempt)
    report = {'phase': args.phase, 'revision': subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip(),
        'inputs': before, 'profile': types.PROFILE, 'environment': {'LC_ALL': 'C', 'TZ': 'UTC'},
        'records': [], 'result': 'fail', 'runtime_assertions': 0}
    try:
        if args.phase == 'fixtures':
            prepare(out, sources, names)
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
        if args.phase == 'fixtures':
            report['result'] = 'pass'
    finally:
        report['stable_inputs'] = before == pins()
        if not report['stable_inputs']:
            report['result'] = 'fail'
        (out / (label + '-report.json')).write_text(json.dumps(report, indent=2) + '\n')
    return report['result'] == 'pass'


if __name__ == '__main__':
    raise SystemExit(0 if main() else 1)
