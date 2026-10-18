#!/usr/bin/env python3
"""Actual intrinsic owners survive NULL-option callbacks and wrapper parsing."""
import json
import os
from pathlib import Path

import global_constant_scalar_name_protocol as driver
import ini_set_owned_null_option_sources as sources

common, text, b64 = driver.common, driver.text, driver.b64
MESSAGE = 'ini_set(): Passing null to parameter #1 ($option) of type string is deprecated'
PREFIX = r"""
dec $test_ini_owned_front(pstate, nat) : bool
def $test_ini_owned_front(S, 0) = true
  -- if S.TODO = (CONFIG_INVOKE pconfigcall) :: ptask_tail*
  -- if pconfigcall.KIND = INTRINSIC_INI_SET
  -- if pconfigcall.OWNER = (n_owner)
  -- if pconfigcall.SENT = [NAMED_SENT (KNOWN PNULL),NAMED_SENT (KNOWN pvalue)]
def $test_ini_owned_front(S, 1) = true
  -- if S.CURRENT = (pcallcontext)
  -- if $error_context_call(S,pcallcontext) = (perrorcall)
  -- if perrorcall.RESUME = CONFIG_INI_NULL_RESULT pconfigcall
  -- if pconfigcall.KIND = INTRINSIC_INI_SET
  -- if pconfigcall.OWNER = (n_owner)
def $test_ini_owned_front(S, 2) = true
  -- if S.TODO = (ERROR_HANDLER_RESULT perrorcall) :: ptask_tail*
  -- if perrorcall.RESUME = CONFIG_INI_NULL_RESULT pconfigcall
  -- if pconfigcall.KIND = INTRINSIC_INI_SET
  -- if pconfigcall.OWNER = (n_owner)
def $test_ini_owned_front(S, 3) = true
  -- if S.TODO = (CONFIG_ARGS pconfigcall) :: ptask_tail*
  -- if pconfigcall.KIND = INTRINSIC_INI_SET
  -- if pconfigcall.OWNER = (n_owner)
  -- if pconfigcall.INDEX = 1
  -- if pconfigcall.SENT = [NAMED_SENT (KNOWN PNULL)]
def $test_ini_owned_front(S, n_stage) = false -- otherwise
dec $test_ini_owned_seek(pstate, nat, nat) : pstate
def $test_ini_owned_seek(S, n_stage, 0) = S
def $test_ini_owned_seek(S, n_stage, n) = S
  -- if $(n > 0)
  -- if $test_ini_owned_front(S,n_stage) \/ (S.COMPLETION =/= NORMAL /\ S.COMPLETION =/= BUDGET)
def $test_ini_owned_seek(S, n_stage, n) = $test_ini_owned_seek($drive_steps($test_running(S),1),n_stage,$nabs($(n - 1)))
  -- if $(n > 0)
  -- if ~$test_ini_owned_front(S,n_stage)
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
"""


def reach(state, start, stage):
    return [state + '_found = $test_ini_owned_seek(' + start + ',' + str(stage) + ',3000)',
        state + '_found.COMPLETION = NORMAL \\/ ' + state + '_found.COMPLETION = BUDGET',
        state + ' = ' + state + '_found[.COMPLETION = NORMAL]',
        '$test_ini_owned_front(' + state + ',' + str(stage) + ')']


def unchanged(after, before, fields):
    return [after + '.' + field + ' = ' + before + '.' + field for field in fields.split()]


def budget(state):
    return [state + '_pause = $drive_steps(' + state + ',0)',
        state + '_pause = ' + state + '[.COMPLETION = BUDGET]',
        state + '_one = $drive_steps(' + state + ',1)',
        state + '_one = $drive_steps(' + state + '_pause[.COMPLETION = NORMAL],1)']


def front(state, start, candidate):
    call, owner = 'pconfigcall_' + state, 'n_owner_' + state
    return [*reach(state, start, 0), state + '.TODO = (CONFIG_INVOKE ' + call + ') :: ptask_' + state + '*',
        call + '.KIND = INTRINSIC_INI_SET', call + '.OWNER = (' + owner + ')',
        call + '.INDEX = 2', call + '.SELECTION = eps', call + '.PACKS = eps', '~' + call + '.NAMED',
        call + '.SENT = [NAMED_SENT (KNOWN PNULL),NAMED_SENT (KNOWN (' + candidate + '))]',
        state + '.OBJECTS[' + owner + '] = INTRINSICCLOSURE INTRINSIC_INI_SET',
        '(HOBJECT ' + owner + ') <- ' + state + '.ALLOCATIONS',
        '$getclass_live_object(' + state + ',' + owner + ')',
        '$config_invoke_valid(' + state + ',' + call + ')',
        '$dynamic_scalar_define_arguments(' + state + ',' + call + ',0)',
        '$config_nodes(' + call + ') = [HOBJECT ' + owner + ']',
        '$task_nodes(CONFIG_INI_NULL_RESULT ' + call + ') = [HOBJECT ' + owner + ']', *common.public(state)]


