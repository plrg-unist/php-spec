#!/usr/bin/env python3
"""A reached runtime NaN Warning throw discards the later class-name body check."""
import json
import os
from pathlib import Path

import global_constant_scalar_name_protocol as driver
import define_class_nan_flag_review_sources as sources

common, text, b64 = driver.common, driver.text, driver.b64

PREFIX = r"""
dec $test_class_nan_throw_front(pstate) : bool
def $test_class_nan_throw_front(S) = true
  -- if S.TODO = (THROW_SEARCH n) :: (ERROR_HANDLER_RESULT perrorcall) :: ptask_tail*
  -- if perrorcall.RESUME = DYNAMIC_CLASS_DEFINE_NAN_RESULT pconfigcall
def $test_class_nan_throw_front(S) = false -- otherwise
dec $test_class_nan_throw_seek(pstate, nat) : pstate
def $test_class_nan_throw_seek(S, 0) = S
def $test_class_nan_throw_seek(S, n) = S
  -- if $(n > 0)
  -- if $test_class_nan_throw_front(S) \/ (S.COMPLETION =/= NORMAL /\ S.COMPLETION =/= BUDGET)
def $test_class_nan_throw_seek(S, n) = $test_class_nan_throw_seek($drive_steps($test_running(S),1),$nabs($(n - 1)))
  -- if $(n > 0)
  -- if ~$test_class_nan_throw_front(S)
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
"""


