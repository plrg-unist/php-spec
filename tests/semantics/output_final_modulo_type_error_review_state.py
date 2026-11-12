#!/usr/bin/env python3
"""Native quiet modulo TypeErrors retain their actual source and C0 ownership."""
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
import output_final_return_type_review_state as prior
import output_final_modulo_type_error_sources as sources

ROOT = Path(__file__).resolve().parents[2]
MESSAGE = b'Unsupported operand types: int % string'
CASES = {'core': sources.INVALID, 'normal': sources.NORMAL,
         'catch': sources.CATCH, 'override': sources.OVERRIDE, 'cleanup': sources.CLEANUP}
_begin = prior.OVERRIDE_PREFIX.index('def $dp_phase(S, 0)')
_end = prior.OVERRIDE_PREFIX.index('def $dp_phase(S, 1)')
PREFIX = prior.OVERRIDE_PREFIX[:_begin] + r'''
def $dp_phase(S, 0) = true
  -- if S.TODO = (BINARY_RIGHT MODULO (KNOWN (PINT 1)) z) :: ptask_tail*
  -- if S.CURRENT = (pcallcontext)
  -- if pcallcontext.FUNCTION = porigin
  -- if S.FRAMES = [pframe]
  -- if pframe.TODO = (STRINGIFY_RESULT n porigin_site 0) :: (OB_USER_OBJECT_STRING pobobjectreturn) :: ptask_native*
  -- if pobobjectreturn.INVOKE.CALL = OB_FINAL pobdrain
''' + prior.OVERRIDE_PREFIX[_end:]
PREFIX = PREFIX.replace('def $dp_phase(S, n) = false -- otherwise', r'''
def $dp_phase(S, 8) = true
  -- if S.TODO = [THROW_SEARCH n]
  -- if S.CURRENT = (pcallcontext)
  -- if S.FRAMES = [pframe]
def $dp_phase(S, n) = false -- otherwise''') + r'''
dec $dz_raw(pstate) : pstate
def $dz_raw(S) = S_next
  -- PhpStep: S ~> S_next
dec $dz_request(pstate, int) : pstate
def $dz_request(S, z) = S_result[.HELD = S.HELD]
  -- if S.TODO = (BINARY_RIGHT MODULO poperand_left z) :: ptask_tail*
  -- if S_left = $resolve_at($hold_task_inputs(S), poperand_left, z)
  -- if S_left.RESULT = KNOWN pvalue_left
  -- if S_right = $resolve_at(S_left, S.RESULT, z)
  -- if S_right.RESULT = KNOWN pvalue_right
  -- if S_result = $binary_source_apply(S_right, MODULO, poperand_left, S.RESULT, pvalue_left, pvalue_right, z)
dec $dz_other(pstate, int) : pstate
def $dz_other(S, z) = $binary_apply(S[.TODO = ptask_tail*], ADD, PINT 1, pvalue_right, z)
  -- if S.TODO = (BINARY_RIGHT ADD (KNOWN (PINT 1)) z) :: ptask_tail*
  -- if S.RESULT = KNOWN pvalue_right
'''



NORMAL_EXTRA = r'''
dec $dn_phase(pstate, nat) : bool
def $dn_phase(S, 0) = true
  -- if S.TODO = (RETURN_VALUE z) :: ptask_tail*
  -- if S.CURRENT = (pcallcontext)
  -- if S.FRAMES = [pframe]
  -- if pframe.TODO = (STRINGIFY_RESULT n porigin_site 0) :: (OB_USER_OBJECT_STRING pobobjectreturn) :: ptask_native*
  -- if pobobjectreturn.INVOKE.CALL = OB_FINAL pobdrain
def $dn_phase(S, 5) = $dp_phase(S, 5)
def $dn_phase(S, n) = false -- otherwise
dec $dn_seek(pstate, nat, nat) : pstate
def $dn_seek(S, n_phase, n) = S -- if S.COMPLETION =/= NORMAL /\ S.COMPLETION =/= BUDGET
def $dn_seek(S, n_phase, n) = S -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET -- if $dn_phase(S, n_phase)
def $dn_seek(S, n_phase, 0) = S -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET -- if ~$dn_phase(S, n_phase)
def $dn_seek(S, n_phase, n) = $dn_seek($drive_steps(S[.COMPLETION = NORMAL], 1), n_phase, $nabs($(n - 1)))
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
  -- if ~$dn_phase(S, n_phase) /\ $(n > 0)

'''


