#!/usr/bin/env python3
"""A reached NaN receive throw discards the outer registration continuation."""
import json
import os
from pathlib import Path

import global_constant_scalar_name_protocol as driver
import define_nan_flag_review_sources as sources

common, text, b64 = driver.common, driver.text, driver.b64

PREFIX = r"""
dec $test_nan_receive_throw_front(pstate) : bool
def $test_nan_receive_throw_front(S) = true
  -- if S.TODO = (THROW_SEARCH n) :: (ERROR_HANDLER_RESULT perrorcall) :: ptask_tail*
  -- if perrorcall.RESUME = DYNAMIC_NAN_DEFINE_FLAG_RESULT pconfigcall
def $test_nan_receive_throw_front(S) = false -- otherwise
dec $test_nan_receive_throw_seek(pstate, nat) : pstate
def $test_nan_receive_throw_seek(S, 0) = S
def $test_nan_receive_throw_seek(S, n) = S
  -- if $(n > 0)
  -- if $test_nan_receive_throw_front(S) \/ (S.COMPLETION =/= NORMAL /\ S.COMPLETION =/= BUDGET)
def $test_nan_receive_throw_seek(S, n) = $test_nan_receive_throw_seek($drive_steps($test_running(S),1),$nabs($(n - 1)))
  -- if $(n > 0)
  -- if ~$test_nan_receive_throw_front(S)
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
"""


