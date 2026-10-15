#!/usr/bin/env python3
"""Masked pending duplicate diagnostics preserve the original exception and row."""
import json
import os
from pathlib import Path

import global_constant_scalar_name_protocol as driver
import define_pending_duplicate_sources as sources

common, text, b64 = driver.common, driver.text, driver.b64

PREFIX = r"""
dec $test_pending_duplicate_front(pstate) : bool
def $test_pending_duplicate_front(S) = true
  -- if S.TODO = (THROW_SEARCH n) :: (ERROR_HANDLER_RESULT perrorcall) :: ptask_tail*
  -- if perrorcall.RESUME = DYNAMIC_CONSTANT_CASE_WARNING pconfigcall
def $test_pending_duplicate_front(S) = false -- otherwise
dec $test_pending_duplicate_seek(pstate, nat) : pstate
def $test_pending_duplicate_seek(S, 0) = S
def $test_pending_duplicate_seek(S, n) = S
  -- if $(n > 0)
  -- if $test_pending_duplicate_front(S) \/ (S.COMPLETION =/= NORMAL /\ S.COMPLETION =/= BUDGET)
def $test_pending_duplicate_seek(S, n) = $test_pending_duplicate_seek($drive_steps($test_running(S),1),$nabs($(n - 1)))
  -- if $(n > 0)
  -- if ~$test_pending_duplicate_front(S)
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
"""


