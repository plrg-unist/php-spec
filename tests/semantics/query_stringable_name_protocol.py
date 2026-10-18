#!/usr/bin/env python3
"""Reached Stringable query calls preserve raw/converted phases and effects."""
import json
import os
from pathlib import Path

import global_constant_scalar_name_protocol as driver
import query_stringable_name_sources as sources

common, text, b64 = driver.common, driver.text, driver.b64

PREFIX = r"""
dec $test_query_string_front(pstate, nat, pintrinsic) : bool
def $test_query_string_front(S, 0, pintrinsic) = true
  -- if S.TODO = (CONFIG_INVOKE pconfigcall) :: ptask_tail*
  -- if pconfigcall.KIND = pintrinsic
  -- if $dynamic_query_string_call(pconfigcall)
def $test_query_string_front(S, 1, pintrinsic) = true
  -- if S.CURRENT = (pcallcontext)
  -- if $context_target(pcallcontext) = METHOD_TARGET n_object porigin_method
  -- if S.FRAMES = pframe :: pframe_tail*
  -- if pframe.TODO = (STRINGIFY_RESULT n_object porigin_child z_call) :: (CONFIG_STRING_RESULT pconfigcall n_object porigin_child z_child z_call) :: ptask_tail*
  -- if pconfigcall.KIND = pintrinsic
  -- if $dynamic_query_string_call(pconfigcall)
def $test_query_string_front(S, 2, pintrinsic) = true
  -- if S.TODO = (CONFIG_STRING_RESULT pconfigcall n_object porigin_child z_child z_call) :: ptask_tail*
  -- if pconfigcall.KIND = pintrinsic
  -- if $dynamic_query_string_call(pconfigcall)
def $test_query_string_front(S, n_stage, pintrinsic) = false -- otherwise
dec $test_query_string_seek(pstate, nat, pintrinsic, nat) : pstate
def $test_query_string_seek(S, n_stage, pintrinsic, 0) = S
def $test_query_string_seek(S, n_stage, pintrinsic, n) = S
  -- if $(n > 0)
  -- if $test_query_string_front(S,n_stage,pintrinsic) \/ (S.COMPLETION =/= NORMAL /\ S.COMPLETION =/= BUDGET)
def $test_query_string_seek(S, n_stage, pintrinsic, n) = $test_query_string_seek($drive_steps($test_running(S),1),n_stage,pintrinsic,$nabs($(n - 1)))
  -- if $(n > 0)
  -- if ~$test_query_string_front(S,n_stage,pintrinsic)
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
"""


def reach(state, start, stage, kind):
    return [state + '_found = $test_query_string_seek(' + start + ',' + str(stage) + ',' + kind + ',3000)',
        state + '_found.COMPLETION = NORMAL \\/ ' + state + '_found.COMPLETION = BUDGET',
        state + ' = ' + state + '_found[.COMPLETION = NORMAL]',
        '$test_query_string_front(' + state + ',' + str(stage) + ',' + kind + ')']


def front(state, start, kind):
    call, obj = 'pconfigcall_' + state, 'n_object_' + state
    return [*reach(state, start, 0, kind),
        state + '.TODO = (CONFIG_INVOKE ' + call + ') :: ptask_' + state + '*',
        call + '.SENT = [NAMED_SENT (KNOWN (POBJECT ' + obj + '))]',
        call + '.KIND = ' + kind, call + '.OWNER = eps', call + '.PACKS = eps', '~' + call + '.NAMED',
        '$dynamic_query_string_valid(' + state + ',' + call + ')',
        '$config_invoke_valid(' + state + ',' + call + ')',
        '~$config_string_kind(' + kind + ')',
        '$config_string_source(' + state + ',' + call + ') = ((porigin_child_' + state + ',z_child_' + state + '))',
        '$config_string_object(' + call + ') = (' + obj + ')',
        *common.public(state)]