def checks(program, path, name):
    assert name == 'nan-flag-first-warning-throw-keeps-inner-binding'
    values = [
        'S_initial = $php_run(' + program + ',0,' + json.dumps(b64(os.fsencode(path))) + ')',
        'S_initial.COMPLETION = BUDGET',
        'S_found = $test_nan_receive_throw_seek(S_initial,2000)',
        'S_found.COMPLETION = NORMAL \\/ S_found.COMPLETION = BUDGET',
        'S = S_found[.COMPLETION = NORMAL]', '$test_nan_receive_throw_front(S)',
        'S.TODO = (THROW_SEARCH n_throw) :: (ERROR_HANDLER_RESULT perrorcall) :: ptask_tail*',
        'perrorcall.RESUME = DYNAMIC_NAN_DEFINE_FLAG_RESULT pconfigcall',
        'perrorcall.LEVEL = 2',
        'perrorcall.MESSAGE = ' + text('unexpected NAN value was coerced to bool'),
        'perrorcall.EVENT = DIAGNOSTIC "Warning" perrorcall.MESSAGE pconfigcall.LINE',
        'perrorcall.SITE = pconfigcall.SITE', 'perrorcall.LINE = pconfigcall.LINE',
        'pconfigcall.SITE = PORIGIN 0 pcpath', 'pconfigcall.LINE = 17',
        'S.ORIGIN = (pconfigcall.SITE)', '$throwable_live(S,n_throw)',
        'S.OBJECTS[n_throw] = THROWABLE pthrowable', 'pthrowable.KIND = "Exception"',
        '$string_bytes($throwable_field(S,n_throw,"message")) = (' + text('first-nan') + ')',
        '$throwable_field(S,n_throw,"previous") = PNULL',
        'pconfigcall.KIND = INTRINSIC_DEFINE', 'pconfigcall.OWNER = eps', 'pconfigcall.PACKS = eps',
        'pconfigcall.NAMED', 'pconfigcall.SELECTION = (n_selection)',
        '$(n_selection < |S.SELECTEDCALLS|)', 'S.SELECTEDCALLS[n_selection].KIND = INTRINSIC_DEFINE',
        'pconfigcall.SENT = [NAMED_SENT (KNOWN pvalue_name),NAMED_SENT (KNOWN pvalue_candidate),NAMED_SENT (KNOWN (PFLOAT n_nan))]',
        'n_nan = 9221120237041090560', '$number_bool(NFLOAT n_nan) = (true,true)',
        '$string_bytes(pvalue_name) = (' + text('NaNReceiveInner35') + ')',
        'pvalue_candidate = PSTRING_CARRIER (REQUEST_STRING n_string) preqbytes_candidate',
        'preqbytes_candidate = ' + text('captured-candidate'), '$string_carrier_valid(S,pvalue_candidate)',
        '$config_invoke_valid(S,pconfigcall)', '~$config_strict(S,pconfigcall)',
        '$dynamic_nan_define_flag_call(pconfigcall)', '$dynamic_nan_define_flag_valid(S,pconfigcall)',
        '~$dynamic_define_quiet_flag(PFLOAT n_nan)', '~$dynamic_scalar_define_flag_call(pconfigcall)',
        '~$dynamic_constant_case_valid(S,pconfigcall)', '$error_call_valid(S,perrorcall)',
        'S.USERCONSTANTS = [puserconstant_inner]',
        'puserconstant_inner.NAME = ' + text('NaNReceiveInner35'),
        'puserconstant_inner.VALUE = PINT 307', 'puserconstant_inner.CLASS = PVSCALAR',
        '$source_constant_lookup(S,' + text('NaNReceiveInner35') + ') = (VALUE (PINT 307))',
        'S.OUTPUTBUFFERS = eps', 'S.ERRORFATALTRACE = eps', *common.public('S'),
    ]
    for variable, expected in [('name', 'changed'), ('candidate', 'changed-value'), ('call', 'defined')]:
        values += ['$lookup(S.ENV,' + text(variable) + ') = (n_live_' + variable + ')',
            'S.STORE[n_live_' + variable + '] = DEFINED pvalue_live_' + variable,
            '$string_bytes(pvalue_live_' + variable + ') = (' + text(expected) + ')']
    values += [
        '$lookup(S.ENV,' + text('flag') + ') = (n_live_flag)', 'S.STORE[n_live_flag] = DEFINED (PINT 0)',
        '$lookup(S.ENV,' + text('warnings') + ') = (n_warnings)', 'S.STORE[n_warnings] = DEFINED (PINT 1)',
        '$lookup(S.ENV,' + text('result') + ') = (n_result)', 'S.STORE[n_result] = DEFINED (PINT 99)',
        'S_discard = S[.TODO = (THROW_SEARCH n_throw) :: ptask_tail*]',
        'S_expected = $error_handler_restore($identity_read_discard(S_discard,perrorcall.RESUME),perrorcall.CALLBACK)',
        '$error_read_discard(S_expected,perrorcall.RESUME) = S_expected',
        *common.step('S_after', 'S'), 'S_after = S_expected',
        'S_after.USERCONSTANTS = [puserconstant_inner]',
        'S_after.TODO = (THROW_SEARCH n_throw) :: ptask_tail*',
        'S_after.OBJECTS[n_throw] = THROWABLE pthrowable', 'S_after.STORE[n_result] = DEFINED (PINT 99)',
        *common.public('S_after'),
        'n_bad_string = |S.STRINGDATA|',
        'pvalue_bad_name = PSTRING_CARRIER (REQUEST_STRING n_bad_string) ' + text('NaNReceiveInner35'),
        '~$string_carrier_valid(S,pvalue_bad_name)',
        'pconfigcall_bad_name = pconfigcall[.SENT = $named_slot_set(pconfigcall.SENT,0,KNOWN pvalue_bad_name)]',
        '~$dynamic_nan_define_flag_valid(S,pconfigcall_bad_name)',
        'pvalue_bad_candidate = PSTRING_CARRIER (REQUEST_STRING n_bad_string) ' + text('captured-candidate'),
        '~$string_carrier_valid(S,pvalue_bad_candidate)',
        'pconfigcall_bad_candidate = pconfigcall[.SENT = $named_slot_set(pconfigcall.SENT,1,KNOWN pvalue_bad_candidate)]',
        '~$dynamic_nan_define_flag_valid(S,pconfigcall_bad_candidate)',
    ]
    for field in ('.SITE = PORIGIN 0 eps', '.LINE = $(pconfigcall.LINE + 1)',
            '.SELECTION = eps', '.OWNER = (0)', '.KIND = INTRINSIC_CONSTANT'):
        values += ['~$dynamic_nan_define_flag_valid(S,pconfigcall[' + field + '])']
    for flag in ('PNULL', 'PBOOL true', 'PINT 1', 'PFLOAT 4607182418800017408'):
        values += ['~$dynamic_nan_define_flag_call(pconfigcall[.SENT = $named_slot_set(pconfigcall.SENT,2,KNOWN (' + flag + '))])']
    for field in ('.LEVEL = 8192', '.MESSAGE = ' + text('changed'), '.LINE = $(perrorcall.LINE + 1)',
            '.EVENT = DIAGNOSTIC "Warning" perrorcall.MESSAGE $(perrorcall.LINE + 1)'):
        values += ['~$error_call_valid(S,perrorcall[' + field + '])']
    values += ['S_pause = $drive_steps(S,0)', 'S_pause = S[.COMPLETION = BUDGET]',
        'S_one = $drive_steps(S,1)', 'S_one = $drive_steps(S_pause[.COMPLETION = NORMAL],1)']
    return values


def main():
    fingerprint = sources.family.fingerprint
    sources.family.fingerprint = lambda: dict(fingerprint(), **{
        str(Path(__file__).relative_to(driver.ROOT)): sources.family.sha(__file__)})
    driver.sources, driver.PREFIX, driver.checks = sources, PREFIX, checks
    driver.main()


if __name__ == '__main__':
    main()
