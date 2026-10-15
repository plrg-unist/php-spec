#!/usr/bin/env python3
"""A captured dynamic shutdown trigger drains its retained compiler fatal."""
import argparse
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
CASE = ('static-native-v33', 'file-fatal-shutdown-dynamic-user-error')
PREFIX = source.PREFIX + r'''
dec $test_runtime_stage(pstate) : bool
def $test_runtime_stage(S) = true
  -- if S.TODO = (ERROR_TRIGGER_PHASE pconfigcall 1) :: ptask_tail*
def $test_runtime_stage(S) = false -- otherwise
dec $test_running(pstate) : pstate
def $test_running(S) = S[.COMPLETION = NORMAL] -- if S.COMPLETION = BUDGET
def $test_running(S) = S -- otherwise
dec $test_runtime_seek(pstate, nat) : pstate
def $test_runtime_seek(S, 0) = S
def $test_runtime_seek(S, n) = S
  -- if $(n > 0)
  -- if $test_runtime_stage(S) \/ S.COMPLETION = SOURCE_PENDING
def $test_runtime_seek(S, n) = $test_runtime_seek($drive_steps($test_running(S), 1), $nabs($(n - 1)))
  -- if $(n > 0)
  -- if ~$test_runtime_stage(S) /\ S.COMPLETION =/= SOURCE_PENDING
dec $test_one(pstate) : pstate
def $test_one(S) = S_next -- PhpStep: S ~> S_next
dec $test_stderr_item(pevent) : nat
def $test_stderr_item(STDERR n*) = 1
def $test_stderr_item(pevent) = 0 -- otherwise
dec $test_stderr_count(pevent*) : nat
def $test_stderr_count(eps) = 0
def $test_stderr_count(pevent :: pevent_tail*) = $($test_stderr_item(pevent) + $test_stderr_count(pevent_tail*))
'''


