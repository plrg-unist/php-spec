#!/usr/bin/env python3
"""Fatal source retirement with retained static roots and genuine shutdown reentry."""
import argparse
import base64
import hashlib
import json
import os
from pathlib import Path
import subprocess

import source_static_retirement_protocol as retirement
from recorded_worker import Worker
from typed_static_invoke_set_protocol import process

ROOT, inputs, types = retirement.ROOT, retirement.inputs, retirement.types
seq, byte_expr, b64 = retirement.seq, retirement.byte_expr, retirement.b64
STAGES = {
    'eval-fatal': ('static-native-v2', 'eval-fatal-weak'),
    'file-shutdown': ('static-native-v16', 'file-fatal-reentry-new'),
    'handler-fatal': ('static-native-v17', 'eval-fatal-handler-false'),
}
PREFIX = r'''dec $stage(pstate) : bool
def $stage(S) = true
  -- if S.TODO = (ERROR_TRIGGER_PHASE pconfigcall 1) :: ptask_tail*
def $stage(S) = false -- otherwise
''' + retirement.PREFIX


def public(name):
    return ['$call_descriptors_valid(' + name + ')', '$declaration_entry_check(' + name + ') = ' + name,
        '$heap_valid($heap_graph(' + name + '))']


def reached(name, expression):
    return [name + '_found = ' + expression,
        name + r'_found.COMPLETION = NORMAL \/ ' + name + '_found.COMPLETION = BUDGET',
        name + ' = ' + name + '_found[.COMPLETION = NORMAL]']


def native_record(sources, suite, case):
    report = json.loads((sources / suite / 'report.json').read_text())
    row, = [row for row in report.get('records', report.get('rows')) if row.get('id', row.get('name')) == case]
    assert report.get('target', report.get('profile')) == types.PROFILE
    assert report['runtime_sha256'] == hashlib.sha256(types.PHP.read_bytes()).hexdigest()
    directory = sources / suite / case
    assert json.loads((directory / 'native/process.json').read_text())['exit_status'] == row['exit'] == 255
    assert (directory / 'native/stdout').read_bytes() == row['stdout'].encode()
    assert (directory / 'native/stderr').read_bytes() == row['stderr'].encode()
    for name, digest in row['originals'].items():
        assert hashlib.sha256((directory / name).read_bytes()).hexdigest() == digest
    return directory, row


