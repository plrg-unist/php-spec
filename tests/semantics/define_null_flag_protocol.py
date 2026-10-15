#!/usr/bin/env python3
"""Reached NULL bool reception, raw API arguments and late define publication."""
import argparse
import json
import os
from pathlib import Path
import sys

import global_constant_scalar_name_protocol as driver
import define_null_flag_sources as sources

common, text, b64 = driver.common, driver.text, driver.b64

PREFIX = r"""
dec $test_null_flag_front(pstate, nat, pvalue) : bool
def $test_null_flag_front(S, 0, pvalue) = true
  -- if S.TODO = (CONFIG_INVOKE pconfigcall) :: ptask_tail*
  -- if pconfigcall.KIND = INTRINSIC_DEFINE
  -- if pconfigcall.SENT = [NAMED_SENT (KNOWN pvalue_name),NAMED_SENT (KNOWN pvalue),NAMED_SENT (KNOWN PNULL)]
def $test_null_flag_front(S, 1, pvalue) = true
  -- if S.TODO = (DYNAMIC_NULL_DEFINE_FLAG_RESULT pconfigcall) :: ptask_tail*
  -- if pconfigcall.SENT = [NAMED_SENT (KNOWN pvalue_name),NAMED_SENT (KNOWN pvalue),NAMED_SENT (KNOWN PNULL)]
def $test_null_flag_front(S, 2, pvalue) = true
  -- if S.TODO = (DYNAMIC_NULL_DEFINE_FLAG_DUPLICATE pconfigcall n_constants) :: ptask_tail*
  -- if pconfigcall.SENT = [NAMED_SENT (KNOWN pvalue_name),NAMED_SENT (KNOWN pvalue),NAMED_SENT (KNOWN PNULL)]
def $test_null_flag_front(S, 3, pvalue) = true
  -- if S.CURRENT = (pcallcontext)
  -- if $error_context_call(S,pcallcontext) = (perrorcall)
  -- if perrorcall.RESUME = DYNAMIC_NULL_DEFINE_FLAG_RESULT pconfigcall
  -- if pconfigcall.SENT = [NAMED_SENT (KNOWN pvalue_name),NAMED_SENT (KNOWN pvalue),NAMED_SENT (KNOWN PNULL)]
def $test_null_flag_front(S, 4, pvalue) = true
  -- if S.CURRENT = (pcallcontext)
  -- if $error_context_call(S,pcallcontext) = (perrorcall)
  -- if perrorcall.RESUME = DYNAMIC_NULL_DEFINE_FLAG_DUPLICATE pconfigcall n_constants
  -- if pconfigcall.SENT = [NAMED_SENT (KNOWN pvalue_name),NAMED_SENT (KNOWN pvalue),NAMED_SENT (KNOWN PNULL)]
def $test_null_flag_front(S, n_stage, pvalue) = false -- otherwise
dec $test_null_flag_seek(pstate, nat, pvalue, nat) : pstate
def $test_null_flag_seek(S, n_stage, pvalue, 0) = S
def $test_null_flag_seek(S, n_stage, pvalue, n) = S
  -- if $(n > 0)
  -- if $test_null_flag_front(S,n_stage,pvalue) \/ (S.COMPLETION =/= NORMAL /\ S.COMPLETION =/= BUDGET)
def $test_null_flag_seek(S, n_stage, pvalue, n) = $test_null_flag_seek($drive_steps($test_running(S),1),n_stage,pvalue,$nabs($(n - 1)))
  -- if $(n > 0)
  -- if ~$test_null_flag_front(S,n_stage,pvalue)
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
"""


def reach(state, start, stage, value):
    return [state + '_found = $test_null_flag_seek(' + start + ',' + str(stage) + ',' + value + ',3000)',
        state + '_found.COMPLETION = NORMAL \\/ ' + state + '_found.COMPLETION = BUDGET',
        state + ' = ' + state + '_found[.COMPLETION = NORMAL]',
        '$test_null_flag_front(' + state + ',' + str(stage) + ',' + value + ')', *common.public(state)]