def start(fixture, path, phase=0):
    return ['S_initial = $php_file_run(' + fixture + ', 0, ' + prior.value(os.fsencode(path)) + ', ' + prior.value(os.fsencode(path.parent)) + ')',
            'S_initial.COMPLETION = BUDGET', *prior.seek('S', 'S_initial', phase),
            'S.CURRENT = (pcallcontext)', 'S.FRAMES = [pframe]',
            'pframe.TODO = (STRINGIFY_RESULT n_object porigin_site 0) :: (OB_USER_OBJECT_STRING pobobjectreturn) :: ptask_native*',
            '$function_at($all_functions(S), pcallcontext.FUNCTION) = (pfunction)']


def capture():
    return ['S.TODO = (BINARY_RIGHT MODULO (KNOWN (PINT 1)) z) :: ptask_tail*',
            'S.ORIGIN = (porigin_operator)', 'S.RESULT = KNOWN pvalue_right',
            'S_request = $dz_raw(S)', 'S_generated = $throwable_transition(S, S_request)',
            'S_generated.COMPLETION = THROWING n_exception',
            'S_capture_found = $drive_steps(S, 1)', 'S_capture_found.COMPLETION = BUDGET',
            'S_capture = S_capture_found[.COMPLETION = NORMAL]',
            'S_capture.TODO = (THROW_SEARCH n_exception) :: ptask_tail*',
            'S_capture.FRAMES = [pframe_capture]',
            'pframe_capture.TODO = (STRINGIFY_RESULT n_object porigin_site 0) :: (OB_USER_OBJECT_STRING pobobjectreturn_capture) :: ptask_native*',
            'pobobjectreturn_capture.SOURCE = (OBJECT_ARITHMETIC_TYPE_ERROR pobreturnerror)']


