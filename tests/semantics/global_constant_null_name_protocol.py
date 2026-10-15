#!/usr/bin/env python3
"""Reached null query warnings, callback order and raw/converted trace views."""
import json
import os
from pathlib import Path

import global_constant_scalar_name_protocol as driver
import global_constant_null_name_sources as sources

common, text, b64 = driver.common, driver.text, driver.b64

PREFIX = r"""
dec $test_null_front(pstate, nat, pintrinsic) : bool
def $test_null_front(S, 0, pintrinsic) = true
  -- if S.TODO = (CONFIG_INVOKE pconfigcall) :: ptask_tail*
  -- if pconfigcall.KIND = pintrinsic
  -- if pconfigcall.SENT = [NAMED_SENT (KNOWN PNULL)]
def $test_null_front(S, 1, pintrinsic) = true
  -- if S.CURRENT = (pcallcontext)
  -- if $error_context_call(S,pcallcontext) = (perrorcall)
  -- if perrorcall.RESUME = DYNAMIC_NULL_CONSTANT_RESULT pconfigcall
  -- if pconfigcall.KIND = pintrinsic
def $test_null_front(S, 2, pintrinsic) = true
  -- if S.TODO = (DYNAMIC_NULL_CONSTANT_RESULT pconfigcall) :: ptask_tail*
  -- if pconfigcall.KIND = pintrinsic
def $test_null_front(S, 3, pintrinsic) = true
  -- if S.TODO = (CONFIG_INVOKE pconfigcall) :: ptask_tail*
  -- if pconfigcall.KIND = pintrinsic
  -- if pconfigcall.SENT = [NAMED_SENT (KNOWN pvalue)]
  -- if $string_bytes(pvalue) = (eps)
def $test_null_front(S, n_stage, pintrinsic) = false -- otherwise
dec $test_null_seek(pstate, nat, pintrinsic, nat) : pstate
def $test_null_seek(S, n_stage, pintrinsic, 0) = S
def $test_null_seek(S, n_stage, pintrinsic, n) = S
  -- if $(n > 0)
  -- if $test_null_front(S,n_stage,pintrinsic) \/ (S.COMPLETION =/= NORMAL /\ S.COMPLETION =/= BUDGET)
def $test_null_seek(S, n_stage, pintrinsic, n) = $test_null_seek($drive_steps($test_running(S),1),n_stage,pintrinsic,$nabs($(n - 1)))
  -- if $(n > 0)
  -- if ~$test_null_front(S,n_stage,pintrinsic)
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
"""


def reach(state, start, stage, kind):
    return [state + '_found = $test_null_seek(' + start + ',' + str(stage) + ',' + kind + ',3000)',
        state + '_found.COMPLETION = NORMAL \\/ ' + state + '_found.COMPLETION = BUDGET',
        state + ' = ' + state + '_found[.COMPLETION = NORMAL]',
        '$test_null_front(' + state + ',' + str(stage) + ',' + kind + ')', *common.public(state)]


def front(state, start, kind):
    call = 'pconfigcall_' + state
    return [*reach(state, start, 0, kind),
        state + '.TODO = (CONFIG_INVOKE ' + call + ') :: ptask_' + state + '*',
        call + '.KIND = ' + kind, call + '.SENT = [NAMED_SENT (KNOWN PNULL)]',
        call + '.OWNER = eps', call + '.PACKS = eps',
        '$config_invoke_valid(' + state + ',' + call + ')',
        '$dynamic_null_constant_call(' + call + ')', '$dynamic_null_constant_valid(' + state + ',' + call + ')']


def unchanged(after, before, fields):
    return [after + '.' + field + ' = ' + before + '.' + field for field in fields.split()]


def budget(state):
    return [state + '_pause = $drive_steps(' + state + ',0)',
        state + '_pause = ' + state + '[.COMPLETION = BUDGET]',
        state + '_one = $drive_steps(' + state + ',1)',
        state + '_one = $drive_steps(' + state + '_pause[.COMPLETION = NORMAL],1)']


def warning(state, source):
    call, error = 'pconfigcall_' + source, 'perrorcall_' + state
    return ['~$config_strict(' + source + ',' + call + ')', *common.step(state, source),
        state + '.TODO = (ERROR_HANDLER_INVOKE ' + error + ') :: ptask_' + source + '*',
        error + '.RESUME = DYNAMIC_NULL_CONSTANT_RESULT ' + call,
        error + '.SITE = ' + call + '.SITE', error + '.LINE = ' + call + '.LINE',
        error + '.LEVEL = 8192', error + '.MESSAGE = $dynamic_null_constant_message(' + call + ')',
        error + '.EVENT = DIAGNOSTIC "Deprecated" ' + error + '.MESSAGE ' + call + '.LINE',
        '$error_call_valid(' + state + ',' + error + ')',
        '$call_task_valid(' + state + ',ERROR_HANDLER_INVOKE ' + error + ')',
        *unchanged(state, source, 'STORE ENV USERCONSTANTS STRINGDATA ARRAYS OBJECTS ALLOCATIONS EVENTS SELECTEDCALLS'),
        *common.public(state)]


