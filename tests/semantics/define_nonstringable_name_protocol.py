#!/usr/bin/env python3
"""Reached nonStringable define calls reject raw names before flag processing."""
import json
import os
from pathlib import Path

import global_constant_scalar_name_protocol as driver
import define_nonstringable_name_sources as sources

common, text, b64 = driver.common, driver.text, driver.b64

PREFIX = r"""
dec $test_define_nonstring_front(pstate, nat) : bool
def $test_define_nonstring_front(S, n_count) = true
  -- if S.TODO = (CONFIG_INVOKE pconfigcall) :: ptask_tail*
  -- if $dynamic_define_nonstring_call(pconfigcall)
  -- if |pconfigcall.SENT| = n_count
def $test_define_nonstring_front(S, n_count) = false -- otherwise
dec $test_define_nonstring_seek(pstate, nat, nat) : pstate
def $test_define_nonstring_seek(S, n_count, 0) = S
def $test_define_nonstring_seek(S, n_count, n) = S
  -- if $(n > 0)
  -- if $test_define_nonstring_front(S,n_count) \/ (S.COMPLETION =/= NORMAL /\ S.COMPLETION =/= BUDGET)
def $test_define_nonstring_seek(S, n_count, n) = $test_define_nonstring_seek($drive_steps($test_running(S),1),n_count,$nabs($(n - 1)))
  -- if $(n > 0)
  -- if ~$test_define_nonstring_front(S,n_count)
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
"""


def unchanged(after, before, fields):
    return [after + '.' + f + ' = ' + before + '.' + f for f in fields.split()]


def front(state, start, candidate, flag):
    call, obj = 'pconfigcall_' + state, 'n_receiver_' + state
    slots = '[NAMED_SENT (KNOWN (POBJECT ' + obj + ')),NAMED_SENT (KNOWN (' + candidate + '))'
    slots += (',NAMED_SENT (KNOWN (' + flag + '))' if flag is not None else '') + ']'
    count = '2' if flag is None else '3'
    return [state + '_found = $test_define_nonstring_seek(' + start + ',' + count + ',3000)',
        state + '_found.COMPLETION = NORMAL \\/ ' + state + '_found.COMPLETION = BUDGET',
        state + ' = ' + state + '_found[.COMPLETION = NORMAL]', '$test_define_nonstring_front(' + state + ',' + count + ')',
        state + '.TODO = (CONFIG_INVOKE ' + call + ') :: ptask_' + state + '*', call + '.SENT = ' + slots,
        call + '.KIND = INTRINSIC_DEFINE', call + '.OWNER = eps', call + '.PACKS = eps', '~' + call + '.NAMED',
        '$dynamic_define_nonstring_valid(' + state + ',' + call + ')', '$config_invoke_valid(' + state + ',' + call + ')',
        '$dynamic_query_nonstring_object(' + state + ',' + obj + ')', '~$stringable_instance(' + state + ',' + obj + ')',
        '~$dynamic_define_string_valid(' + state + ',' + call + ')', '~$config_string_launch(' + state + ',' + call + ')',
        '~$config_string_launch(' + state + '[.FILEINCLUDEPATH = (eps)],' + call + ')', *common.public(state)]