def core(fixture, path):
    bindings = start(fixture, path) + capture() + [
        'S.OBJECTS[n_object] = INSTANCE porigin_class',
        'pobreturnerror_site = pobreturnerror[.SITE = pfunction.ORIGIN]',
        'pobreturnerror_line = pobreturnerror[.LINE = $(pobreturnerror.LINE + 1)]',
        'pfunction_missing = pfunction[.CODE = pfunction.CODE[.EXPRESSIONS = eps]]',
        'pobreturnerror_message = pobreturnerror[.MESSAGE = $ptascii("wrong")]',
        'pobobjectreturn_message = pobobjectreturn_capture[.SOURCE = (OBJECT_ARITHMETIC_TYPE_ERROR pobreturnerror_message)]',
        'pobobjectreturn_tag = pobobjectreturn_capture[.SOURCE = (OBJECT_RETURN_ERROR pobreturnerror)]',
        'S_message = S_capture[.FRAMES = [pframe_capture[.TODO = (STRINGIFY_RESULT n_object porigin_site 0) :: (OB_USER_OBJECT_STRING pobobjectreturn_message) :: ptask_native*]]]',
        'S_tag = S_capture[.FRAMES = [pframe_capture[.TODO = (STRINGIFY_RESULT n_object porigin_site 0) :: (OB_USER_OBJECT_STRING pobobjectreturn_tag) :: ptask_native*]]]',
        'S_code = $throwable_constructor_field(S_capture, n_exception, "code", PINT 1)',
        'S_previous = $throwable_set_previous_id(S_capture, n_exception, (n_exception))',
        'S_owned = S[.TODO = S.TODO ++ [THROW_SEARCH n_object]]',
        'S_owned_next = $throwable_transition(S_owned, $dz_request(S_owned, z))',
        'S_operation = S[.TODO = (BINARY_RIGHT ADD (KNOWN (PINT 1)) z) :: ptask_tail*]',
        'S_operation_next = $throwable_transition(S_operation, $dz_other(S_operation, z))',
        'pobreturnerror_operation = pobreturnerror[.MESSAGE = $ptascii("Unsupported operand types: int + string")]',
        'S_string = S[.TODO = (BINARY_RIGHT MODULO (KNOWN (PSTRING ($ptascii("1")))) z) :: ptask_tail*]',
        'S_string_next = $throwable_transition(S_string, $dz_request(S_string, z))',
        'pobreturnerror_string = pobreturnerror[.MESSAGE = $ptascii("Unsupported operand types: string % string")]',
        'S_numeric = S[.RESULT = KNOWN (PSTRING ($ptascii("2")))]',
        'S_divzero = S[.RESULT = KNOWN (PINT 0)]',
        'S_divzero_next = $throwable_transition(S_divzero, $dz_request(S_divzero, z))',
        'pobreturnerror_divzero = pobreturnerror[.MESSAGE = $ptascii("Modulo by zero")]',
        'S_leading = S[.RESULT = KNOWN (PSTRING ($ptascii("2x")))]',
        'S_zero = $drive_steps(S_capture, 0)', *prior.seek('S_leave', 'S_capture', 8),
        'S_leave_zero = $drive_steps(S_leave, 0)',
        'S_stage_found = $drive_steps(S_leave, 1)', 'S_stage_found.COMPLETION = BUDGET',
        'S_stage = S_stage_found[.COMPLETION = NORMAL]',
        'S_stage.TODO = [DESTRUCTOR_RELEASE pdestructionrelease, DESTRUCTOR_FRAME_EXIT pdestructionframe, OUTPUT_FINAL_OBJECT_CV pobobjectreturn_capture, OUTPUT_DRAIN pobdrain]',
        'S_stage_zero = $drive_steps(S_stage, 0)',
        'S_exit_found = $drive_steps(S_stage, 1)', 'S_exit_found.COMPLETION = BUDGET',
        'S_exit = S_exit_found[.COMPLETION = NORMAL]',
        'S_exit.TODO = [DESTRUCTOR_FRAME_EXIT pdestructionframe, OUTPUT_FINAL_OBJECT_CV pobobjectreturn_capture, OUTPUT_DRAIN pobdrain]',
        'S_exit_zero = $drive_steps(S_exit, 0)',
        'S_report_found = $drive_steps(S_exit, 1)', 'S_report_found.COMPLETION = BUDGET',
        'S_report = S_report_found[.COMPLETION = NORMAL]',
        'S_report.TODO = [OUTPUT_FINAL_PENDING pobdeactivate n_exception true]',
        *prior.seek('S_retired', 'S_report', 2),
        'S_retired.DESTRUCTION.ABANDONED = [pdestructioncleanup]',
        'pobobjectreturn_site = pobobjectreturn_capture[.SOURCE = (OBJECT_ARITHMETIC_TYPE_ERROR pobreturnerror_site)]',
        'pdestructioncleanup_site = pdestructioncleanup[.SOURCE = OUTPUT_FINAL_OBJECT_THROW pobobjectreturn_site pobdeactivate pobreturnerror.SITE n_exception]',
        'S_receipt_site = S_retired[.DESTRUCTION.ABANDONED = [pdestructioncleanup_site]]']
    fatal = (b'Fatal error: Uncaught TypeError: ' + MESSAGE + b' in ' + os.fsencode(path) + b':6\nStack trace:\n'
             b'#0 [internal function]: T->__toString()\n#1 {main}\n  thrown in ' + os.fsencode(path) + b' on line 6\n')
    checks = [
        ('genuine modulo conversion mutates only scalar RESULT before exact materialization', 'S_request.COMPLETION = THROWN "TypeError" ' + prior.value(MESSAGE) + r' 6 /\ S_request = $dz_request(S, z) /\ $string_bytes(pvalue_right) = ($ptascii("X")) /\ $coerce_number(pvalue_right) = BADNUMBER /\ $value_nodes(pvalue_right) = eps /\ $base_nodes(S.BASE) = eps /\ S_request.EVENTS = S.EVENTS /\ $long_convertible(PINT 1) /\ ~$long_convertible(pvalue_right) /\ $integer_coerce(S, PINT 1, z) = S[.RESULT = KNOWN (PINT 1)] /\ S_request.RESULT = KNOWN (PINT 1) /\ z = 6 /\ S.CVS = eps /\ S.ENV = eps /\ pfunction.CVS = eps /\ $effective_method(S, porigin_class, $ptascii("__destruct"), |S.CLASSES|) = eps /\ $ob_object_arithmetic_type_error_capture(S, S_generated) = ((pobobjectreturn, pobreturnerror)) /\ pobreturnerror = {SITE porigin_operator, OBJECT n_exception, MESSAGE ' + prior.value(MESSAGE) + r', LINE 6} /\ $ob_object_arithmetic_type_error_source(S_capture, pfunction, pobreturnerror)'),
        ('operator source identity numeric and ownership refusals', r'$call_current_valid(S_owned) /\ S_owned_next = S_generated[.TODO = ptask_tail* ++ [THROW_SEARCH n_object]] /\ $ob_object_arithmetic_type_error_capture(S_owned, S_owned_next) = eps /\ $ob_object_arithmetic_type_error_capture(S_operation, S_operation_next) = eps /\ S_operation_next.COMPLETION = THROWING n_exception /\ $ob_object_arithmetic_type_error_source(S_operation_next, pfunction, pobreturnerror_operation) /\ $ob_object_return_error_live(S_operation_next, pobreturnerror_operation) /\ S_string_next.COMPLETION = THROWING n_exception /\ $ob_object_arithmetic_type_error_capture(S_string, S_string_next) = ((pobobjectreturn, pobreturnerror_string)) /\ $ob_object_arithmetic_type_error_source(S_string_next, pfunction, pobreturnerror_string) /\ $ob_object_return_error_live(S_string_next, pobreturnerror_string) /\ $ob_object_arithmetic_type_error_capture(S_numeric, S_generated) = eps /\ S_divzero_next.COMPLETION = THROWING n_exception /\ $ob_object_division_error_source(S_divzero_next, pfunction, pobreturnerror_divzero) /\ ~$ob_object_arithmetic_type_error_source(S_divzero_next, pfunction, pobreturnerror_divzero) /\ $ob_object_arithmetic_type_error_capture(S_divzero, S_divzero_next) = eps /\ $coerce_number(PSTRING ($ptascii("2x"))) = COERCED (NINT 2) true /\ $ob_object_arithmetic_type_error_capture(S_leading, S_generated) = eps /\ $ob_object_arithmetic_type_error_capture(S[.RESULT = KNOWN (POBJECT n_object)], S_generated) = eps /\ $ob_object_arithmetic_type_error_capture(S[.HELD = [HOBJECT n_object]], S_generated) = eps /\ $ob_object_arithmetic_type_error_capture(S[.BASE = BASE_VALUE (KNOWN (POBJECT n_object))], S_generated) = eps /\ $ob_object_arithmetic_type_error_capture(S, S_generated[.COMPLETION = NORMAL]) = eps /\ $ob_object_arithmetic_type_error_capture(S, S_generated[.COMPLETION = THROWING n_object]) = eps /\ ~$ob_object_arithmetic_type_error_source(S_capture, pfunction, pobreturnerror_site) /\ ~$ob_object_arithmetic_type_error_source(S_capture, pfunction, pobreturnerror_line) /\ ~$ob_object_arithmetic_type_error_source(S_capture, pfunction_missing, pobreturnerror)'),
        ('fixed generated kind and live pending admission', r'$ob_object_source_return_error(pobobjectreturn_capture.SOURCE) = eps /\ $ob_object_source_generated_error(pobobjectreturn_capture.SOURCE) = (pobreturnerror) /\ $ob_object_source_kind(pobobjectreturn_capture.SOURCE) = "TypeError" /\ $ob_object_source_kind(pobobjectreturn_tag.SOURCE) = "TypeError" /\ $ob_object_return_error_live(S_tag, pobreturnerror) /\ $ob_object_final_saved_context(S_capture) = ((pcallcontext, pobobjectreturn_capture)) /\ $ob_object_final_saved_context(S_tag) = eps /\ $ob_object_final_saved_context(S_message) = eps /\ $ob_object_final_saved_context(S_code) = eps /\ $ob_object_final_saved_context(S_previous) = eps'),
        ('pending metadata adds no owner and preserves zero budget', r'$ob_object_source_birth(pobobjectreturn_capture.SOURCE) = eps /\ $task_nodes(OB_USER_OBJECT_STRING pobobjectreturn_capture) = $task_nodes(OB_USER_OBJECT_STRING pobobjectreturn) /\ $output_final_cv_unwind(S_capture) /\ $heap_count(HOBJECT n_object, $machine_roots(S_capture)) = 2 /\ $heap_count(HOBJECT n_exception, $machine_roots(S_capture)) = 1 /\ S_zero = S_capture[.COMPLETION = BUDGET] /\ ' + prior.public('S_capture')),
        ('actual bare VM exit and empty retirement precede C0', r'S_leave.TODO = [THROW_SEARCH n_exception] /\ S_leave_zero = S_leave[.COMPLETION = BUDGET] /\ S_stage.CURRENT = eps /\ S_stage.FRAMES = eps /\ S_stage.ORIGIN = eps /\ pdestructionrelease.JOBS = eps /\ S_stage.DESTRUCTION.RELEASES = [pdestructionrelease] /\ ~$ob_object_final_cv_ready(S_stage, pobobjectreturn_capture, pdestructionframe, n_exception) /\ S_stage_zero = S_stage[.COMPLETION = BUDGET] /\ S_exit.CURRENT = eps /\ S_exit.FRAMES = eps /\ S_exit.ORIGIN = eps /\ S_exit.DESTRUCTION.RELEASES = eps /\ pdestructionframe.PENDING = (n_exception) /\ pdestructionframe.VALUE = KNOWN PNULL /\ pdestructionframe.FUNCTION = pfunction.ORIGIN /\ pdestructionframe.CALLER = eps /\ pdestructionframe.ORIGIN = eps /\ $ob_object_final_cv_ready(S_exit, pobobjectreturn_capture, pdestructionframe, n_exception) /\ $heap_count(HOBJECT n_object, $machine_roots(S_exit)) = 2 /\ $heap_count(HOBJECT n_exception, $machine_roots(S_exit)) = 1 /\ S_exit.EVENTS = [OUTPUT ([80])] /\ S_exit_zero = S_exit[.COMPLETION = BUDGET] /\ ' + prior.public('S_exit')),
        ('C0 reports actual TypeError before cast release', 'S_report.EVENTS = [OUTPUT ([80]), STDERR ' + prior.value(fatal) + r'] /\ pobdeactivate.COMPLETION = REQUESTFATAL ($ptascii("TypeError")) ' + prior.value(MESSAGE) + r' 6 /\ $heap_count(HOBJECT n_object, $machine_roots(S_report)) = 2 /\ $heap_count(HOBJECT n_exception, $machine_roots(S_report)) = 1 /\ ' + prior.public('S_report')),
        ('retired error leaves authenticated source and cast receipt', r'~((HOBJECT n_exception) <- S_retired.ALLOCATIONS) /\ $heap_count(HOBJECT n_exception, $machine_roots(S_retired)) = 0 /\ $heap_count(HOBJECT n_object, $machine_roots(S_retired)) = 2 /\ $eager_cleanup_valid(S_retired, pdestructioncleanup) /\ ~$eager_cleanup_valid(S_receipt_site, pdestructioncleanup_site) /\ S_retired.EVENTS = S_report.EVENTS /\ ' + prior.public('S_retired')),
    ]
    return bindings, checks