def refusals(state):
    call, owner = 'pconfigcall_' + state, 'n_owner_' + state
    values = []
    for field in ('.OWNER = eps', '.OWNER = (|' + state + '.OBJECTS|)', '.NAMED = true',
            '.LINE = $(' + call + '.LINE + 1)', '.SITE = PORIGIN 0 eps', '.INDEX = 1',
            '.SELECTION = (0)', '.SENT = ' + call + '.SENT[0:1]',
            '.SENT = ' + call + '.SENT ++ [NAMED_SENT (KNOWN PNULL)]'):
        values += ['~$config_ini_null_valid(' + state + ',' + call + '[' + field + '])']
    values += ['~$config_ini_null_valid(' + state + '[.OBJECTS[' + owner + '] = INTRINSICCLOSURE INTRINSIC_INI_GET],' + call + ')',
        'pvalue_bad_' + state + ' = PSTRING_CARRIER (REQUEST_STRING (|' + state + '.STRINGDATA|)) ' + text('bad64'),
        '~$config_ini_null_valid(' + state + ',' + call + '[.SENT = $named_slot_set(' + call + '.SENT,1,KNOWN pvalue_bad_' + state + ')])']
    return values


def handled(state, candidate, warnings, precision, result):
    call, owner = 'pconfigcall_' + state, 'n_owner_' + state
    dispatch, entered, returned, resume, after = [state + '_' + s for s in ('dispatch', 'entered', 'return', 'resume', 'after')]
    error, error_return = 'perrorcall_' + state, 'perrorcall_return_' + state
    return ['$config_ini_null_valid(' + state + ',' + call + ')', '$error_handler_eligible(' + state + ',8192)',
        *common.step(dispatch, state), dispatch + '.TODO = (ERROR_HANDLER_INVOKE ' + error + ') :: ptask_' + state + '*',
        error + '.RESUME = CONFIG_INI_NULL_RESULT ' + call, error + '.LEVEL = 8192',
        error + '.MESSAGE = ' + text(MESSAGE), error + '.SITE = ' + call + '.SITE', error + '.LINE = ' + call + '.LINE',
        error + '.EVENT = DIAGNOSTIC "Deprecated" ' + error + '.MESSAGE ' + error + '.LINE',
        '$error_call_valid(' + dispatch + ',' + error + ')', *common.public(dispatch),
        *reach(entered, dispatch, 1), entered + '.CURRENT = (pcallcontext_' + state + ')',
        '$error_context_valid(' + entered + ',pcallcontext_' + state + ')',
        '$error_handler_trace_values(' + entered + ',pcallcontext_' + state + ',' + call + ') = [PNULL,' + candidate + ']',
        entered + '.OBJECTS[' + owner + '] = INTRINSICCLOSURE INTRINSIC_INI_SET',
        *common.public(entered), *reach(returned, entered, 2),
        returned + '.TODO = (ERROR_HANDLER_RESULT ' + error_return + ') :: ptask_' + state + '*',
        error_return + '.RESUME = CONFIG_INI_NULL_RESULT ' + call,
        '$call_task_valid(' + returned + ',ERROR_HANDLER_RESULT ' + error_return + ')',
        returned + '.RESULT = KNOWN (PBOOL ' + result + ')', returned + '.CURRENT = ' + state + '.CURRENT',
        returned + '.ENV = ' + state + '.ENV', returned + '.FRAMES = ' + state + '.FRAMES',
        returned + '.PRECISIONINI = ' + text(precision),
        '$lookup(' + returned + '.ENV,' + text('warnings') + ') = (n_warnings_' + state + ')',
        returned + '.STORE[n_warnings_' + state + '] = DEFINED (PINT ' + str(warnings) + ')',
        *common.public(returned), *common.step(resume, returned),
        resume + '.TODO = (CONFIG_INI_NULL_RESULT ' + call + ') :: ptask_' + state + '*',
        resume + '.ERRORHANDLER.CALLBACK = (' + error_return + '.CALLBACK)', resume + '.RESULT = KNOWN PNULL',
        '$call_task_valid(' + resume + ',CONFIG_INI_NULL_RESULT ' + call + ')',
        *unchanged(resume, returned, 'STORE ENV ARRAYS OBJECTS STRINGDATA USERCONSTANTS PRECISIONINI PRECISIONMODIFIED'),
        resume + '.EVENTS = ' + returned + '.EVENTS' + (' ++ [DIAGNOSTIC "Deprecated" ' + error + '.MESSAGE ' + error + '.LINE]' if result == 'false' else ''),
        *common.public(resume), *common.step(after, resume),
        after + ' = ' + resume + '[.TODO = ptask_' + state + '*][.RESULT = KNOWN (PBOOL false)][.BASE = BASE_VALUE (KNOWN PNULL)]',
        '$getclass_live_object(' + after + ',' + owner + ')', *common.public(after)]


