#!/usr/bin/env python3
"""Genuine pending ignored-warning discard installs only the captured row."""
import json
import os
from pathlib import Path

import global_constant_scalar_name_protocol as driver
import define_scalar_flag_review_sources as sources

common, text, b64 = driver.common, driver.text, driver.b64

PREFIX = r"""
dec $test_flag_pending_front(pstate) : bool
def $test_flag_pending_front(S) = true
  -- if S.TODO = (THROW_SEARCH n) :: (ERROR_HANDLER_RESULT perrorcall) :: ptask_tail*
  -- if perrorcall.RESUME = DYNAMIC_SCALAR_DEFINE_FLAG_RESULT pconfigcall
def $test_flag_pending_front(S) = false -- otherwise
dec $test_flag_pending_seek(pstate, nat) : pstate
def $test_flag_pending_seek(S, 0) = S
def $test_flag_pending_seek(S, n) = S
  -- if $(n > 0)
  -- if $test_flag_pending_front(S) \/ (S.COMPLETION =/= NORMAL /\ S.COMPLETION =/= BUDGET)
def $test_flag_pending_seek(S, n) = $test_flag_pending_seek($drive_steps($test_running(S),1),$nabs($(n - 1)))
  -- if $(n > 0)
  -- if ~$test_flag_pending_front(S)
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
"""