def error(after, before, class_name, caller, three=True):
    call, obj = 'pconfigcall_' + before, 'n_receiver_' + before
    n = 'n_error_' + after
    frames = '[ENTRY (KINT 0) (DIRECT (PARRAY n_api_' + after + '))'
    if caller: frames += ',ENTRY (KINT 1) (DIRECT (PARRAY n_caller_' + after + '))'
    args = '[ENTRY (KINT 0) (DIRECT (POBJECT ' + obj + ')),ENTRY (KINT 1) (DIRECT pvalue_candidate_' + after + ')'
    captures = ['$named_slot_at(' + call + '.SENT,1) = NAMED_SENT (KNOWN pvalue_candidate_' + after + ')']
    if three:
        args += ',ENTRY (KINT 2) (DIRECT pvalue_flag_' + after + ')'
        captures += ['$named_slot_at(' + call + '.SENT,2) = NAMED_SENT (KNOWN pvalue_flag_' + after + ')']
    values = [*captures, *common.step(after,before), after + '.TODO = (THROW_SEARCH ' + n + ') :: ptask_' + before + '*',
        after + '.OBJECTS[' + n + '] = THROWABLE pthrowable_' + after,
        'pthrowable_' + after + '.KIND = "TypeError"', 'pthrowable_' + after + '.ORIGIN = (' + call + '.SITE)',
        '$string_bytes($throwable_field(' + after + ',' + n + ',"message")) = (' + text('define(): Argument #1 ($constant_name) must be of type string, ' + class_name + ' given') + ')',
        '$throwable_field(' + after + ',' + n + ',"previous") = PNULL',
        '$throwable_field(' + after + ',' + n + ',"line") = PINT ' + call + '.LINE',
        '$string_bytes($throwable_field(' + after + ',' + n + ',"file")) = ($call_sourcefile(' + after + '.FILES,' + call + '.SITE))',
        '$throwable_field(' + after + ',' + n + ',"trace") = PARRAY n_trace_' + after,
        after + '.ARRAYS[n_trace_' + after + '].ITEMS = ' + frames + ']',
        '$trace_array_field(' + after + ',n_api_' + after + ',' + text('function') + ') = PSTRING ' + text('define'),
        '$trace_array_field(' + after + ',n_api_' + after + ',' + text('line') + ') = PINT ' + call + '.LINE',
        '$trace_array_field(' + after + ',n_api_' + after + ',' + text('args') + ') = PARRAY n_args_' + after,
        after + '.ARRAYS[n_args_' + after + '].ITEMS = ' + args + ']',
        '$node_children(' + after + ',HARRAY n_args_' + after + ') = [HOBJECT ' + obj + ']',
        after + '.OBJECTS[' + obj + '] = ' + before + '.OBJECTS[' + obj + ']',
        '$objectprops_at(' + after + '.OBJECTPROPS,' + obj + ') = $objectprops_at(' + before + '.OBJECTPROPS,' + obj + ')',
        '~$dynamic_query_nonstring_object(' + after + ',' + n + ')',
        *unchanged(after,before,'STORE ENV USERCONSTANTS STRINGDATA EVENTS SELECTEDCALLS AUTOLOAD CLASSNAMES CLASSCONSTANTCACHE SOURCES POOLS FILES'),
        *common.public(after)]
    if caller:
        values += ['$trace_array_field(' + after + ',n_caller_' + after + ',' + text('function') + ') = PSTRING ' + text(caller)]
    return values


def refusals(state):
    call, obj = 'pconfigcall_' + state, 'n_receiver_' + state
    values = []
    for field in ('.SITE = PORIGIN 0 eps', '.LINE = $(' + call + '.LINE + 1)', '.INDEX = 0', '.SELECTION = (|' + state + '.SELECTEDCALLS|)'):
        values += ['~$dynamic_define_nonstring_valid(' + state + ',' + call + '[' + field + '])']
    for field in ('.OWNER = (0)', '.NAMED = true', '.KIND = INTRINSIC_CONSTANT', '.SENT = eps',
            '.SENT = ' + call + '.SENT[0:1]', '.SENT = ' + call + '.SENT ++ [NAMED_SENT (KNOWN PNULL),NAMED_SENT (KNOWN PNULL)]'):
        values += ['~$dynamic_define_nonstring_call(' + call + '[' + field + '])']
    for candidate in ('PARRAY 0','POBJECT ' + obj):
        values += ['$dynamic_define_nonstring_call(' + call + '[.SENT = $named_slot_set(' + call + '.SENT,1,KNOWN (' + candidate + '))])',
            '~$dynamic_define_nonstring_valid(' + state + ',' + call + '[.SENT = $named_slot_set(' + call + '.SENT,1,KNOWN (' + candidate + '))])']
    values += ['pconfigcall_dead_' + state + ' = ' + call + '[.SENT = $named_slot_set(' + call + '.SENT,0,KNOWN (POBJECT (|' + state + '.OBJECTS|)))]',
        '$dynamic_define_nonstring_call(pconfigcall_dead_' + state + ')',
        '~$dynamic_define_nonstring_valid(' + state + ',pconfigcall_dead_' + state + ')',
        '~$dynamic_query_nonstring_object(' + state + '[.OBJECTS[' + obj + '] = INSTANCE (PORIGIN 0 eps)],' + obj + ')']
    return values


def budget(state):
    return [state + '_pause = $drive_steps(' + state + ',0)', state + '_pause = ' + state + '[.COMPLETION = BUDGET]',
        state + '_one = $drive_steps(' + state + ',1)', state + '_one = $drive_steps(' + state + '_pause[.COMPLETION = NORMAL],1)']