def front(state, start, value, name):
    call = 'pconfigcall_' + state
    return [*reach(state, start, 0, value),
        state + '.TODO = (CONFIG_INVOKE ' + call + ') :: ptask_' + state + '*',
        call + '.KIND = INTRINSIC_DEFINE', call + '.OWNER = eps', call + '.PACKS = eps',
        call + '.SENT = [NAMED_SENT (KNOWN pvalue_captured_name_' + state + '),NAMED_SENT (KNOWN (' + value + ')),NAMED_SENT (KNOWN PNULL)]',
        '$string_bytes(pvalue_captured_name_' + state + ') = (' + text(name) + ')',
        '$config_invoke_valid(' + state + ',' + call + ')', '$dynamic_null_define_flag_call(' + call + ')',
        '$dynamic_null_define_flag_valid(' + state + ',' + call + ')']


def unchanged(after, before, fields):
    return [after + '.' + field + ' = ' + before + '.' + field for field in fields.split()]


def budget(state):
    return [state + '_pause = $drive_steps(' + state + ',0)',
        state + '_pause = ' + state + '[.COMPLETION = BUDGET]',
        state + '_one = $drive_steps(' + state + ',1)',
        state + '_one = $drive_steps(' + state + '_pause[.COMPLETION = NORMAL],1)']


def warning(state, source, call, level, resume, message, event):
    error = 'perrorcall_' + state
    return [*common.step(state, source), state + '.TODO = (ERROR_HANDLER_INVOKE ' + error + ') :: ptask_' + source + '*',
        error + '.RESUME = ' + resume, error + '.SITE = ' + call + '.SITE', error + '.LINE = ' + call + '.LINE',
        error + '.LEVEL = ' + str(level), error + '.MESSAGE = ' + message,
        error + '.EVENT = DIAGNOSTIC ' + json.dumps(event) + ' ' + message + ' ' + call + '.LINE',
        '$error_call_valid(' + state + ',' + error + ')', '$call_task_valid(' + state + ',ERROR_HANDLER_INVOKE ' + error + ')',
        *unchanged(state, source, 'STORE ENV USERCONSTANTS STRINGDATA ARRAYS OBJECTS ALLOCATIONS EVENTS SELECTEDCALLS'),
        *common.public(state)]


def default_warning(state, source, call, resume, message, event):
    return [*common.step(state, source), state + '.TODO = (' + resume + ') :: ptask_' + source + '*',
        '$(|'+ state + '.EVENTS| = |' + source + '.EVENTS| + 1)',
        state + '.EVENTS[|' + source + '.EVENTS|] = DIAGNOSTIC ' + json.dumps(event) + ' ' + message + ' ' + call + '.LINE',
        '$call_task_valid(' + state + ',' + resume + ')',
        *unchanged(state, source, 'STORE ENV USERCONSTANTS STRINGDATA ARRAYS OBJECTS ALLOCATIONS SELECTEDCALLS'),
        *common.public(state)]


def handler(state, start, stage, value, call, args):
    return [*reach(state, start, stage, value), state + '.CURRENT = (pcallcontext_' + state + ')',
        '$error_context_call(' + state + ',pcallcontext_' + state + ') = (perrorcall_' + state + ')',
        '$error_context_valid(' + state + ',pcallcontext_' + state + ')',
        '$error_context_trigger(' + state + ',pcallcontext_' + state + ') = (' + call + ')',
        '$error_handler_trace_values(' + state + ',pcallcontext_' + state + ',' + call + ') = ' + args]