def weak(state, kind, name, result):
    call, obj = 'pconfigcall_' + state, 'n_object_' + state
    child, line = 'porigin_child_' + state, 'z_child_' + state
    entered, returned, ready, done = state + '_entered', state + '_returned', state + '_ready', state + '_done'
    values = ['~$config_strict(' + state + ',' + call + ')',
        '$config_string_launch(' + state + ',' + call + ')',
        '$config_string_site_valid(' + state + ',' + call + ',' + obj + ',' + child + ',' + line + ',' + call + '.LINE)',
        *common.step(state + '_launch', state),
        state + '_launch.TODO = (CALL_ARGS (METHOD_TARGET ' + obj + ' porigin_method_' + state + ') eps 0 eps (' + child + ') ' + call + '.LINE) :: (STRINGIFY_RESULT ' + obj + ' ' + child + ' ' + call + '.LINE) :: (CONFIG_STRING_RESULT ' + call + ' ' + obj + ' ' + child + ' ' + line + ' ' + call + '.LINE) :: ptask_' + state + '*',
        *reach(entered, state + '_launch', 1, kind),
        entered + '.CURRENT = (pcallcontext_' + state + ')',
        '$config_string_trace_context(' + entered + ',pcallcontext_' + state + ')',
        '$config_string_site_valid(' + entered + ',' + call + ',' + obj + ',' + child + ',' + line + ',' + call + '.LINE)',
        *common.public(entered),
        *reach(returned, entered, 2, kind),
        returned + '.TODO = (CONFIG_STRING_RESULT ' + call + ' ' + obj + ' ' + child + ' ' + line + ' ' + call + '.LINE) :: ptask_' + state + '*',
        returned + '.RESULT = KNOWN pvalue_string_' + state,
        '$string_bytes(pvalue_string_' + state + ') = (' + text(name) + ')',
        '$string_carrier_valid(' + returned + ',pvalue_string_' + state + ')',
        '$config_string_site_valid(' + returned + ',' + call + ',' + obj + ',' + child + ',' + line + ',' + call + '.LINE)',
        *common.public(returned), *common.step(ready, returned),
        'pconfigcall_converted_' + state + ' = ' + call + '[.SENT = [NAMED_SENT (KNOWN pvalue_string_' + state + ')]]',
        ready + '.TODO = (CONFIG_INVOKE pconfigcall_converted_' + state + ') :: ptask_' + state + '*',
        ready + '.ORIGIN = (' + call + '.SITE)', ready + '.RESULT = KNOWN PNULL',
        ready + '.BASE = BASE_VALUE (KNOWN PNULL)',
        '$config_invoke_valid(' + ready + ',pconfigcall_converted_' + state + ')',
        '~$dynamic_query_string_call(pconfigcall_converted_' + state + ')',
        '~$config_string_launch(' + ready + ',pconfigcall_converted_' + state + ')']
    values += [ready + '.' + field + ' = ' + returned + '.' + field for field in (
        'STORE','ENV','ARRAYS','OBJECTS','OBJECTPROPS','USERCONSTANTS','STRINGDATA','EVENTS','SELECTEDCALLS','AUTOLOAD','CLASSNAMES','CLASSCONSTANTCACHE')]
    values += [*common.public(ready)]
    if result is not None:
        values += [*common.step(done, ready, result), done + '.TODO = ptask_' + state + '*',
            done + '.STORE = ' + ready + '.STORE', done + '.USERCONSTANTS = ' + ready + '.USERCONSTANTS']
    return values


