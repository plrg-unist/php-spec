#!/usr/bin/env python3
"""Reached quiet scalar flags, raw warning arguments and strict rejection."""
import argparse
import json
import os
from pathlib import Path
import sys

import global_constant_scalar_name_protocol as driver
import define_scalar_flag_sources as sources

common, text, b64 = driver.common, driver.text, driver.b64

PREFIX = r"""
dec $test_scalar_flag_front(pstate, nat, preqbytes) : bool
def $test_scalar_flag_front(S, 0, preqbytes) = true
  -- if S.TODO = (CONFIG_INVOKE pconfigcall) :: ptask_tail*
  -- if pconfigcall.KIND = INTRINSIC_DEFINE
  -- if pconfigcall.SENT = [NAMED_SENT (KNOWN pvalue_name),NAMED_SENT (KNOWN pvalue),NAMED_SENT (KNOWN pvalue_flag)]
  -- if $string_bytes(pvalue_name) = (preqbytes)
def $test_scalar_flag_front(S, 1, preqbytes) = true
  -- if S.TODO = (DYNAMIC_SCALAR_DEFINE_FLAG_RESULT pconfigcall) :: ptask_tail*
  -- if pconfigcall.SENT = [NAMED_SENT (KNOWN pvalue_name),NAMED_SENT (KNOWN pvalue),NAMED_SENT (KNOWN pvalue_flag)]
  -- if $string_bytes(pvalue_name) = (preqbytes)
def $test_scalar_flag_front(S, 2, preqbytes) = true
  -- if S.TODO = (DYNAMIC_SCALAR_DEFINE_FLAG_DUPLICATE pconfigcall n_constants) :: ptask_tail*
  -- if pconfigcall.SENT = [NAMED_SENT (KNOWN pvalue_name),NAMED_SENT (KNOWN pvalue),NAMED_SENT (KNOWN pvalue_flag)]
  -- if $string_bytes(pvalue_name) = (preqbytes)
def $test_scalar_flag_front(S, 3, preqbytes) = true
  -- if S.CURRENT = (pcallcontext)
  -- if $error_context_call(S,pcallcontext) = (perrorcall)
  -- if perrorcall.RESUME = DYNAMIC_SCALAR_DEFINE_FLAG_RESULT pconfigcall
  -- if pconfigcall.SENT = [NAMED_SENT (KNOWN pvalue_name),NAMED_SENT (KNOWN pvalue),NAMED_SENT (KNOWN pvalue_flag)]
  -- if $string_bytes(pvalue_name) = (preqbytes)
def $test_scalar_flag_front(S, 4, preqbytes) = true
  -- if S.CURRENT = (pcallcontext)
  -- if $error_context_call(S,pcallcontext) = (perrorcall)
  -- if perrorcall.RESUME = DYNAMIC_SCALAR_DEFINE_FLAG_DUPLICATE pconfigcall n_constants
  -- if pconfigcall.SENT = [NAMED_SENT (KNOWN pvalue_name),NAMED_SENT (KNOWN pvalue),NAMED_SENT (KNOWN pvalue_flag)]
  -- if $string_bytes(pvalue_name) = (preqbytes)
def $test_scalar_flag_front(S, n_stage, preqbytes) = false -- otherwise
dec $test_scalar_flag_seek(pstate, nat, preqbytes, nat) : pstate
def $test_scalar_flag_seek(S, n_stage, preqbytes, 0) = S
def $test_scalar_flag_seek(S, n_stage, preqbytes, n) = S
  -- if $(n > 0)
  -- if $test_scalar_flag_front(S,n_stage,preqbytes) \/ (S.COMPLETION =/= NORMAL /\ S.COMPLETION =/= BUDGET)
def $test_scalar_flag_seek(S, n_stage, preqbytes, n) = $test_scalar_flag_seek($drive_steps($test_running(S),1),n_stage,preqbytes,$nabs($(n - 1)))
  -- if $(n > 0)
  -- if ~$test_scalar_flag_front(S,n_stage,preqbytes)
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
"""


def reach(state, start, stage, name):
    return [state + '_found = $test_scalar_flag_seek(' + start + ',' + str(stage) + ',' + text(name) + ',3000)',
        state + '_found.COMPLETION = NORMAL \\/ ' + state + '_found.COMPLETION = BUDGET',
        state + ' = ' + state + '_found[.COMPLETION = NORMAL]',
        '$test_scalar_flag_front(' + state + ',' + str(stage) + ',' + text(name) + ')', *common.public(state)]