def checks(program, path, name):
    values = ['S_initial = $php_run(' + program + ',0,' + json.dumps(b64(os.fsencode(path))) + ')',
        'S_initial.COMPLETION = BUDGET']
    if name == 'literal-null-flag-publication-and-duplicate':
        values += [*front('S', 'S_initial', 'PINT 173', 'LiteralNullFlag33'),
            '~$config_strict(S,pconfigcall_S)', 'pconfigcall_S.SELECTION = eps',
            '$intrinsic_argument(S,pconfigcall_S.SITE,2) = ((expression,false,eps,porigin_flag,z_flag))',
            '$compiled_read(S,porigin_flag) = (PNULL)',
            '$dynamic_define_known(S,pconfigcall_S.SITE,1) = (PINT 173)', 'S.USERCONSTANTS = eps',
            *default_warning('S_resume', 'S', 'pconfigcall_S', 'DYNAMIC_NULL_DEFINE_FLAG_RESULT pconfigcall_S',
                '$dynamic_null_define_flag_message()', 'Deprecated'),
            *common.step('S_published', 'S_resume', 'PBOOL true'),
            '$(|S_published.USERCONSTANTS| = |S_resume.USERCONSTANTS| + 1)',
            'puserconstant = S_published.USERCONSTANTS[|S_resume.USERCONSTANTS|]',
            'S_published.USERCONSTANTS = S_resume.USERCONSTANTS ++ [puserconstant]',
            'puserconstant.NAME = ' + text('LiteralNullFlag33'), 'puserconstant.ORIGIN = pconfigcall_S.SITE',
            'puserconstant.VALUE = PINT 173', 'puserconstant.CLASS = PVSCALAR',
            'puserconstant.READS = eps', 'puserconstant.RECEIVES = eps',
            'S_published = S_resume[.TODO = ptask_S*][.USERCONSTANTS = [puserconstant]][.RESULT = KNOWN (PBOOL true)][.BASE = BASE_VALUE (KNOWN PNULL)]',
            '$user_constants_valid(S_published,S_published.USERCONSTANTS)',
            '~$user_constants_valid(S_published,[puserconstant[.NAME = ' + text('wrong') + ']])',
            '~$user_constants_valid(S_published,[puserconstant[.VALUE = PINT 174]])',
            '~$user_constants_valid(S_published,[puserconstant[.CLASS = (PVSTRING true)]])',
            '~$user_constants_valid(S_published,[puserconstant,puserconstant])',
            'pconfigcall_bad = pconfigcall_S[.SENT = $named_slot_set(pconfigcall_S.SENT,1,KNOWN (PINT 174))]',
            '$config_invoke_valid(S,pconfigcall_bad)', '~$dynamic_null_define_flag_valid(S,pconfigcall_bad)',
            'S_bad = $drive_steps(S[.TODO = (CONFIG_INVOKE pconfigcall_bad) :: ptask_S*],1)',
            'S_bad.COMPLETION = UNSUPPORTED "null define flag reception"',
            *front('S_second', 'S_published', 'PINT 174', 'LiteralNullFlag33'),
            *default_warning('S_second_resume', 'S_second', 'pconfigcall_S_second',
                'DYNAMIC_NULL_DEFINE_FLAG_RESULT pconfigcall_S_second', '$dynamic_null_define_flag_message()', 'Deprecated'),
            *default_warning('S_duplicate', 'S_second_resume', 'pconfigcall_S_second',
                'DYNAMIC_NULL_DEFINE_FLAG_DUPLICATE pconfigcall_S_second 1',
                '$global_constant_duplicate_message(' + text('LiteralNullFlag33') + ')', 'Warning'),
            '$dynamic_null_define_flag_duplicate_valid(S_duplicate,pconfigcall_S_second,1)',
            '~$dynamic_null_define_flag_duplicate_valid(S_duplicate,pconfigcall_S_second,0)',
            *common.step('S_return', 'S_duplicate', 'PBOOL false'),
            'S_return = S_duplicate[.TODO = ptask_S_second_resume*][.RESULT = KNOWN (PBOOL false)][.BASE = BASE_VALUE (KNOWN PNULL)]',
            *budget('S_resume'), *budget('S_duplicate')]
    elif name == 'captured-null-flag-and-callback-created-duplicate':
        values += [*front('S', 'S_initial', 'PINT 181', 'CapturedNullFlag33'),
            '~$config_strict(S,pconfigcall_S)', 'S.USERCONSTANTS = eps',
            'pconfigcall_S.SELECTION = (n_selection)', '$(n_selection < |S.SELECTEDCALLS|)',
            'S.SELECTEDCALLS[n_selection].KIND = INTRINSIC_DEFINE',
            '$lookup(S.ENV,' + text('flag') + ') = (n_flag_cell)', 'S.STORE[n_flag_cell] = DEFINED (PBOOL false)',
            '$lookup(S.ENV,' + text('call') + ') = (n_callee_cell)', 'S.STORE[n_callee_cell] = DEFINED pvalue_live_callee',
            '$string_bytes(pvalue_live_callee) = (' + text('defined') + ')',
            *warning('S_warning', 'S', 'pconfigcall_S', 8192,
                'DYNAMIC_NULL_DEFINE_FLAG_RESULT pconfigcall_S', '$dynamic_null_define_flag_message()', 'Deprecated'),
            *handler('S_deprecation_handler', 'S_warning', 3, 'PINT 181', 'pconfigcall_S',
                '[pvalue_captured_name_S,(PINT 181),PNULL]'),
            *reach('S_resume', 'S_deprecation_handler', 1, 'PINT 181'),
            'S_resume.TODO = (DYNAMIC_NULL_DEFINE_FLAG_RESULT pconfigcall_S) :: ptask_S_resume*',
            '$call_task_valid(S_resume,DYNAMIC_NULL_DEFINE_FLAG_RESULT pconfigcall_S)',
            'S_resume.RESULT = KNOWN PNULL',
            '$user_constant_at(S_resume.USERCONSTANTS,' + text('CapturedNullFlag33') + ') = (puserconstant_callback)',
            'puserconstant_callback.VALUE = PINT 281', 'puserconstant_callback.ORIGIN =/= pconfigcall_S.SITE',
            'S_resume.STORE[n_flag_cell] = DEFINED (PBOOL true)',
            '$lookup(S_resume.ENV,' + text('name') + ') = (n_name_cell)',
            'S_resume.STORE[n_name_cell] = DEFINED pvalue_live_name', '$string_bytes(pvalue_live_name) = (' + text('changed') + ')',
            'S_resume.STORE[n_callee_cell] = DEFINED pvalue_callback_callee',
            '$string_bytes(pvalue_callback_callee) = (' + text('constant') + ')',
            'n_constants = |S_resume.USERCONSTANTS|',
            *warning('S_duplicate_warning', 'S_resume', 'pconfigcall_S', 2,
                'DYNAMIC_NULL_DEFINE_FLAG_DUPLICATE pconfigcall_S n_constants',
                '$global_constant_duplicate_message(' + text('CapturedNullFlag33') + ')', 'Warning'),
            *handler('S_duplicate_handler', 'S_duplicate_warning', 4, 'PINT 181', 'pconfigcall_S',
                '[pvalue_captured_name_S,(PINT 181),PNULL]'),
            'perrorcall_S_duplicate_handler.RESUME = DYNAMIC_NULL_DEFINE_FLAG_DUPLICATE pconfigcall_S n_constants',
            '$user_constant_at(S_duplicate_handler.USERCONSTANTS,' + text('CapturedNullFlag33') + ') = (puserconstant_callback)',
            '~$dynamic_null_define_flag_duplicate_valid(S_resume,pconfigcall_S,0)',
            '~$dynamic_null_define_flag_duplicate_valid(S_resume,pconfigcall_S,$(n_constants + 1))',
            '~$error_call_valid(S_warning,perrorcall_S_warning[.LEVEL = 2])',
            '~$error_call_valid(S_duplicate_warning,perrorcall_S_duplicate_warning[.LEVEL = 8192])',
            *budget('S_resume'), *budget('S_duplicate_warning')]
        values += ['n_bad_string = |S.STRINGDATA|']
        for slot, label, payload in ((0, 'name', 'CapturedNullFlag33'), (1, 'value', 'captured-value')):
            values += ['pvalue_invalid_' + label + ' = PSTRING_CARRIER (REQUEST_STRING n_bad_string) ' + text(payload),
                '~$string_carrier_valid(S,pvalue_invalid_' + label + ')',
                'pconfigcall_invalid_' + label + ' = pconfigcall_S[.SENT = $named_slot_set(pconfigcall_S.SENT,' + str(slot) + ',KNOWN pvalue_invalid_' + label + ')]',
                '$dynamic_null_define_flag_call(pconfigcall_invalid_' + label + ')',
                '$config_invoke_valid(S,pconfigcall_invalid_' + label + ')',
                '~$dynamic_null_define_flag_valid(S,pconfigcall_invalid_' + label + ')']
        for change in ('.SITE = PORIGIN 0 eps', '.LINE = $(pconfigcall_S.LINE + 1)', '.SELECTION = eps', '.KIND = INTRINSIC_CONSTANT'):
            values += ['~$dynamic_null_define_flag_valid(S,pconfigcall_S[' + change + '])']
        values += ['~$dynamic_null_define_flag_call(pconfigcall_S[.OWNER = (0)])',
            '~$dynamic_null_define_flag_call(pconfigcall_S[.SENT = $named_slot_set(pconfigcall_S.SENT,2,KNOWN (PBOOL true))])']
    else:
        assert name == 'strict-null-flag-after-all-argument-effects'
        values += [*front('S', 'S_initial', 'PINT 191', 'StrictNullFlag33'), '$config_strict(S,pconfigcall_S)',
            '$test_outputs(S.EVENTS) = ' + text('B|V|N|'), 'S.USERCONSTANTS = eps',
            '$lookup(S.ENV,' + text('result') + ') = (n_result_cell)', 'S.STORE[n_result_cell] = DEFINED (PINT 99)',
            '~$call_task_valid(S,DYNAMIC_NULL_DEFINE_FLAG_RESULT pconfigcall_S)',
            *common.step('S_error', 'S'), 'S_error.TODO = (THROW_SEARCH n_error) :: ptask_error*',
            'S_error.OBJECTS[n_error] = THROWABLE pthrowable_error', 'pthrowable_error.KIND = "TypeError"',
            'pthrowable_error.ORIGIN = (pconfigcall_S.SITE)',
            '$string_bytes($throwable_field(S_error,n_error,"message")) = (' + text('define(): Argument #3 ($case_insensitive) must be of type bool, null given') + ')',
            '$throwable_field(S_error,n_error,"line") = PINT pconfigcall_S.LINE',
            '$throwable_field(S_error,n_error,"trace") = PARRAY n_trace',
            'S_error.ARRAYS[n_trace].ITEMS = [ENTRY (KINT 0) (DIRECT (PARRAY n_frame))]',
            '$trace_array_field(S_error,n_frame,' + text('function') + ') = PSTRING ' + text('define'),
            '$trace_array_field(S_error,n_frame,' + text('args') + ') = PARRAY n_args',
            'S_error.ARRAYS[n_args].ITEMS = [ENTRY (KINT 0) (DIRECT pvalue_captured_name_S),ENTRY (KINT 1) (DIRECT (PINT 191)),ENTRY (KINT 2) (DIRECT PNULL)]',
            'S_error.STORE[n_result_cell] = DEFINED (PINT 99)',
            *unchanged('S_error', 'S', 'USERCONSTANTS STORE STRINGDATA EVENTS SELECTEDCALLS'), *common.public('S_error'), *budget('S')]
    return values


if __name__ == '__main__':
    selection = argparse.ArgumentParser(add_help=False)
    selection.add_argument('--case', action='append', default=[])
    selected, remaining = selection.parse_known_args()
    assert len(selected.case) == len(set(selected.case)) and set(selected.case) <= sources.family.CASES.keys()
    if selected.case:
        sources.family.CASES = {name: sources.family.CASES[name] for name in selected.case}
    sys.argv = [sys.argv[0], *remaining]
    original_inputs = sources.family.fingerprint
    sources.family.fingerprint = lambda: dict(original_inputs(), **{str(Path(__file__).relative_to(driver.ROOT)): sources.family.sha(__file__)})
    driver.sources, driver.PREFIX, driver.checks = sources, PREFIX, checks
    driver.main()
