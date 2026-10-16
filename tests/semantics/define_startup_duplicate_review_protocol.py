#!/usr/bin/env python3
"""A reached startup duplicate keeps the builtin and exact throwing cleanup."""
import json
import os
from pathlib import Path

import global_constant_scalar_name_protocol as driver
import define_startup_duplicate_review_sources as sources

common, text, b64 = driver.common, driver.text, driver.b64

PREFIX = r"""
dec $test_startup_duplicate_throw_front(pstate) : bool
def $test_startup_duplicate_throw_front(S) = true
  -- if S.TODO = (THROW_SEARCH n) :: (ERROR_HANDLER_RESULT perrorcall) :: ptask_tail*
  -- if perrorcall.RESUME = DYNAMIC_CONSTANT_DUPLICATE pconfigcall n_constants
  -- if $dynamic_define_values(pconfigcall) = (($ptascii("NAN"),PINT 823))
def $test_startup_duplicate_throw_front(S) = false -- otherwise
dec $test_startup_duplicate_throw_seek(pstate, nat) : pstate
def $test_startup_duplicate_throw_seek(S, 0) = S
def $test_startup_duplicate_throw_seek(S, n) = S
  -- if $(n > 0)
  -- if $test_startup_duplicate_throw_front(S) \/ (S.COMPLETION =/= NORMAL /\ S.COMPLETION =/= BUDGET)
def $test_startup_duplicate_throw_seek(S, n) = $test_startup_duplicate_throw_seek($drive_steps($test_running(S),1),$nabs($(n - 1)))
  -- if $(n > 0)
  -- if ~$test_startup_duplicate_throw_front(S)
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
"""