def front(state, start, name, value):
    call = 'pconfigcall_' + state
    return [*reach(state, start, 0, name), state + '.TODO = (CONFIG_INVOKE ' + call + ') :: ptask_' + state + '*',
        call + '.SENT = [NAMED_SENT (KNOWN pvalue_name_' + state + '),NAMED_SENT (KNOWN (' + value + ')),NAMED_SENT (KNOWN pvalue_flag_' + state + ')]',
        call + '.KIND = INTRINSIC_DEFINE', call + '.OWNER = eps', call + '.PACKS = eps',
        '$config_invoke_valid(' + state + ',' + call + ')', '$dynamic_scalar_define_flag_call(' + call + ')',
        '$dynamic_scalar_define_flag_valid(' + state + ',' + call + ')']


def unchanged(after, before, fields):
    return [after + '.' + field + ' = ' + before + '.' + field for field in fields.split()]


def budget(state):
    return [state + '_pause = $drive_steps(' + state + ',0)', state + '_pause = ' + state + '[.COMPLETION = BUDGET]',
        state + '_one = $drive_steps(' + state + ',1)', state + '_one = $drive_steps(' + state + '_pause[.COMPLETION = NORMAL],1)']


def warning(state, source, call, resume, message):
    error = 'perrorcall_' + state
    return [*common.step(state, source), state + '.TODO = (ERROR_HANDLER_INVOKE ' + error + ') :: ptask_' + source + '*',
        error + '.RESUME = ' + resume, error + '.SITE = ' + call + '.SITE', error + '.LINE = ' + call + '.LINE',
        error + '.LEVEL = 2', error + '.MESSAGE = ' + message,
        error + '.EVENT = DIAGNOSTIC "Warning" ' + message + ' ' + call + '.LINE',
        '$error_call_valid(' + state + ',' + error + ')', *common.public(state),
        *unchanged(state, source, 'STORE ENV USERCONSTANTS STRINGDATA ARRAYS OBJECTS ALLOCATIONS EVENTS SELECTEDCALLS')]


def handler(state, start, stage, name, call, args):
    return [*reach(state, start, stage, name), state + '.CURRENT = (pcallcontext_' + state + ')',
        '$error_context_call(' + state + ',pcallcontext_' + state + ') = (perrorcall_' + state + ')',
        '$error_context_valid(' + state + ',pcallcontext_' + state + ')',
        '$error_context_trigger(' + state + ',pcallcontext_' + state + ') = (' + call + ')',
        '$error_handler_trace_values(' + state + ',pcallcontext_' + state + ',' + call + ') = ' + args]