def fatal_checks(marker, contexts, context):
    checks = ['S_ready.COMPLETION = NORMAL', *reached('S', '$seek(S_ready,1800)'),
        'S.ORIGIN = (porigin)', 'porigin = PORIGIN 1 pcpath',
        'S.TODO = (ERROR_TRIGGER_PHASE pconfigcall 1) :: ptask_tail*',
        '$error_trigger_level(S,pconfigcall) = (256)', 'S.' + contexts + ' = [' + context + ']',
        context + '.OWNER = 0', 'S.FRAMES = eps', 'S.CURRENT = eps',
        '$source_static_user_source(S)', 'S.STATICS = [pstaticcell]',
        '$source_static_origin(S,pstaticcell.ORIGIN)',
        'S.STORE[pstaticcell.CELL] = DEFINED (POBJECT n_object)',
        '$weakref_find(S,S.ALLOCATIONS,n_object) = (n_weak)',
        '$weakref_get(S,n_weak) = POBJECT n_object',
        '$frames_roots($eager_fatal_frame(S) :: S.FRAMES) ++ $operand_nodes(S.RESULT) ++ $base_nodes(S.BASE) = eps',
        '$test_outputs(S.EVENTS) = $ptascii("B|")', *public('S'),
        'S_raw = $one(S)', 'S_raw.COMPLETION = USERFATAL ($ptascii("stop")) 1 true',
        'S_raw.ERRORORIGIN = S.ORIGIN', 'S_raw.ORIGIN = S.ORIGIN', 'S_raw.TODO = eps',
        'S_raw.STATICS = S.STATICS', 'S_raw.' + contexts + ' = S.' + contexts,
        '$shutdown_file(S_raw) = $call_sourcefile(S.FILES,porigin)',
        '$weakref_get(S_raw,n_weak) = POBJECT n_object',
        '$eager_fatal_ready(S,S_raw.COMPLETION)',
        '~$eager_fatal_ready(S[.' + contexts + ' = eps],S_raw.COMPLETION)',
        '~$eager_fatal_ready(S[.TODO = [ERROR_TRIGGER_PHASE pconfigcall 1]],S_raw.COMPLETION)',
        *reached('S_production', '$drive_steps(S,1)'),
        'S_production.SHUTDOWN.PHASE = SHUTDOWN_RUNNING',
        'S_production.SHUTDOWN.COMPLETION = REQUESTFATAL ($ptascii("Error")) ($ptascii("stop")) 1',
        'S_production.EVALCONTEXTS = eps', 'S_production.FILECONTEXTS = eps',
        'S_production.STATICS = S.STATICS', 'S_production.CURRENT = eps', 'S_production.FRAMES = eps',
        'S_production.DESTRUCTION.ABANDONED = [pdestructioncleanup]',
        'pdestructioncleanup.SOURCE = DESTRUCTOR_FATAL pdestructionfatal',
        'pdestructionfatal.FRAME.TODO = S.TODO', 'pdestructionfatal.FRAME.ORIGIN = S.ORIGIN',
        'pdestructionfatal.ERRORORIGIN = pdestructionfatal.FRAME.ORIGIN',
        'pdestructionfatal.EVALCONTEXTS = S.EVALCONTEXTS', 'pdestructionfatal.FILECONTEXTS = S.FILECONTEXTS',
        '$eager_fatal_nodes(pdestructionfatal) = eps',
        '$eager_fatal_valid(S_production,pdestructioncleanup,pdestructionfatal)',
        'n_object <- S_production.DESTRUCTION.CALLED',
        '$weakref_get(S_production,n_weak) = POBJECT n_object',
        '$source_static_origin(S_production,pstaticcell.ORIGIN)',
        '~$source_static_running(S_production,1)',
        '~$static_task_valid(S_production[.ORIGIN = (pstaticcell.ORIGIN)],pstaticcell.ORIGIN,false)',
        *public('S_production'),
        'pdestructionfatal_empty = pdestructionfatal[.ERRORORIGIN = eps]',
        'pdestructioncleanup_empty = pdestructioncleanup[.SOURCE = DESTRUCTOR_FATAL pdestructionfatal_empty]',
        '~$call_descriptors_valid(S_production[.DESTRUCTION.ABANDONED = [pdestructioncleanup_empty]])',
        'pdestructionfatal_main = pdestructionfatal[.ERRORORIGIN = (PORIGIN 0 eps)]',
        'pdestructioncleanup_main = pdestructioncleanup[.SOURCE = DESTRUCTOR_FATAL pdestructionfatal_main]',
        '~$call_descriptors_valid(S_production[.DESTRUCTION.ABANDONED = [pdestructioncleanup_main]])',
        'pdestructionfatal_missing = pdestructionfatal[.FRAME.TODO = [ERROR_TRIGGER_PHASE pconfigcall 1]]',
        'pdestructioncleanup_missing = pdestructioncleanup[.SOURCE = DESTRUCTOR_FATAL pdestructionfatal_missing]',
        '~$call_descriptors_valid(S_production[.DESTRUCTION.ABANDONED = [pdestructioncleanup_missing]])']
    if marker.startswith('FILE'):
        checks += [context + '.UNIT = (1)', context + '.PHASE = FILE_UNIT_RUN',
            'S_production.INCLUDEDOPENED = S.INCLUDEDOPENED', context + '.OPENED = (preqbytes_opened)',
            'preqbytes_opened <- S_production.INCLUDEDOPENED']
    else:
        checks += [context + '.UNIT = 1', context + '.PHASE = UNIT_RUN']
    return checks


