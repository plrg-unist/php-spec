#!/usr/bin/env python3
"""Returned Stringable class names reach the existing raw ValueError path."""
import json
import os
from pathlib import Path

import global_constant_scalar_name_protocol as driver
import define_stringable_name_protocol as cast
import define_stringable_class_name_sources as sources

common, text, b64 = driver.common, driver.text, driver.b64
PREFIX = cast.PREFIX


def error(state, caller, three):
    before, after = state + '_ready', state + '_error'
    call, obj = 'pconfigcall_converted_' + state, 'n_object_' + state
    thrown = 'n_error_' + state
    frames = '[ENTRY (KINT 0) (DIRECT (PARRAY n_api_' + state + '))'
    if caller:
        frames += ',ENTRY (KINT 1) (DIRECT (PARRAY n_caller_' + state + '))'
    arguments = '[ENTRY (KINT 0) (DIRECT pvalue_string_' + state + '),ENTRY (KINT 1) (DIRECT pvalue_candidate_' + state + ')'
    if three:
        arguments += ',ENTRY (KINT 2) (DIRECT (PBOOL false))'
    values = ['$dynamic_class_define_call(' + call + ')',
        '$dynamic_class_define_valid(' + before + ',' + call + ')',
        *common.step(after,before),
        after + '.TODO = (THROW_SEARCH ' + thrown + ') :: ptask_' + state + '*',
        after + '.OBJECTS[' + thrown + '] = THROWABLE pthrowable_' + state,
        'pthrowable_' + state + '.KIND = "ValueError"',
        'pthrowable_' + state + '.ORIGIN = (' + call + '.SITE)',
        '$throwable_live(' + after + ',' + thrown + ')',
        '$string_bytes($throwable_field(' + after + ',' + thrown + ',"message")) = (' + text('define(): Argument #1 ($constant_name) cannot be a class constant') + ')',
        '$throwable_field(' + after + ',' + thrown + ',"previous") = PNULL',
        '$throwable_field(' + after + ',' + thrown + ',"line") = PINT ' + call + '.LINE',
        '$string_bytes($throwable_field(' + after + ',' + thrown + ',"file")) = ($call_sourcefile(' + before + '.FILES,' + call + '.SITE))',
        '$throwable_field(' + after + ',' + thrown + ',"trace") = PARRAY n_trace_' + state,
        after + '.ARRAYS[n_trace_' + state + '].ITEMS = ' + frames + ']',
        '$trace_array_field(' + after + ',n_api_' + state + ',' + text('function') + ') = PSTRING ' + text('define'),
        '$trace_array_field(' + after + ',n_api_' + state + ',' + text('line') + ') = PINT ' + call + '.LINE',
        '$trace_array_field(' + after + ',n_api_' + state + ',' + text('args') + ') = PARRAY n_args_' + state,
        after + '.ARRAYS[n_args_' + state + '].ITEMS = ' + arguments + ']',
        '$node_children(' + after + ',HARRAY n_args_' + state + ') = eps',
        after + '.OBJECTS[' + obj + '] = ' + before + '.OBJECTS[' + obj + ']',
        '$objectprops_at(' + after + '.OBJECTPROPS,' + obj + ') = $objectprops_at(' + before + '.OBJECTPROPS,' + obj + ')',
        *cast.unchanged(after,before,'STORE ENV USERCONSTANTS STRINGDATA EVENTS SELECTEDCALLS AUTOLOAD CLASSNAMES CLASSES CLASSCONSTANTCACHE SOURCES POOLS FILES STATICS REFCELLS'),
        *common.public(after)]
    if caller:
        values += ['$trace_array_field(' + after + ',n_caller_' + state + ',' + text('function') + ') = PSTRING ' + text(caller)]
    return values


def result_controls(state, name):
    returned, ready = state + '_returned', state + '_ready'
    call, converted = 'pconfigcall_' + state, 'pconfigcall_converted_' + state
    values = []
    for index,value in enumerate(('PSTRING (' + text('A::B') + ' ++ [0])',
            'PSTRING ' + text('__COMPILER_HALT_OFFSET__'),
            'PSTRING_CARRIER (REQUEST_STRING (|' + returned + '.STRINGDATA|)) ' + text(name))):
        refused = state + '_refused_' + str(index)
        values += [refused + ' = $dynamic_define_string_finish(' + returned + ',' + call + ',' + value + ')',
            refused + '.COMPLETION = UNSUPPORTED "Stringable define global name"']
    bad_name = 'PSTRING_CARRIER (REQUEST_STRING (|' + ready + '.STRINGDATA|)) ' + text(name)
    values += ['pconfigcall_bad_name_' + state + ' = ' + converted + '[.SENT = $named_slot_set(' + converted + '.SENT,0,KNOWN (' + bad_name + '))]',
        '$dynamic_class_define_call(pconfigcall_bad_name_' + state + ')',
        '~$dynamic_class_define_valid(' + ready + ',pconfigcall_bad_name_' + state + ')']
    for field in ('.SITE = PORIGIN 0 eps', '.LINE = $(' + converted + '.LINE + 1)', '.INDEX = 0'):
        values += ['~$dynamic_class_define_valid(' + ready + ',' + converted + '[' + field + '])']
    return values


