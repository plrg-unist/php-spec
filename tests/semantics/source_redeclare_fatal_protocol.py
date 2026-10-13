#!/usr/bin/env python3
"""Fresh shutdown sources after an authenticated redeclaration compiler fatal."""
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
STAGES = {'eval-wait': ('static-native-v23', 'eval-inner-redeclare-retained-static'),
    'file-wait': ('static-native-v25', 'redeclare-shutdown-file-wait-reporting-zero')}
PREFIX = retirement.PREFIX[retirement.PREFIX.index('dec $test_output'):retirement.PREFIX.index('dec $test_clean_event')]


def certificate(name):
    return ['$eager_fatal_compiler_valid(' + name + ',pdestructioncleanup,pdestructionfatal)',
        '$eager_fatal_valid(' + name + ',pdestructioncleanup,pdestructionfatal)', *fatal.public(name)]


def prepare(out, sources, names):
    out.mkdir()
    frontend = Worker([str(types.PHP), '-n', *types.FLAGS, '-d',
        'extension=' + str(ROOT / '.tools/php-file.so'), str(ROOT / 'frontend/worker.php')], out / 'frontend')
    adapter = None
    try:
        adapter = Worker([str(ROOT / '_build/default/adapter/main.exe'), str(ROOT)], out / 'adapter')
        def checked(data, mode, unit=0, path=None):
            request = {'op': 'parse', 'source': b64(data)} if mode == 'main' else {
                'op': 'parse-eval' if mode == 'eval' else 'parse-file', 'id': str(unit),
                'mode': mode, 'profile': 'cli-raw-85', 'source': b64(data)}
            if mode == 'file':
                request.update({key: b64(os.fsencode(path)) for key in ['requested', 'resolved', 'opened']})
            parsed = frontend.request(request)
            assert parsed['accepted'], parsed
            fixture = adapter.request({'op': 'check', 'ast': parsed['ast'], 'fixture': True})['fixture']
            return parsed['ast'], fixture
        for name in names:
            directory, native = fatal.native_record(sources, *STAGES[name])
            main_path = directory / 'main.php'
            main_ast, main_fixture = checked(main_path.read_bytes(), 'main')
            outer, = [node for _, node, ancestors in retirement.nodes(main_ast['program'])
                if node['node'] == 'Expr_Eval' and 'Stmt_Function' not in ancestors]
            first_bytes = base64.b64decode(outer['fields'][0]['fields'][0]['bytes'])
            first_ast, first_fixture = checked(first_bytes, 'eval', 1)
            inner, = [node for _, node, _ in retirement.nodes(first_ast['program']) if node['node'] == 'Expr_Eval']
            second_bytes = base64.b64decode(inner['fields'][0]['fields'][0]['bytes'])
            _, second_fixture = checked(second_bytes, 'eval', 2)
            is_file = name == 'file-wait'
            if is_file:
                child_path = directory / 'later.php'
                child_bytes = child_path.read_bytes()
            else:
                calls = [node for _, node, ancestors in retirement.nodes(main_ast['program'])
                    if node['node'] == 'Expr_Eval' and 'Stmt_Function' in ancestors]
                assert len(calls) == 2
                child_bytes = base64.b64decode(calls[0]['fields'][0]['fields'][0]['bytes'])
                assert child_bytes == base64.b64decode(calls[1]['fields'][0]['fields'][0]['bytes'])
                child_path = None
            _, child_fixture = checked(child_bytes, 'file' if is_file else 'eval', 3, child_path)
            checks = ['S_wait1 = $php_file_run(' + main_fixture + ',2000,' + byte_expr(os.fsencode(main_path)) + ',' + byte_expr(os.fsencode(directory)) + ')',
                'S_wait1.COMPLETION = SOURCE_PENDING',
                'S_ready1 = $eval_resume(S_wait1,SOURCE_ACCEPT 1 ' + seq(first_bytes) + ' ' + first_fixture + ')',
                'S_ready1.COMPLETION = NORMAL',
                'S_wait2 = $drive_steps(S_ready1,2000)', 'S_wait2.COMPLETION = SOURCE_PENDING',
                'S_compiled2 = $eval_resume(S_wait2,SOURCE_ACCEPT 2 ' + seq(second_bytes) + ' ' + second_fixture + ')',
                '$destructor_bailout(S_compiled2.COMPLETION)', 'S_compiled2.COMPILESTOP']
            for unit in [3, 4]:
                prior = 'S_compiled2' if unit == 3 else 'S_ready3'
                waiting, ready = 'S_wait' + str(unit), 'S_ready' + str(unit)
                response = 'SOURCE_ACCEPT ' + str(unit) + ' ' + seq(child_bytes) + ' ' + child_fixture
                if is_file:
                    opened = 'S_open' + str(unit)
                    context_open = 'pfilecontext_open' + str(unit)
                    facts = 'FILE_OPENED ' + context_open + '.NONCE ' + context_open + '.CALLER ' + context_open + '.REQUESTED ' + seq(os.fsencode(child_path)) + ' ' + seq(os.fsencode(child_path)) + ' ' + seq(child_bytes)
                    checks += [opened + ' = $drive_steps(' + prior + ',2000)', opened + '.COMPLETION = SOURCE_PENDING',
                        opened + '.FILECONTEXTS = [' + context_open + ']', *fatal.public(opened),
                        '$file_open_response_valid(' + opened + ',' + facts + ')',
                        waiting + ' = $file_open_resume(' + opened + ',' + facts + ')']
                    contexts, context, guard, resume = 'FILECONTEXTS', 'pfilecontext_' + str(unit), '$file_parse_response_valid', '$file_parse_resume'
                else:
                    checks += [waiting + ' = $drive_steps(' + prior + ',2000)']
                    contexts, context, guard, resume = 'EVALCONTEXTS', 'pevalcontext_' + str(unit), '$eval_response_valid', '$eval_resume'
                checks += [waiting + '.COMPLETION = SOURCE_PENDING', waiting + '.' + contexts + ' = [' + context + ']',
                    context + '.UNIT = ' + ('(' + str(unit) + ')' if is_file else str(unit)),
                    context + '.PHASE = ' + ('FILE_PARSE_WAIT' if is_file else 'PARSER_WAIT'),
                    waiting + '.COMPILESTOP = false', waiting + '.REPORTING = ' + ('0' if is_file else '30719'),
                    waiting + '.EXITSTATUS = 255', '$test_outputs(' + waiting + '.EVENTS) = $ptascii(' + json.dumps('B|S|alive|' + ('5|' if unit == 4 else '')) + ')']
                if unit == 3:
                    checks += [waiting + '.STATICS = [pstaticcell]', '$source_static_origin(' + waiting + ',pstaticcell.ORIGIN)',
                        waiting + '.STORE[pstaticcell.CELL] = DEFINED (POBJECT n_object)',
                        '$weakref_find(' + waiting + ',' + waiting + '.ALLOCATIONS,n_object) = (n_weak)',
                        waiting + '.DESTRUCTION.ABANDONED = [pdestructioncleanup]',
                        'pdestructioncleanup.SOURCE = DESTRUCTOR_FATAL pdestructionfatal', 'pdestructionfatal.COMPILESTOP',
                        'pdestructionfatal.REPORTING = 30719', 'pdestructionfatal.DECLARATIONS = S_compiled2.DECLARATIONS',
                        '$shutdown_compiler_snapshot(pdestructionfatal.COMPLETION) = (pdestructionfatal.FROZEN)',
                        'S_history = $eager_fatal_history(' + waiting + ',pdestructionfatal)',
                        '$eager_fatal_ready(S_history,pdestructionfatal.COMPLETION)',
                        '$call_current_valid(S_history)', '$call_frames_valid(S_history,S_history.FRAMES)',
                        '$call_tasks_valid(S_history,S_history.TODO)', *certificate(waiting),
                        'pdestructionfatal_stale = pdestructionfatal[.DECLARATIONS = S_wait2.DECLARATIONS]',
                        '$(|S_wait2.DECLARATIONS| < |pdestructionfatal.DECLARATIONS|)',
                        'pdestructioncleanup_stale = pdestructioncleanup[.SOURCE = DESTRUCTOR_FATAL pdestructionfatal_stale]',
                        '~$call_descriptors_valid(' + waiting + '[.DESTRUCTION.ABANDONED = [pdestructioncleanup_stale]])',
                        'pdestructionfatal_wrong = pdestructionfatal[.ERRORORIGIN = (PORIGIN 0 eps)]',
                        'pdestructioncleanup_wrong = pdestructioncleanup[.SOURCE = DESTRUCTOR_FATAL pdestructionfatal_wrong]',
                        '~$call_descriptors_valid(' + waiting + '[.DESTRUCTION.ABANDONED = [pdestructioncleanup_wrong]])',
                        'pdestructionfatal_raw = pdestructionfatal[.COMPLETION = FATAL ($ptascii("forged")) 1][.FROZEN = REQUESTFATAL ($ptascii("Error")) ($ptascii("forged")) 1]',
                        'pdestructioncleanup_raw = pdestructioncleanup[.SOURCE = DESTRUCTOR_FATAL pdestructionfatal_raw]',
                        '~$call_descriptors_valid(' + waiting + '[.DESTRUCTION.ABANDONED = [pdestructioncleanup_raw]])',
                        'pdestructionfatal_frozen = pdestructionfatal[.FROZEN = REQUESTFATAL ($ptascii("Error")) ($ptascii("forged")) 1]',
                        'pdestructioncleanup_frozen = pdestructioncleanup[.SOURCE = DESTRUCTOR_FATAL pdestructionfatal_frozen]',
                        '~$call_descriptors_valid(' + waiting + '[.DESTRUCTION.ABANDONED = [pdestructioncleanup_frozen]])',
                        '~$call_descriptors_valid(' + waiting + '[.' + contexts + ' = eps])',
                        '~$call_descriptors_valid(' + waiting + '[.' + contexts + ' = [' + context + '[.UNIT = ' + ('(2)' if is_file else '2') + ']]])',
                        '~$call_descriptors_valid(' + waiting + '[.' + contexts + ' = [' + context + '[.SITE = PORIGIN 0 eps]]])',
                        '~$call_descriptors_valid(' + waiting + '[.REPORTING = ' + ('30719' if is_file else '0') + '])']
                else:
                    checks += [waiting + '.STATICS = S_wait3.STATICS', '$source_unit(' + waiting + '.SOURCES,3) =/= eps',
                        *certificate(waiting)]
                checks += ['$weakref_get(' + waiting + ',n_weak) = POBJECT n_object',
                    'n_object <- ' + waiting + '.DESTRUCTION.CALLED', guard + '(' + waiting + ',' + response + ')',
                    '~' + guard + '(' + waiting + ',SOURCE_ACCEPT 2 ' + seq(child_bytes) + ' ' + child_fixture + ')',
                    ready + ' = ' + resume + '(' + waiting + ',' + response + ')', ready + '.COMPLETION = NORMAL',
                    *fatal.public(ready)]
            checks += ['S_final = $drive_steps(S_ready4,2000)', 'S_final.COMPLETION = pdestructionfatal.FROZEN',
                'S_final.SHUTDOWN.PHASE = SHUTDOWN_DONE', 'S_final.SHUTDOWN.COMPLETION = pdestructionfatal.FROZEN',
                'S_final.EXITSTATUS = 255', 'S_final.EVALCONTEXTS = eps', 'S_final.FILECONTEXTS = eps',
                'S_final.STATICS = S_wait3.STATICS', '$weakref_get(S_final,n_weak) = POBJECT n_object',
                '$test_outputs(S_final.EVENTS) = $ptascii(' + json.dumps(native['stdout']) + ')', *fatal.public('S_final')]
            target = out / name
            target.mkdir()
            (target / 'protocol.watsup').write_text(PREFIX + '\ndec $main() : bool\ndef $main() = true\n' + ''.join('  -- if ' + check + '\n' for check in checks))
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
        ROOT / 'tests/semantics/_build/default/numeric_runner.exe', ROOT / 'frontend/target.php', ROOT / 'adapter/wire.ml']
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
                result = process([str(ROOT / 'tests/semantics/_build/default/numeric_runner.exe'), '--sl', *modules, str(directory / 'protocol.watsup')], directory / label, 90, ROOT)
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
