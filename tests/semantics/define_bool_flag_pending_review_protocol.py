#!/usr/bin/env python3
"""Strict selected boolean-warning discard preserves the captured string row."""
import json
import os
from pathlib import Path

import global_constant_scalar_name_protocol as driver
import define_bool_flag_pending_sources as sources

common, text, b64 = driver.common, driver.text, driver.b64

PREFIX = r"""
dec $test_bool_pending_front(pstate) : bool
def $test_bool_pending_front(S) = true
  -- if S.TODO = (THROW_SEARCH n) :: (ERROR_HANDLER_RESULT perrorcall) :: ptask_tail*
  -- if perrorcall.RESUME = DYNAMIC_CONSTANT_CASE_WARNING pconfigcall
def $test_bool_pending_front(S) = false -- otherwise
dec $test_bool_pending_seek(pstate, nat) : pstate
def $test_bool_pending_seek(S, 0) = S
def $test_bool_pending_seek(S, n) = S
  -- if $(n > 0)
  -- if $test_bool_pending_front(S) \/ (S.COMPLETION =/= NORMAL /\ S.COMPLETION =/= BUDGET)
def $test_bool_pending_seek(S, n) = $test_bool_pending_seek($drive_steps($test_running(S),1),$nabs($(n - 1)))
  -- if $(n > 0)
  -- if ~$test_bool_pending_front(S)
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
"""


