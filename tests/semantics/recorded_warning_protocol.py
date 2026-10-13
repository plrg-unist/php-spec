#!/usr/bin/env python3
"""Nonfatal warning producers while a file-compiler diagnostic is recorded."""
import argparse
import base64
import hashlib
import json
import os
from pathlib import Path
import subprocess

import source_redeclare_fatal_protocol as source
from recorded_worker import Worker
from typed_static_invoke_set_protocol import process

fatal, retirement = source.fatal, source.retirement
ROOT, inputs, types = source.ROOT, source.inputs, source.types
seq, byte_expr, b64 = source.seq, source.byte_expr, source.b64
STAGES = {'api-warning': ('static-native-v30', 'file-fatal-shutdown-recorded-user-warning', 512),
    'read-warning': ('static-native-v31', 'file-fatal-shutdown-recorded-variable-warning', 2)}
PREFIX = source.PREFIX + r'''
dec $test_warning_stage(pstate, int) : bool
def $test_warning_stage(S, 512) = true
  -- if S.TODO = (ERROR_TRIGGER_PHASE pconfigcall 1) :: ptask_tail*
def $test_warning_stage(S, 2) = true
  -- if S.TODO = ptask :: ptask_tail*
  -- if $error_read_state_shape(S, ptask, S.RESULT, S.BASE) = (perrorread)
  -- if perrorread.NAME = $ptascii("undefined")
def $test_warning_stage(S, i) = false -- otherwise
dec $test_running(pstate) : pstate
def $test_running(S) = S[.COMPLETION = NORMAL] -- if S.COMPLETION = BUDGET
def $test_running(S) = S -- otherwise
dec $test_warning_seek(pstate, nat, int) : pstate
def $test_warning_seek(S, 0, i) = S
def $test_warning_seek(S, n, i) = S
  -- if $(n > 0)
  -- if $test_warning_stage(S, i) \/ S.COMPLETION = SOURCE_PENDING
def $test_warning_seek(S, n, i) = $test_warning_seek($drive_steps($test_running(S), 1), $nabs($(n - 1)), i)
  -- if $(n > 0)
  -- if ~$test_warning_stage(S, i) /\ S.COMPLETION =/= SOURCE_PENDING
dec $test_stderr_item(pevent) : nat
def $test_stderr_item(STDERR n*) = 1
def $test_stderr_item(pevent) = 0 -- otherwise
dec $test_stderr_count(pevent*) : nat
def $test_stderr_count(eps) = 0
def $test_stderr_count(pevent :: pevent_tail*) = $($test_stderr_item(pevent) + $test_stderr_count(pevent_tail*))
'''