def checks(program, path, name):
    values = ['S_initial = $php_run(' + program + ',0,' + json.dumps(b64(os.fsencode(path))) + ')',
        'S_initial.COMPLETION = BUDGET']
    if name == 'weak-scalar-flags-and-historical-rows':
        values += [*front('S', 'S_initial', 'FlagStringZero31', 'PINT 131'), '~$config_strict(S,pconfigcall_S)',
            '$string_bytes(pvalue_flag_S) = (' + text('0') + ')', '$string_carrier_valid(S,pvalue_flag_S)',
            '~$truth(S,pvalue_flag_S)', '~$dynamic_scalar_define_flag_case_valid(S,pconfigcall_S)',
            'S.USERCONSTANTS = eps', *common.step('S_published', 'S', 'PBOOL true'),
            'S_published.TODO = ptask_S*', '$(|S_published.USERCONSTANTS| = 1)', 'puserconstant = S_published.USERCONSTANTS[0]',
            'puserconstant.NAME = ' + text('FlagStringZero31'), 'puserconstant.ORIGIN = pconfigcall_S.SITE',
            'puserconstant.VALUE = PINT 131', 'puserconstant.CLASS = PVSCALAR', '$user_constants_valid(S_published,S_published.USERCONSTANTS)',
            *unchanged('S_published', 'S', 'STORE ENV STRINGDATA ARRAYS OBJECTS ALLOCATIONS SELECTEDCALLS EVENTS'),
            *front('S_literal', 'S_published', 'FlagStringFalse31', 'PINT 132'),
            '$intrinsic_argument(S_literal,pconfigcall_S_literal.SITE,2) = ((expression,false,eps,porigin_flag,z_flag))',
            '$compiled_read(S_literal,porigin_flag) = (pvalue_known_flag)',
            '$string_bytes(pvalue_known_flag) = (' + text('false') + ')',
            '$truth(S_literal,pvalue_flag_S_literal)', '$dynamic_scalar_define_flag_case_valid(S_literal,pconfigcall_S_literal)',
            'pconfigcall_bad = pconfigcall_S_literal[.SENT = $named_slot_set(pconfigcall_S_literal.SENT,2,KNOWN (PINT 0))]',
            '$config_invoke_valid(S_literal,pconfigcall_bad)', '~$dynamic_scalar_define_flag_valid(S_literal,pconfigcall_bad)',
            'S_bad = $drive_steps(S_literal[.TODO = (CONFIG_INVOKE pconfigcall_bad) :: ptask_S_literal*],1)',
            'S_bad.COMPLETION = UNSUPPORTED "scalar define flag reception"',
            *warning('S_warning', 'S_literal', 'pconfigcall_S_literal', 'DYNAMIC_SCALAR_DEFINE_FLAG_RESULT pconfigcall_S_literal', '$dynamic_constant_case_message()'),
            *reach('S_resume', 'S_warning', 1, 'FlagStringFalse31'),
            'S_resume.TODO = (DYNAMIC_SCALAR_DEFINE_FLAG_RESULT pconfigcall_S_literal) :: ptask_resume*',
            '$call_task_valid(S_resume,DYNAMIC_SCALAR_DEFINE_FLAG_RESULT pconfigcall_S_literal)',
            *common.step('S_literal_published', 'S_resume', 'PBOOL true'),
            *front('S_request', 'S_literal_published', 'FlagRequest31', 'PINT 137'),
            'pvalue_flag_S_request = PSTRING_CARRIER (REQUEST_STRING n_string) preqbytes_flag',
            'preqbytes_flag = ' + text('false'), '$string_carrier_valid(S_request,pvalue_flag_S_request)',
            'S_request.STRINGDATA[n_string] = preqbytes_flag', '$truth(S_request,pvalue_flag_S_request)',
            'n_bad = |S_request.STRINGDATA|', 'pvalue_bad = PSTRING_CARRIER (REQUEST_STRING n_bad) preqbytes_flag',
            '~$string_carrier_valid(S_request,pvalue_bad)',
            '~$dynamic_scalar_define_flag_valid(S_request,pconfigcall_S_request[.SENT = $named_slot_set(pconfigcall_S_request.SENT,2,KNOWN pvalue_bad)])',
            *warning('S_request_warning', 'S_request', 'pconfigcall_S_request', 'DYNAMIC_SCALAR_DEFINE_FLAG_RESULT pconfigcall_S_request', '$dynamic_constant_case_message()'),
            *budget('S'), *budget('S_resume'), *budget('S_request_warning')]
        for flag in ('PNULL', 'PBOOL false', 'PBOOL true', 'PFLOAT 9221120237041090560', 'PARRAY 0', 'POBJECT 0'):
            values += ['~$dynamic_define_quiet_flag(' + flag + ')',
                '~$dynamic_scalar_define_flag_call(pconfigcall_S[.SENT = $named_slot_set(pconfigcall_S.SENT,2,KNOWN (' + flag + '))])']
        values += ['$dynamic_constant_case_valid(S,pconfigcall_S[.SENT = $named_slot_set(pconfigcall_S.SENT,2,KNOWN (PBOOL true))])']
    elif name == 'captured-flag-and-callback-created-duplicate':
        values += [*front('S', 'S_initial', 'CapturedFlag31', 'PINT 147'),
            'pconfigcall_S.SELECTION = (n_selection)', 'S.SELECTEDCALLS[n_selection].KIND = INTRINSIC_DEFINE',
            '$string_bytes(pvalue_flag_S) = (' + text('false') + ')',
            '$lookup(S.ENV,' + text('flag') + ') = (n_flag_cell)', 'S.STORE[n_flag_cell] = DEFINED (PINT 0)',
            '$lookup(S.ENV,' + text('call') + ') = (n_callee_cell)', 'S.STORE[n_callee_cell] = DEFINED pvalue_callee',
            '$string_bytes(pvalue_callee) = (' + text('constant') + ')',
            *warning('S_warning', 'S', 'pconfigcall_S', 'DYNAMIC_SCALAR_DEFINE_FLAG_RESULT pconfigcall_S', '$dynamic_constant_case_message()'),
            *handler('S_handler', 'S_warning', 3, 'CapturedFlag31', 'pconfigcall_S', '[pvalue_name_S,(PINT 147),pvalue_flag_S]'),
            *reach('S_resume', 'S_handler', 1, 'CapturedFlag31'),
            'S_resume.TODO = (DYNAMIC_SCALAR_DEFINE_FLAG_RESULT pconfigcall_S) :: ptask_S_resume*',
            '$user_constant_at(S_resume.USERCONSTANTS,' + text('CapturedFlag31') + ') = (puserconstant_callback)',
            'puserconstant_callback.VALUE = PINT 247', '$string_bytes(pvalue_flag_S) = (' + text('false') + ')',
            'S_resume.STORE[n_flag_cell] = DEFINED pvalue_live_flag',
            '$string_bytes(pvalue_live_flag) = (' + text('0') + ')',
            'n_constants = |S_resume.USERCONSTANTS|',
            *warning('S_duplicate_warning', 'S_resume', 'pconfigcall_S', 'DYNAMIC_SCALAR_DEFINE_FLAG_DUPLICATE pconfigcall_S n_constants', '$global_constant_duplicate_message(' + text('CapturedFlag31') + ')'),
            *handler('S_duplicate_handler', 'S_duplicate_warning', 4, 'CapturedFlag31', 'pconfigcall_S', '[pvalue_name_S,(PINT 147),pvalue_flag_S]'),
            '$error_context_call(S_duplicate_handler,pcallcontext_S_duplicate_handler) = (perrorcall_duplicate)',
            'perrorcall_duplicate.RESUME = DYNAMIC_SCALAR_DEFINE_FLAG_DUPLICATE pconfigcall_S n_constants',
            '~$dynamic_scalar_define_flag_duplicate_valid(S_resume,pconfigcall_S,0)',
            '~$dynamic_scalar_define_flag_duplicate_valid(S_resume,pconfigcall_S,$(n_constants + 1))',
            '~$error_call_valid(S_warning,perrorcall_S_warning[.LEVEL = 8192])', *budget('S_resume'), *budget('S_duplicate_warning')]
        for change in ('.SITE = PORIGIN 0 eps', '.LINE = $(pconfigcall_S.LINE + 1)', '.SELECTION = eps', '.KIND = INTRINSIC_CONSTANT'):
            values += ['~$dynamic_scalar_define_flag_valid(S,pconfigcall_S[' + change + '])']
    else:
        assert name == 'strict-flag-errors-after-all-argument-effects'
        values += [*front('S', 'S_initial', 'StrictIntFlag31', 'PINT 151'), '$config_strict(S,pconfigcall_S)',
            'pvalue_flag_S = PINT 0', '$test_outputs(S.EVENTS) = ' + text('B|V|N|'), 'S.USERCONSTANTS = eps',
            '$lookup(S.ENV,' + text('result') + ') = (n_result_cell)', 'S.STORE[n_result_cell] = DEFINED (PINT 99)',
            '~$call_task_valid(S,DYNAMIC_SCALAR_DEFINE_FLAG_RESULT pconfigcall_S)',
            *common.step('S_error', 'S'), 'S_error.TODO = (THROW_SEARCH n_error) :: ptask_error*',
            'S_error.OBJECTS[n_error] = THROWABLE pthrowable_error', 'pthrowable_error.KIND = "TypeError"',
            'pthrowable_error.ORIGIN = (pconfigcall_S.SITE)',
            '$string_bytes($throwable_field(S_error,n_error,"message")) = (' + text('define(): Argument #3 ($case_insensitive) must be of type bool, int given') + ')',
            '$throwable_field(S_error,n_error,"line") = PINT pconfigcall_S.LINE',
            '$throwable_field(S_error,n_error,"trace") = PARRAY n_trace',
            'S_error.ARRAYS[n_trace].ITEMS = [ENTRY (KINT 0) (DIRECT (PARRAY n_frame))]',
            '$trace_array_field(S_error,n_frame,' + text('function') + ') = PSTRING ' + text('define'),
            '$trace_array_field(S_error,n_frame,' + text('args') + ') = PARRAY n_args',
            'S_error.ARRAYS[n_args].ITEMS = [ENTRY (KINT 0) (DIRECT pvalue_name_S),ENTRY (KINT 1) (DIRECT (PINT 151)),ENTRY (KINT 2) (DIRECT (PINT 0))]',
            'S_error.STORE[n_result_cell] = DEFINED (PINT 99)',
            *unchanged('S_error', 'S', 'USERCONSTANTS STORE STRINGDATA SELECTEDCALLS EVENTS'), *common.public('S_error'), *budget('S')]
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