def checks(program, path, name):
    assert name == 'throwing-ignored-warning-keeps-raw-float-flag'
    values = [
        'S_initial = $php_run(' + program + ',0,' + json.dumps(b64(os.fsencode(path))) + ')',
        'S_initial.COMPLETION = BUDGET',
        'S_found = $test_flag_pending_seek(S_initial,1000)',
        'S_found.COMPLETION = NORMAL \\/ S_found.COMPLETION = BUDGET',
        'S = S_found[.COMPLETION = NORMAL]',
        '$test_flag_pending_front(S)',
        'S.TODO = (THROW_SEARCH n_throw) :: (ERROR_HANDLER_RESULT perrorcall) :: ptask_tail*',
        'perrorcall.RESUME = DYNAMIC_SCALAR_DEFINE_FLAG_RESULT pconfigcall',
        'perrorcall.LEVEL = 2',
        'perrorcall.MESSAGE = $dynamic_constant_case_message()',
        'perrorcall.SITE = pconfigcall.SITE',
        'perrorcall.LINE = pconfigcall.LINE',
        'S.ORIGIN = (pconfigcall.SITE)',
        '$throwable_live(S,n_throw)',
        'S.OBJECTS[n_throw] = THROWABLE pthrowable',
        'pthrowable.KIND = "Exception"',
        '$string_bytes($throwable_field(S,n_throw,"message")) = (' + text('stop') + ')',
        'pconfigcall.KIND = INTRINSIC_DEFINE',
        'pconfigcall.OWNER = eps',
        'pconfigcall.PACKS = eps',
        'pconfigcall.SELECTION = (n_selection)',
        '$(n_selection < |S.SELECTEDCALLS|)',
        'S.SELECTEDCALLS[n_selection].KIND = INTRINSIC_DEFINE',
        'pconfigcall.SENT = [NAMED_SENT (KNOWN pvalue_captured_name), NAMED_SENT (KNOWN (PINT 159)), NAMED_SENT (KNOWN (PFLOAT 4612811918334230528))]',
        '$string_bytes(pvalue_captured_name) = (' + text('RawScalarFlag31') + ')',
        '$config_invoke_valid(S,pconfigcall)',
        '$dynamic_scalar_define_flag_case_valid(S,pconfigcall)',
        'S.USERCONSTANTS = eps',
        '$source_constant_lookup(S,' + text('RawScalarFlag31') + ') = eps',
        *common.public('S'),
    ]
    for variable, expected in [('name', text('changed')), ('flag', text('0')), ('call', text('constant'))]:
        values += [
            '$lookup(S.ENV,' + text(variable) + ') = (n_' + variable + ')',
            'S.STORE[n_' + variable + '] = DEFINED pvalue_' + variable,
            '$string_bytes(pvalue_' + variable + ') = (' + expected + ')',
        ]
    values += [
        '$lookup(S.ENV,' + text('value') + ') = (n_value)',
        'S.STORE[n_value] = DEFINED (PINT 999)',
        '$lookup(S.ENV,' + text('result') + ') = (n_result)',
        'S.STORE[n_result] = DEFINED (PINT 99)',
        'S_discard = S[.TODO = (THROW_SEARCH n_throw) :: ptask_tail*]',
        'S_before = $error_handler_restore($identity_read_discard(S_discard,perrorcall.RESUME),perrorcall.CALLBACK)',
        '$dynamic_scalar_define_flag_case_valid(S_before,pconfigcall)',
        '$throwable_live(S_before,n_throw)',
        'puserconstant = {NAME ' + text('RawScalarFlag31') + ', ORIGIN pconfigcall.SITE, VALUE (PINT 159), CLASS PVSCALAR, READS eps, RECEIVES eps}',
        'S_expected = S_before[.USERCONSTANTS = S_before.USERCONSTANTS ++ [puserconstant]]',
        'S_hook = $dynamic_scalar_define_flag_pending(S_before,pconfigcall)',
        'S_hook = S_expected',
        '$error_read_discard(S_before,perrorcall.RESUME) = S_expected',
        *common.step('S_after', 'S'),
        'S_after = S_expected',
        'S_after.TODO = (THROW_SEARCH n_throw) :: ptask_tail*',
        'S_after.OBJECTS[n_throw] = THROWABLE pthrowable',
        '$throwable_live(S_after,n_throw)',
        'S_after.STORE[n_result] = DEFINED (PINT 99)',
        '$user_constant_at(S_after.USERCONSTANTS,' + text('RawScalarFlag31') + ') = (puserconstant)',
        '$source_constant_lookup(S_after,' + text('RawScalarFlag31') + ') = (VALUE (PINT 159))',
        '$user_constants_valid(S_after,S_after.USERCONSTANTS)',
        *common.public('S_after'),
        'S_duplicate = S_before[.USERCONSTANTS = [puserconstant]]',
        '$user_constants_valid(S_duplicate,S_duplicate.USERCONSTANTS)',
        'S_duplicate_after = $dynamic_scalar_define_flag_pending(S_duplicate,pconfigcall)',
        'S_duplicate_after.COMPLETION = UNSUPPORTED "scalar define flag pending-exception registration"',
        'S_duplicate_after.USERCONSTANTS = S_duplicate.USERCONSTANTS',
        'S_duplicate_after.TODO = eps',
        'n_bad_throw = |S_before.OBJECTS|',
        'S_bad_throw = S_before[.TODO = (THROW_SEARCH n_bad_throw) :: ptask_tail*]',
        '~$throwable_live(S_bad_throw,n_bad_throw)',
        'S_bad_throw_after = $dynamic_scalar_define_flag_pending(S_bad_throw,pconfigcall)',
        'S_bad_throw_after.COMPLETION = UNSUPPORTED "scalar define flag pending-exception registration"',
        'S_bad_throw_after.USERCONSTANTS = S_before.USERCONSTANTS',
    ]
    for field in ('.SITE = PORIGIN 0 eps', '.LINE = $(pconfigcall.LINE + 1)', '.SELECTION = eps', '.KIND = INTRINSIC_DEFINED'):
        values += ['~$dynamic_scalar_define_flag_case_valid(S_before,pconfigcall[' + field + '])']
    values += [
        'n_bad_string = |S_before.STRINGDATA|',
        'pvalue_bad_flag = PSTRING_CARRIER (REQUEST_STRING n_bad_string) ' + text('false'),
        '~$string_carrier_valid(S_before,pvalue_bad_flag)',
        'pconfigcall_bad_flag = pconfigcall[.SENT = $named_slot_set(pconfigcall.SENT,2,KNOWN pvalue_bad_flag)]',
        '$dynamic_scalar_define_flag_call(pconfigcall_bad_flag)',
        '~$dynamic_scalar_define_flag_case_valid(S_before,pconfigcall_bad_flag)',
        'S_bad_flag_after = $dynamic_scalar_define_flag_pending(S_before,pconfigcall_bad_flag)',
        'S_bad_flag_after.COMPLETION = UNSUPPORTED "scalar define flag pending-exception registration"',
        'S_bad_flag_after.USERCONSTANTS = S_before.USERCONSTANTS',
        'S_pause = $drive_steps(S,0)',
        'S_pause = S[.COMPLETION = BUDGET]',
        'S_one = $drive_steps(S,1)',
        'S_one = $drive_steps(S_pause[.COMPLETION = NORMAL],1)',
    ]
    return values


def main():
    fingerprint = sources.family.fingerprint
    sources.family.fingerprint = lambda: dict(fingerprint(), **{
        str(Path(__file__).relative_to(driver.ROOT)): sources.family.sha(__file__)})
    driver.sources, driver.PREFIX, driver.checks = sources, PREFIX, checks
    driver.main()


if __name__ == '__main__':
    main()
