#!/usr/bin/env python3
"""Generated FINAL return-TypeErrors retain real native owners through reporting."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import tempfile
import time

from recorded_worker import Worker
import output_api_failure_sources as common
import output_deprecation_warning_review_state as runner
import output_final_return_type_sources as sources

ROOT = Path(__file__).resolve().parents[2]
MESSAGE = b'T::__toString(): Return value must be of type string, int returned'
CASES = {'core': sources.STRICT, 'weak': sources.CASES['weak-return-coercion'],
         'catch': sources.CATCH, 'override': sources.OVERRIDE, 'cleanup': sources.CLEANUP}
PREFIX = runner.PREFIX.split('dec $dp_phase', 1)[0] + r'''
dec $rt_normal(ptask*) : pobobjectreturn?
def $rt_normal((STRINGIFY_RESULT n porigin 0) :: (OB_USER_OBJECT_STRING pobobjectreturn) :: ptask_tail*) = (pobobjectreturn)
  -- if ptask_tail* = pobobjectreturn.TAIL
def $rt_normal((OB_USER_OBJECT_RETURN pobobjectreturn poperand) :: ptask_tail*) = (pobobjectreturn)
  -- if ptask_tail* = pobobjectreturn.TAIL
def $rt_normal(ptask*) = eps -- otherwise
dec $rt_result(pstate, pobobjectreturn) : preqbytes?
def $rt_result(S, pobobjectreturn) = $string_bytes(pvalue)
  -- if pobobjectreturn.RETURNED = (KNOWN pvalue)
def $rt_result(S, pobobjectreturn) = $string_bytes(pvalue)
  -- if pobobjectreturn.RETURNED = eps
  -- if S.RESULT = KNOWN pvalue
def $rt_result(S, pobobjectreturn) = eps -- otherwise
dec $dp_phase(pstate, nat) : bool
def $dp_phase(S, 0) = true
  -- if S.TODO = (RETURN_VALUE z) :: ptask_tail*
  -- if S.RESULT = KNOWN (PINT 42)
  -- if S.CURRENT = (pcallcontext)
  -- if S.FRAMES = [pframe]
  -- if pframe.TODO = (STRINGIFY_RESULT n porigin 0) :: (OB_USER_OBJECT_STRING pobobjectreturn) :: ptask_native*
  -- if pobobjectreturn.INVOKE.CALL = OB_FINAL pobdrain
def $dp_phase(S, 1) = true
  -- if S.TODO = (DESTRUCTOR_FRAME_EXIT pdestructionframe) :: (OUTPUT_FINAL_OBJECT_CV pobobjectreturn) :: ptask_tail*
  -- if pdestructionframe.PENDING = (n)
def $dp_phase(S, 2) = true
  -- if S.TODO = [OUTPUT_FINAL_DEACTIVATE pobdeactivate]
  -- if pobdeactivate.INDEX = 0
def $dp_phase(S, 3) = true
  -- if S.TODO = (CATCH_BIND porigin n_index n) :: ptask_tail*
  -- if S.CURRENT = (pcallcontext)
  -- if S.FRAMES = [pframe]
def $dp_phase(S, 4) = true
  -- if S.TODO = (RETURN_UNWIND (KNOWN pvalue) porigin?) :: ptask_tail*
  -- if $string_bytes(pvalue) = ($ptascii("H"))
  -- if S.CURRENT = (pcallcontext)
  -- if S.FRAMES = [pframe]
def $dp_phase(S, 5) = true
  -- if S.CURRENT = eps /\ S.FRAMES = eps
  -- if $rt_normal(S.TODO) =/= eps
def $dp_phase(S, 6) = true
  -- if S.TODO = (DESTRUCTOR_ENTER pdestructorcall) :: ptask_tail*
  -- if pdestructorcall.FRAME = (pdestructionframe)
  -- if pdestructionframe.PENDING = (n)
def $dp_phase(S, n) = false -- otherwise
''' + 'dec $dp_seek' + runner.PREFIX.split('dec $dp_seek', 1)[1]
OVERRIDE_PREFIX = PREFIX.replace('def $dp_phase(S, n) = false -- otherwise', r'''
def $dp_phase(S, 7) = true
  -- if S.TODO = [RETURN_UNWIND (KNOWN pvalue) porigin?]
  -- if $string_bytes(pvalue) = ($ptascii("H"))
  -- if S.CURRENT = (pcallcontext)
  -- if S.FRAMES = [pframe]
def $dp_phase(S, n) = false -- otherwise''')


def value(data):
    return runner.bytes_expr(data)


def public(state):
    return r' /\ '.join([f'$call_descriptors_valid({state})', f'$heap_valid($heap_graph({state}))',
                         f'$output_state_valid({state})', f'$destruction_state_valid({state})'])


def seek(target, start, phase):
    return [f'{target}_found = $dp_seek({start}, {phase}, 1024)',
            f'{target}_found.COMPLETION = NORMAL \\/ {target}_found.COMPLETION = BUDGET',
            f'{target} = {target}_found[.COMPLETION = NORMAL]']


def start(fixture, path):
    return ['S_initial = $php_file_run(' + fixture + ', 0, ' + value(os.fsencode(path)) + ', ' + value(os.fsencode(path.parent)) + ')',
            'S_initial.COMPLETION = BUDGET', *seek('S', 'S_initial', 0),
            'S.TODO = (RETURN_VALUE z) :: ptask_tail*',
            'S.CURRENT = (pcallcontext)', 'S.FRAMES = [pframe]',
            'pframe.TODO = (STRINGIFY_RESULT n_object porigin_site 0) :: (OB_USER_OBJECT_STRING pobobjectreturn) :: ptask_native*',
            '$function_at($all_functions(S), pcallcontext.FUNCTION) = (pfunction)',
            'S.ORIGIN = (porigin_return)']


def capture():
    return ['S_request = $typed_return_value(S, z)',
            'S_generated = $throwable_transition(S, S_request)',
            'S_generated.COMPLETION = THROWING n_exception',
            'S_capture_found = $drive_steps(S, 1)', 'S_capture_found.COMPLETION = BUDGET',
            'S_capture = S_capture_found[.COMPLETION = NORMAL]',
            'S_capture.TODO = (THROW_SEARCH n_exception) :: ptask_tail*',
            'S_capture.FRAMES = [pframe_capture]',
            'pframe_capture.TODO = (STRINGIFY_RESULT n_object porigin_site 0) :: (OB_USER_OBJECT_STRING pobobjectreturn_capture) :: ptask_native*',
            'pobobjectreturn_capture.SOURCE = (OBJECT_RETURN_ERROR pobreturnerror)']


def core(fixture, path):
    bindings = start(fixture, path) + capture() + [
        'S_pending_bad = S_capture[.TODO = (THROW_SEARCH n_object) :: ptask_tail*]',
        'pobreturnerror_site = pobreturnerror[.SITE = pfunction.ORIGIN]',
        'pobreturnerror_line = pobreturnerror[.LINE = $(pobreturnerror.LINE + 1)]',
        'pobreturnerror_message = pobreturnerror[.MESSAGE = $ptascii("wrong")]',
        'pobreturnerror_object = pobreturnerror[.OBJECT = n_object]',
        'pobobjectreturn_message = pobobjectreturn_capture[.SOURCE = (OBJECT_RETURN_ERROR pobreturnerror_message)]',
        'S_context_message = S_capture[.FRAMES = [pframe_capture[.TODO = (STRINGIFY_RESULT n_object porigin_site 0) :: (OB_USER_OBJECT_STRING pobobjectreturn_message) :: ptask_native*]]]',
        'S_context_code = $throwable_constructor_field(S_capture, n_exception, "code", PINT 1)',
        'S_context_previous = $throwable_set_previous_id(S_capture, n_exception, (n_exception))',
        'S_owned = S[.TODO = S.TODO ++ [THROW_SEARCH n_object]]',
        'S_owned_request = $typed_return_value(S_owned, z)',
        'S_owned_generated = $throwable_transition(S_owned, S_owned_request)',
        *seek('S_exit', 'S_capture', 1),
        'S_exit.TODO = [DESTRUCTOR_FRAME_EXIT pdestructionframe, OUTPUT_FINAL_OBJECT_CV pobobjectreturn_capture, OUTPUT_DRAIN pobdrain]',
        'S_zero = $drive_steps(S_exit, 0)',
        'S_report_found = $drive_steps(S_exit, 1)', 'S_report_found.COMPLETION = BUDGET',
        'S_report = S_report_found[.COMPLETION = NORMAL]',
        'S_report.TODO = [OUTPUT_FINAL_PENDING pobdeactivate n_exception true]',
        'S_report.DESTRUCTION.ABANDONED = [pdestructioncleanup]',
        *seek('S_retired', 'S_report', 2),
        'S_retired.DESTRUCTION.ABANDONED = [pdestructioncleanup_retired]',
        'pobobjectreturn_site = pobobjectreturn_capture[.SOURCE = (OBJECT_RETURN_ERROR pobreturnerror_site)]',
        'pdestructioncleanup_site = pdestructioncleanup_retired[.SOURCE = OUTPUT_FINAL_OBJECT_THROW pobobjectreturn_site pobdeactivate pobreturnerror.SITE n_exception]',
        'S_receipt_site = S_retired[.DESTRUCTION.ABANDONED = [pdestructioncleanup_site]]',
    ]
    fatal = (b'Fatal error: Uncaught TypeError: ' + MESSAGE + b' in ' + os.fsencode(path) + b':7\nStack trace:\n'
             b'#0 [internal function]: T->__toString()\n#1 {main}\n  thrown in ' + os.fsencode(path) + b' on line 7\n')
    checks = [
        ('genuine request and nonowning capture', 'S_request.COMPLETION = THROWN "TypeError" ' + value(MESSAGE) + r' 7 /\ $ob_object_return_error_capture(S, S_generated) = ((pobobjectreturn, pobreturnerror)) /\ pobreturnerror = {SITE porigin_return, OBJECT n_exception, MESSAGE ' + value(MESSAGE) + r', LINE 7} /\ $ob_object_source_birth(pobobjectreturn_capture.SOURCE) = eps /\ $task_nodes(OB_USER_OBJECT_STRING pobobjectreturn_capture) = $task_nodes(OB_USER_OBJECT_STRING pobobjectreturn) /\ $heap_count(HOBJECT n_object, $machine_roots(S_capture)) = 2 /\ $heap_count(HOBJECT n_exception, $machine_roots(S_capture)) = 1'),
        ('producer and normalized fact refusals', r'$ob_object_final_cv_method(S_owned) = (pobobjectreturn) /\ $call_current_valid(S_owned) /\ $call_task_valid(S_owned, RETURN_VALUE z) /\ S_owned_generated = S_generated[.TODO = ptask_tail* ++ [THROW_SEARCH n_object]] /\ $ob_object_return_error_capture(S_owned, S_owned_generated) = eps /\ $ob_object_return_error_capture(S, S_generated[.COMPLETION = THROWING n_object]) = eps /\ ~$ob_object_return_error_source(S_capture, pfunction, pobreturnerror_site) /\ ~$ob_object_return_error_source(S_capture, pfunction, pobreturnerror_line) /\ ~$ob_object_return_error_source(S_capture, pfunction, pobreturnerror_object) /\ ~$ob_object_return_error_live(S_capture, pobreturnerror_message) /\ $ob_object_final_saved_context(S_pending_bad) = eps'),
        ('pending admission checks live normalized fields', r'$ob_object_final_saved_context(S_capture) = ((pcallcontext, pobobjectreturn_capture)) /\ $ob_object_source_native_pending(pobobjectreturn_message.SOURCE) = ((pobreturnerror.SITE, n_exception)) /\ $heap_graph(S_context_message) = $heap_graph(S_capture) /\ $ob_object_final_saved_context(S_context_message) = eps /\ $throwable_live(S_context_code, n_exception) /\ $throwable_field(S_context_code, n_exception, "code") = PINT 1 /\ $ob_object_final_saved_context(S_context_code) = eps /\ $throwable_field(S_context_previous, n_exception, "previous") = POBJECT n_exception /\ $ob_object_final_saved_context(S_context_previous) = eps'),
        ('public pending and exact native owners', public('S_capture') + r' /\ $ob_object_source_native_pending(pobobjectreturn_capture.SOURCE) = ((pobreturnerror.SITE, n_exception)) /\ $output_final_cv_unwind(S_capture) /\ $throwable_field(S_capture, n_exception, "previous") = PNULL'),
        ('real null-C barrier and budget', r'S_exit.CURRENT = eps /\ S_exit.FRAMES = eps /\ S_exit.ORIGIN = eps /\ pdestructionframe.CALLER = eps /\ pdestructionframe.ORIGIN = eps /\ pdestructionframe.FUNCTION = pfunction.ORIGIN /\ pdestructionframe.PENDING = (n_exception) /\ pdestructionframe.VALUE = KNOWN PNULL /\ $heap_count(HOBJECT n_object, $machine_roots(S_exit)) = 2 /\ $heap_count(HOBJECT n_exception, $machine_roots(S_exit)) = 1 /\ S_zero = S_exit[.COMPLETION = BUDGET] /\ ' + public('S_exit')),
        ('actual TypeError fatal before cast release', 'S_report.EVENTS = [OUTPUT ([80]), STDERR ' + value(fatal) + r'] /\ pobdeactivate.COMPLETION = REQUESTFATAL ($ptascii("TypeError")) ' + value(MESSAGE) + r' 7 /\ $heap_count(HOBJECT n_object, $machine_roots(S_report)) = 2 /\ $heap_count(HOBJECT n_exception, $machine_roots(S_report)) = 1 /\ $eager_cleanup_valid(S_report, pdestructioncleanup) /\ ' + public('S_report')),
        ('retired error leaves only authenticated cast receipt', r'~((HOBJECT n_exception) <- S_retired.ALLOCATIONS) /\ $heap_count(HOBJECT n_exception, $machine_roots(S_retired)) = 0 /\ $heap_count(HOBJECT n_object, $machine_roots(S_retired)) = 2 /\ $eager_cleanup_valid(S_retired, pdestructioncleanup_retired) /\ ~$eager_cleanup_valid(S_receipt_site, pdestructioncleanup_site) /\ S_retired.EVENTS = S_report.EVENTS /\ ' + public('S_retired')),
    ]
    return bindings, checks


def clearing(name, fixture, path):
    bindings = start(fixture, path) + capture()
    checks = []
    if name == 'catch':
        bindings += seek('S_caught', 'S_capture', 3) + [
            'S_caught.TODO = (CATCH_BIND porigin_try n_index n_exception) :: ptask_catch*',
            'S_caught.FRAMES = [pframe_caught]',
            'pframe_caught.TODO = (STRINGIFY_RESULT n_object porigin_site 0) :: (OB_USER_OBJECT_STRING pobobjectreturn_caught) :: ptask_native*']
        checks.append(('actual catch consumes generated history', r'pobobjectreturn_caught.SOURCE = eps /\ $heap_count(HOBJECT n_exception, $machine_roots(S_caught)) = 1 /\ ' + public('S_caught')))
        origin = 'S_caught'
    else:
        origin = 'S_capture'
    bindings += seek('S_H', origin, 7 if name == 'override' else 4) + [
        'S_H.FRAMES = [pframe_H]',
        'pframe_H.TODO = (STRINGIFY_RESULT n_object porigin_site 0) :: (OB_USER_OBJECT_STRING pobobjectreturn_H) :: ptask_native*',
        *seek('S_restored', 'S_H', 5), '$rt_normal(S_restored.TODO) = (pobobjectreturn_restored)']
    if name == 'override':
        checks.append(('finally consumes history at real owner drop', r'pobobjectreturn_H.SOURCE = eps /\ ~((HOBJECT n_exception) <- S_H.ALLOCATIONS) /\ $heap_count(HOBJECT n_exception, $machine_roots(S_H)) = 0 /\ ' + public('S_H')))
    checks.append(('normal H publication retires error and retains retval', r'pobobjectreturn_H.SOURCE = eps /\ pobobjectreturn_restored.SOURCE = eps /\ $rt_result(S_restored, pobobjectreturn_restored) = ($ptascii("H")) /\ ~((HOBJECT n_exception) <- S_restored.ALLOCATIONS) /\ $heap_count(HOBJECT n_object, $machine_roots(S_restored)) = 1 /\ S_restored.EVENTS = [OUTPUT ([80])] /\ ' + public('S_restored')))
    return bindings, checks


def cleanup(fixture, path):
    bindings = start(fixture, path) + capture() + [
        '$lookup(S.ENV, $ptascii("d")) = (n_cell)', 'S.STORE[n_cell] = DEFINED (POBJECT n_local)',
        *seek('S_entry', 'S_capture', 6),
        'S_entry.TODO = (DESTRUCTOR_ENTER pdestructorcall) :: ptask_entry*',
        'S_entered_found = $drive_steps(S_entry, 1)', 'S_entered_found.COMPLETION = BUDGET',
        'S_entered = S_entered_found[.COMPLETION = NORMAL]', 'S_entered.CURRENT = (pcallcontext_local)',
        *seek('S_exit', 'S_entered', 1),
        'S_exit.TODO = (DESTRUCTOR_FRAME_EXIT pdestructionframe) :: (OUTPUT_FINAL_OBJECT_CV pobobjectreturn_capture) :: ptask_native_exit*']
    checks = [
        ('normal local destructor enters after actual null-C restore', r'S_entry.CURRENT = eps /\ ~pdestructorcall.USER /\ pdestructorcall.CALLER = eps /\ pdestructorcall.SITE = eps /\ pdestructorcall.OBJECT = n_local /\ pcallcontext_local.CALLSITE = eps /\ pcallcontext_local.LINE = $(-1) /\ $heap_count(HOBJECT n_object, $machine_roots(S_entered)) = 2 /\ $heap_count(HOBJECT n_local, $machine_roots(S_entered)) = 2 /\ $heap_count(HOBJECT n_exception, $machine_roots(S_entered)) = 1 /\ ' + public('S_entered')),
        ('warning and local retirement precede original pending barrier', r'S_exit.EVENTS = [OUTPUT ([80]), WARNING ($ptascii("missing")) 4] /\ ~((HOBJECT n_local) <- S_exit.ALLOCATIONS) /\ pdestructionframe.PENDING = (n_exception) /\ pdestructionframe.FUNCTION = pfunction.ORIGIN /\ pobreturnerror.LINE = 9 /\ $throwable_field(S_exit, n_exception, "previous") = PNULL /\ $heap_count(HOBJECT n_object, $machine_roots(S_exit)) = 2 /\ $heap_count(HOBJECT n_exception, $machine_roots(S_exit)) = 1 /\ ' + public('S_exit')),
    ]
    return bindings, checks


def weak(fixture, path):
    bindings = start(fixture, path) + ['S_value = $typed_return_value(S, z)',
                                     'S_value.RESULT = KNOWN pvalue_text',
                                     *seek('S_restored', 'S', 5),
                                     '$rt_normal(S_restored.TODO) = (pobobjectreturn_restored)']
    checks = [
        ('weak scalar return creates no generated error certificate', r'~pfunction.CODE.STRICT /\ S_value.COMPLETION = NORMAL /\ $string_bytes(pvalue_text) = ($ptascii("42")) /\ $ob_object_return_error_capture(S, S_value) = eps /\ pobobjectreturn.SOURCE = eps'),
        ('normal weak publication retains its real retval owner', r'$rt_result(S_restored, pobobjectreturn_restored) = ($ptascii("42")) /\ pobobjectreturn_restored.SOURCE = eps /\ |S_restored.OBJECTS| = 1 /\ $heap_count(HOBJECT n_object, $machine_roots(S_restored)) = 1 /\ S_restored.EVENTS = [OUTPUT ([80])] /\ ' + public('S_restored')),
    ]
    return bindings, checks


def fingerprint(fixture):
    paths = [ROOT / name for name in json.loads((ROOT / 'spec/semantics/modules.json').read_text())]
    paths += [Path(__file__), ROOT / 'tests/semantics/output_final_return_type_sources.py',
              ROOT / 'tests/semantics/profile.json', ROOT / '.tools/php/bin/php', ROOT / '.tools/php-file.so',
              ROOT / '_build/default/adapter/main.exe', ROOT / 'tests/semantics/_build/default/numeric_runner.exe', fixture]
    return {str(path.relative_to(ROOT)) if path.is_relative_to(ROOT) else str(path): common.sha(path) for path in paths}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--stage', choices=['all', *CASES], default='all')
    parser.add_argument('--output', type=Path)
    parser.add_argument('--checked-root', type=Path, help='optional checked-AST cache from this review')
    parser.add_argument('--native-root', type=Path, help='optional frozen strict/weak source paths')
    parser.add_argument('--prepare-only', action='store_true')
    args = parser.parse_args()
    out = args.output or Path(tempfile.mkdtemp(prefix='output-final-return-type-review-', dir=ROOT / '.tools'))
    out.mkdir(parents=True, exist_ok=True)
    report = {'revision': subprocess.check_output(['git', '-C', str(ROOT), 'rev-parse', 'HEAD']).decode().strip(),
              'profile': common.PROFILE, 'native_agreement_credit': 0, 'records': [], 'passed': False}
    try:
        for name in CASES if args.stage == 'all' else [args.stage]:
            directory = out / name; directory.mkdir()
            source = CASES[name]
            if args.native_root and name in ('core', 'weak'):
                path = args.native_root / ('native-01' if name == 'core' else 'native-02') / 'source.php'
                assert path.read_bytes() == source
            elif args.checked_root and name != 'core':
                path = args.checked_root / 'control-preparation-01' / name / 'source.php'
                assert path.read_bytes() == source
            else:
                path = directory / 'source.php'; path.write_bytes(source)
            if args.checked_root:
                cached = args.checked_root / ('baseline-01/checked.json' if name == 'core' else f'control-preparation-01/{name}/checked.json')
                checked = json.loads(cached.read_text())
            else:
                frontend = Worker([str(ROOT / '.tools/php/bin/php'), '-n', '-d',
                                   'extension=' + str(ROOT / '.tools/php-file.so'), str(ROOT / 'frontend/worker.php')], directory / 'frontend')
                try:
                    parsed = frontend.request({'op': 'parse', 'source': common.base64.b64encode(source).decode()})
                finally:
                    frontend.close()
                adapter = Worker([str(ROOT / '_build/default/adapter/main.exe'), str(ROOT)], directory / 'adapter')
                try:
                    checked = adapter.request({'op': 'check', 'ast': parsed['ast'], 'fixture': True})
                finally:
                    adapter.close()
            (directory / 'checked.json').write_text(json.dumps(checked) + '\n')
            emit = core if name == 'core' else weak if name == 'weak' else cleanup if name == 'cleanup' else lambda f, p: clearing(name, f, p)
            bindings, checks = emit(checked['fixture'], path)
            fixture = directory / 'state.watsup'
            prefix = OVERRIDE_PREFIX if name == 'override' else PREFIX
            fixture.write_text(prefix + '\ndec $main() : bool*\ndef $main() = [' + ', '.join('(' + condition + ')' for _, condition in checks) + ']\n' + ''.join('  -- if ' + binding + '\n' for binding in bindings))
            record = {'id': name, 'source_sha256': hashlib.sha256(source).hexdigest(), 'fixture_sha256': common.sha(fixture),
                      'groups': [label for label, _ in checks], 'before': fingerprint(fixture), 'passed': False}
            report['records'].append(record)
            if args.prepare_only:
                record.update(prepared=True, semantic_execution_credit=0)
                continue
            modules = json.loads((ROOT / 'spec/semantics/modules.json').read_text())
            started = time.monotonic()
            try:
                result = common.run([str(ROOT / 'tests/semantics/_build/default/numeric_runner.exe'), '--sl',
                                     *[str(ROOT / module) for module in modules], str(fixture)], directory, 'state', 300)
            finally:
                record['seconds'] = round(time.monotonic() - started, 3)
                record['after'] = fingerprint(fixture)
            observed = re.findall(rb'true|false', result.stdout)
            record['observed'] = [item == b'true' for item in observed]
            assert result.returncode == 0 and not result.stderr and record['observed'] == [True] * len(checks), (result.returncode, result.stderr, record['observed'])
            assert record['before'] == record['after'], 'watched inputs changed'
            record['passed'] = True
        assert report['records'], 'no fixture selected'
        report['passed'] = not args.prepare_only and all(record['passed'] for record in report['records'])
        report['prepared'] = args.prepare_only
    except BaseException as error:
        report['failure'] = {'type': type(error).__name__, 'message': str(error)}
        raise
    finally:
        (out / 'report.json').write_text(json.dumps(report, indent=2) + '\n')
        print(out / 'report.json', report['passed'], flush=True)


if __name__ == '__main__':
    main()