def refusals(state):
    call, obj = 'pconfigcall_' + state, 'n_object_' + state
    child, line = 'porigin_child_' + state, 'z_child_' + state
    values = []
    for field in ('.SITE = PORIGIN 0 eps', '.LINE = $(' + call + '.LINE + 1)', '.INDEX = 0', '.SELECTION = (|' + state + '.SELECTEDCALLS|)'):
        values += ['~$dynamic_query_string_valid(' + state + ',' + call + '[' + field + '])']
    for field in ('.OWNER = (0)', '.NAMED = true', '.KIND = INTRINSIC_DEFINE', '.SENT = eps', '.SENT = ' + call + '.SENT ++ [NAMED_SENT (KNOWN PNULL)]', '.SENT = [NAMED_SENT (KNOWN PNULL)]'):
        bad = call + '[' + field + ']'
        values += ['~$dynamic_query_string_call(' + bad + ')',
            '~$config_string_site_valid(' + state + ',' + bad + ',' + obj + ',' + child + ',' + line + ',' + call + '.LINE)',
            '~$config_string_launch(' + state + '[.FILEINCLUDEPATH = (eps)],' + bad + ')']
    values += ['~$config_string_site_valid(' + state + ',' + call + ',' + obj + ',' + child + ',$(' + line + ' + 1),' + call + '.LINE)',
        '~$config_string_site_valid(' + state + ',' + call + ',' + obj + ',PORIGIN 0 eps,' + line + ',' + call + '.LINE)',
        'pconfigcall_dead_' + state + ' = ' + call + '[.SENT = [NAMED_SENT (KNOWN (POBJECT (|' + state + '.OBJECTS|)))]]',
        '$dynamic_query_string_call(pconfigcall_dead_' + state + ')',
        '~$dynamic_query_string_valid(' + state + ',pconfigcall_dead_' + state + ')']
    return values


def budget(state):
    return [state + '_pause = $drive_steps(' + state + ',0)', state + '_pause = ' + state + '[.COMPLETION = BUDGET]',
        state + '_one = $drive_steps(' + state + ',1)', state + '_one = $drive_steps(' + state + '_pause[.COMPLETION = NORMAL],1)']


def error(after, before, call, argument, kind, message, api, caller):
    return [*common.step(after, before),
        after + '.TODO = (THROW_SEARCH n_error_' + after + ') :: ptask_S*',
        after + '.OBJECTS[n_error_' + after + '] = THROWABLE pthrowable_' + after,
        'pthrowable_' + after + '.KIND = ' + json.dumps(kind), 'pthrowable_' + after + '.ORIGIN = (' + call + '.SITE)',
        '$string_bytes($throwable_field(' + after + ',n_error_' + after + ',"message")) = (' + text(message) + ')',
        '$throwable_field(' + after + ',n_error_' + after + ',"previous") = PNULL',
        '$throwable_field(' + after + ',n_error_' + after + ',"line") = PINT ' + call + '.LINE',
        '$string_bytes($throwable_field(' + after + ',n_error_' + after + ',"file")) = ($call_sourcefile(' + after + '.FILES,' + call + '.SITE))',
        '$throwable_field(' + after + ',n_error_' + after + ',"trace") = PARRAY n_trace_' + after,
        after + '.ARRAYS[n_trace_' + after + '].ITEMS = [ENTRY (KINT 0) (DIRECT (PARRAY n_api_' + after + ')),ENTRY (KINT 1) (DIRECT (PARRAY n_caller_' + after + '))]',
        '$trace_array_field(' + after + ',n_api_' + after + ',' + text('function') + ') = PSTRING ' + text(api),
        '$trace_array_field(' + after + ',n_api_' + after + ',' + text('args') + ') = PARRAY n_args_' + after,
        after + '.ARRAYS[n_args_' + after + '].ITEMS = [ENTRY (KINT 0) (DIRECT ' + argument + ')]',
        '$trace_array_field(' + after + ',n_caller_' + after + ',' + text('function') + ') = PSTRING ' + text(caller),
        *[after + '.' + field + ' = ' + before + '.' + field for field in (
            'STORE','ENV','USERCONSTANTS','STRINGDATA','EVENTS','SELECTEDCALLS','AUTOLOAD','CLASSNAMES','CLASSCONSTANTCACHE')],
        *common.public(after)]