def checks(program, path, name):
    assert name == 'strict-selected-pending-duplicate-masked-handler'
    warning = text('Constant StrictPendingDup34 already defined, this will be an error in PHP 9')
    values = [
        'S_initial = $php_run(' + program + ',0,' + json.dumps(b64(os.fsencode(path))) + ')',
        'S_initial.COMPLETION = BUDGET',
        'S_found = $test_pending_duplicate_seek(S_initial,2000)',
        'S_found.COMPLETION = NORMAL \\/ S_found.COMPLETION = BUDGET',
        'S = S_found[.COMPLETION = NORMAL]', '$test_pending_duplicate_front(S)',
        'S.TODO = (THROW_SEARCH n_throw) :: (ERROR_HANDLER_RESULT perrorcall) :: ptask_tail*',
        'perrorcall.RESUME = DYNAMIC_CONSTANT_CASE_WARNING pconfigcall',
        'perrorcall.LEVEL = 2', 'perrorcall.MESSAGE = $dynamic_constant_case_message()',
        'perrorcall.SITE = pconfigcall.SITE', 'perrorcall.LINE = pconfigcall.LINE',
        'pconfigcall.SITE = PORIGIN 0 pcpath', 'pconfigcall.LINE = 32',
        'S.ORIGIN = (pconfigcall.SITE)', '$throwable_live(S,n_throw)',
        'S.OBJECTS[n_throw] = THROWABLE pthrowable', 'pthrowable.KIND = "Exception"',
        '$string_bytes($throwable_field(S,n_throw,"message")) = (' + text('masked-first') + ')',
        '$throwable_field(S,n_throw,"previous") = PNULL',
        'pconfigcall.KIND = INTRINSIC_DEFINE', 'pconfigcall.OWNER = eps', 'pconfigcall.PACKS = eps',
        'pconfigcall.NAMED', 'pconfigcall.SELECTION = (n_selection)',
        '$(n_selection < |S.SELECTEDCALLS|)', 'S.SELECTEDCALLS[n_selection].KIND = INTRINSIC_DEFINE',
        'pconfigcall.SENT = [NAMED_SENT (KNOWN pvalue_captured_name),NAMED_SENT (KNOWN pvalue_captured_value),NAMED_SENT (KNOWN (PBOOL true))]',
        '$string_bytes(pvalue_captured_name) = (' + text('StrictPendingDup34') + ')',
        'pvalue_captured_value = PSTRING_CARRIER (REQUEST_STRING n_string) preqbytes_value',
        'preqbytes_value = ' + text('capture-value'), '$string_carrier_valid(S,pvalue_captured_value)',
        '$config_invoke_valid(S,pconfigcall)', '$config_strict(S,pconfigcall)',
        '$dynamic_constant_case_valid(S,pconfigcall)',
        'S.USERCONSTANTS = [puserconstant_original]',
        'puserconstant_original.NAME = ' + text('StrictPendingDup34'),
        'puserconstant_original.VALUE = PINT 279', 'puserconstant_original.CLASS = PVSCALAR',
        '$source_constant_lookup(S,' + text('StrictPendingDup34') + ') = (VALUE (PINT 279))',
        'S.OUTPUTBUFFERS = eps', 'S.ERRORFATALTRACE = eps', *common.public('S'),
    ]
    for variable, expected in [('name', 'handler'), ('candidate', 'handler-value'), ('call', 'constant')]:
        values += ['$lookup(S.ENV,' + text(variable) + ') = (n_live_' + variable + ')',
            'S.STORE[n_live_' + variable + '] = DEFINED pvalue_live_' + variable,
            '$string_bytes(pvalue_live_' + variable + ') = (' + text(expected) + ')']
    values += [
        '$lookup(S.ENV,' + text('flag') + ') = (n_live_flag)', 'S.STORE[n_live_flag] = DEFINED (PBOOL false)',
        '$lookup(S.ENV,' + text('result') + ') = (n_result)', 'S.STORE[n_result] = DEFINED (PINT 99)',
        'S_discard = S[.TODO = (THROW_SEARCH n_throw) :: ptask_tail*]',
        'S_before = $error_handler_restore($identity_read_discard(S_discard,perrorcall.RESUME),perrorcall.CALLBACK)',
        'S_before.ERRORHANDLER.LEVELS = 8192',
        'S_before.ERRORHANDLER.CALLBACK = (pvalue_handler)',
        '$string_bytes(pvalue_handler) = (' + text('maskedPendingDup34') + ')',
        '~$error_handler_eligible(S_before,2)', '$display_mode(S_before.DISPLAYINI) = 2',
        '$long_and(S_before.REPORTING,2) =/= 0',
        'S_expected = S_before[.EVENTS = S_before.EVENTS ++ [DIAGNOSTIC "Warning" (' + warning + ') 32]]',
        '$dynamic_constant_case_pending(S_before,pconfigcall) = S_expected',
        '$error_read_discard(S_before,perrorcall.RESUME) = S_expected',
        *common.step('S_after', 'S'), 'S_after = S_expected',
        'S_after.USERCONSTANTS = [puserconstant_original]',
        'S_after.TODO = (THROW_SEARCH n_throw) :: ptask_tail*',
        'S_after.OBJECTS[n_throw] = THROWABLE pthrowable', 'S_after.STORE[n_result] = DEFINED (PINT 99)',
        *common.public('S_after'),
        'ptraceframe_seed* = $config_trace_frames(S_before,pconfigcall,$trace_extra(S_before,$getclass_trace_operands(pconfigcall.SENT)))',
        'ptraceframe_seed* =/= eps',
        'S_seed = S[.ERRORFATALTRACE = ptraceframe_seed*]', *common.public('S_seed'),
        *common.step('S_seed_after', 'S_seed'), 'S_seed_after = S_expected',
        'S_quiet = S_seed[.REPORTING = 0][.REPORTINGINI = ' + text('0') + '][.REPORTINGMODIFIED = true]',
        'S_quiet_discard = S_quiet[.TODO = (THROW_SEARCH n_throw) :: ptask_tail*]',
        'S_quiet_before = $error_handler_restore($identity_read_discard(S_quiet_discard,perrorcall.RESUME),perrorcall.CALLBACK)',
        '~$error_handler_eligible(S_quiet_before,2)',
        'S_quiet_expected = S_quiet_before[.ERRORFATALTRACE = eps]',
        *common.step('S_quiet_after', 'S_quiet'), 'S_quiet_after = S_quiet_expected',
        'S_quiet_after.EVENTS = S.EVENTS', *common.public('S_quiet_after'),
        'n_bad_throw = |S_before.OBJECTS|',
        'S_bad_throw = S_before[.TODO = (THROW_SEARCH n_bad_throw) :: ptask_tail*]',
        '~$throwable_live(S_bad_throw,n_bad_throw)',
        'S_bad_throw_after = $dynamic_constant_case_pending(S_bad_throw,pconfigcall)',
        'S_bad_throw_after.COMPLETION = UNSUPPORTED "boolean define flag pending-exception registration"',
        'S_bad_throw_after.USERCONSTANTS = S_before.USERCONSTANTS',
        'n_bad_string = |S_before.STRINGDATA|',
        'pvalue_bad_name = PSTRING_CARRIER (REQUEST_STRING n_bad_string) ' + text('StrictPendingDup34'),
        '~$string_carrier_valid(S_before,pvalue_bad_name)',
        'pconfigcall_bad_name = pconfigcall[.SENT = $named_slot_set(pconfigcall.SENT,0,KNOWN pvalue_bad_name)]',
        '$dynamic_constant_case_valid(S_before,pconfigcall_bad_name)',
        'S_bad_name_after = $dynamic_constant_case_pending(S_before,pconfigcall_bad_name)',
        'S_bad_name_after.COMPLETION = UNSUPPORTED "boolean define flag pending-exception registration"',
        'S_bad_name_after.USERCONSTANTS = S_before.USERCONSTANTS',
    ]
    for field in ('.SITE = PORIGIN 0 eps', '.SELECTION = eps'):
        values += ['~$dynamic_constant_case_valid(S_before,pconfigcall[' + field + '])']
    values += ['S_pause = $drive_steps(S,0)', 'S_pause = S[.COMPLETION = BUDGET]',
        'S_one = $drive_steps(S,1)', 'S_one = $drive_steps(S_pause[.COMPLETION = NORMAL],1)']
    return values


def main():
    fingerprint = sources.family.fingerprint
    sources.family.fingerprint = lambda: dict(fingerprint(), **{
        str(Path(__file__).relative_to(driver.ROOT)): sources.family.sha(__file__)})
    sources.family.CASES = {name: value for name, value in sources.family.CASES.items()
        if name == 'strict-selected-pending-duplicate-masked-handler'}
    driver.sources, driver.PREFIX, driver.checks = sources, PREFIX, checks
    driver.main()


if __name__ == '__main__':
    main()