def normal(fixture, path):
    bindings = [b.replace('$dp_seek', '$dn_seek') for b in start(fixture, path)] + [
        'S.TODO = (RETURN_VALUE z) :: ptask_tail*',
        'S_value = $typed_return_value(S, z)', 'S_value.RESULT = KNOWN pvalue_text',
        *prior.seek('S_restored', 'S', 5), '$rt_normal(S_restored.TODO) = (pobobjectreturn_restored)']
    checks = [
        ('full numeric string modulo cannot mint an error receipt', r'S_value.COMPLETION = NORMAL /\ $string_bytes(pvalue_text) = ($ptascii("1")) /\ $ob_object_arithmetic_type_error_capture(S, S_value) = eps /\ pobobjectreturn.SOURCE = eps /\ S.CVS = eps /\ S.ENV = eps /\ |S.OBJECTS| = 1'),
        ('normal arithmetic weak coercion publishes1 with retvalT1', r'$rt_result(S_restored, pobobjectreturn_restored) = ($ptascii("1")) /\ pobobjectreturn_restored.SOURCE = eps /\ |S_restored.OBJECTS| = 1 /\ $heap_count(HOBJECT n_object, $machine_roots(S_restored)) = 1 /\ S_restored.EVENTS = [OUTPUT ([80])] /\ ' + prior.public('S_restored')),
    ]
    return bindings, checks


