#!/usr/bin/env python3
"""Reached NULL-name deprecation, raw false flags and converted duplicate views."""
import argparse
import json
import os
from pathlib import Path
import sys

import define_null_name_protocol as null
import define_null_name_false_flag_sources as sources

driver, common, text, b64 = null.driver, null.common, null.text, null.b64
PREFIX = null.PREFIX.replace(
    '  -- if pconfigcall.KIND = INTRINSIC_DEFINE\n',
    '  -- if $dynamic_null_define_call(pconfigcall)\n'
    '  -- if pconfigcall.SENT = [NAMED_SENT (KNOWN PNULL),NAMED_SENT (KNOWN pvalue),NAMED_SENT (KNOWN pvalue_flag)]\n'
    '  -- if $dynamic_define_false_scalar_flag(pvalue_flag)\n')
PREFIX += r"""
dec $test_null_false_config_front(pstate) : bool
def $test_null_false_config_front(S) = true
  -- if S.TODO = (CONFIG_INVOKE pconfigcall) :: ptask_tail*
  -- if $dynamic_null_define_call(pconfigcall)
  -- if pconfigcall.SENT = [NAMED_SENT (KNOWN PNULL),NAMED_SENT (KNOWN pvalue),NAMED_SENT (KNOWN pvalue_flag)]
  -- if $dynamic_define_false_scalar_flag(pvalue_flag)
def $test_null_false_config_front(S) = false -- otherwise
dec $test_null_false_config_seek(pstate, nat) : pstate
def $test_null_false_config_seek(S, 0) = S
def $test_null_false_config_seek(S, n) = S
  -- if $(n > 0)
  -- if $test_null_false_config_front(S) \/ (S.COMPLETION =/= NORMAL /\ S.COMPLETION =/= BUDGET)
def $test_null_false_config_seek(S, n) = $test_null_false_config_seek($drive_steps($test_running(S),1),$nabs($(n - 1)))
  -- if $(n > 0)
  -- if ~$test_null_false_config_front(S)
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
"""


def front(state, start, value):
    call = 'pconfigcall_' + state
    return [*null.front(state, start, value),
        call + '.SENT = [NAMED_SENT (KNOWN PNULL),NAMED_SENT (KNOWN (' + value + ')),NAMED_SENT (KNOWN pvalue_flag_' + state + ')]',
        '$dynamic_define_false_scalar_flag(pvalue_flag_' + state + ')',
        '$dynamic_scalar_define_flag_carrier_valid(' + state + ',' + call + ')']


def captured_front(state, start):
    call = 'pconfigcall_' + state
    return [state + '_found = $test_null_false_config_seek(' + start + ',3000)',
        state + '_found.COMPLETION = NORMAL \\/ ' + state + '_found.COMPLETION = BUDGET',
        state + ' = ' + state + '_found[.COMPLETION = NORMAL]', '$test_null_false_config_front(' + state + ')',
        state + '.TODO = (CONFIG_INVOKE ' + call + ') :: ptask_' + state + '*',
        call + '.SENT = [NAMED_SENT (KNOWN PNULL),NAMED_SENT (KNOWN pvalue_candidate),NAMED_SENT (KNOWN pvalue_flag_' + state + ')]',
        call + '.KIND = INTRINSIC_DEFINE', call + '.OWNER = eps', call + '.PACKS = eps',
        '$config_invoke_valid(' + state + ',' + call + ')', '$dynamic_null_define_valid(' + state + ',' + call + ')',
        '$dynamic_define_false_scalar_flag(pvalue_flag_' + state + ')',
        '$dynamic_scalar_define_flag_carrier_valid(' + state + ',' + call + ')', *common.public(state)]


def default_deprecation(after, before):
    call = 'pconfigcall_' + before
    return ['~$config_strict(' + before + ',' + call + ')', '~$error_handler_eligible(' + before + ',8192)',
        *common.step(after, before), after + '.TODO = (DYNAMIC_NULL_DEFINE_RESULT ' + call + ') :: ptask_' + before + '*',
        '$call_task_valid(' + after + ',DYNAMIC_NULL_DEFINE_RESULT ' + call + ')',
        after + '.EVENTS = ' + before + '.EVENTS ++ [DIAGNOSTIC "Deprecated" $dynamic_null_constant_message(' + call + ') ' + call + '.LINE]',
        *null.unchanged(after, before, 'STORE ENV USERCONSTANTS STRINGDATA ARRAYS OBJECTS ALLOCATIONS SELECTEDCALLS SOURCES POOLS FILES STATICS'),
        *common.public(after)]