def checks(program, path, name):
    assert name == 'strict-selected-true-captured-carrier'
    values = [
        'S_initial = $php_run(' + program + ',0,' + json.dumps(b64(os.fsencode(path))) + ')',
        'S_initial.COMPLETION = BUDGET',
        'S_found = $test_bool_pending_seek(S_initial,1500)',
        'S_found.COMPLETION = NORMAL \\/ S_found.COMPLETION = BUDGET',
        'S = S_found[.COMPLETION = NORMAL]',
        '$test_bool_pending_front(S)',
        'S.TODO = (THROW_SEARCH n_throw) :: (ERROR_HANDLER_RESULT perrorcall) :: ptask_tail*',
        'perrorcall.RESUME = DYNAMIC_CONSTANT_CASE_WARNING pconfigcall',
        'perrorcall.LEVEL = 2', 'perrorcall.MESSAGE = $dynamic_constant_case_message()',
        'perrorcall.SITE = pconfigcall.SITE', 'perrorcall.LINE = pconfigcall.LINE',
        'S.ORIGIN = (pconfigcall.SITE)', '$throwable_live(S,n_throw)',
        'S.OBJECTS[n_throw] = THROWABLE pthrowable', 'pthrowable.KIND = "Exception"',
        '$string_bytes($throwable_field(S,n_throw,"message")) = (' + text('strict-stop') + ')',
        'pconfigcall.KIND = INTRINSIC_DEFINE', 'pconfigcall.OWNER = eps', 'pconfigcall.PACKS = eps',
        'pconfigcall.NAMED', 'pconfigcall.SELECTION = (n_selection)',
        '$(n_selection < |S.SELECTEDCALLS|)', 'S.SELECTEDCALLS[n_selection].KIND = INTRINSIC_DEFINE',
        'pconfigcall.SENT = [NAMED_SENT (KNOWN pvalue_captured_name),NAMED_SENT (KNOWN pvalue_captured_value),NAMED_SENT (KNOWN (PBOOL true))]',
        '$string_bytes(pvalue_captured_name) = (' + text('StrictBoolTail32') + ')',
        'pvalue_captured_value = PSTRING_CARRIER (REQUEST_STRING n_string) preqbytes_value',
        'preqbytes_value = ' + text('capture-value'), '$string_carrier_valid(S,pvalue_captured_value)',
        'S.STRINGDATA[n_string] = preqbytes_value',
        '$config_invoke_valid(S,pconfigcall)', '$config_strict(S,pconfigcall)',
        '$dynamic_constant_case_valid(S,pconfigcall)',
        'S.USERCONSTANTS = [puserconstant_sibling]',
        'puserconstant_sibling.NAME = ' + text('SiblingBoolTail32'),
        'puserconstant_sibling.VALUE = PINT 232', 'puserconstant_sibling.CLASS = PVSCALAR',
        '$source_constant_lookup(S,' + text('StrictBoolTail32') + ') = eps',
        *common.public('S'),
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
        '$config_strict(S_before,pconfigcall)', '$dynamic_constant_case_valid(S_before,pconfigcall)',
        '$throwable_live(S_before,n_throw)',
        'puserconstant = {NAME ' + text('StrictBoolTail32') + ', ORIGIN pconfigcall.SITE, VALUE pvalue_captured_value, CLASS PVSTRING false, READS eps, RECEIVES eps}',
        'S_expected = S_before[.USERCONSTANTS = S_before.USERCONSTANTS ++ [puserconstant]]',
        '$dynamic_constant_case_pending(S_before,pconfigcall) = S_expected',
        '$error_read_discard(S_before,perrorcall.RESUME) = S_expected',
        *common.step('S_after', 'S'), 'S_after = S_expected',
        'S_after.TODO = (THROW_SEARCH n_throw) :: ptask_tail*',
        'S_after.OBJECTS[n_throw] = THROWABLE pthrowable', '$throwable_live(S_after,n_throw)',
        'S_after.STORE[n_result] = DEFINED (PINT 99)',
        'S_after.USERCONSTANTS = [puserconstant_sibling,puserconstant]',
        '$source_constant_lookup(S_after,' + text('StrictBoolTail32') + ') = (VALUE pvalue_captured_value)',
        '$source_constant_lookup(S_after,' + text('SiblingBoolTail32') + ') = (VALUE (PINT 232))',
        '$user_constants_valid(S_after,S_after.USERCONSTANTS)', *common.public('S_after'),
        'S_duplicate = S_before[.USERCONSTANTS = S_before.USERCONSTANTS ++ [puserconstant]]',
        '$user_constants_valid(S_duplicate,S_duplicate.USERCONSTANTS)',
        'S_duplicate_after = $dynamic_constant_case_pending(S_duplicate,pconfigcall)',
        'S_duplicate_after.COMPLETION = UNSUPPORTED "boolean define flag pending-exception registration"',
        'S_duplicate_after.USERCONSTANTS = S_duplicate.USERCONSTANTS', 'S_duplicate_after.TODO = eps',
        'n_bad_throw = |S_before.OBJECTS|',
        'S_bad_throw = S_before[.TODO = (THROW_SEARCH n_bad_throw) :: ptask_tail*]',
        '~$throwable_live(S_bad_throw,n_bad_throw)',
        'S_bad_throw_after = $dynamic_constant_case_pending(S_bad_throw,pconfigcall)',
        'S_bad_throw_after.COMPLETION = UNSUPPORTED "boolean define flag pending-exception registration"',
        'S_bad_throw_after.USERCONSTANTS = S_before.USERCONSTANTS',
        'S_no_throw = S_before[.TODO = eps]', '$error_read_discard(S_no_throw,perrorcall.RESUME) = S_no_throw',
    ]
    for field in ('.SITE = PORIGIN 0 eps', '.LINE = $(pconfigcall.LINE + 1)',
            '.SELECTION = eps', '.KIND = INTRINSIC_DEFINED'):
        values += ['~$dynamic_constant_case_valid(S_before,pconfigcall[' + field + '])']
    values += [
        'n_bad_string = |S_before.STRINGDATA|',
        'pvalue_bad = PSTRING_CARRIER (REQUEST_STRING n_bad_string) preqbytes_value',
        '~$string_carrier_valid(S_before,pvalue_bad)',
        'pconfigcall_bad = pconfigcall[.SENT = $named_slot_set(pconfigcall.SENT,1,KNOWN pvalue_bad)]',
        '~$dynamic_constant_case_valid(S_before,pconfigcall_bad)',
        'S_bad_value_after = $dynamic_constant_case_pending(S_before,pconfigcall_bad)',
        'S_bad_value_after.COMPLETION = UNSUPPORTED "boolean define flag pending-exception registration"',
        'S_bad_value_after.USERCONSTANTS = S_before.USERCONSTANTS',
        'pvalue_bad_name = PSTRING_CARRIER (REQUEST_STRING n_bad_string) ' + text('StrictBoolTail32'),
        '~$string_carrier_valid(S_before,pvalue_bad_name)',
        'pconfigcall_bad_name = pconfigcall[.SENT = $named_slot_set(pconfigcall.SENT,0,KNOWN pvalue_bad_name)]',
        '$dynamic_constant_case_valid(S_before,pconfigcall_bad_name)',
        'S_bad_name_after = $dynamic_constant_case_pending(S_before,pconfigcall_bad_name)',
        'S_bad_name_after.COMPLETION = UNSUPPORTED "boolean define flag pending-exception registration"',
        'S_bad_name_after.USERCONSTANTS = S_before.USERCONSTANTS',
        'pconfigcall_false = pconfigcall[.SENT = $named_slot_set(pconfigcall.SENT,2,KNOWN (PBOOL false))]',
        '~$dynamic_constant_case_valid(S_before,pconfigcall_false)',
        'S_false_after = $dynamic_constant_case_pending(S_before,pconfigcall_false)',
        'S_false_after.COMPLETION = UNSUPPORTED "boolean define flag pending-exception registration"',
        'S_false_after.USERCONSTANTS = S_before.USERCONSTANTS',
        'S_pause = $drive_steps(S,0)', 'S_pause = S[.COMPLETION = BUDGET]',
        'S_one = $drive_steps(S,1)', 'S_one = $drive_steps(S_pause[.COMPLETION = NORMAL],1)',
    ]
    return values


def main():
    fingerprint = sources.family.fingerprint
    sources.family.fingerprint = lambda: dict(fingerprint(), **{
        str(Path(__file__).relative_to(driver.ROOT)): sources.family.sha(__file__)})
    sources.family.CASES = {name: value for name, value in sources.family.CASES.items()
        if name == 'strict-selected-true-captured-carrier'}
    driver.sources, driver.PREFIX, driver.checks = sources, PREFIX, checks
    driver.main()


if __name__ == '__main__':
    main()