def checks(program, path, name):
    assert name == 'request-startup-nan-duplicate-throw-preserves-builtin'
    values = [
        'S_initial = $php_run(' + program + ',0,' + json.dumps(b64(os.fsencode(path))) + ')',
        'S_initial.COMPLETION = BUDGET', 'S_found = $test_startup_duplicate_throw_seek(S_initial,2500)',
        'S_found.COMPLETION = NORMAL \\/ S_found.COMPLETION = BUDGET',
        'S = S_found[.COMPLETION = NORMAL]', '$test_startup_duplicate_throw_front(S)',
        'S.TODO = (THROW_SEARCH n_throw) :: (ERROR_HANDLER_RESULT perrorcall) :: ptask_tail*',
        'perrorcall.RESUME = DYNAMIC_CONSTANT_DUPLICATE pconfigcall n_prefix', 'n_prefix = 0',
        'perrorcall.LEVEL = 2', 'perrorcall.MESSAGE = $global_constant_duplicate_message(' + text('NAN') + ')',
        'perrorcall.EVENT = DIAGNOSTIC "Warning" perrorcall.MESSAGE pconfigcall.LINE',
        'perrorcall.SITE = pconfigcall.SITE', 'perrorcall.LINE = pconfigcall.LINE',
        'S.ORIGIN = (pconfigcall.SITE)', '$throwable_live(S,n_throw)',
        'S.OBJECTS[n_throw] = THROWABLE pthrowable', 'pthrowable.KIND = "Exception"',
        '$string_bytes($throwable_field(S,n_throw,"message")) = (' + text('startup-duplicate') + ')',
        '$throwable_field(S,n_throw,"previous") = PNULL',
        'pconfigcall.KIND = INTRINSIC_DEFINE', 'pconfigcall.OWNER = eps', 'pconfigcall.PACKS = eps',
        'pconfigcall.NAMED', 'pconfigcall.SELECTION = (n_selection)',
        '$(n_selection < |S.SELECTEDCALLS|)', 'S.SELECTEDCALLS[n_selection].KIND = INTRINSIC_DEFINE',
        'pconfigcall.SENT = [NAMED_SENT (KNOWN pvalue_name),NAMED_SENT (KNOWN (PINT 823)),NAMED_SENT (KNOWN (PBOOL false))]',
        'pvalue_name = PSTRING_CARRIER (REQUEST_STRING n_name_string) preqbytes_name',
        'preqbytes_name = ' + text('NAN'), '$string_carrier_valid(S,pvalue_name)',
        '$config_invoke_valid(S,pconfigcall)', '~$config_strict(S,pconfigcall)',
        '$dynamic_define_source(S,pconfigcall.SITE)', '$dynamic_scalar_define_arguments(S,pconfigcall,0)',
        '$dynamic_startup_define_duplicate_valid(S,pconfigcall,n_prefix)',
        '$dynamic_constant_duplicate_valid(S,pconfigcall,n_prefix)',
        '$call_task_valid(S,perrorcall.RESUME)', '$error_call_valid(S,perrorcall)',
        '$builtin_value_bytes(' + text('NAN') + ') = (PFLOAT 9221120237041090560)',
        '$source_constant_lookup(S,' + text('NAN') + ') = (VALUE (PFLOAT 9221120237041090560))',
        'S.USERCONSTANTS = [puserconstant_sibling]',
        'puserconstant_sibling.NAME = ' + text('StartupDuplicateSibling43'),
        'puserconstant_sibling.VALUE = PINT 811', 'puserconstant_sibling.CLASS = PVSCALAR',
        '$user_constant_at(S.USERCONSTANTS,' + text('NAN') + ') = eps',
        '$source_constant_lookup(S,' + text('StartupDuplicateSibling43') + ') = (VALUE (PINT 811))',
        '$lookup(S.ENV,' + text('pending') + ') = (n_pending)', 'S.STORE[n_pending] = DEFINED (POBJECT n_throw)',
        '$throwable_field(S,n_throw,"trace") = PARRAY n_trace',
        'S.ARRAYS[n_trace].ITEMS = [ENTRY (KINT 0) (DIRECT (PARRAY n_handler)),ENTRY (KINT 1) (DIRECT (PARRAY n_api)),ENTRY (KINT 2) (DIRECT (PARRAY n_caller))]',
        '$trace_array_field(S,n_handler,' + text('function') + ') = PSTRING ' + text('throwStartupDuplicate43'),
        '$trace_array_field(S,n_api,' + text('function') + ') = PSTRING ' + text('define'),
        '$trace_array_field(S,n_api,' + text('line') + ') = PINT pconfigcall.LINE',
        '$trace_array_field(S,n_api,' + text('args') + ') = PARRAY n_args',
        'S.ARRAYS[n_args].ITEMS = [ENTRY (KINT 0) (DIRECT pvalue_name),ENTRY (KINT 1) (DIRECT (PINT 823)),ENTRY (KINT 2) (DIRECT (PBOOL false))]',
        '$trace_array_field(S,n_caller,' + text('function') + ') = PSTRING ' + text('startupDuplicateCaller43'),
        'S.OUTPUTBUFFERS = eps', 'S.ERRORFATALTRACE = eps', *common.public('S'),
        '$lookup(S.ENV,' + text('name') + ') = (n_name)', 'S.STORE[n_name] = DEFINED pvalue_live_name',
        '$string_bytes(pvalue_live_name) = (' + text('PHP_INT_SIZE') + ')',
        '$lookup(S.ENV,' + text('candidate') + ') = (n_candidate)', 'S.STORE[n_candidate] = DEFINED (PINT 997)',
        '$lookup(S.ENV,' + text('flag') + ') = (n_live_flag)', 'S.STORE[n_live_flag] = DEFINED (PBOOL true)',
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
        '$source_constant_lookup(S_after,' + text('NAN') + ') = (VALUE (PFLOAT 9221120237041090560))',
        *common.public('S_after'),
        '$dynamic_startup_define_duplicate_valid(S,pconfigcall,1)',
        '$dynamic_constant_duplicate_valid(S,pconfigcall,1)',
        'n_bad_prefix = $(|S.USERCONSTANTS| + 1)',
        '~$dynamic_startup_define_duplicate_valid(S,pconfigcall,n_bad_prefix)',
        '~$dynamic_constant_duplicate_valid(S,pconfigcall,n_bad_prefix)',
        'n_bad_string = |S.STRINGDATA|',
    ]
    for index, label, value in ((0, 'name', 'NAN'), (1, 'candidate', 'candidate43')):
        values += ['pvalue_bad_' + label + ' = PSTRING_CARRIER (REQUEST_STRING n_bad_string) ' + text(value),
            '~$string_carrier_valid(S,pvalue_bad_' + label + ')',
            '~$dynamic_startup_define_duplicate_valid(S,pconfigcall[.SENT = $named_slot_set(pconfigcall.SENT,' + str(index) + ',KNOWN pvalue_bad_' + label + ')],n_prefix)']
    for field in ('.SITE = PORIGIN 0 eps', '.LINE = $(pconfigcall.LINE + 1)',
            '.SELECTION = eps', '.OWNER = (0)', '.KIND = INTRINSIC_CONSTANT'):
        values += ['~$dynamic_startup_define_duplicate_valid(S,pconfigcall[' + field + '],n_prefix)']
    for flag in ('PBOOL true', 'PNULL', 'PINT 0', 'PFLOAT 9221120237041090560', 'PSTRING ' + text('0')):
        values += ['~$dynamic_startup_define_duplicate_valid(S,pconfigcall[.SENT = $named_slot_set(pconfigcall.SENT,2,KNOWN (' + flag + '))],n_prefix)',
            '~$dynamic_constant_duplicate_valid(S,pconfigcall[.SENT = $named_slot_set(pconfigcall.SENT,2,KNOWN (' + flag + '))],n_prefix)']
    for raw_name in ('PSTRING ' + text('null'), 'PSTRING ' + text('True'), 'PSTRING ' + text('PHP_VERSION'),
            'PSTRING ' + text('Unbound43'), 'PSTRING ' + text('C::K'), 'PINT 8'):
        values += ['~$dynamic_startup_define_duplicate_valid(S,pconfigcall[.SENT = $named_slot_set(pconfigcall.SENT,0,KNOWN (' + raw_name + '))],n_prefix)']
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