def clearing(name, fixture, path):
    bindings = start(fixture, path) + capture(); checks = []
    if name == 'catch':
        bindings += prior.seek('S_caught', 'S_capture', 3) + ['S_caught.TODO = (CATCH_BIND porigin_try n_index n_exception) :: ptask_catch*',
            'S_caught.FRAMES = [pframe_caught]',
            'pframe_caught.TODO = (STRINGIFY_RESULT n_object porigin_site 0) :: (OB_USER_OBJECT_STRING pobobjectreturn_caught) :: ptask_native*']
        checks.append(('actual no-variable catch consumes arithmetic history', r'pobobjectreturn_caught.SOURCE = eps /\ S_caught.CVS = eps /\ S_caught.ENV = eps /\ $heap_count(HOBJECT n_exception, $machine_roots(S_caught)) = 1 /\ ' + prior.public('S_caught')))
        origin='S_caught'
    else:origin='S_capture'
    bindings += prior.seek('S_H', origin, 7 if name == 'override' else 4) + ['S_H.FRAMES = [pframe_H]',
        'pframe_H.TODO = (STRINGIFY_RESULT n_object porigin_site 0) :: (OB_USER_OBJECT_STRING pobobjectreturn_H) :: ptask_native*',
        *prior.seek('S_restored', 'S_H', 5), '$rt_normal(S_restored.TODO) = (pobobjectreturn_restored)']
    if name == 'override':
        checks.append(('finally consumes real arithmetic history before VM pop', r'pobobjectreturn_H.SOURCE = eps /\ ~((HOBJECT n_exception) <- S_H.ALLOCATIONS) /\ $heap_count(HOBJECT n_exception, $machine_roots(S_H)) = 0 /\ ' + prior.public('S_H')))
    checks.append(('H publication retires error and retains real retval', r'pobobjectreturn_H.SOURCE = eps /\ pobobjectreturn_restored.SOURCE = eps /\ $rt_result(S_restored, pobobjectreturn_restored) = ($ptascii("H")) /\ ~((HOBJECT n_exception) <- S_restored.ALLOCATIONS) /\ $heap_count(HOBJECT n_object, $machine_roots(S_restored)) = 1 /\ S_restored.EVENTS = [OUTPUT ([80])] /\ ' + prior.public('S_restored')))
    return bindings,checks