def default_duplicate(after, before, original):
    call = 'pconfigcall_' + original
    return ['~$error_handler_eligible(' + before + ',2)', *common.step(after, before),
        after + '.TODO = (DYNAMIC_NULL_DEFINE_DUPLICATE ' + call + ' 1) :: ptask_' + original + '*',
        '$dynamic_null_define_duplicate_valid(' + after + ',' + call + ',1)',
        after + '.EVENTS = ' + before + '.EVENTS ++ [DIAGNOSTIC "Warning" $global_constant_duplicate_message(eps) ' + call + '.LINE]',
        *null.unchanged(after, before, 'STORE ENV USERCONSTANTS STRINGDATA ARRAYS OBJECTS ALLOCATIONS SELECTEDCALLS SOURCES POOLS FILES STATICS'),
        *common.public(after)]


def strict_error(after, before, value):
    call = 'pconfigcall_' + before
    return ['$config_strict(' + before + ',' + call + ')', '~$call_task_valid(' + before + ',DYNAMIC_NULL_DEFINE_RESULT ' + call + ')',
        *common.step(after, before), after + '.TODO = (THROW_SEARCH n_error_' + after + ') :: ptask_' + before + '*',
        after + '.OBJECTS[n_error_' + after + '] = THROWABLE pthrowable_' + after,
        'pthrowable_' + after + '.KIND = "TypeError"', 'pthrowable_' + after + '.ORIGIN = (' + call + '.SITE)',
        '$string_bytes($throwable_field(' + after + ',n_error_' + after + ',"message")) = (' + text('define(): Argument #1 ($constant_name) must be of type string, null given') + ')',
        '$throwable_field(' + after + ',n_error_' + after + ',"previous") = PNULL',
        '$throwable_field(' + after + ',n_error_' + after + ',"line") = PINT ' + call + '.LINE',
        '$string_bytes($throwable_field(' + after + ',n_error_' + after + ',"file")) = ($call_sourcefile(' + before + '.FILES,' + call + '.SITE))',
        '$throwable_field(' + after + ',n_error_' + after + ',"trace") = PARRAY n_trace_' + after,
        after + '.ARRAYS[n_trace_' + after + '].ITEMS = [ENTRY (KINT 0) (DIRECT (PARRAY n_frame_' + after + '))]',
        '$trace_array_field(' + after + ',n_frame_' + after + ',' + text('function') + ') = PSTRING ' + text('define'),
        '$trace_array_field(' + after + ',n_frame_' + after + ',' + text('args') + ') = PARRAY n_args_' + after,
        after + '.ARRAYS[n_args_' + after + '].ITEMS = [ENTRY (KINT 0) (DIRECT PNULL),ENTRY (KINT 1) (DIRECT (' + value + ')),ENTRY (KINT 2) (DIRECT pvalue_flag_' + before + ')]',
        *null.unchanged(after, before, 'STORE ENV USERCONSTANTS STRINGDATA SELECTEDCALLS EVENTS SOURCES POOLS FILES STATICS ERRORHANDLER'), *common.public(after)]