def checks(program, path, name):
    values = ['S_initial = $php_run(' + program + ',0,' + json.dumps(b64(os.fsencode(path))) + ')',
        'S_initial.COMPLETION = BUDGET']
    if name == 'retained-intrinsic-null-default-and-true-handler':
        values += [*front('S', 'S_initial', 'PINT 2071'), '~$config_strict(S,pconfigcall_S)',
            '~$config_method_receiver(S,pconfigcall_S)', '$config_ini_null_valid(S,pconfigcall_S)',
            '~$error_handler_eligible(S,8192)', *common.step('S_after', 'S'),
            'S_after.TODO = ptask_S*', 'S_after.RESULT = KNOWN (PBOOL false)',
            'S_after.EVENTS = S.EVENTS ++ [DIAGNOSTIC "Deprecated" $config_ini_null_message(pconfigcall_S) pconfigcall_S.LINE]',
            'S_after.PRECISIONINI = ' + text('14'), '$getclass_live_object(S_after,n_owner_S)',
            *front('S_handled', 'S_after', 'PSTRING_CARRIER INTERNED_STRING ' + text('value64')),
            'n_owner_S_handled = n_owner_S',
            *handled('S_handled', 'PSTRING_CARRIER INTERNED_STRING ' + text('value64'), 1, '8', 'true'),
            *refusals('S_handled'), *budget('S'), *budget('S_handled_resume'),
            'S_final = $drive_steps(S_handled_after,3000)', 'S_final.COMPLETION = NORMAL',
            '$test_outputs(S_final.EVENTS) = ' + text('B|F|14|H|8192|' + MESSAGE + '|F|1|8')]
    elif name == 'captured-intrinsic-owner-before-value-rebinding-and-fallback':
        values += [*reach('S_pre', 'S_initial', 3),
            'S_pre.TODO = (CONFIG_ARGS pconfigcall_pre) :: ptask_pre*',
            'pconfigcall_pre.OWNER = (n_owner_pre)', '$call_task_valid(S_pre,CONFIG_ARGS pconfigcall_pre)',
            '$lookup(S_pre.ENV,' + text('call') + ') = (n_call)', 'S_pre.STORE[n_call] = DEFINED (POBJECT n_owner_pre)',
            '$lookup(S_pre.ENV,' + text('keep') + ') = (n_keep)', 'S_pre.STORE[n_keep] = DEFINED (POBJECT n_owner_pre)',
            '$lookup(S_pre.ENV,' + text('value') + ') = (n_value)', 'S_pre.STORE[n_value] = DEFINED pvalue_captured',
            'pvalue_captured = PSTRING_CARRIER (REQUEST_STRING n_candidate) ' + text('captured-value64'),
            '$lookup(S_pre.ENV,' + text('effects') + ') = (n_effects)', 'S_pre.STORE[n_effects] = DEFINED (PINT 0)',
            '$test_outputs(S_pre.EVENTS) = ' + text('B|'), *front('S', 'S_pre', 'pvalue_captured'),
            'pconfigcall_S = pconfigcall_pre[.INDEX = 2][.SENT = [NAMED_SENT (KNOWN PNULL),NAMED_SENT (KNOWN pvalue_captured)]]',
            'n_owner_S = n_owner_pre', 'S.STORE[n_keep] = DEFINED (POBJECT n_owner_S)',
            'S.STORE[n_call] = DEFINED (POBJECT n_replacement)', 'n_replacement =/= n_owner_S',
            'S.OBJECTS[n_replacement] = INTRINSICCLOSURE INTRINSIC_INI_GET',
            'S.STORE[n_effects] = DEFINED (PINT 1)', '$test_outputs(S.EVENTS) = ' + text('B|V|'),
            '$string_carrier_valid(S,pvalue_captured)', '~$config_method_receiver(S,pconfigcall_S)',
            *handled('S', 'pvalue_captured', 1, '9', 'false'),
            'S_after.STORE[n_keep] = DEFINED (POBJECT n_owner_S)',
            *refusals('S'), *budget('S'), *budget('S_resume'),
            'S_final = $drive_steps(S_after,3000)', 'S_final.COMPLETION = NORMAL',
            'S_final.PRECISIONINI = ' + text('10'),
            '$test_outputs(S_final.EVENTS) = ' + text('B|V|W|8192|' + MESSAGE + '|F|9|1|1|handler-value64|D|Z|9|10')]
    else:
        assert name == 'strict-intrinsic-call-before-weak-explicit-invoke-null'
        values += [*front('S', 'S_initial', 'PINT 2089'), '$config_strict(S,pconfigcall_S)',
            '~$config_method_receiver(S,pconfigcall_S)', '~$config_ini_null_valid(S,pconfigcall_S)',
            '$lookup(S.ENV,' + text('keep') + ') = (n_keep)', 'S.STORE[n_keep] = DEFINED (POBJECT n_owner_S)',
            '$lookup(S.ENV,' + text('result') + ') = (n_result)', 'S.STORE[n_result] = DEFINED (PINT 99)',
            '$test_outputs(S.EVENTS) = ' + text('B|V|'), 'S.PRECISIONINI = ' + text('9'),
            *common.step('S_error', 'S'), 'S_error.TODO = (THROW_SEARCH n_error) :: ptask_S*',
            'S_error.OBJECTS[n_error] = THROWABLE pthrowable_error', 'pthrowable_error.KIND = "TypeError"',
            '$string_bytes($throwable_field(S_error,n_error,"message")) = (' + text('ini_set(): Argument #1 ($option) must be of type string, null given') + ')',
            '$throwable_field(S_error,n_error,"trace") = PARRAY n_trace',
            'S_error.ARRAYS[n_trace].ITEMS = [ENTRY (KINT 0) (DIRECT (PARRAY n_api)),ENTRY (KINT 1) (DIRECT (PARRAY n_caller))]',
            '$trace_array_field(S_error,n_api,' + text('function') + ') = PSTRING ' + text('ini_set'),
            '$trace_array_field(S_error,n_api,' + text('args') + ') = PARRAY n_args',
            'S_error.ARRAYS[n_args].ITEMS = [ENTRY (KINT 0) (DIRECT PNULL),ENTRY (KINT 1) (DIRECT (PINT 2089))]',
            '$trace_array_field(S_error,n_caller,' + text('function') + ') = PSTRING ' + text('strictIntrinsicCaller64'),
            'S_error.STORE[n_result] = DEFINED (PINT 99)', *unchanged('S_error', 'S', 'STORE ENV EVENTS PRECISIONINI ERRORHANDLER'),
            *common.public('S_error'), *front('S_wrapper', 'S_error', 'PINT 2093'),
            'n_owner_S_wrapper = n_owner_S', '$config_method_receiver(S_wrapper,pconfigcall_S_wrapper)',
            '$exit_strict(S_wrapper,pconfigcall_S_wrapper.SITE)', '~$config_strict(S_wrapper,pconfigcall_S_wrapper)',
            *handled('S_wrapper', 'PINT 2093', 1, '8', 'true'),
            *refusals('S_wrapper'), *budget('S'), *budget('S_wrapper_resume'),
            'S_final = $drive_steps(S_wrapper_after,3000)', 'S_final.COMPLETION = NORMAL',
            '$test_outputs(S_final.EVENTS) = ' + text('B|V|ini_set(): Argument #1 ($option) must be of type string, null given|99|1|0|9|E|H|8192|' + MESSAGE + '|F|8|1|1|0|Z')]
    values += ['S_final.TODO = eps', 'S_final.CURRENT = eps', 'S_final.FRAMES = eps',
        'S_final.ERRORHANDLER.CALLBACK = eps', 'S_final.USERCONSTANTS = eps', *common.public('S_final')]
    return values


def main():
    fingerprint = sources.family.fingerprint
    sources.family.fingerprint = lambda: dict(fingerprint(), **{
        str(Path(__file__).relative_to(driver.ROOT)): sources.family.sha(__file__)})
    driver.sources, driver.PREFIX, driver.checks = sources, PREFIX, checks
    driver.main()


if __name__ == '__main__':
    main()
