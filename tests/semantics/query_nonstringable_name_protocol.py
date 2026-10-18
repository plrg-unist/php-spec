#!/usr/bin/env python3
"""Actual query TypeErrors keep nonStringable receivers and argument effects."""
import json
import os
from pathlib import Path

import global_constant_scalar_name_protocol as driver
import query_nonstringable_name_sources as sources

common, text, b64 = driver.common, driver.text, driver.b64

PREFIX = r"""
dec $test_query_nonstring_front(pstate, pintrinsic) : bool
def $test_query_nonstring_front(S, pintrinsic) = true
  -- if S.TODO = (CONFIG_INVOKE pconfigcall) :: ptask_tail*
  -- if pconfigcall.KIND = pintrinsic
  -- if $dynamic_query_string_call(pconfigcall)
def $test_query_nonstring_front(S, pintrinsic) = false -- otherwise
dec $test_query_nonstring_seek(pstate, pintrinsic, nat) : pstate
def $test_query_nonstring_seek(S, pintrinsic, 0) = S
def $test_query_nonstring_seek(S, pintrinsic, n) = S
  -- if $(n > 0)
  -- if $test_query_nonstring_front(S,pintrinsic) \/ (S.COMPLETION =/= NORMAL /\ S.COMPLETION =/= BUDGET)
def $test_query_nonstring_seek(S, pintrinsic, n) = $test_query_nonstring_seek($drive_steps($test_running(S),1),pintrinsic,$nabs($(n - 1)))
  -- if $(n > 0)
  -- if ~$test_query_nonstring_front(S,pintrinsic)
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
"""


def front(state, start, kind):
    call, obj = 'pconfigcall_' + state, 'n_object_' + state
    return [state + '_found = $test_query_nonstring_seek(' + start + ',' + kind + ',3000)',
        state + '_found.COMPLETION = NORMAL \\/ ' + state + '_found.COMPLETION = BUDGET',
        state + ' = ' + state + '_found[.COMPLETION = NORMAL]',
        '$test_query_nonstring_front(' + state + ',' + kind + ')',
        state + '.TODO = (CONFIG_INVOKE ' + call + ') :: ptask_' + state + '*',
        call + '.KIND = ' + kind, call + '.SENT = [NAMED_SENT (KNOWN (POBJECT ' + obj + '))]',
        call + '.OWNER = eps', call + '.PACKS = eps', '~' + call + '.NAMED', call + '.INDEX = 1',
        '$config_invoke_valid(' + state + ',' + call + ')',
        '$dynamic_query_nonstring_object(' + state + ',' + obj + ')',
        '$dynamic_query_nonstring_valid(' + state + ',' + call + ')',
        '~$dynamic_query_string_valid(' + state + ',' + call + ')',
        '~$config_string_launch(' + state + ',' + call + ')',
        '~$stringable_instance(' + state + ',' + obj + ')',
        '(HOBJECT ' + obj + ') <- ' + state + '.ALLOCATIONS',
        '$lookup(' + state + '.ENV,' + text('keep') + ') = (n_keep_' + state + ')',
        state + '.STORE[n_keep_' + state + '] = DEFINED (POBJECT ' + obj + ')',
        '$lookup(' + state + '.ENV,' + text('result') + ') = (n_result_' + state + ')',
        state + '.STORE[n_result_' + state + '] = DEFINED (PINT 99)', *common.public(state)]


def error(after, before, api, classname, caller=None):
    call, obj = 'pconfigcall_' + before, 'n_object_' + before
    values = [*common.step(after, before),
        after + '.TODO = (THROW_SEARCH n_error_' + after + ') :: ptask_' + before + '*',
        after + '.OBJECTS[n_error_' + after + '] = THROWABLE pthrowable_' + after,
        'pthrowable_' + after + '.KIND = "TypeError"', 'pthrowable_' + after + '.ORIGIN = (' + call + '.SITE)',
        '$string_bytes($throwable_field(' + after + ',n_error_' + after + ',"message")) = (' + text(api+'(): Argument #1 ($'+('name' if api=='constant' else 'constant_name')+') must be of type string, '+classname+' given') + ')',
        '$throwable_field(' + after + ',n_error_' + after + ',"line") = PINT ' + call + '.LINE',
        '$string_bytes($throwable_field(' + after + ',n_error_' + after + ',"file")) = ($call_sourcefile(' + before + '.FILES,' + call + '.SITE))',
        '$throwable_field(' + after + ',n_error_' + after + ',"previous") = PNULL',
        '$throwable_field(' + after + ',n_error_' + after + ',"trace") = PARRAY n_trace_' + after]
    entries = '[ENTRY (KINT 0) (DIRECT (PARRAY n_api_' + after + '))'
    if caller is not None:
        entries += ',ENTRY (KINT 1) (DIRECT (PARRAY n_caller_' + after + '))'
    values += [after + '.ARRAYS[n_trace_' + after + '].ITEMS = ' + entries + ']',
        '$trace_array_field(' + after + ',n_api_' + after + ',' + text('function') + ') = PSTRING ' + text(api),
        '$trace_array_field(' + after + ',n_api_' + after + ',' + text('line') + ') = PINT ' + call + '.LINE',
        '$trace_array_field(' + after + ',n_api_' + after + ',' + text('args') + ') = PARRAY n_args_' + after,
        after + '.ARRAYS[n_args_' + after + '].ITEMS = [ENTRY (KINT 0) (DIRECT (POBJECT ' + obj + '))]',
        '$node_children(' + after + ',HARRAY n_args_' + after + ') = [HOBJECT ' + obj + ']',
        after + '.OBJECTS[' + obj + '] = ' + before + '.OBJECTS[' + obj + ']',
        '$objectprops_at(' + after + '.OBJECTPROPS,' + obj + ') = $objectprops_at(' + before + '.OBJECTPROPS,' + obj + ')',
        '~$dynamic_query_nonstring_object(' + after + ',n_error_' + after + ')']
    if caller is not None:
        values += ['$trace_array_field(' + after + ',n_caller_' + after + ',' + text('function') + ') = PSTRING ' + text(caller)]
    values += [after + '.' + field + ' = ' + before + '.' + field for field in (
        'STORE','ENV','OBJECTTABLES','USERCONSTANTS','STRINGDATA','EVENTS','SELECTEDCALLS','AUTOLOAD','CLASSNAMES','CLASSCONSTANTCACHE','REFCELLS')]
    return values + [after + '.STORE[n_result_' + before + '] = DEFINED (PINT 99)', *common.public(after)]