def resume(state, start, original, kind):
    return [*reach(state, start, 2, kind),
        state + '.TODO = (DYNAMIC_NULL_CONSTANT_RESULT pconfigcall_' + original + ') :: ptask_' + state + '*',
        '$call_task_valid(' + state + ',DYNAMIC_NULL_CONSTANT_RESULT pconfigcall_' + original + ')',
        '$dynamic_null_constant_valid(' + state + ',pconfigcall_' + original + ')']


def finish(state, source, result):
    return [*common.step(state, source, result), state + '.TODO = ptask_' + source + '*',
        state + '.BASE = BASE_VALUE (KNOWN PNULL)',
        *unchanged(state, source, 'STORE ENV USERCONSTANTS STRINGDATA ARRAYS OBJECTS OBJECTPROPS REFCELLS ALLOCATIONS SELECTEDCALLS SOURCES POOLS FILES STATICS')]


def checks(program, path, name):
    values = ['S_initial = $php_run(' + program + ',0,' + json.dumps(b64(os.fsencode(path))) + ')',
        'S_initial.COMPLETION = BUDGET']
    if name == 'callback-publication-before-empty-name-lookup':
        values += [*front('S', 'S_initial', 'INTRINSIC_CONSTANT'),
            '$user_constant_at(S.USERCONSTANTS,eps) = eps', 'pconfigcall_S.SELECTION = (n_selection)',
            '$(n_selection < |S.SELECTEDCALLS|)', 'S.SELECTEDCALLS[n_selection].KIND = INTRINSIC_CONSTANT',
            '$lookup(S.ENV,' + text('name') + ') = (n_name_cell)', 'S.STORE[n_name_cell] = DEFINED PNULL',
            '$lookup(S.ENV,' + text('call') + ') = (n_callee_cell)',
            *warning('S_warning', 'S'), *reach('S_handler', 'S_warning', 1, 'INTRINSIC_CONSTANT'),
            'S_handler.CURRENT = (pcallcontext_handler)',
            '$error_context_call(S_handler,pcallcontext_handler) = (perrorcall_handler)',
            'perrorcall_handler.RESUME = DYNAMIC_NULL_CONSTANT_RESULT pconfigcall_S',
            '$error_context_valid(S_handler,pcallcontext_handler)',
            '$error_context_trigger(S_handler,pcallcontext_handler) = (pconfigcall_S)',
            '$error_handler_trace_values(S_handler,pcallcontext_handler,pconfigcall_S) = [PNULL]',
            *reach('S_literal', 'S_handler', 3, 'INTRINSIC_DEFINED'),
            'S_literal.TODO = (CONFIG_INVOKE pconfigcall_literal) :: ptask_literal*',
            '$intrinsic_argument(S_literal,pconfigcall_literal.SITE,0) = ((expression,false,preqbytes?,porigin_argument,z))',
            '$compiled_read(S_literal,porigin_argument) = (pvalue_literal)', '$string_bytes(pvalue_literal) = (eps)',
            'pconfigcall_bad_raw = pconfigcall_literal[.SENT = [NAMED_SENT (KNOWN PNULL)]]',
            '$config_invoke_valid(S_literal,pconfigcall_bad_raw)', '~$dynamic_null_constant_valid(S_literal,pconfigcall_bad_raw)',
            'S_bad_raw = $drive_steps(S_literal[.TODO = (CONFIG_INVOKE pconfigcall_bad_raw) :: ptask_literal*],1)',
            'S_bad_raw.COMPLETION = BUDGET',
            'S_bad_raw.TODO = [ERROR_UNWIND (UNSUPPORTED "null constant name reception")]',
            *resume('S_resume', 'S_literal', 'S', 'INTRINSIC_CONSTANT'),
            '$user_constant_at(S_resume.USERCONSTANTS,eps) = (puserconstant_empty)',
            'puserconstant_empty.VALUE = PINT 129', 'S_resume.STORE[n_name_cell] = DEFINED pvalue_name',
            '$string_bytes(pvalue_name) = (' + text('changed') + ')', 'S_resume.STORE[n_callee_cell] = DEFINED pvalue_callee',
            '$string_bytes(pvalue_callee) = (' + text('defined') + ')',
            *finish('S_value', 'S_resume', 'PINT 129'), *budget('S_resume')]
        for change in ('.SITE = PORIGIN 0 eps', '.LINE = $(pconfigcall_S.LINE + 1)', '.KIND = INTRINSIC_DEFINED', '.SELECTION = eps'):
            values += ['~$dynamic_null_constant_valid(S,pconfigcall_S[' + change + '])']
        for raw in ('PINT 0', 'PSTRING ' + text(''), 'PARRAY 0', 'POBJECT 0'):
            values += ['~$dynamic_null_constant_call(pconfigcall_S[.SENT = [NAMED_SENT (KNOWN (' + raw + '))]])']
        values += ['~$dynamic_null_constant_call(pconfigcall_S[.OWNER = (0)])',
            '~$error_call_valid(S_warning,perrorcall_S_warning[.LEVEL = 2])',
            '~$error_call_valid(S_warning,perrorcall_S_warning[.MESSAGE = ' + text('changed') + '])', *budget('S')]
    elif name == 'default-deprecation-and-converted-missing-error':
        values += [*front('S', 'S_initial', 'INTRINSIC_DEFINED'), *warning('S_warning', 'S'),
            *resume('S_resume', 'S_warning', 'S', 'INTRINSIC_DEFINED'),
            '$(|S_resume.EVENTS| > 0)',
            'S_resume.EVENTS[$nabs($(|S_resume.EVENTS| - 1))] = DIAGNOSTIC "Deprecated" $dynamic_null_constant_message(pconfigcall_S) pconfigcall_S.LINE',
            '$user_constant_at(S_resume.USERCONSTANTS,eps) = eps', *finish('S_value', 'S_resume', 'PBOOL false'),
            *front('S_missing', 'S_value', 'INTRINSIC_CONSTANT'),
            '$lookup(S_missing.ENV,' + text('name') + ') = (n_name_cell)', 'S_missing.STORE[n_name_cell] = DEFINED PNULL',
            '$lookup(S_missing.ENV,' + text('result') + ') = (n_result_cell)', 'S_missing.STORE[n_result_cell] = DEFINED (PINT 99)',
            *warning('S_missing_warning', 'S_missing'), *resume('S_missing_resume', 'S_missing_warning', 'S_missing', 'INTRINSIC_CONSTANT'),
            'S_missing_resume_converted = $typed_apply(S_missing_resume,TYPESTRING PNULL,pconfigcall_S_missing.LINE)',
            'S_missing_resume_converted.RESULT = KNOWN pvalue_received', '$string_bytes(pvalue_received) = (eps)',
            '$string_carrier_valid(S_missing_resume_converted,pvalue_received)',
            'pconfigcall_S_missing_resume = pconfigcall_S_missing',
            *driver.error('S_error', 'S_missing_resume', 'constant', 'Error', 'pvalue_received', 'Undefined constant ""'),
            'S_error.STORE[n_name_cell] = DEFINED PNULL', 'S_error.STORE[n_result_cell] = DEFINED (PINT 99)',
            *budget('S_missing_resume')]
    else:
        assert name == 'strict-null-name-errors-without-deprecation'
        values += [*front('S', 'S_initial', 'INTRINSIC_CONSTANT'), '$config_strict(S,pconfigcall_S)',
            '$test_outputs(S.EVENTS) = ' + text('B|N|'),
            '$lookup(S.ENV,' + text('result') + ') = (n_result_cell)', 'S.STORE[n_result_cell] = DEFINED (PINT 99)',
            '~$call_task_valid(S,DYNAMIC_NULL_CONSTANT_RESULT pconfigcall_S)',
            *driver.error('S_error', 'S', 'constant', 'TypeError', 'PNULL', 'constant(): Argument #1 ($name) must be of type string, null given'),
            'S_error.STRINGDATA = S.STRINGDATA', *front('S_defined', 'S_error', 'INTRINSIC_DEFINED'),
            '$config_strict(S_defined,pconfigcall_S_defined)',
            *driver.error('S_defined_error', 'S_defined', 'defined', 'TypeError', 'PNULL', 'defined(): Argument #1 ($constant_name) must be of type string, null given'),
            'S_defined_error.STRINGDATA = S_defined.STRINGDATA', 'S_defined_error.STORE[n_result_cell] = DEFINED (PINT 99)',
            *budget('S')]
    return values


if __name__ == '__main__':
    original_inputs = sources.family.fingerprint
    sources.family.fingerprint = lambda: dict(original_inputs(), **{str(Path(__file__).relative_to(driver.ROOT)): sources.family.sha(__file__)})
    driver.sources, driver.PREFIX, driver.checks = sources, PREFIX, checks
    driver.main()