def checks(program,path,name):
    values = ['S_initial = $php_run(' + program + ',0,' + json.dumps(b64(os.fsencode(path))) + ')', 'S_initial.COMPLETION = BUDGET']
    if name == 'ordinary-define-object-name-before-true-flag-warning':
        values += [*front('S','S_initial','PINT 1543',None),
            'S.OBJECTS[n_receiver_S] = INSTANCE porigin_class', 'S.USERCONSTANTS = eps',
            '~$config_strict(S,pconfigcall_S)', *error('S_error','S','PlainDefineName56',None,False),
            *front('S_true','S_error','PINT 1549','PBOOL true'), 'n_receiver_S_true = n_receiver_S',
            '~$config_strict(S_true,pconfigcall_S_true)', *error('S_true_error','S_true','PlainDefineName56',None),
            '$lookup(S_true_error.ENV,' + text('result') + ') = (n_result)', 'S_true_error.STORE[n_result] = DEFINED (PINT 99)',
            '~$dynamic_define_nonstring_valid(S,pconfigcall_S[.SENT = $named_slot_set(pconfigcall_S.SENT,1,KNOWN (PINT 1544))])',
            '~$dynamic_define_nonstring_valid(S_true,pconfigcall_S_true[.SENT = $named_slot_set(pconfigcall_S_true.SENT,2,KNOWN (PBOOL false))])',
            *refusals('S'), *refusals('S_true'), *budget('S')]
    else:
        strict = name == 'strict-stdclass-define-before-third-integer-type-error'
        assert strict or name == 'selected-nonstringable-define-before-null-flag-reception'
        candidate,flag = ('PINT 1571','PINT 17') if strict else ('pvalue_candidate','PNULL')
        values += [*front('S','S_initial',candidate,flag), 'pconfigcall_S.SELECTION = (n_selection)',
            'S.SELECTEDCALLS[n_selection].KIND = INTRINSIC_DEFINE',
            ('$config_strict(S,pconfigcall_S)' if strict else '~$config_strict(S,pconfigcall_S)'),
            '$lookup(S.ENV,' + text('result') + ') = (n_result)', 'S.STORE[n_result] = DEFINED (PINT 99)',
            '$lookup(S.ENV,' + text('effects') + ') = (n_effects)', 'S.STORE[n_effects] = DEFINED (PINT ' + ('1' if strict else '2') + ')',
            '$test_outputs(S.EVENTS) = ' + text('B|F|' if strict else 'B|V|F|'), 'S.USERCONSTANTS = eps']
        if strict:
            values += ['S.OBJECTS[n_receiver_S] = STDINSTANCE',
                '~$dynamic_define_nonstring_valid(S,pconfigcall_S[.SENT = $named_slot_set(pconfigcall_S.SENT,1,KNOWN (PINT 1573))])']
        else:
            values += ['S.OBJECTS[n_receiver_S] = INSTANCE porigin_class',
                'pvalue_candidate = PSTRING_CARRIER (REQUEST_STRING n_candidate) ' + text('captured-candidate56'),
                '$string_carrier_valid(S,pvalue_candidate)',
                '$lookup(S.ENV,' + text('value') + ') = (n_live_value)', 'S.STORE[n_live_value] = DEFINED (PINT 997)',
                '$lookup(S.ENV,' + text('flag') + ') = (n_flag)', 'S.STORE[n_flag] = DEFINED (PBOOL true)']
        for variable,expected in (('call','constant' if strict else 'defined'),('name','strict-live56' if strict else 'flag-live56')):
            values += ['$lookup(S.ENV,' + text(variable) + ') = (n_live_' + variable + ')',
                'S.STORE[n_live_' + variable + '] = DEFINED pvalue_live_' + variable,
                '$string_bytes(pvalue_live_' + variable + ') = (' + text(expected) + ')']
        values += [*error('S_error','S','stdClass' if strict else 'SelectedPlainDefine56','plainDefineStrictCaller56' if strict else 'plainDefineCaller56'),
            'S_error.STORE[n_result] = DEFINED (PINT 99)', *refusals('S'), *budget('S')]
        for slot in (1,2):
            bad='PSTRING_CARRIER (REQUEST_STRING (|S.STRINGDATA|)) ' + text('captured-candidate56' if slot==1 else '0')
            values += ['~$dynamic_query_arity_arguments(S,[NAMED_SENT (KNOWN (' + bad + '))])',
                '~$dynamic_define_nonstring_valid(S,pconfigcall_S[.SENT = $named_slot_set(pconfigcall_S.SENT,' + str(slot) + ',KNOWN (' + bad + '))])']
    return values


def main():
    fingerprint = sources.family.fingerprint
    sources.family.fingerprint = lambda: dict(fingerprint(), **{
        str(Path(__file__).relative_to(driver.ROOT)): sources.family.sha(__file__)})
    driver.sources,driver.PREFIX,driver.checks = sources,PREFIX,checks
    driver.main()


if __name__ == '__main__':
    main()