def checks(program,path,name):
    values = ['S_initial = $php_run(' + program + ',0,' + json.dumps(b64(os.fsencode(path))) + ')',
        'S_initial.COMPLETION = BUDGET']
    selected = name == 'selected-stringable-class-name-keeps-earlier-candidate-and-false'
    recovery = name == 'bare-class-name-error-recovers-with-global-stringable-definition'
    assert selected or recovery or name == 'stringable-class-define-name-errors-after-conversion'
    result_name = 'Captured57::VALUE' if selected else '::' if recovery else 'Missing57::VALUE'
    values += [*cast.front('S','S_initial',selected or recovery), 'S.USERCONSTANTS = eps',
        '$lookup(S.ENV,' + text('result') + ') = (n_result)', 'S.STORE[n_result] = DEFINED (PINT 99)']
    if selected:
        values += ['pconfigcall_S.SELECTION = (n_selection)', 'S.SELECTEDCALLS[n_selection].KIND = INTRINSIC_DEFINE',
            'pvalue_candidate_S = PSTRING_CARRIER (REQUEST_STRING n_candidate) ' + text('captured-candidate57'),
            '$string_carrier_valid(S,pvalue_candidate_S)', '$test_outputs(S.EVENTS) = ' + text('B|V|'),
            '$lookup(S.ENV,' + text('effects') + ') = (n_effects)', 'S.STORE[n_effects] = DEFINED (PINT 1)']
    else:
        values += ['pconfigcall_S.SELECTION = eps', 'pvalue_candidate_S = PINT ' + ('1621' if recovery else '1601')]
    values += [*cast.weak('S',result_name), 'S_ready.USERCONSTANTS = eps',
        '$lookup(S_ready.ENV,' + text('calls') + ') = (n_calls)', 'S_ready.STORE[n_calls] = DEFINED (PINT 1)',
        *error('S','stringClassCaller57' if selected else None,selected or recovery),
        'S_error.STORE[n_result] = DEFINED (PINT 99)',
        *cast.refusals('S'), *result_controls('S',result_name), *cast.budget('S'), *cast.budget('S_returned')]
    if selected:
        values += ['pvalue_string_S = PSTRING_CARRIER (REQUEST_STRING n_name) ' + text(result_name),
            'S_ready.STORE[n_effects] = DEFINED (PINT 1)',
            '$lookup(S_ready.ENV,' + text('flag') + ') = (n_flag)', 'S_ready.STORE[n_flag] = DEFINED (PBOOL true)',
            '$lookup(S_ready.ENV,' + text('value') + ') = (n_value)', 'S_ready.STORE[n_value] = DEFINED (PINT 997)',
            '~$dynamic_define_string_valid(S,pconfigcall_S[.SENT = $named_slot_set(pconfigcall_S.SENT,1,KNOWN (PSTRING_CARRIER (REQUEST_STRING (|S.STRINGDATA|)) ' + text('captured-candidate57') + '))])',
            '~$dynamic_class_define_valid(S_ready,pconfigcall_converted_S[.SENT = $named_slot_set(pconfigcall_converted_S.SENT,1,KNOWN (PSTRING_CARRIER (REQUEST_STRING (|S_ready.STRINGDATA|)) ' + text('captured-candidate57') + '))])']
        for variable,expected in (('call','constant'),('name','cast-live57')):
            values += ['$lookup(S_ready.ENV,' + text(variable) + ') = (n_live_' + variable + ')',
                'S_ready.STORE[n_live_' + variable + '] = DEFINED pvalue_live_' + variable,
                '$string_bytes(pvalue_live_' + variable + ') = (' + text(expected) + ')']
    else:
        candidate = '1623' if recovery else '1603'
        values += ['~$dynamic_class_define_valid(S_ready,pconfigcall_converted_S[.SENT = $named_slot_set(pconfigcall_converted_S.SENT,1,KNOWN (PINT ' + candidate + '))])']
    if recovery:
        values += [*cast.front('S_global','S_error',False), 'n_object_S_global = n_object_S',
            'pvalue_candidate_S_global = PINT 1637', *cast.weak('S_global','STRINGCLASSRECOVERY57'),
            '$source_constant_lookup(S_global_ready,' + text('STRINGCLASSRECOVERY57') + ') = eps',
            *common.step('S_published','S_global_ready','PBOOL true'),
            'S_published.USERCONSTANTS = [{NAME ' + text('STRINGCLASSRECOVERY57') + ',ORIGIN pconfigcall_S_global.SITE,VALUE (PINT 1637),CLASS PVSCALAR,READS eps,RECEIVES eps}]',
            *cast.unchanged('S_published','S_global_ready','STORE ENV ARRAYS OBJECTS OBJECTPROPS STRINGDATA EVENTS'),
            '$source_constant_lookup(S_published,' + text('STRINGCLASSRECOVERY57') + ') = (VALUE (PINT 1637))',
            '$lookup(S_published.ENV,' + text('calls') + ') = (n_calls_global)', 'S_published.STORE[n_calls_global] = DEFINED (PINT 2)',
            'S_published.STORE[n_result] = DEFINED (PINT 99)', *common.public('S_published'), *cast.budget('S_global_ready')]
    return values


def main():
    fingerprint = sources.family.fingerprint
    sources.family.fingerprint = lambda: dict(fingerprint(), **{
        str(Path(__file__).relative_to(driver.ROOT)): sources.family.sha(__file__),
        str(Path(cast.__file__).relative_to(driver.ROOT)): sources.family.sha(cast.__file__)})
    driver.sources, driver.PREFIX, driver.checks = sources, PREFIX, checks
    driver.main()


if __name__ == '__main__':
    main()
