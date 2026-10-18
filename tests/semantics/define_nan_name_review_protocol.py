#!/usr/bin/env python3
"""A genuine first NaN-name Warning throw cancels the later duplicate phase."""
import json
import os
from pathlib import Path

import global_constant_scalar_name_protocol as driver
import define_nan_name_review_sources as sources

common, text, b64 = driver.common, driver.text, driver.b64

PREFIX = r"""
dec $test_nan_name_first_throw_front(pstate) : bool
def $test_nan_name_first_throw_front(S) = true
  -- if S.TODO = (THROW_SEARCH n) :: (ERROR_HANDLER_RESULT perrorcall) :: ptask_tail*
  -- if perrorcall.RESUME = DYNAMIC_NAN_DEFINE_NAME_RESULT pconfigcall pvalue_string z_precision
def $test_nan_name_first_throw_front(S) = false -- otherwise
dec $test_nan_name_first_throw_seek(pstate, nat) : pstate
def $test_nan_name_first_throw_seek(S, 0) = S
def $test_nan_name_first_throw_seek(S, n) = S
  -- if $(n > 0)
  -- if $test_nan_name_first_throw_front(S) \/ (S.COMPLETION =/= NORMAL /\ S.COMPLETION =/= BUDGET)
def $test_nan_name_first_throw_seek(S, n) = $test_nan_name_first_throw_seek($drive_steps($test_running(S),1),$nabs($(n - 1)))
  -- if $(n > 0)
  -- if ~$test_nan_name_first_throw_front(S)
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
"""


