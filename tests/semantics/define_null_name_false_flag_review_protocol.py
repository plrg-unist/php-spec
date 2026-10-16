#!/usr/bin/env python3
"""The first NULL-name deprecation throw leaves its received empty key absent."""
import json
import os
from pathlib import Path

import global_constant_scalar_name_protocol as driver
import define_null_name_false_flag_review_sources as sources

common, text, b64 = driver.common, driver.text, driver.b64

PREFIX = r"""
dec $test_null_name_false_throw_front(pstate) : bool
def $test_null_name_false_throw_front(S) = true
  -- if S.TODO = (THROW_SEARCH n) :: (ERROR_HANDLER_RESULT perrorcall) :: ptask_tail*
  -- if perrorcall.RESUME = DYNAMIC_NULL_DEFINE_RESULT pconfigcall
def $test_null_name_false_throw_front(S) = false -- otherwise
dec $test_null_name_false_throw_seek(pstate, nat) : pstate
def $test_null_name_false_throw_seek(S, 0) = S
def $test_null_name_false_throw_seek(S, n) = S
  -- if $(n > 0)
  -- if $test_null_name_false_throw_front(S) \/ (S.COMPLETION =/= NORMAL /\ S.COMPLETION =/= BUDGET)
def $test_null_name_false_throw_seek(S, n) = $test_null_name_false_throw_seek($drive_steps($test_running(S),1),$nabs($(n - 1)))
  -- if $(n > 0)
  -- if ~$test_null_name_false_throw_front(S)
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
"""