def prepare(out, sources, names):
    out.mkdir()
    frontend = Worker([str(types.PHP), '-n', *types.FLAGS, '-d',
        'extension=' + str(ROOT / '.tools/php-file.so'), str(ROOT / 'frontend/worker.php')], out / 'frontend')
    adapter = None
    try:
        adapter = Worker([str(ROOT / '_build/default/adapter/main.exe'), str(ROOT)], out / 'adapter')
        def checked(source, mode, unit=1):
            request = {'op': 'parse', 'source': b64(source)} if mode == 'main' else {
                'op': 'parse-eval' if mode == 'eval' else 'parse-file', 'id': str(unit),
                'mode': mode, 'profile': 'cli-raw-85', 'source': b64(source)}
            if mode == 'file':
                request.update({'requested': b64(os.fsencode(child_path)), 'resolved': b64(os.fsencode(child_path)),
                    'opened': b64(os.fsencode(child_path))})
            parsed = frontend.request(request)
            assert parsed['accepted'], parsed
            return parsed['ast'], adapter.request({'op': 'check', 'ast': parsed['ast'], 'fixture': True})['fixture']
        for name in names:
            prefix = PREFIX
            directory, native = native_record(sources, *STAGES[name])
            main_path = directory / 'main.php'
            main_ast, main_fixture = checked(main_path.read_bytes(), 'main')
            is_file = name == 'file-shutdown'
            if is_file:
                child_path = directory / 'unit.php'
                child_bytes = child_path.read_bytes()
            else:
                evaluation, = [node for _, node, _ in retirement.nodes(main_ast['program']) if node['node'] == 'Expr_Eval']
                child_bytes = base64.b64decode(evaluation['fields'][0]['fields'][0]['bytes'])
            _, child_fixture = checked(child_bytes, 'file' if is_file else 'eval')
            checks = ['S_wait = $php_file_run(' + main_fixture + ',1800,' + byte_expr(os.fsencode(main_path)) + ',' + byte_expr(os.fsencode(directory)) + ')',
                'S_wait.COMPLETION = SOURCE_PENDING']
            if is_file:
                checks += ['S_wait.FILECONTEXTS = [pfilecontext_wait]',
                    'S_parse = $file_open_resume(S_wait,FILE_OPENED pfilecontext_wait.NONCE pfilecontext_wait.CALLER pfilecontext_wait.REQUESTED ' + seq(os.fsencode(child_path)) + ' ' + seq(os.fsencode(child_path)) + ' ' + seq(child_bytes) + ')',
                    'S_parse.COMPLETION = SOURCE_PENDING',
                    'S_ready = $file_parse_resume(S_parse,SOURCE_ACCEPT 1 ' + seq(child_bytes) + ' ' + child_fixture + ')']
                checks += fatal_checks('FILE_END 1', 'FILECONTEXTS', 'pfilecontext')
                evaluations = [node for _, node, ancestors in retirement.nodes(main_ast['program'])
                    if node['node'] == 'Expr_Eval' and 'Stmt_Function' in ancestors]
                assert len(evaluations) == 2
                inner_bytes = base64.b64decode(evaluations[0]['fields'][0]['fields'][0]['bytes'])
                assert inner_bytes == base64.b64decode(evaluations[1]['fields'][0]['fields'][0]['bytes'])
                _, inner_fixture = checked(inner_bytes, 'eval', unit=2)
                checks += ['S_wait_inner = $drive_steps(S,1800)', 'S_wait_inner.COMPLETION = SOURCE_PENDING',
                    'S_wait_inner.EVALCONTEXTS = [pevalcontext_inner]', 'pevalcontext_inner.UNIT = 2',
                    'pevalcontext_inner.PHASE = PARSER_WAIT', 'S_wait_inner.FILECONTEXTS = eps',
                    'S_wait_inner.STATICS = S.STATICS', '$weakref_get(S_wait_inner,n_weak) = POBJECT n_object',
                    '$test_outputs(S_wait_inner.EVENTS) = $ptascii("B|S|alive-a|")', *public('S_wait_inner'),
                    '$eval_response_valid(S_wait_inner,SOURCE_ACCEPT 2 ' + seq(inner_bytes) + ' ' + inner_fixture + ')',
                    '~$eval_response_valid(S_wait_inner,SOURCE_ACCEPT 1 ' + seq(inner_bytes) + ' ' + inner_fixture + ')',
                    'S_ready_inner = $eval_resume(S_wait_inner,SOURCE_ACCEPT 2 ' + seq(inner_bytes) + ' ' + inner_fixture + ')',
                    'S_ready_inner.COMPLETION = NORMAL', 'S_ready_inner.STATICS = S.STATICS',
                    'S_wait_again = $drive_steps(S_ready_inner,1800)', 'S_wait_again.COMPLETION = SOURCE_PENDING',
                    'S_wait_again.EVALCONTEXTS = [pevalcontext_again]', 'pevalcontext_again.UNIT = 3',
                    'S_wait_again.STATICS = S.STATICS', '$weakref_get(S_wait_again,n_weak) = POBJECT n_object',
                    '$test_outputs(S_wait_again.EVENTS) = $ptascii("B|S|alive-a|5|")', *public('S_wait_again'),
                    '$eval_response_valid(S_wait_again,SOURCE_ACCEPT 3 ' + seq(inner_bytes) + ' ' + inner_fixture + ')',
                    'S_ready_again = $eval_resume(S_wait_again,SOURCE_ACCEPT 3 ' + seq(inner_bytes) + ' ' + inner_fixture + ')',
                    'S_ready_again.COMPLETION = NORMAL', 'S_final = $drive_steps(S_ready_again,1800)']
            else:
                checks += ['S_ready = $eval_resume(S_wait,SOURCE_ACCEPT 1 ' + seq(child_bytes) + ' ' + child_fixture + ')']
                if name == 'handler-fatal':
                    prefix = PREFIX.replace('(ERROR_TRIGGER_PHASE pconfigcall 1)', '(ERROR_HANDLER_RESULT perrorcall)')
                    checks += ['S_ready.COMPLETION = NORMAL', *reached('S', '$seek(S_ready,1800)'),
                        'S.TODO = (ERROR_HANDLER_RESULT perrorcall) :: ptask_tail*', 'perrorcall.LEVEL = 256',
                        'S.RESULT = KNOWN (PBOOL false)', '$error_entered_call_valid(S,perrorcall)',
                        'S.ORIGIN = (porigin)', 'porigin = PORIGIN 1 pcpath',
                        'S.EVALCONTEXTS = [pevalcontext]', 'pevalcontext.UNIT = 1',
                        'pevalcontext.PHASE = UNIT_RUN', 'pevalcontext.OWNER = 0',
                        'S.FRAMES = eps', 'S.CURRENT = eps', '$source_static_user_source(S)',
                        'S.STATICS = [pstaticcell]', 'S.STORE[pstaticcell.CELL] = DEFINED (POBJECT n_object)',
                        '$weakref_find(S,S.ALLOCATIONS,n_object) = (n_weak)',
                        '$test_outputs(S.EVENTS) = $ptascii("B|H|")', *public('S'),
                        'S_raw = $one(S)', 'S_raw.COMPLETION = USERFATAL ($ptascii("stop")) 1 true',
                        'S_raw.ERRORORIGIN = S.ORIGIN', 'S_raw.STATICS = S.STATICS',
                        '$eager_fatal_ready(S,S_raw.COMPLETION)', *reached('S_production', '$drive_steps(S,1)'),
                        'S_production.EVALCONTEXTS = eps', 'S_production.FILECONTEXTS = eps',
                        'S_production.STATICS = S.STATICS',
                        'S_production.DESTRUCTION.ABANDONED = [pdestructioncleanup]',
                        'pdestructioncleanup.SOURCE = DESTRUCTOR_FATAL pdestructionfatal',
                        'pdestructionfatal.FRAME.TODO = S.TODO', 'pdestructionfatal.FRAME.ORIGIN = S.ORIGIN',
                        'pdestructionfatal.VALUE = S.RESULT',
                        'pdestructionfatal.ERRORORIGIN = pdestructionfatal.FRAME.ORIGIN',
                        'S_history = $eager_fatal_history(S_production,pdestructionfatal)',
                        'S_history.TODO = S.TODO', '$eager_fatal_ready(S_history,pdestructionfatal.COMPLETION)',
                        '$eager_fatal_source_valid(S_history,pdestructionfatal.COMPLETION)',
                        '$eager_fatal_valid(S_production,pdestructioncleanup,pdestructionfatal)',
                        '$weakref_get(S_production,n_weak) = POBJECT n_object',
                        'n_object <- S_production.DESTRUCTION.CALLED', *public('S_production'),
                        'pdestructionfatal_wrong = pdestructionfatal[.ERRORORIGIN = (PORIGIN 0 eps)]',
                        'pdestructioncleanup_wrong = pdestructioncleanup[.SOURCE = DESTRUCTOR_FATAL pdestructionfatal_wrong]',
                        '~$call_descriptors_valid(S_production[.DESTRUCTION.ABANDONED = [pdestructioncleanup_wrong]])',
                        'pdestructionfatal_true = pdestructionfatal[.VALUE = KNOWN (PBOOL true)][.BASE = BASE_VALUE (KNOWN (PBOOL true))]',
                        'pdestructioncleanup_true = pdestructioncleanup[.SOURCE = DESTRUCTOR_FATAL pdestructionfatal_true]',
                        '~$call_descriptors_valid(S_production[.DESTRUCTION.ABANDONED = [pdestructioncleanup_true]])']
                else:
                    checks += fatal_checks('EVAL_END 1', 'EVALCONTEXTS', 'pevalcontext')
                checks += ['S_final = $drive_steps(S,1800)']
            checks += ['S_final.COMPLETION = REQUESTFATAL ($ptascii("Error")) ($ptascii("stop")) 1',
                'S_final.EVALCONTEXTS = eps', 'S_final.FILECONTEXTS = eps', 'S_final.STATICS = S.STATICS',
                '$weakref_get(S_final,n_weak) = POBJECT n_object', 'n_object <- S_final.DESTRUCTION.CALLED',
                '$test_outputs(S_final.EVENTS) = $ptascii(' + json.dumps(native['stdout']) + ')', *public('S_final')]
            target = out / name
            target.mkdir()
            (target / 'protocol.watsup').write_text(prefix + '\ndec $main() : bool\ndef $main() = true\n' +
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
    paths = [Path(__file__), Path(retirement.__file__), ROOT / 'tests/semantics/recorded_worker.py',
        ROOT / 'tests/semantics/_build/default/numeric_runner.exe']
    for name in names:
        suite, case = STAGES[name]
        directory = sources / suite / case
        paths += [sources / suite / 'report.json', *sorted(directory.glob('*.php')),
            *[directory / 'native' / item for item in ['stdout', 'stderr', 'process.json', 'command.json']]]
        if args.phase == 'check':
            paths += [out / name / 'protocol.watsup', out / name / 'assertions.json']
    pins = lambda: dict(inputs.inputs(), **{str(path): hashlib.sha256(path.read_bytes()).hexdigest() for path in paths})
    before = pins()
    label = args.phase if args.attempt == 1 else args.phase + '-' + str(args.attempt)
    report = {'phase': args.phase, 'revision': subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip(),
        'semantic_diff_sha256': hashlib.sha256(subprocess.check_output(['git', 'diff', 'HEAD', '--', 'spec/semantics'], cwd=ROOT)).hexdigest(),
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