def checks(program, path, name):
    assert name == 'runtime-nan-name-first-warning-throw-cancels-duplicate'
    values = [
        'S_initial = $php_run(' + program + ',0,' + json.dumps(b64(os.fsencode(path))) + ')',
        'S_initial.COMPLETION = BUDGET', 'S_found = $test_nan_name_first_throw_seek(S_initial,2500)',
        'S_found.COMPLETION = NORMAL \\/ S_found.COMPLETION = BUDGET',
        'S = S_found[.COMPLETION = NORMAL]', '$test_nan_name_first_throw_front(S)',
        'S.TODO = (THROW_SEARCH n_throw) :: (ERROR_HANDLER_RESULT perrorcall) :: ptask_tail*',
        'perrorcall.RESUME = DYNAMIC_NAN_DEFINE_NAME_RESULT pconfigcall pvalue_string z_precision',
        'z_precision = 14', '$precision_value(S) = 1',
        'perrorcall.LEVEL = 2', 'perrorcall.MESSAGE = ' + text('unexpected NAN value was coerced to string'),
        'perrorcall.EVENT = DIAGNOSTIC "Warning" perrorcall.MESSAGE pconfigcall.LINE',
        'perrorcall.SITE = pconfigcall.SITE', 'perrorcall.LINE = pconfigcall.LINE',
        'S.ORIGIN = (pconfigcall.SITE)', '$throwable_live(S,n_throw)',
        'S.OBJECTS[n_throw] = THROWABLE pthrowable', 'pthrowable.KIND = "Exception"',
        '$string_bytes($throwable_field(S,n_throw,"message")) = (' + text('nan-name-before-body') + ')',
        '$throwable_field(S,n_throw,"previous") = PNULL',
        'pconfigcall.KIND = INTRINSIC_DEFINE', 'pconfigcall.OWNER = eps', 'pconfigcall.PACKS = eps',
        'pconfigcall.NAMED', 'pconfigcall.SELECTION = (n_selection)',
        '$(n_selection < |S.SELECTEDCALLS|)', 'S.SELECTEDCALLS[n_selection].KIND = INTRINSIC_DEFINE',
        'pconfigcall.SENT = [NAMED_SENT (KNOWN (PFLOAT n_nan)),NAMED_SENT (KNOWN (PINT 983)),NAMED_SENT (KNOWN (PBOOL false))]',
        'n_nan = 18444492273895866368', '$float_decode(n_nan) = NOTNUMBER n_nan',
        '$float_sub(9218868437227405312,9218868437227405312) = n_nan',
        '$number_text(NFLOAT n_nan,14) = (' + text('NAN') + ',true)',
        '$number_text(NFLOAT n_nan,1) = (' + text('N') + ',true)',
        '$config_invoke_valid(S,pconfigcall)', '~$config_strict(S,pconfigcall)',
        '$dynamic_nan_define_name_call(pconfigcall)', '$dynamic_nan_define_name_valid(S,pconfigcall)',
        '~$dynamic_nan_define_name_entry(S,pconfigcall)',
        'pvalue_string = PSTRING_CARRIER (REQUEST_STRING n_string) ' + text('NAN'),
        '$string_carrier_valid(S,pvalue_string)',
        '$dynamic_nan_define_name_received(S,pconfigcall,pvalue_string,z_precision)',
        '$dynamic_nan_define_name_received(S,pconfigcall,pvalue_string,3)',
        '$dynamic_nan_define_name_received(S,pconfigcall,pvalue_string,-1)',
        '~$dynamic_nan_define_name_received(S,pconfigcall,pvalue_string,1)',
        '~$dynamic_nan_define_name_received(S,pconfigcall,pvalue_string,2)',
        '~$dynamic_scalar_define_received(S,pconfigcall,pvalue_string,z_precision)',
        '~$dynamic_scalar_define_duplicate_valid(S,pconfigcall,pvalue_string,z_precision,0)',
        '$call_task_valid(S,perrorcall.RESUME)', '$error_call_valid(S,perrorcall)',
        'S.USERCONSTANTS = [puserconstant_sibling]',
        'puserconstant_sibling.NAME = ' + text('NaNNameSibling46'),
        'puserconstant_sibling.VALUE = PINT 977', 'puserconstant_sibling.CLASS = PVSCALAR',
        '$user_constant_at(S.USERCONSTANTS,' + text('NAN') + ') = eps',
        '$source_constant_lookup(S,' + text('NAN') + ') = (VALUE (PFLOAT 9221120237041090560))',
        '$source_constant_lookup(S,' + text('NaNNameSibling46') + ') = (VALUE (PINT 977))',
        '$lookup(S.ENV,' + text('pending') + ') = (n_pending)', 'S.STORE[n_pending] = DEFINED (POBJECT n_throw)',
        '$throwable_field(S,n_throw,"trace") = PARRAY n_trace',
        'S.ARRAYS[n_trace].ITEMS = [ENTRY (KINT 0) (DIRECT (PARRAY n_handler)),ENTRY (KINT 1) (DIRECT (PARRAY n_api)),ENTRY (KINT 2) (DIRECT (PARRAY n_caller))]',
        '$trace_array_field(S,n_handler,' + text('function') + ') = PSTRING ' + text('throwNaNName46'),
        '$trace_array_field(S,n_api,' + text('function') + ') = PSTRING ' + text('define'),
        '$trace_array_field(S,n_api,' + text('line') + ') = PINT pconfigcall.LINE',
        '$trace_array_field(S,n_api,' + text('args') + ') = PARRAY n_args',
        'S.ARRAYS[n_args].ITEMS = [ENTRY (KINT 0) (DIRECT (PFLOAT n_nan)),ENTRY (KINT 1) (DIRECT (PINT 983)),ENTRY (KINT 2) (DIRECT (PBOOL false))]',
        '$trace_array_field(S,n_caller,' + text('function') + ') = PSTRING ' + text('nanNameCaller46'),
        'S.OUTPUTBUFFERS = eps', 'S.ERRORFATALTRACE = eps', *common.public('S'),
        '$lookup(S.ENV,' + text('name') + ') = (n_name)', 'S.STORE[n_name] = DEFINED (PFLOAT 4612811918334230528)',
        '$lookup(S.ENV,' + text('candidate') + ') = (n_candidate)', 'S.STORE[n_candidate] = DEFINED (PINT 997)',
        '$lookup(S.ENV,' + text('flag') + ') = (n_flag)', 'S.STORE[n_flag] = DEFINED (PBOOL true)',
        '$lookup(S.ENV,' + text('call') + ') = (n_call)', 'S.STORE[n_call] = DEFINED pvalue_live_call',
        '$string_bytes(pvalue_live_call) = (' + text('constant') + ')',
        '$lookup(S.ENV,' + text('count') + ') = (n_count)', 'S.STORE[n_count] = DEFINED (PINT 1)',
        '$lookup(S.ENV,' + text('result') + ') = (n_result)', 'S.STORE[n_result] = DEFINED (PINT 99)',
        'S_discard = S[.TODO = (THROW_SEARCH n_throw) :: ptask_tail*]',
        'S_expected = $error_handler_restore($identity_read_discard(S_discard,perrorcall.RESUME),perrorcall.CALLBACK)',
        '$error_read_discard(S_expected,perrorcall.RESUME) = S_expected',
        *common.step('S_after', 'S'), 'S_after = S_expected',
        'S_after.USERCONSTANTS = [puserconstant_sibling]', 'S_after.TODO = (THROW_SEARCH n_throw) :: ptask_tail*',
        'S_after.OBJECTS[n_throw] = THROWABLE pthrowable', 'S_after.STORE[n_result] = DEFINED (PINT 99)',
        'S_after.STRINGDATA = S.STRINGDATA', '$precision_value(S_after) = 1',
        *common.public('S_after'), 'n_bad_string = |S.STRINGDATA|',
        'pvalue_bad_string = PSTRING_CARRIER (REQUEST_STRING n_bad_string) ' + text('NAN'),
        '~$dynamic_nan_define_name_received(S,pconfigcall,pvalue_bad_string,z_precision)',
        '~$error_call_valid(S,perrorcall[.RESUME = DYNAMIC_NAN_DEFINE_NAME_RESULT pconfigcall pvalue_bad_string z_precision])',
        'pvalue_bad_candidate = PSTRING_CARRIER (REQUEST_STRING n_bad_string) ' + text('candidate46'),
        '~$dynamic_nan_define_name_valid(S,pconfigcall[.SENT = $named_slot_set(pconfigcall.SENT,1,KNOWN pvalue_bad_candidate)])',
    ]
    for field in ('.SITE = PORIGIN 0 eps', '.LINE = $(pconfigcall.LINE + 1)', '.SELECTION = eps', '.OWNER = (0)', '.KIND = INTRINSIC_CONSTANT'):
        values += ['~$dynamic_nan_define_name_valid(S,pconfigcall[' + field + '])']
    for precision in ('-2', '9223372036854775808'):
        values += ['~$dynamic_nan_define_name_received(S,pconfigcall,pvalue_string,' + precision + ')']
    for flag in ('PBOOL true', 'PNULL', 'PINT 0', 'PSTRING ' + text('0'), 'PFLOAT 0'):
        values += ['~$dynamic_nan_define_name_call(pconfigcall[.SENT = $named_slot_set(pconfigcall.SENT,2,KNOWN (' + flag + '))])']
    for raw in ('PNULL', 'PFLOAT 9218868437227405312', 'PFLOAT 18442240474082181120', 'PSTRING ' + text('NAN')):
        values += ['~$dynamic_nan_define_name_call(pconfigcall[.SENT = $named_slot_set(pconfigcall.SENT,0,KNOWN (' + raw + '))])']
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