def checks(program, path, name):
    values = ['S_initial = $php_run(' + program + ',0,' + json.dumps(b64(os.fsencode(path))) + ')', 'S_initial.COMPLETION = BUDGET']
    if name == 'literal-null-names-false-flags-and-default-duplicates':
        values += [*front('S', 'S_initial', 'PINT 601'), 'pvalue_flag_S = PINT 0', 'S.USERCONSTANTS = eps',
            *default_deprecation('S_deprecated', 'S'), *common.step('S_first', 'S_deprecated', 'PBOOL true'),
            'S_first.TODO = ptask_S*',
            'S_first.USERCONSTANTS = [{NAME eps,ORIGIN pconfigcall_S.SITE,VALUE (PINT 601),CLASS PVSCALAR,READS eps,RECEIVES eps}]',
            *null.unchanged('S_first', 'S_deprecated', 'STORE ENV STRINGDATA ARRAYS OBJECTS ALLOCATIONS SELECTEDCALLS SOURCES POOLS FILES STATICS'),
            '$user_constants_valid(S_first,S_first.USERCONSTANTS)']
        start = 'S_first'
        for state, number, flag in [('S_empty', 602, '$string_bytes(pvalue_flag_S_empty) = (eps)'),
                ('S_zero', 603, 'pvalue_flag_S_zero = PFLOAT 9223372036854775808'),
                ('S_string', 604, '$string_bytes(pvalue_flag_S_string) = (' + text('0') + ')')]:
            values += [*front(state, start, 'PINT ' + str(number)), flag,
                *default_deprecation(state + '_deprecated', state),
                *default_duplicate(state + '_duplicate', state + '_deprecated', state),
                *common.step(state + '_return', state + '_duplicate', 'PBOOL false'),
                state + '_return.TODO = ptask_' + state + '*',
                *null.unchanged(state + '_return', state + '_duplicate', 'STORE ENV USERCONSTANTS STRINGDATA SELECTEDCALLS'),
                state + '_return.USERCONSTANTS = S_first.USERCONSTANTS']
            start = state + '_return'
        values += ['pconfigcall_bad_flag = pconfigcall_S[.SENT = $named_slot_set(pconfigcall_S.SENT,2,KNOWN (PSTRING ' + text('0') + '))]',
            '$dynamic_null_define_call(pconfigcall_bad_flag)', '~$dynamic_null_define_valid(S,pconfigcall_bad_flag)',
            *null.budget('S'), *null.budget('S_zero_duplicate')]
        for flag in ('PBOOL true', 'PNULL', 'PINT 1', 'PFLOAT 9221120237041090560', 'PSTRING ' + text('false'), 'PARRAY 0', 'POBJECT 0'):
            values += ['~$dynamic_null_define_call(pconfigcall_S[.SENT = $named_slot_set(pconfigcall_S.SENT,2,KNOWN (' + flag + '))])']
        values += ['$dynamic_null_define_call(pconfigcall_S[.SENT = $named_slot_set(pconfigcall_S.SENT,2,KNOWN (PBOOL false))])',
            '~$dynamic_scalar_define_call(pconfigcall_S)', '~$dynamic_null_define_duplicate_valid(S_zero_duplicate,pconfigcall_S_zero,0)',
            '~$dynamic_null_define_duplicate_valid(S_zero_duplicate,pconfigcall_S_zero,2)']
    elif name == 'captured-null-and-request-zero-through-returning-handlers':
        values += [*captured_front('S', 'S_initial'), 'S.USERCONSTANTS = eps',
            'pvalue_flag_S = PSTRING_CARRIER (REQUEST_STRING n_flag_string) preqbytes_flag', 'preqbytes_flag = ' + text('0'),
            'pvalue_candidate = PSTRING_CARRIER (REQUEST_STRING n_candidate) preqbytes_candidate', 'preqbytes_candidate = ' + text('captured-value41'),
            '$string_carrier_valid(S,pvalue_flag_S)', '$string_carrier_valid(S,pvalue_candidate)',
            '$test_outputs(S.EVENTS) = ' + text('B|V|N|'), 'pconfigcall_S.SELECTION = (n_selection)',
            'S.SELECTEDCALLS[n_selection].KIND = INTRINSIC_DEFINE',
            '$lookup(S.ENV,' + text('flag') + ') = (n_flag)', 'S.STORE[n_flag] = DEFINED pvalue_live_flag', '$truth(S,pvalue_live_flag)',
            '$lookup(S.ENV,' + text('result') + ') = (n_result)', 'S.STORE[n_result] = DEFINED (PINT 99)',
            *null.deprecated('S_warning', 'S'),
            *null.handler('S_first_handler', 'S_warning', 3, 'pvalue_candidate', 'pconfigcall_S', '[PNULL,pvalue_candidate,pvalue_flag_S]'),
            *null.received('S_resume', 'S_first_handler', 'S', 'pvalue_candidate'),
            '$user_constant_at(S_resume.USERCONSTANTS,eps) = (puserconstant_inner)', 'puserconstant_inner.VALUE = PINT 613',
            'S_resume.STORE[n_flag] = DEFINED (PBOOL true)', 'S_resume.STORE[n_result] = DEFINED (PINT 99)',
            '$lookup(S_resume.ENV,' + text('count') + ') = (n_count)', 'S_resume.STORE[n_count] = DEFINED (PINT 1)',
            '$lookup(S_resume.ENV,' + text('name') + ') = (n_name)', 'S_resume.STORE[n_name] = DEFINED pvalue_live_name',
            '$string_bytes(pvalue_live_name) = (' + text('handler-name') + ')',
            '$lookup(S_resume.ENV,' + text('value') + ') = (n_value)', 'S_resume.STORE[n_value] = DEFINED pvalue_live_value',
            '$string_bytes(pvalue_live_value) = (' + text('handler-value') + ')',
            '$lookup(S_resume.ENV,' + text('call') + ') = (n_call)', 'S_resume.STORE[n_call] = DEFINED pvalue_live_call',
            '$string_bytes(pvalue_live_call) = (' + text('constant') + ')',
            *null.warning('S_duplicate_warning', 'S_resume', 'pconfigcall_S', 2, 'DYNAMIC_NULL_DEFINE_DUPLICATE pconfigcall_S 1', '$global_constant_duplicate_message(eps)', 'Warning'),
            'pconfigcall_view = pconfigcall_S[.SENT = $named_slot_set(pconfigcall_S.SENT,0,KNOWN (PSTRING_CARRIER INTERNED_STRING eps))]',
            *null.handler('S_second_handler', 'S_duplicate_warning', 4, 'pvalue_candidate', 'pconfigcall_view', '[(PSTRING_CARRIER INTERNED_STRING eps),pvalue_candidate,pvalue_flag_S]'),
            *null.reach('S_duplicate', 'S_second_handler', 2, 'pvalue_candidate'),
            'S_duplicate.TODO = (DYNAMIC_NULL_DEFINE_DUPLICATE pconfigcall_S 1) :: ptask_duplicate*',
            'S_duplicate.STORE[n_count] = DEFINED (PINT 2)', 'S_duplicate.STORE[n_result] = DEFINED (PINT 99)',
            '$user_constant_at(S_duplicate.USERCONSTANTS,eps) = (puserconstant_inner)',
            *common.step('S_return', 'S_duplicate', 'PBOOL false'), 'S_return.TODO = ptask_duplicate*',
            *null.unchanged('S_return', 'S_duplicate', 'STORE ENV USERCONSTANTS STRINGDATA EVENTS SELECTEDCALLS'),
            'n_bad_string = |S.STRINGDATA|', 'pvalue_bad_flag = PSTRING_CARRIER (REQUEST_STRING n_bad_string) preqbytes_flag',
            '$dynamic_define_false_scalar_flag(pvalue_bad_flag)', '~$string_carrier_valid(S,pvalue_bad_flag)',
            '~$dynamic_scalar_define_flag_carrier_valid(S,pconfigcall_S[.SENT = $named_slot_set(pconfigcall_S.SENT,2,KNOWN pvalue_bad_flag)])',
            '~$dynamic_null_define_valid(S,pconfigcall_S[.SENT = $named_slot_set(pconfigcall_S.SENT,2,KNOWN pvalue_bad_flag)])',
            '~$error_call_valid(S_warning,perrorcall_S_warning[.LEVEL = 2])',
            '~$error_call_valid(S_duplicate_warning,perrorcall_S_duplicate_warning[.LEVEL = 8192])',
            *null.budget('S_resume'), *null.budget('S_duplicate')]
        for change in ('.SITE = PORIGIN 0 eps', '.LINE = $(pconfigcall_S.LINE + 1)', '.SELECTION = eps', '.KIND = INTRINSIC_CONSTANT'):
            values += ['~$dynamic_null_define_valid(S,pconfigcall_S[' + change + '])']
    else:
        assert name == 'strict-null-name-precedes-nonbool-flag-after-effects'
        values += [*front('S', 'S_initial', 'PINT 647'), 'pvalue_flag_S = PINT 0', 'S.USERCONSTANTS = eps',
            '$test_outputs(S.EVENTS) = ' + text('B|V|N|'), 'pconfigcall_S.SELECTION = (n_selection)',
            '$lookup(S.ENV,' + text('flag') + ') = (n_flag)', 'S.STORE[n_flag] = DEFINED (PBOOL true)',
            '$lookup(S.ENV,' + text('result') + ') = (n_result)', 'S.STORE[n_result] = DEFINED (PINT 99)',
            *strict_error('S_error', 'S', 'PINT 647'),
            *front('S_zero', 'S_error', 'PINT 649'), 'pvalue_flag_S_zero = PFLOAT 9223372036854775808',
            *strict_error('S_zero_error', 'S_zero', 'PINT 649'),
            'S_zero_error.STORE[n_result] = DEFINED (PINT 99)', *null.budget('S')]
    return values


def main():
    selection = argparse.ArgumentParser(add_help=False)
    selection.add_argument('--case', action='append', default=[])
    selected, remaining = selection.parse_known_args()
    assert len(selected.case) == len(set(selected.case)) and set(selected.case) <= sources.family.CASES.keys()
    if selected.case:
        sources.family.CASES = {name: sources.family.CASES[name] for name in selected.case}
    sys.argv = [sys.argv[0], *remaining]
    fingerprint = sources.family.fingerprint
    sources.family.fingerprint = lambda: dict(fingerprint(), **{
        str(Path(__file__).relative_to(driver.ROOT)): sources.family.sha(__file__),
        str(Path(null.__file__).relative_to(driver.ROOT)): sources.family.sha(null.__file__)})
    driver.sources, driver.PREFIX, driver.checks = sources, PREFIX, checks
    driver.main()


if __name__ == '__main__':
    main()