def checks(program, path, name):
    assert name == 'runtime-nan-flag-throw-cancels-class-name-error'
    values = [
        'S_initial = $php_run(' + program + ',0,' + json.dumps(b64(os.fsencode(path))) + ')',
        'S_initial.COMPLETION = BUDGET',
        'S_found = $test_class_nan_throw_seek(S_initial,2000)',
        'S_found.COMPLETION = NORMAL \\/ S_found.COMPLETION = BUDGET',
        'S = S_found[.COMPLETION = NORMAL]', '$test_class_nan_throw_front(S)',
        'S.TODO = (THROW_SEARCH n_throw) :: (ERROR_HANDLER_RESULT perrorcall) :: ptask_tail*',
        'perrorcall.RESUME = DYNAMIC_CLASS_DEFINE_NAN_RESULT pconfigcall',
        'perrorcall.LEVEL = 2',
        'perrorcall.MESSAGE = ' + text('unexpected NAN value was coerced to bool'),
        'perrorcall.EVENT = DIAGNOSTIC "Warning" perrorcall.MESSAGE pconfigcall.LINE',
        'perrorcall.SITE = pconfigcall.SITE', 'perrorcall.LINE = pconfigcall.LINE',
        'pconfigcall.SITE = PORIGIN 0 pcpath',
        'S.ORIGIN = (pconfigcall.SITE)', '$throwable_live(S,n_throw)',
        'S.OBJECTS[n_throw] = THROWABLE pthrowable', 'pthrowable.KIND = "Exception"',
        '$string_bytes($throwable_field(S,n_throw,"message")) = (' + text('nan-before-class') + ')',
        '$throwable_field(S,n_throw,"previous") = PNULL',
        'pconfigcall.KIND = INTRINSIC_DEFINE', 'pconfigcall.OWNER = eps', 'pconfigcall.PACKS = eps',
        'pconfigcall.NAMED', 'pconfigcall.SELECTION = (n_selection)',
        '$(n_selection < |S.SELECTEDCALLS|)', 'S.SELECTEDCALLS[n_selection].KIND = INTRINSIC_DEFINE',
        'pconfigcall.SENT = [NAMED_SENT (KNOWN pvalue_name),NAMED_SENT (KNOWN pvalue_candidate),NAMED_SENT (KNOWN (PFLOAT n_nan))]',
        'n_nan = 18444492273895866368', '$number_bool(NFLOAT n_nan) = (true,true)',
        '$float_sub(9218868437227405312,9218868437227405312) = n_nan',
        '$lookup(S.ENV,' + text('infinity') + ') = (n_infinity)',
        'S.STORE[n_infinity] = DEFINED (PFLOAT 9218868437227405312)',
        'pvalue_name = PSTRING_CARRIER (REQUEST_STRING n_name) preqbytes_name',
        'preqbytes_name = ' + text('Captured::NaN39'), '$string_carrier_valid(S,pvalue_name)',
        'pvalue_candidate = PSTRING_CARRIER (REQUEST_STRING n_candidate) preqbytes_candidate',
        'preqbytes_candidate = ' + text('captured-value39'), '$string_carrier_valid(S,pvalue_candidate)',
        '$config_invoke_valid(S,pconfigcall)', '~$config_strict(S,pconfigcall)',
        '$dynamic_class_define_nan_call(pconfigcall)', '$dynamic_class_define_nan_valid(S,pconfigcall)',
        '$dynamic_nan_define_flag_call(pconfigcall)', '~$dynamic_nan_define_flag_valid(S,pconfigcall)',
        '~$call_task_valid(S,DYNAMIC_NAN_DEFINE_FLAG_RESULT pconfigcall)',
        '~$dynamic_define_quiet_flag(PFLOAT n_nan)', '~$dynamic_class_define_null_call(pconfigcall)',
        '$call_task_valid(S,DYNAMIC_CLASS_DEFINE_NAN_RESULT pconfigcall)', '$error_call_valid(S,perrorcall)',
        'S.USERCONSTANTS = [puserconstant_inner]',
        'puserconstant_inner.NAME = ' + text('ClassNaNInner39'),
        'puserconstant_inner.VALUE = PINT 353', 'puserconstant_inner.CLASS = PVSCALAR',
        '$source_constant_lookup(S,' + text('ClassNaNInner39') + ') = (VALUE (PINT 353))',
        '$lookup(S.ENV,' + text('pending') + ') = (n_pending)', 'S.STORE[n_pending] = DEFINED (POBJECT n_throw)',
        '$throwable_field(S,n_throw,"trace") = PARRAY n_trace',
        'S.ARRAYS[n_trace].ITEMS = [ENTRY (KINT 0) (DIRECT (PARRAY n_handler)),ENTRY (KINT 1) (DIRECT (PARRAY n_api)),ENTRY (KINT 2) (DIRECT (PARRAY n_caller))]',
        '$trace_array_field(S,n_handler,' + text('function') + ') = PSTRING ' + text('throwClassNaN39'),
        '$trace_array_field(S,n_api,' + text('function') + ') = PSTRING ' + text('define'),
        '$trace_array_field(S,n_api,' + text('line') + ') = PINT pconfigcall.LINE',
        '$trace_array_field(S,n_api,' + text('args') + ') = PARRAY n_args',
        'S.ARRAYS[n_args].ITEMS = [ENTRY (KINT 0) (DIRECT pvalue_name),ENTRY (KINT 1) (DIRECT pvalue_candidate),ENTRY (KINT 2) (DIRECT (PFLOAT n_nan))]',
        '$trace_array_field(S,n_caller,' + text('function') + ') = PSTRING ' + text('classNaNCaller39'),
        'S.OUTPUTBUFFERS = eps', 'S.ERRORFATALTRACE = eps', *common.public('S'),
    ]
    for variable, expected in [('name', 'changed-nan-name'), ('candidate', 'changed-nan-value'), ('call', 'constant')]:
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
    ]
    for slot, label, value in ((0, 'name', 'Captured::NaN39'), (1, 'candidate', 'captured-value39')):
        values += ['pvalue_bad_' + label + ' = PSTRING_CARRIER (REQUEST_STRING n_bad_string) ' + text(value),
            '~$string_carrier_valid(S,pvalue_bad_' + label + ')',
            '~$dynamic_class_define_nan_valid(S,pconfigcall[.SENT = $named_slot_set(pconfigcall.SENT,' + str(slot) + ',KNOWN pvalue_bad_' + label + ')])']
    for field in ('.SITE = PORIGIN 0 eps', '.LINE = $(pconfigcall.LINE + 1)',
            '.SELECTION = eps', '.OWNER = (0)', '.KIND = INTRINSIC_CONSTANT'):
        values += ['~$dynamic_class_define_nan_valid(S,pconfigcall[' + field + '])']
    for flag in ('PNULL', 'PBOOL true', 'PINT 1', 'PFLOAT 4607182418800017408'):
        values += ['~$dynamic_class_define_nan_call(pconfigcall[.SENT = $named_slot_set(pconfigcall.SENT,2,KNOWN (' + flag + '))])']
    for name_value in ('PSTRING ' + text('Ordinary39'), 'PSTRING (' + text('Bad::39') + ' ++ [0])', 'PNULL'):
        values += ['~$dynamic_class_define_nan_call(pconfigcall[.SENT = $named_slot_set(pconfigcall.SENT,0,KNOWN (' + name_value + '))])']
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