def refusals(state):
    call, obj = 'pconfigcall_' + state, 'n_object_' + state
    values = []
    for change in ('.SITE = PORIGIN 0 eps', '.LINE = $(' + call + '.LINE + 1)', '.INDEX = 0', '.SELECTION = (|' + state + '.SELECTEDCALLS|)'):
        values += ['~$dynamic_query_nonstring_valid(' + state + ',' + call + '[' + change + '])']
    for change in ('.OWNER = (0)', '.NAMED = true', '.KIND = INTRINSIC_DEFINE', '.SENT = eps', '.SENT = ' + call + '.SENT ++ [NAMED_SENT (KNOWN PNULL)]', '.SENT = [NAMED_SENT (KNOWN PNULL)]'):
        values += ['~$dynamic_query_nonstring_valid(' + state + ',' + call + '[' + change + '])']
    values += ['~$dynamic_query_nonstring_object(' + state + ',(|' + state + '.OBJECTS|))',
        '~$dynamic_query_nonstring_object(' + state + '[.ALLOCATIONS = eps],' + obj + ')',
        'S_wrong_class_' + state + ' = ' + state + '[.OBJECTS[' + obj + '] = INSTANCE (PORIGIN 0 eps)]',
        '~$dynamic_query_nonstring_object(S_wrong_class_' + state + ',' + obj + ')',
        '~$dynamic_query_nonstring_valid(S_wrong_class_' + state + ',' + call + ')',
        'pconfigcall_dead_' + state + ' = ' + call + '[.SENT = [NAMED_SENT (KNOWN (POBJECT (|' + state + '.OBJECTS|)))]]',
        '$dynamic_query_string_call(pconfigcall_dead_' + state + ')',
        '~$dynamic_query_nonstring_valid(' + state + ',pconfigcall_dead_' + state + ')']
    return values


def budget(state):
    return [state + '_pause = $drive_steps(' + state + ',0)', state + '_pause = ' + state + '[.COMPLETION = BUDGET]',
        state + '_one = $drive_steps(' + state + ',1)', state + '_one = $drive_steps(' + state + '_pause[.COMPLETION = NORMAL],1)']


def checks(program, path, name):
    kind = 'INTRINSIC_DEFINED' if name.startswith('strict-') else 'INTRINSIC_CONSTANT'
    values = ['S_initial = $php_run(' + program + ',0,' + json.dumps(b64(os.fsencode(path))) + ')',
        'S_initial.COMPLETION = BUDGET', *front('S', 'S_initial', kind)]
    if name == 'ordinary-object-query-names-reject-before-lookup':
        values += ['~$config_strict(S,pconfigcall_S)',
            'S.OBJECTS[n_object_S] = INSTANCE porigin_class',
            '$effective_method(S,porigin_class,' + text('__toString') + ',|S.CLASSES|) = eps',
            *error('S_error','S','constant','PlainQueryName54'),
            *front('S_defined','S_error','INTRINSIC_DEFINED'),
            'n_object_S_defined = n_object_S', '~$config_strict(S_defined,pconfigcall_S_defined)',
            *error('S_defined_error','S_defined','defined','PlainQueryName54'),
            *refusals('S'), *budget('S'), *budget('S_defined')]
    else:
        strict = name == 'strict-stdclass-defined-rejects-after-argument-effects'
        assert strict or name == 'selected-constant-object-name-keeps-earlier-receiver'
        values += [('$config_strict' if strict else '~$config_strict') + '(S,pconfigcall_S)',
            'pconfigcall_S.SELECTION = (n_selection)',
            'S.SELECTEDCALLS[n_selection].KIND = ' + kind,
            '$lookup(S.ENV,' + text('effects') + ') = (n_effects)', 'S.STORE[n_effects] = DEFINED (PINT 1)',
            '$test_outputs(S.EVENTS) = ' + text('B|N|')]
        if strict: values += ['S.OBJECTS[n_object_S] = STDINSTANCE']
        for variable, expected in (('call','constant' if strict else 'defined'),('name','strict-live54' if strict else 'live-name54')):
            values += ['$lookup(S.ENV,' + text(variable) + ') = (n_live_' + variable + ')',
                'S.STORE[n_live_' + variable + '] = DEFINED pvalue_live_' + variable,
                '$string_bytes(pvalue_live_' + variable + ') = (' + text(expected) + ')']
        values += [*error('S_error','S','defined' if strict else 'constant',
            'stdClass' if strict else 'SelectedPlainQuery54','strictPlainQueryCaller54' if strict else 'plainQueryCaller54'),
            *refusals('S'), *budget('S')]
    return values


def main():
    fingerprint = sources.family.fingerprint
    sources.family.fingerprint = lambda: dict(fingerprint(), **{
        str(Path(__file__).relative_to(driver.ROOT)): sources.family.sha(__file__)})
    driver.sources, driver.PREFIX, driver.checks = sources, PREFIX, checks
    driver.main()


if __name__ == '__main__':
    main()