def catch(fixture,path):
    return clearing('catch',fixture,path)


def override(fixture,path):
    return clearing('override',fixture,path)


def cleanup(fixture, path):
    bindings = start(fixture, path) + capture() + ['$lookup(S.ENV, $ptascii("d")) = (n_cell)',
        'S.STORE[n_cell] = DEFINED (POBJECT n_local)', *prior.seek('S_entry', 'S_capture', 6),
        'S_entry.TODO = (DESTRUCTOR_ENTER pdestructorcall) :: ptask_entry*',
        'S_entered_found = $drive_steps(S_entry, 1)', 'S_entered_found.COMPLETION = BUDGET',
        'S_entered = S_entered_found[.COMPLETION = NORMAL]', 'S_entered.CURRENT = (pcallcontext_local)',
        *prior.seek('S_exit', 'S_entered', 1),
        'S_exit.TODO = (DESTRUCTOR_FRAME_EXIT pdestructionframe) :: (OUTPUT_FINAL_OBJECT_CV pobobjectreturn_capture) :: ptask_native_exit*']
    checks = [
        ('normal local destructor enters after actual native departure', r'S_entry.CURRENT = eps /\ ~pdestructorcall.USER /\ pdestructorcall.CALLER = eps /\ pdestructorcall.SITE = eps /\ pdestructorcall.OBJECT = n_local /\ pcallcontext_local.CALLSITE = eps /\ pcallcontext_local.LINE = $(-1) /\ $heap_count(HOBJECT n_object, $machine_roots(S_entered)) = 2 /\ $heap_count(HOBJECT n_local, $machine_roots(S_entered)) = 2 /\ $heap_count(HOBJECT n_exception, $machine_roots(S_entered)) = 1 /\ ' + prior.public('S_entered')),
        ('Warning and local retirement precede original arithmetic barrier', r'S_exit.EVENTS = [OUTPUT ([80]), WARNING ($ptascii("missing")) 4] /\ ~((HOBJECT n_local) <- S_exit.ALLOCATIONS) /\ pdestructionframe.PENDING = (n_exception) /\ pdestructionframe.FUNCTION = pfunction.ORIGIN /\ pobreturnerror.SITE = porigin_operator /\ pobreturnerror.LINE = z /\ $throwable_field(S_exit, n_exception, "previous") = PNULL /\ $heap_count(HOBJECT n_object, $machine_roots(S_exit)) = 2 /\ $heap_count(HOBJECT n_exception, $machine_roots(S_exit)) = 1 /\ ' + prior.public('S_exit')),
    ]
    return bindings, checks