def checks(program, path, name):
    assert name == 'null-name-false-request-flag-first-throw-leaves-empty-key-absent'
    values = [
        'S_initial = $php_run(' + program + ',0,' + json.dumps(b64(os.fsencode(path))) + ')',
        'S_initial.COMPLETION = BUDGET',
        'S_found = $test_null_name_false_throw_seek(S_initial,2500)',
        'S_found.COMPLETION = NORMAL \\/ S_found.COMPLETION = BUDGET',
        'S = S_found[.COMPLETION = NORMAL]', '$test_null_name_false_throw_front(S)',
        'S.TODO = (THROW_SEARCH n_throw) :: (ERROR_HANDLER_RESULT perrorcall) :: ptask_tail*',
        'perrorcall.RESUME = DYNAMIC_NULL_DEFINE_RESULT pconfigcall',
        'perrorcall.LEVEL = 8192',
        'perrorcall.MESSAGE = ' + text('define(): Passing null to parameter #1 ($constant_name) of type string is deprecated'),
        'perrorcall.EVENT = DIAGNOSTIC "Deprecated" perrorcall.MESSAGE pconfigcall.LINE',
        'perrorcall.SITE = pconfigcall.SITE', 'perrorcall.LINE = pconfigcall.LINE',
        'S.ORIGIN = (pconfigcall.SITE)', '$throwable_live(S,n_throw)',
        'S.OBJECTS[n_throw] = THROWABLE pthrowable', 'pthrowable.KIND = "Exception"',
        '$string_bytes($throwable_field(S,n_throw,"message")) = (' + text('null-name-before-registration') + ')',
        '$throwable_field(S,n_throw,"previous") = PNULL',
        'pconfigcall.KIND = INTRINSIC_DEFINE', 'pconfigcall.OWNER = eps', 'pconfigcall.PACKS = eps',
        'pconfigcall.NAMED', 'pconfigcall.SELECTION = (n_selection)',
        '$(n_selection < |S.SELECTEDCALLS|)', 'S.SELECTEDCALLS[n_selection].KIND = INTRINSIC_DEFINE',
        'pconfigcall.SENT = [NAMED_SENT (KNOWN PNULL),NAMED_SENT (KNOWN pvalue_candidate),NAMED_SENT (KNOWN pvalue_flag)]',
        'pvalue_candidate = PSTRING_CARRIER (REQUEST_STRING n_candidate) preqbytes_candidate',
        'preqbytes_candidate = ' + text('outer-value41'), '$string_carrier_valid(S,pvalue_candidate)',
        'pvalue_flag = PSTRING_CARRIER (REQUEST_STRING n_flag) preqbytes_flag',
        'preqbytes_flag = ' + text('0'), '$string_carrier_valid(S,pvalue_flag)', '~$truth(S,pvalue_flag)',
        '$dynamic_define_false_scalar_flag(pvalue_flag)', '$dynamic_scalar_define_flag_carrier_valid(S,pconfigcall)',
        '$dynamic_scalar_define_values(pconfigcall) = ((PNULL,pvalue_candidate))',
        '$config_invoke_valid(S,pconfigcall)', '~$config_strict(S,pconfigcall)',
        '$dynamic_null_define_call(pconfigcall)', '$dynamic_null_define_valid(S,pconfigcall)',
        '~$dynamic_scalar_define_call(pconfigcall)',
        '$call_task_valid(S,perrorcall.RESUME)', '$error_call_valid(S,perrorcall)',
        'S.USERCONSTANTS = [puserconstant_inner]',
        'puserconstant_inner.NAME = ' + text('NullFalseInner41'),
        'puserconstant_inner.VALUE = PINT 617', 'puserconstant_inner.CLASS = PVSCALAR',
        '$source_constant_lookup(S,' + text('NullFalseInner41') + ') = (VALUE (PINT 617))',
        '$source_constant_lookup(S,eps) = eps', '~$dynamic_null_define_duplicate_valid(S,pconfigcall,1)',
        '$lookup(S.ENV,' + text('pending') + ') = (n_pending)', 'S.STORE[n_pending] = DEFINED (POBJECT n_throw)',
        '$throwable_field(S,n_throw,"trace") = PARRAY n_trace',
        'S.ARRAYS[n_trace].ITEMS = [ENTRY (KINT 0) (DIRECT (PARRAY n_handler)),ENTRY (KINT 1) (DIRECT (PARRAY n_api)),ENTRY (KINT 2) (DIRECT (PARRAY n_caller))]',
        '$trace_array_field(S,n_handler,' + text('function') + ') = PSTRING ' + text('throwNullFalseName41'),
        '$trace_array_field(S,n_api,' + text('function') + ') = PSTRING ' + text('define'),
        '$trace_array_field(S,n_api,' + text('line') + ') = PINT pconfigcall.LINE',
        '$trace_array_field(S,n_api,' + text('args') + ') = PARRAY n_args',
        'S.ARRAYS[n_args].ITEMS = [ENTRY (KINT 0) (DIRECT PNULL),ENTRY (KINT 1) (DIRECT pvalue_candidate),ENTRY (KINT 2) (DIRECT pvalue_flag)]',
        '$trace_array_field(S,n_caller,' + text('function') + ') = PSTRING ' + text('nullFalseCaller41'),
        'S.OUTPUTBUFFERS = eps', 'S.ERRORFATALTRACE = eps', *common.public('S'),
    ]
    for variable, expected in [('name', 'changed-null-name'), ('candidate', 'changed-candidate'), ('call', 'constant')]:
        values += ['$lookup(S.ENV,' + text(variable) + ') = (n_live_' + variable + ')',
            'S.STORE[n_live_' + variable + '] = DEFINED pvalue_live_' + variable,
            '$string_bytes(pvalue_live_' + variable + ') = (' + text(expected) + ')']
    values += [
        '$lookup(S.ENV,' + text('flag') + ') = (n_live_flag)', 'S.STORE[n_live_flag] = DEFINED (PBOOL true)',
        '$lookup(S.ENV,' + text('warnings') + ') = (n_warnings)', 'S.STORE[n_warnings] = DEFINED (PINT 1)',
        '$lookup(S.ENV,' + text('result') + ') = (n_result)', 'S.STORE[n_result] = DEFINED (PINT 99)',
        'S_discard = S[.TODO = (THROW_SEARCH n_throw) :: ptask_tail*]',
        'S_expected = $error_handler_restore($identity_read_discard(S_discard,perrorcall.RESUME),perrorcall.CALLBACK)',
        '$error_read_discard(S_expected,perrorcall.RESUME) = S_expected',
        *common.step('S_after', 'S'), 'S_after = S_expected',
        'S_after.USERCONSTANTS = [puserconstant_inner]', '$source_constant_lookup(S_after,eps) = eps',
        'S_after.TODO = (THROW_SEARCH n_throw) :: ptask_tail*',
        'S_after.OBJECTS[n_throw] = THROWABLE pthrowable', 'S_after.STORE[n_result] = DEFINED (PINT 99)',
        *common.public('S_after'),
        'n_bad_string = |S.STRINGDATA|',
    ]
    for slot, label, value in ((1, 'candidate', 'outer-value41'), (2, 'flag', '0')):
        values += ['pvalue_bad_' + label + ' = PSTRING_CARRIER (REQUEST_STRING n_bad_string) ' + text(value),
            '~$string_carrier_valid(S,pvalue_bad_' + label + ')',
            '~$dynamic_null_define_valid(S,pconfigcall[.SENT = $named_slot_set(pconfigcall.SENT,' + str(slot) + ',KNOWN pvalue_bad_' + label + ')])']
    values += ['$dynamic_null_define_call(pconfigcall[.SENT = $named_slot_set(pconfigcall.SENT,2,KNOWN (PBOOL false))])']
    for field in ('.SITE = PORIGIN 0 eps', '.LINE = $(pconfigcall.LINE + 1)',
            '.SELECTION = eps', '.OWNER = (0)', '.KIND = INTRINSIC_CONSTANT'):
        values += ['~$dynamic_null_define_valid(S,pconfigcall[' + field + '])']
    for flag in ('PNULL', 'PBOOL true', 'PINT 1', 'PFLOAT 4607182418800017408', 'PFLOAT 9221120237041090560', 'PSTRING ' + text('false')):
        values += ['~$dynamic_null_define_call(pconfigcall[.SENT = $named_slot_set(pconfigcall.SENT,2,KNOWN (' + flag + '))])']
    for raw_name in ('PBOOL false', 'PFLOAT 4612811918334230528', 'PSTRING ' + text('Ordinary41')):
        values += ['~$dynamic_null_define_call(pconfigcall[.SENT = $named_slot_set(pconfigcall.SENT,0,KNOWN (' + raw_name + '))])']
    for field in ('.LEVEL = 2', '.MESSAGE = ' + text('changed'), '.LINE = $(perrorcall.LINE + 1)',
            '.EVENT = DIAGNOSTIC "Deprecated" perrorcall.MESSAGE $(perrorcall.LINE + 1)'):
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