def prepare(out, sources):
    out.mkdir()
    frontend = Worker([str(types.PHP), '-n', *types.FLAGS, '-d',
        'extension=' + str(ROOT / '.tools/php-file.so'), str(ROOT / 'frontend/worker.php')], out / 'frontend')
    adapter = None
    try:
        adapter = Worker([str(ROOT / '_build/default/adapter/main.exe'), str(ROOT)], out / 'adapter')

        def checked(data, mode, unit=0, path=None):
            request = {'op': 'parse', 'source': b64(data)} if mode == 'main' else {
                'op': 'parse-file', 'id': str(unit), 'mode': mode, 'profile': 'cli-raw-85', 'source': b64(data)}
            if mode == 'file':
                request.update({key: b64(os.fsencode(path)) for key in ['requested', 'resolved', 'opened']})
            parsed = frontend.request(request)
            assert parsed['accepted'], parsed
            return parsed['ast'], adapter.request({'op': 'check', 'ast': parsed['ast'], 'fixture': True})['fixture']

        case, native = fatal.native_record(sources, *CASE)
        main_ast, main = checked((case / 'main.php').read_bytes(), 'main')
        # Pick an authentic echo in the same shutdown function as the trigger.
        shutdown = next(node for _, node, _ in retirement.nodes(main_ast['program'])
            if node['node'] == 'Stmt_Function' and node['fields'][2]['fields'][0]['bytes'] == b64(b'source_shutdown'))
        shutdown_path = next(path for path, node, _ in retirement.nodes(main_ast['program']) if node is shutdown)
        echo_path = next(path for path, node, _ in retirement.nodes(main_ast['program'])
            if node['node'] == 'Stmt_Echo' and path[:len(shutdown_path)] == shutdown_path)
        echo = 'PORIGIN 0 (' + '[' + ', '.join(echo_path) + ']' + ')'
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
            checks += [opened + '.COMPLETION = SOURCE_PENDING', opened + '.FILECONTEXTS = ' + context + ' :: pfilecontext_tail_' + str(unit) + '*',
                '$file_open_response_valid(' + opened + ',' + response + ')', parsed + ' = $file_open_resume(' + opened + ',' + response + ')',
                '$file_parse_response_valid(' + parsed + ',' + accepted + ')', compiled + ' = $file_parse_resume(' + parsed + ',' + accepted + ')']
        checks += ['$recorded_compile_fatal(S_compiled_2.COMPLETION)',
            *fatal.reached('S', '$test_runtime_seek(S_compiled_2,1800)'),
            'S.TODO = (ERROR_TRIGGER_PHASE pconfigcall 1) :: ptask_tail*', '$error_trigger_level(S,pconfigcall) = (256)',
            '$error_trigger_message(S,pconfigcall) = ($ptascii("late"))', '$error_handler_eligible(S,256)',
            'S.RECORDEDCOMPILEERROR = (n_record)',
            '$recorded_compile_at(S.DECLARATIONS,(n_record)) = ((pcompletion_cached,porigin_cached?))',
            '$recorded_compile_fatal(pcompletion_cached)', 'porigin_cached? = (PORIGIN 2 eps)', 'porigin_cached? =/= S.ORIGIN',
            '$recorded_runtime_pending(S,256)', '~$recorded_runtime_site(S,pconfigcall.SITE)',
            '$recorded_runtime_call_valid(S,pconfigcall)', 'pconfigcall.SELECTION = (n_nonce)',
            'S.SELECTEDCALLS[n_nonce] = pselectedcall', 'pselectedcall.KIND = INTRINSIC_TRIGGER_ERROR',
            'pselectedcall.ORIGINAL = $ptascii("trigger_error")', 'pselectedcall.NONCE = n_nonce',
            'pconfigcall.OWNER = eps', 'pconfigcall.PACKS = eps', '$config_nodes(pconfigcall) = eps',
            'pconfigcall.SENT = [NAMED_SENT (KNOWN pvalue_message), NAMED_SENT (KNOWN (PINT 256))]',
            '$string_bytes(pvalue_message) = ($ptascii("late"))', '$string_carrier_valid(S,pvalue_message)',
            'pdeclcause = $declaration_cause(S)', '$declaration_cause_valid(S,' + echo + ',pdeclcause)',
            '~$recorded_runtime_site(S,' + echo + ')', '$test_outputs(S.EVENTS) = $ptascii("B|S|alive|")',
            '$test_stderr_count(S.EVENTS) = 1', *fatal.public('S'),
            '~$recorded_runtime_pending(S[.TODO = (ERROR_TRIGGER_PHASE pconfigcall 0) :: ptask_tail*],256)',
            'pconfigcall_warning = pconfigcall[.SENT = $named_slot_set(pconfigcall.SENT,1,KNOWN (PINT 512))]',
            '~$recorded_runtime_pending(S[.TODO = (ERROR_TRIGGER_PHASE pconfigcall_warning 1) :: ptask_tail*],256)',
            'S_raw = $test_one(S)', 'S_raw.COMPLETION = pcompletion_cached', 'S_raw.ERRORORIGIN = porigin_cached?',
            'S_raw.RECORDEDCOMPILEERROR = eps', 'S_raw.TODO = eps', 'S_raw.CURRENT = S.CURRENT', 'S_raw.FRAMES = S.FRAMES',
            'S_raw.ERRORHANDLER = S.ERRORHANDLER', 'S_raw.EVENTS = S.EVENTS', 'S_raw.ERRORFATALTRACE = eps',
            'S_raw.DECLARATIONS = S.DECLARATIONS ++ [PDRECORDEDCALLFATAL pconfigcall pdeclcause n_record]',
            'S_raw.TRACE = ptraceframe :: ptraceframe_tail*', 'ptraceframe.FILE = ' + seq(os.fsencode(case / 'main.php')),
            'ptraceframe.LINE = 11', 'ptraceframe.FUNCTION = $ptascii("trigger_error")',
            '$error_trigger_trace_values(S,pconfigcall) = [$string_plain(pvalue_message),PINT 256]',
            'ptraceframe.ARGS = [(KINT 0,$string_plain(pvalue_message)),(KINT 1,PINT 256)]',
            'S_budget = $drive_steps(S,0)', 'S_budget = S[.COMPLETION = BUDGET]',
            'S_resume = S_budget[.COMPLETION = NORMAL]', 'S_resume = S',
            'S_final = $drive_steps(S_resume,2000)', 'S_final.SHUTDOWN.PHASE = SHUTDOWN_DONE', 'S_final.EXITSTATUS = 255',
            'S_final.RECORDEDCOMPILEERROR = eps', 'S_final.DECLARATIONS = S_raw.DECLARATIONS',
            '$test_outputs(S_final.EVENTS) = $ptascii(' + json.dumps(native['stdout']) + ')', '$test_stderr_count(S_final.EVENTS) = 2',
            'S_final.STATICS = [pstaticcell]', 'S_final.STORE[pstaticcell.CELL] = DEFINED (POBJECT n_object)',
            '$weakref_find(S_final,S_final.ALLOCATIONS,n_object) = (n_weak)', '$weakref_get(S_final,n_weak) = POBJECT n_object',
            'n_object <- S_final.DESTRUCTION.CALLED', 'S_final.DESTRUCTION.ABANDONED = [pdestructioncleanup_old,pdestructioncleanup_new]',
            'pdestructioncleanup_old.SOURCE = DESTRUCTOR_FATAL pdestructionfatal_old', 'pdestructioncleanup_new.SOURCE = DESTRUCTOR_FATAL pdestructionfatal_new',
            'pdestructionfatal_old.COMPILESTOP', '~pdestructionfatal_new.COMPILESTOP',
            'pdestructionfatal_new.FRAME.TODO = S.TODO', 'pdestructionfatal_new.FRAME.ORIGIN = S.ORIGIN',
            'pdestructionfatal_new.COMPLETION = pcompletion_cached', 'pdestructionfatal_new.ERRORORIGIN = porigin_cached?',
            'pdestructionfatal_new.TRACE = S_raw.TRACE', 'pdestructionfatal_new.DECLARATIONS = S_final.DECLARATIONS',
            '$eager_fatal_valid(S_final,pdestructioncleanup_old,pdestructionfatal_old)',
            '$eager_fatal_valid(S_final,pdestructioncleanup_new,pdestructionfatal_new)', *fatal.public('S_final'),
            'S_history = $eager_fatal_history(S_final,pdestructionfatal_new)', 'S_history.DECLARATIONS = S.DECLARATIONS',
            'S_history.RECORDEDCOMPILEERROR = (n_record)', '$recorded_runtime_snapshot_valid(S_final,S_history,pdestructionfatal_new)',
            'S_replayed = $recorded_runtime_fatal(S_history,pconfigcall)', 'S_replayed.DECLARATIONS = S_final.DECLARATIONS',
            'S_replayed.COMPLETION = pcompletion_cached', 'S_replayed.ERRORORIGIN = porigin_cached?', 'S_replayed.TRACE = S_raw.TRACE',
            '~$call_descriptors_valid(S_final[.RECORDEDCOMPILEERROR = (n_record)])']
        checks += ['$recorded_runtime_call_cutoff(S_final.DECLARATIONS) = ((pconfigcall,pdeclcause,n_record))',
            '$recorded_runtime_cutoff(S_final.DECLARATIONS) = eps',
            '$recorded_history_index(S_final,S_final.DECLARATIONS) = eps',
            '$recorded_history_index(S_final,S.DECLARATIONS) = (n_record)',
            'pselectedcall_later = pselectedcall[.NONCE = S.SELECTSEQ][.KIND = INTRINSIC_USER_ERROR][.ORIGINAL = $ptascii("user_error")][.LOOKUP = $ptascii("user_error")]',
            '$selected_entry_source_valid(S,pselectedcall_later)',
            'S_later = S[.SELECTEDCALLS = S.SELECTEDCALLS ++ [pselectedcall_later]][.SELECTSEQ = $(S.SELECTSEQ + 1)]',
            '$recorded_runtime_call_valid(S_later,pconfigcall)',
            'pconfigcall_later = pconfigcall[.SELECTION = (pselectedcall_later.NONCE)][.KIND = INTRINSIC_USER_ERROR]',
            '$recorded_runtime_call_valid(S_later,pconfigcall_later)',
            'S_final_later = S_final[.SELECTEDCALLS = S_later.SELECTEDCALLS][.SELECTSEQ = S_later.SELECTSEQ]',
            'pdestructionfatal_later = pdestructionfatal_new[.FRAME.TODO = (ERROR_TRIGGER_PHASE pconfigcall_later 1) :: ptask_tail*]',
            '~$recorded_runtime_snapshot_valid(S_final_later,$eager_fatal_history(S_final_later,pdestructionfatal_later),pdestructionfatal_later)']
        for label, change in [
            ('selection', '.SELECTION = eps'), ('nonce', '.SELECTION = (S.SELECTSEQ)'),
            ('kind', '.KIND = INTRINSIC_USER_ERROR'), ('site', '.SITE = (' + echo + ')'),
            ('line', '.LINE = $(pconfigcall.LINE + 1)'), ('index', '.INDEX = 1'),
            ('owner', '.OWNER = (n_object)'), ('named', '.NAMED = true'),
            ('pack', '.PACKS = [{INDEX 0, SITE pconfigcall.SITE, LINE pconfigcall.LINE, ARRAY 0, ITEMS eps}]'),
            ('message', '.SENT = [NAMED_SENT (KNOWN (PSTRING_CARRIER INTERNED_STRING ($ptascii("other")))),NAMED_SENT (KNOWN (PINT 256))]'),
            ('carrier', '.SENT = [NAMED_SENT (KNOWN (PSTRING_CARRIER (REQUEST_STRING (|S.STRINGDATA|)) ($ptascii("late")))),NAMED_SENT (KNOWN (PINT 256))]'),
            ('coercion', '.SENT = [NAMED_SENT (KNOWN pvalue_message),NAMED_SENT (KNOWN (PSTRING ($ptascii("256"))))]')]:
            checks += ['pconfigcall_' + label + ' = pconfigcall[' + change + ']',
                '~$recorded_runtime_call_valid(S,pconfigcall_' + label + ')']
        for label, cfg, index in [('site', 'pconfigcall_site', 'n_record'),
                ('nonce', 'pconfigcall_nonce', 'n_record'), ('index', 'pconfigcall', '(|S.DECLARATIONS|)')]:
            checks += ['pdeclaration_' + label + '* = S.DECLARATIONS ++ [PDRECORDEDCALLFATAL ' + cfg + ' pdeclcause ' + index + ']',
                'pdestructionfatal_' + label + ' = pdestructionfatal_new[.DECLARATIONS = pdeclaration_' + label + '*]',
                'pdestructioncleanup_' + label + ' = pdestructioncleanup_new[.SOURCE = DESTRUCTOR_FATAL pdestructionfatal_' + label + ']',
                '~$call_descriptors_valid(S_final[.DECLARATIONS = pdeclaration_' + label + '*][.DESTRUCTION.ABANDONED = [pdestructioncleanup_old,pdestructioncleanup_' + label + ']])']
        checks += ['pdeclaration_fixed* = S.DECLARATIONS ++ [PDRECORDEDFATAL pconfigcall.SITE pdeclcause n_record]',
            '~$declaration_history_valid(S_final[.DECLARATIONS = pdeclaration_fixed*])',
            'pdestructionfatal_omitted = pdestructionfatal_new[.DECLARATIONS = S.DECLARATIONS]',
            'pdestructioncleanup_omitted = pdestructioncleanup_new[.SOURCE = DESTRUCTOR_FATAL pdestructionfatal_omitted]',
            '~$recorded_runtime_snapshot_valid(S_final,$eager_fatal_history(S_final,pdestructionfatal_omitted),pdestructionfatal_omitted)',
            '~$call_descriptors_valid(S_final[.DESTRUCTION.ABANDONED = [pdestructioncleanup_old,pdestructioncleanup_new,pdestructioncleanup_omitted]])',
            'pdestructionfatal_fresh = pdestructionfatal_omitted[.COMPLETION = FATAL ($ptascii("late")) 11][.ERRORORIGIN = (pconfigcall.SITE)][.FROZEN = REQUESTFATAL ($ptascii("Error")) ($ptascii("late")) 11]',
            'pdestructioncleanup_fresh = pdestructioncleanup_new[.SOURCE = DESTRUCTOR_FATAL pdestructionfatal_fresh]',
            '~$recorded_runtime_snapshot_valid(S_final,$eager_fatal_history(S_final,pdestructionfatal_fresh),pdestructionfatal_fresh)',
            '~$call_descriptors_valid(S_final[.DESTRUCTION.ABANDONED = [pdestructioncleanup_old,pdestructioncleanup_new,pdestructioncleanup_fresh]])']
        for label, change in [
            ('phase', '.FRAME.TODO = (ERROR_TRIGGER_PHASE pconfigcall 2) :: ptask_tail*'),
            ('level', '.FRAME.TODO = (ERROR_TRIGGER_PHASE pconfigcall_warning 1) :: ptask_tail*'),
            ('origin', '.ERRORORIGIN = (PORIGIN 0 eps)'),
            ('tuple', '.COMPLETION = FATAL ($ptascii("late")) 11][.FROZEN = REQUESTFATAL ($ptascii("Error")) ($ptascii("late")) 11')]:
            checks += ['pdestructionfatal_' + label + ' = pdestructionfatal_new[' + change + ']',
                'pdestructioncleanup_' + label + ' = pdestructioncleanup_new[.SOURCE = DESTRUCTOR_FATAL pdestructionfatal_' + label + ']',
                '~$call_descriptors_valid(S_final[.DESTRUCTION.ABANDONED = [pdestructioncleanup_old,pdestructioncleanup_' + label + ']])']
        (out / 'protocol.watsup').write_text(PREFIX + '\ndec $main() : bool\ndef $main() = true\n' + ''.join('  -- if ' + item + '\n' for item in checks))
        (out / 'assertions.json').write_text(json.dumps(checks, indent=2) + '\n')
    finally:
        if adapter:
            adapter.close()
        frontend.close()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--phase', choices=['fixtures', 'check'], required=True)
    parser.add_argument('--sources', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    out, sources = args.output.resolve(), args.sources.resolve()
    case = sources.joinpath(*CASE)
    paths = [Path(__file__), Path(source.__file__), Path(fatal.__file__), Path(retirement.__file__),
        ROOT / 'tests/semantics/recorded_worker.py', ROOT / 'tests/semantics/_build/default/numeric_runner.exe',
        ROOT / 'frontend/target.php', ROOT / 'adapter/wire.ml', case.parent / 'run.py', case.parent / 'report.json',
        *sorted(case.glob('*.php')), *[case / 'native' / name for name in ['stdout', 'stderr', 'process.json', 'command.json']]]
    if args.phase == 'check':
        paths += [out / 'protocol.watsup', out / 'assertions.json']
    pins = lambda: dict(inputs.inputs(), **{str(path): hashlib.sha256(path.read_bytes()).hexdigest() for path in paths})
    before = pins()
    label = args.phase
    assert not (out / (label + '-report.json')).exists()
    if args.phase == 'check':
        assert not (out / label).exists()
    report = {'phase': args.phase, 'revision': subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip(),
        'semantic_diff_sha256': hashlib.sha256(subprocess.check_output(['git', 'diff', 'HEAD', '--', 'spec/semantics'], cwd=ROOT)).hexdigest(),
        'module_count': len(json.loads((ROOT / 'spec/semantics/modules.json').read_text())),
        'inputs': before, 'profile': types.PROFILE, 'environment': {'LC_ALL': 'C', 'TZ': 'UTC'},
        'sl_timeout': 90, 'result': 'fail', 'runtime_assertions': 0}
    try:
        if args.phase == 'fixtures':
            prepare(out, sources)
            report['result'] = 'pass'
        else:
            modules = [str(ROOT / name) for name in json.loads((ROOT / 'spec/semantics/modules.json').read_text())]
            result = process([str(ROOT / 'tests/semantics/_build/default/numeric_runner.exe'), '--sl', *modules, str(out / 'protocol.watsup')], out / label, 90, ROOT)
            passed = result.returncode == 0 and result.stdout == b'true\n' and not result.stderr
            report['result'] = 'pass' if passed else 'fail'
            report['runtime_assertions'] = len(json.loads((out / 'assertions.json').read_text())) if passed else 0
    finally:
        report['stable_inputs'] = before == pins()
        if not report['stable_inputs']:
            report['result'] = 'fail'
            report['runtime_assertions'] = 0
        (out / (label + '-report.json')).write_text(json.dumps(report, indent=2) + '\n')
    return report['result'] == 'pass'


if __name__ == '__main__':
    raise SystemExit(0 if main() else 1)