def fingerprint(fixture):
    result = prior.fingerprint(fixture)
    for name in ('tests/semantics/output_final_modulo_type_error_sources.py',
                 'tests/semantics/output_final_modulo_type_error_review_state.py'):
        result[name] = prior.common.sha(ROOT / name)
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--stage', choices=['all', *CASES], default='all')
    parser.add_argument('--output', type=Path)
    parser.add_argument('--checked-root', type=Path)
    parser.add_argument('--native-root', type=Path)
    parser.add_argument('--prepare-only', action='store_true')
    args = parser.parse_args()
    out = args.output or Path(tempfile.mkdtemp(prefix='output-final-modulo-type-error-review-', dir=ROOT / '.tools'))
    out.mkdir(parents=True, exist_ok=True)
    report = {'revision': subprocess.check_output(['git', '-C', str(ROOT), 'rev-parse', 'HEAD']).decode().strip(),
              'profile': prior.common.PROFILE, 'native_agreement_credit': 0, 'records': [], 'passed': False}
    try:
        for name in CASES if args.stage == 'all' else [args.stage]:
            directory = out / name; directory.mkdir(); source = CASES[name]
            if args.native_root and name in ('core', 'normal'):
                path = args.native_root / ('native-01' if name == 'core' else 'native-02') / 'source.php'
                assert path.read_bytes() == source
            elif args.checked_root and name != 'core':
                path = args.checked_root / 'control-preparation-01' / name / 'source.php'
                assert path.read_bytes() == source
            else:
                path = directory / 'source.php'; path.write_bytes(source)
            if args.checked_root:
                cache = args.checked_root / ('baseline-01/checked.json' if name == 'core' else f'control-preparation-01/{name}/checked.json')
                checked = json.loads(cache.read_text())
            else:
                frontend = Worker([str(ROOT / '.tools/php/bin/php'), '-n', '-d', 'extension=' + str(ROOT / '.tools/php-file.so'), str(ROOT / 'frontend/worker.php')], directory / 'frontend')
                try:
                    parsed = frontend.request({'op': 'parse', 'source': prior.common.base64.b64encode(source).decode()})
                finally:
                    frontend.close()
                adapter = Worker([str(ROOT / '_build/default/adapter/main.exe'), str(ROOT)], directory / 'adapter')
                try:
                    checked = adapter.request({'op': 'check', 'ast': parsed['ast'], 'fixture': True})
                finally:
                    adapter.close()
            (directory / 'checked.json').write_text(json.dumps(checked) + '\n')
            bindings, checks = globals()[name](checked['fixture'], path)
            fixture = directory / 'state.watsup'
            fixture.write_text(PREFIX + (NORMAL_EXTRA if name == 'normal' else '') + '\ndec $main() : bool*\ndef $main() = [' + ', '.join('(' + condition + ')' for _, condition in checks) + ']\n' + ''.join('  -- if ' + binding + '\n' for binding in bindings))
            record = {'id': name, 'source_sha256': hashlib.sha256(source).hexdigest(), 'fixture_sha256': prior.common.sha(fixture), 'groups': [label for label, _ in checks], 'before': fingerprint(fixture), 'passed': False}
            report['records'].append(record)
            if args.prepare_only:
                record.update(prepared=True, application_credit=0); continue
            modules = json.loads((ROOT / 'spec/semantics/modules.json').read_text()); started = time.monotonic()
            try:
                result = prior.common.run([str(ROOT / 'tests/semantics/_build/default/numeric_runner.exe'), '--sl', *[str(ROOT / module) for module in modules], str(fixture)], directory, 'state', 300)
            finally:
                record['seconds'] = round(time.monotonic() - started, 3); record['after'] = fingerprint(fixture)
            record['observed'] = [value == b'true' for value in re.findall(rb'true|false', result.stdout)]
            assert result.returncode == 0 and not result.stderr and record['observed'] == [True] * len(checks), (result.returncode, result.stderr, record['observed'])
            assert record['before'] == record['after'], 'watched inputs changed'
            record['passed'] = True
        assert report['records'], 'no fixture selected'
        report['passed'] = not args.prepare_only and all(record['passed'] for record in report['records'])
        report['prepared'] = args.prepare_only
    except BaseException as error:
        report['failure'] = {'type': type(error).__name__, 'message': str(error)}; raise
    finally:
        (out / 'report.json').write_text(json.dumps(report, indent=2) + '\n'); print(out / 'report.json', report['passed'], flush=True)


if __name__ == '__main__':
    main()