def prepare(out, sources, names):
    out.mkdir()
    frontend = Worker([str(types.PHP), '-n', *types.FLAGS, '-d',
        'extension=' + str(ROOT / '.tools/php-file.so'), str(ROOT / 'frontend/worker.php')], out / 'frontend')
    adapter = None
    try:
        adapter = Worker([str(ROOT / '_build/default/adapter/main.exe'), str(ROOT)], out / 'adapter')

        def checked(data, mode, unit=0, path=None):
            request = {'op': 'parse', 'source': b64(data)} if mode == 'main' else {
                'op': 'parse-file' if mode == 'file' else 'parse-eval', 'id': str(unit),
                'mode': mode, 'profile': 'cli-raw-85', 'source': b64(data)}
            if mode == 'file':
                request.update({key: b64(os.fsencode(path)) for key in ['requested', 'resolved', 'opened']})
            parsed = frontend.request(request)
            assert parsed['accepted'], parsed
            return parsed['ast'], adapter.request({'op': 'check', 'ast': parsed['ast'], 'fixture': True})['fixture']

        for name in names:
            suite, case_name, level = STAGES[name]
            case, native = fatal.native_record(sources, suite, case_name)
            main_ast, main = checked((case / 'main.php').read_bytes(), 'main')
            child, = [node for _, node, ancestors in retirement.nodes(main_ast['program'])
                if node['node'] == 'Expr_Eval' and 'Stmt_Function' in ancestors]
            child_bytes = base64.b64decode(child['fields'][0]['fields'][0]['bytes'])
            _, child_fixture = checked(child_bytes, 'eval', 3)
            checks = ['S_open_1 = $php_file_run(' + main + ',2000,' + byte_expr(os.fsencode(case / 'main.php')) + ',' + byte_expr(os.fsencode(case)) + ')']
            for unit, filename in [(1, 'unit.php'), (2, 'inner.php')]:
                data = (case / filename).read_bytes()
                _, fixture = checked(data, 'file', unit, case / filename)
                opened, parsed, compiled = 'S_open_' + str(unit), 'S_parse_' + str(unit), 'S_compiled_' + str(unit)
                context = 'pfilecontext_open_' + str(unit)
                if unit == 2:
                    checks += [opened + ' = $drive_steps(S_compiled_1,2000)']
                response = 'FILE_OPENED ' + context + '.NONCE ' + context + '.CALLER ' + context + '.REQUESTED ' + seq(os.fsencode(case / filename)) + ' ' + seq(os.fsencode(case / filename)) + ' ' + seq(data)
                accepted = 'SOURCE_ACCEPT ' + str(unit) + ' ' + seq(data) + ' ' + fixture
                checks += [opened + '.COMPLETION = SOURCE_PENDING',
                    opened + '.FILECONTEXTS = ' + context + ' :: pfilecontext_tail_' + str(unit) + '*',
                    '$file_open_response_valid(' + opened + ',' + response + ')',
                    parsed + ' = $file_open_resume(' + opened + ',' + response + ')',
                    '$file_parse_response_valid(' + parsed + ',' + accepted + ')',
                    compiled + ' = $file_parse_resume(' + parsed + ',' + accepted + ')']
            checks += ['$recorded_compile_fatal(S_compiled_2.COMPLETION)',
                'S_found = $test_warning_seek(S_compiled_2,1800,' + str(level) + ')',
                r'S_found.COMPLETION = NORMAL \/ S_found.COMPLETION = BUDGET',
                'S = S_found[.COMPLETION = NORMAL]', '$test_warning_stage(S,' + str(level) + ')',
                'S.CURRENT =/= eps', 'S.RECORDEDCOMPILEERROR = (n_record)',
                '$recorded_compile_at(S.DECLARATIONS,S.RECORDEDCOMPILEERROR) = ((pcompletion_fatal,(PORIGIN 2 eps)))',
                '$recorded_compile_fatal(pcompletion_fatal)', '$eval_compile_fatal_current(S) = eps',
                '$error_handler_eligible(S,' + str(level) + ')', '$eval_compile_recorded_error(S,' + str(level) + ')',
                '$test_outputs(S.EVENTS) = $ptascii("B|S|alive|")', '$test_stderr_count(S.EVENTS) = 1',
                *fatal.public('S'),
                '~$eval_compile_recorded_error(S[.RECORDEDCOMPILEERROR = eps],' + str(level) + ')',
                '~$call_descriptors_valid(S[.RECORDEDCOMPILEERROR = eps])',
                '~$eval_compile_recorded_error(S[.RECORDEDCOMPILEERROR = (|S.DECLARATIONS|)],' + str(level) + ')',
                '~$call_descriptors_valid(S[.RECORDEDCOMPILEERROR = (|S.DECLARATIONS|)])']
            checks += ['~$eval_compile_recorded_error(S,' + str(fatal_level) + ')' for fatal_level in [1, 4, 16, 64, 256, 4096]]
            if level == 512:
                checks += ['S.TODO = (ERROR_TRIGGER_PHASE pconfigcall 1) :: ptask_tail*',
                    '$error_trigger_level(S,pconfigcall) = (512)', '$error_trigger_message(S,pconfigcall) = ($ptascii("late"))',
                    *fatal.reached('S_step', '$drive_steps(S,1)'),
                    'S_step.TODO = (ERROR_TRIGGER_PHASE pconfigcall 2) :: ptask_tail*',
                    'S_step.CURRENT = S.CURRENT', 'S_step.FRAMES = S.FRAMES', 'S_step.ERRORHANDLER = S.ERRORHANDLER',
                    'S_step.RECORDEDCOMPILEERROR = S.RECORDEDCOMPILEERROR', 'S_step.EVENTS = S.EVENTS', *fatal.public('S_step'),
                    *fatal.reached('S_done', '$drive_steps(S_step,1)'),
                    'S_done.RESULT = KNOWN (PBOOL true)']
                prefix = 'B|S|alive|Q|'
            else:
                checks += ['$error_read_plan(S) = (perrorread)', 'perrorread.NAME = $ptascii("undefined")',
                    '$error_read_pending(S)', *fatal.reached('S_step', '$drive_steps(S,1)'),
                    'S_step.TODO = (ERROR_READ_RESULT perrorread) :: ptask_tail*',
                    'S_step.CURRENT = S.CURRENT', 'S_step.FRAMES = S.FRAMES', 'S_step.ERRORHANDLER = S.ERRORHANDLER',
                    'S_step.RECORDEDCOMPILEERROR = S.RECORDEDCOMPILEERROR', 'S_step.EVENTS = S.EVENTS', *fatal.public('S_step'),
                    *fatal.reached('S_done', '$drive_steps(S_step,1)'),
                    'S_done.TODO = perrorread.TASK :: ptask_tail*', 'S_done.RESULT = KNOWN PNULL']
                prefix = 'B|S|alive|null|Q|'
            checks += ['S_done.EVENTS = S.EVENTS', 'S_done.RECORDEDCOMPILEERROR = S.RECORDEDCOMPILEERROR',
                *fatal.public('S_done'), 'S_wait = $drive_steps(S_done,2000)', 'S_wait.COMPLETION = SOURCE_PENDING',
                'S_wait.EVALCONTEXTS = [pevalcontext]', 'pevalcontext.UNIT = 3',
                'S_wait.RECORDEDCOMPILEERROR = (n_record)', '$test_outputs(S_wait.EVENTS) = $ptascii(' + json.dumps(prefix) + ')',
                '$test_stderr_count(S_wait.EVENTS) = 1', *fatal.public('S_wait'),
                '$eval_response_valid(S_wait,SOURCE_ACCEPT 3 ' + seq(child_bytes) + ' ' + child_fixture + ')',
                'S_ready = $eval_resume(S_wait,SOURCE_ACCEPT 3 ' + seq(child_bytes) + ' ' + child_fixture + ')',
                'S_ready.COMPLETION = NORMAL', 'S_final = $drive_steps(S_ready,2000)',
                'S_final.SHUTDOWN.PHASE = SHUTDOWN_DONE', 'S_final.EXITSTATUS = 255',
                'S_final.RECORDEDCOMPILEERROR = (n_record)', '$test_outputs(S_final.EVENTS) = $ptascii(' + json.dumps(native['stdout']) + ')',
                '$test_stderr_count(S_final.EVENTS) = 1', 'S_final.STATICS = [pstaticcell]',
                'S_final.STORE[pstaticcell.CELL] = DEFINED (POBJECT n_object)',
                '$weakref_find(S_final,S_final.ALLOCATIONS,n_object) = (n_weak)',
                '$weakref_get(S_final,n_weak) = POBJECT n_object', 'n_object <- S_final.DESTRUCTION.CALLED', *fatal.public('S_final')]
            target = out / name
            target.mkdir()
            (target / 'protocol.watsup').write_text(PREFIX + '\ndec $main() : bool\ndef $main() = true\n' + ''.join('  -- if ' + item + '\n' for item in checks))
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
    names, out, sources = args.stage or list(STAGES), args.output.resolve(), args.sources.resolve()
    assert args.attempt > 0 and names and len(set(names)) == len(names) and set(names) <= STAGES.keys()
    paths = [Path(__file__), Path(source.__file__), Path(fatal.__file__), Path(retirement.__file__),
        ROOT / 'tests/semantics/recorded_worker.py', ROOT / 'tests/semantics/_build/default/numeric_runner.exe',
        ROOT / 'frontend/target.php', ROOT / 'adapter/wire.ml']
    for name in names:
        suite, case_name, _ = STAGES[name]
        case = sources / suite / case_name
        paths += [case.parent / 'run.py', case.parent / 'report.json', *sorted(case.glob('*.php')),
            *[case / 'native' / item for item in ['stdout', 'stderr', 'process.json', 'command.json']]]
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
                result = process([str(ROOT / 'tests/semantics/_build/default/numeric_runner.exe'), '--sl', *modules, str(out / name / 'protocol.watsup')], out / name / label, 90, ROOT)
                passed = result.returncode == 0 and result.stdout == b'true\n' and not result.stderr
                count = len(json.loads((out / name / 'assertions.json').read_text()))
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