def checks(program, path, name):
    kind = 'INTRINSIC_DEFINED' if name.startswith('strict-') else 'INTRINSIC_CONSTANT'
    values = ['S_initial = $php_run(' + program + ',0,' + json.dumps(b64(os.fsencode(path))) + ')',
        'S_initial.COMPLETION = BUDGET', *front('S', 'S_initial', kind)]
    if name == 'weak-stringable-query-names-before-global-lookup':
        values += [*weak('S', kind, 'QueryStringValue53', 'PINT 1451'),
            *front('S_defined', 'S_done', 'INTRINSIC_DEFINED'),
            'n_object_S_defined = n_object_S',
            *weak('S_defined', 'INTRINSIC_DEFINED', 'QueryStringValue53', 'PBOOL true'),
            '$lookup(S_defined_done.ENV,' + text('calls') + ') = (n_calls)',
            'S_defined_done.STORE[n_calls] = DEFINED (PINT 2)',
            '$test_outputs(S_defined_done.EVENTS) = ' + text('B|S|1451|S|'),
            *refusals('S'), *budget('S'), *budget('S_returned')]
    elif name == 'selected-stringable-constant-keeps-converted-missing-name':
        values += ['pconfigcall_S.SELECTION = (n_selection)',
            'S.SELECTEDCALLS[n_selection].KIND = INTRINSIC_CONSTANT',
            '$lookup(S.ENV,' + text('result') + ') = (n_result)', 'S.STORE[n_result] = DEFINED (PINT 99)',
            *weak('S', kind, 'MissingQueryString53', None),
            '$lookup(S_returned.ENV,' + text('calls') + ') = (n_calls)', 'S_returned.STORE[n_calls] = DEFINED (PINT 1)']
        for variable, expected in (('call','defined'), ('name','live-name53')):
            values += ['$lookup(S_returned.ENV,' + text(variable) + ') = (n_live_' + variable + ')',
                'S_returned.STORE[n_live_' + variable + '] = DEFINED pvalue_live_' + variable,
                '$string_bytes(pvalue_live_' + variable + ') = (' + text(expected) + ')']
        values += ['pvalue_string_S = PSTRING_CARRIER (REQUEST_STRING n_string) preqbytes_string',
            *error('S_error','S_ready','pconfigcall_converted_S','pvalue_string_S','Error','Undefined constant "MissingQueryString53"','constant','queryMissingCaller53'),
            'S_error.STORE[n_result] = DEFINED (PINT 99)', *refusals('S'), *budget('S'), *budget('S_returned')]
        for value in ('PSTRING ' + text('A::B'), 'PSTRING (' + text('name53') + ' ++ [0])', 'PSTRING ' + text('__COMPILER_HALT_OFFSET__'),
                'PSTRING_CARRIER (REQUEST_STRING (|S_returned.STRINGDATA|)) ' + text('MissingQueryString53')):
            values += ['S_refused_' + str(len(values)) + ' = $dynamic_query_string_finish(S_returned,pconfigcall_S,' + value + ')',
                'S_refused_' + str(len(values)) + '.COMPLETION = UNSUPPORTED "Stringable query global name"']
    else:
        assert name == 'strict-stringable-defined-rejects-before-method'
        values += ['$config_strict(S,pconfigcall_S)', '~$config_string_launch(S,pconfigcall_S)',
            '~$config_string_site_valid(S,pconfigcall_S,n_object_S,porigin_child_S,z_child_S,pconfigcall_S.LINE)',
            '$lookup(S.ENV,' + text('effects') + ') = (n_effects)', 'S.STORE[n_effects] = DEFINED (PINT 1)',
            '$lookup(S.ENV,' + text('result') + ') = (n_result)', 'S.STORE[n_result] = DEFINED (PINT 99)',
            '$test_outputs(S.EVENTS) = ' + text('B|N|'),
            *error('S_error','S','pconfigcall_S','(POBJECT n_object_S)','TypeError',
                'defined(): Argument #1 ($constant_name) must be of type string, StrictQueryString53 given','defined','queryStrictCaller53'),
            'S_error.STORE[n_result] = DEFINED (PINT 99)', *refusals('S'), *budget('S')]
    return values


def main():
    fingerprint = sources.family.fingerprint
    sources.family.fingerprint = lambda: dict(fingerprint(), **{
        str(Path(__file__).relative_to(driver.ROOT)): sources.family.sha(__file__)})
    driver.sources, driver.PREFIX, driver.checks = sources, PREFIX, checks
    driver.main()


if __name__ == '__main__':
    main()
