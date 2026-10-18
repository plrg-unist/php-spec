#!/usr/bin/env python3
"""Actual name conversion precedes NULL deprecation and late registration."""
import json
import os
from pathlib import Path

import define_stringable_name_protocol as cast
import define_null_flag_protocol as reception
import define_stringable_null_flag_sources as sources

driver, common, text, b64 = cast.driver, cast.common, cast.text, cast.b64
PREFIX = cast.PREFIX + reception.PREFIX
DEPRECATED = 'define(): Passing null to parameter #3 ($case_insensitive) of type bool is deprecated'
DUPLICATE = 'Constant CAPTURENULL60 already defined, this will be an error in PHP 9'


def front(state, start):
    call, obj = 'pconfigcall_' + state, 'n_object_' + state
    return [*cast.reach(state, start, 0),
        state + '.TODO = (CONFIG_INVOKE ' + call + ') :: ptask_' + state + '*',
        call + '.SENT = [NAMED_SENT (KNOWN (POBJECT ' + obj + ')),NAMED_SENT (KNOWN pvalue_candidate_' + state + '),NAMED_SENT (KNOWN PNULL)]',
        call + '.KIND = INTRINSIC_DEFINE', call + '.INDEX = 3',
        call + '.OWNER = eps', call + '.PACKS = eps', '~' + call + '.NAMED',
        '$dynamic_define_string_valid(' + state + ',' + call + ')', '$config_invoke_valid(' + state + ',' + call + ')',
        '$config_string_source(' + state + ',' + call + ') = ((porigin_child_' + state + ',z_child_' + state + '))',
        '$config_string_object(' + call + ') = (' + obj + ')', *common.public(state)]


def deprecated(state, class_like=False):
    before, after, call = state + '_ready', state + '_deprecated', 'pconfigcall_converted_' + state
    marker = 'DYNAMIC_CLASS_DEFINE_NULL_RESULT' if class_like else 'DYNAMIC_NULL_DEFINE_FLAG_RESULT'
    valid = '$dynamic_class_define_null_valid' if class_like else '$dynamic_null_define_flag_valid'
    return [valid + '(' + before + ',' + call + ')', '~$config_strict(' + before + ',' + call + ')',
        '~$error_handler_eligible(' + before + ',8192)', *common.step(after, before),
        after + '.TODO = (' + marker + ' ' + call + ') :: ptask_' + state + '*',
        '$call_task_valid(' + after + ',' + marker + ' ' + call + ')',
        after + '.EVENTS = ' + before + '.EVENTS ++ [DIAGNOSTIC "Deprecated" $dynamic_null_define_flag_message() ' + call + '.LINE]',
        *cast.unchanged(after, before, 'STORE ENV USERCONSTANTS STRINGDATA ARRAYS OBJECTS SELECTEDCALLS'),
        *common.public(after)]


def error(state, before, converted, caller):
    after, call, obj = state + '_error', 'pconfigcall_' + ('converted_' if converted else '') + state, 'n_object_' + state
    frames = '[ENTRY (KINT 0) (DIRECT (PARRAY n_api_' + state + '))'
    if caller:
        frames += ',ENTRY (KINT 1) (DIRECT (PARRAY n_caller_' + state + '))'
    raw = 'pvalue_string_' + state if converted else 'POBJECT ' + obj
    message = 'define(): Argument #1 ($constant_name) cannot be a class constant' if converted else 'define(): Argument #1 ($constant_name) must be of type string, StrictNullFlagName60 given'
    values = [*common.step(after, before),
        after + '.TODO = (THROW_SEARCH n_error_' + state + ') :: ptask_' + state + '*',
        after + '.OBJECTS[n_error_' + state + '] = THROWABLE pthrowable_' + state,
        'pthrowable_' + state + '.KIND = ' + json.dumps('ValueError' if converted else 'TypeError'),
        'pthrowable_' + state + '.ORIGIN = (' + call + '.SITE)',
        '$throwable_live(' + after + ',n_error_' + state + ')',
        '$string_bytes($throwable_field(' + after + ',n_error_' + state + ',"message")) = (' + text(message) + ')',
        '$throwable_field(' + after + ',n_error_' + state + ',"previous") = PNULL',
        '$throwable_field(' + after + ',n_error_' + state + ',"line") = PINT ' + call + '.LINE',
        '$throwable_field(' + after + ',n_error_' + state + ',"trace") = PARRAY n_trace_' + state,
        after + '.ARRAYS[n_trace_' + state + '].ITEMS = ' + frames + ']',
        '$trace_array_field(' + after + ',n_api_' + state + ',' + text('function') + ') = PSTRING ' + text('define'),
        '$trace_array_field(' + after + ',n_api_' + state + ',' + text('args') + ') = PARRAY n_args_' + state,
        after + '.ARRAYS[n_args_' + state + '].ITEMS = [ENTRY (KINT 0) (DIRECT (' + raw + ')),ENTRY (KINT 1) (DIRECT pvalue_candidate_' + state + '),ENTRY (KINT 2) (DIRECT PNULL)]',
        '$node_children(' + after + ',HARRAY n_args_' + state + ') = ' + ('eps' if converted else '[HOBJECT ' + obj + ']'),
        after + '.OBJECTS[' + obj + '] = ' + before + '.OBJECTS[' + obj + ']',
        '$objectprops_at(' + after + '.OBJECTPROPS,' + obj + ') = $objectprops_at(' + before + '.OBJECTPROPS,' + obj + ')',
        *cast.unchanged(after, before, 'STORE ENV USERCONSTANTS STRINGDATA EVENTS SELECTEDCALLS AUTOLOAD CLASSNAMES CLASSCONSTANTCACHE'),
        *common.public(after)]
    if caller:
        values += ['$trace_array_field(' + after + ',n_caller_' + state + ',' + text('function') + ') = PSTRING ' + text(caller)]
    return values


def dispatch(state, before, marker, level, message, event):
    error_call = 'perrorcall_' + state
    return [*common.step(state, before), state + '.TODO = (ERROR_HANDLER_INVOKE ' + error_call + ') :: ptask_S*',
        error_call + '.RESUME = ' + marker, error_call + '.SITE = pconfigcall_S.SITE',
        error_call + '.LINE = pconfigcall_S.LINE', error_call + '.LEVEL = ' + str(level),
        error_call + '.MESSAGE = ' + message,
        error_call + '.EVENT = DIAGNOSTIC ' + json.dumps(event) + ' ' + message + ' pconfigcall_S.LINE',
        '$error_call_valid(' + state + ',' + error_call + ')',
        *cast.unchanged(state, before, 'STORE ENV USERCONSTANTS STRINGDATA ARRAYS OBJECTS EVENTS SELECTEDCALLS'), *common.public(state)]


def captured():
    args = '[pvalue_string_S,pvalue_candidate_S,PNULL]'
    values = ['pconfigcall_S.SELECTION = (n_selection)', 'S.SELECTEDCALLS[n_selection].KIND = INTRINSIC_DEFINE',
        'pvalue_candidate_S = PSTRING_CARRIER (REQUEST_STRING n_candidate) ' + text('captured-candidate60'),
        '$string_carrier_valid(S,pvalue_candidate_S)', 'S.USERCONSTANTS = eps',
        '$test_outputs(S.EVENTS) = ' + text('B|V|F|'),
        '$lookup(S.ENV,' + text('flag') + ') = (n_flag)', 'S.STORE[n_flag] = DEFINED (PBOOL true)',
        '$lookup(S.ENV,' + text('effects') + ') = (n_effects)', 'S.STORE[n_effects] = DEFINED (PINT 2)',
        '$lookup(S.ENV,' + text('result') + ') = (n_result)', 'S.STORE[n_result] = DEFINED (PINT 99)',
        '$lookup(S.ENV,' + text('warnings') + ') = (n_warnings)', 'S.STORE[n_warnings] = DEFINED (PINT 0)',
        *cast.weak('S', 'CAPTURENULL60'),
        'pvalue_string_S = PSTRING_CARRIER (REQUEST_STRING n_name) ' + text('CAPTURENULL60'),
        '$dynamic_null_define_flag_valid(S_ready,pconfigcall_converted_S)',
        'S_ready.STORE[n_flag] = DEFINED (PBOOL true)', 'S_ready.STORE[n_effects] = DEFINED (PINT 2)',
        *dispatch('S_dispatch', 'S_ready', 'DYNAMIC_NULL_DEFINE_FLAG_RESULT pconfigcall_converted_S',8192,'$dynamic_null_define_flag_message()','Deprecated'),
        *reception.handler('S_handler', 'S_dispatch', 3, 'pvalue_candidate_S', 'pconfigcall_converted_S', args),
        'perrorcall_S_handler.RESUME = DYNAMIC_NULL_DEFINE_FLAG_RESULT pconfigcall_converted_S',
        'perrorcall_S_handler.LEVEL = 8192', 'perrorcall_S_handler.MESSAGE = ' + text(DEPRECATED),
        *reception.reach('S_resume', 'S_handler', 1, 'pvalue_candidate_S'),
        'S_resume.TODO = (DYNAMIC_NULL_DEFINE_FLAG_RESULT pconfigcall_converted_S) :: ptask_S*',
        'S_resume.RESULT = KNOWN PNULL', 'S_resume.USERCONSTANTS = [puserconstant_inner]',
        'puserconstant_inner.NAME = ' + text('CAPTURENULL60'), 'puserconstant_inner.VALUE = PINT 1823',
        'puserconstant_inner.ORIGIN =/= pconfigcall_S.SITE', 'puserconstant_inner.CLASS = PVSCALAR',
        'S_resume.STORE[n_warnings] = DEFINED (PINT 1)', 'S_resume.STORE[n_result] = DEFINED (PINT 99)',
        'S_resume.STORE[n_flag] = DEFINED (PBOOL true)',
        '$test_outputs(S_resume.EVENTS) = ' + text('B|V|F|S|W|8192|' + DEPRECATED + '|'),
        '$dynamic_null_define_flag_duplicate_valid(S_resume,pconfigcall_converted_S,1)',
        '~$dynamic_null_define_flag_duplicate_valid(S_resume,pconfigcall_converted_S,0)',
        *dispatch('S_duplicate_dispatch', 'S_resume', 'DYNAMIC_NULL_DEFINE_FLAG_DUPLICATE pconfigcall_converted_S 1',2,'$global_constant_duplicate_message(' + text('CAPTURENULL60') + ')','Warning'),
        *reception.handler('S_duplicate_handler','S_duplicate_dispatch',4,'pvalue_candidate_S','pconfigcall_converted_S',args),
        'perrorcall_S_duplicate_handler.RESUME = DYNAMIC_NULL_DEFINE_FLAG_DUPLICATE pconfigcall_converted_S 1',
        'perrorcall_S_duplicate_handler.LEVEL = 2', 'perrorcall_S_duplicate_handler.MESSAGE = ' + text(DUPLICATE),
        *reception.reach('S_duplicate_resume','S_duplicate_handler',2,'pvalue_candidate_S'),
        'S_duplicate_resume.TODO = (DYNAMIC_NULL_DEFINE_FLAG_DUPLICATE pconfigcall_converted_S 1) :: ptask_S*',
        'S_duplicate_resume.USERCONSTANTS = [puserconstant_inner]',
        'S_duplicate_resume.STORE[n_warnings] = DEFINED (PINT 2)',
        'S_duplicate_resume.STORE[n_flag] = DEFINED (PBOOL true)',
        'S_duplicate_resume.EVENTS[$nabs($(|S_duplicate_resume.EVENTS| - 1))] = DIAGNOSTIC "Warning" ' + text(DUPLICATE) + ' pconfigcall_S.LINE',
        *common.step('S_done', 'S_duplicate_resume', 'PBOOL false'),
        'S_done.TODO = ptask_S*', 'S_done.USERCONSTANTS = [puserconstant_inner]',
        *cast.refusals('S'), *cast.budget('S'), *cast.budget('S_returned'), *cast.budget('S_resume')]
    for slot, label, payload in [(0,'name','CAPTURENULL60'),(1,'candidate','captured-candidate60')]:
        values += ['pvalue_invalid_' + label + ' = PSTRING_CARRIER (REQUEST_STRING (|S_ready.STRINGDATA|)) ' + text(payload),
            '~$dynamic_null_define_flag_valid(S_ready,pconfigcall_converted_S[.SENT = $named_slot_set(pconfigcall_converted_S.SENT,' + str(slot) + ',KNOWN pvalue_invalid_' + label + ')])']
    for variable, expected in [('call','defined'),('name','handler-live60')]:
        values += ['$lookup(S_resume.ENV,' + text(variable) + ') = (n_live_' + variable + ')',
            'S_resume.STORE[n_live_' + variable + '] = DEFINED pvalue_live_' + variable,
            '$string_bytes(pvalue_live_' + variable + ') = (' + text(expected) + ')']
    values += ['$lookup(S_resume.ENV,' + text('value') + ') = (n_live_value)', 'S_resume.STORE[n_live_value] = DEFINED (PINT 991)',
        'S_final = $drive_steps(S_done,3000)', 'S_final.COMPLETION = NORMAL',
        'S_final.TODO = eps', 'S_final.CURRENT = eps', 'S_final.FRAMES = eps',
        'S_final.USERCONSTANTS = [puserconstant_inner]', 'S_final.ERRORHANDLER.CALLBACK = eps',
        '$test_outputs(S_final.EVENTS) = ' + text('B|V|F|S|W|8192|' + DEPRECATED + '|W|2|' + DUPLICATE + '|F|1823|1|2|2|defined|handler-live60|991|T|Z'),
        *common.public('S_final')]
    return values


def checks(program, path, name):
    values = ['S_initial = $php_run(' + program + ',0,' + json.dumps(b64(os.fsencode(path))) + ')',
        'S_initial.COMPLETION = BUDGET', *front('S','S_initial')]
    if name == 'stringable-null-flag-fresh-duplicate-and-class-priority':
        values += ['pvalue_candidate_S = PINT 1807', 'S.USERCONSTANTS = eps',
            *cast.weak('S','STRINGNULL60'), *deprecated('S'),
            *common.step('S_published','S_deprecated','PBOOL true'), 'S_published.TODO = ptask_S*',
            'S_published.USERCONSTANTS = [puserconstant_first]',
            'puserconstant_first = {NAME ' + text('STRINGNULL60') + ',ORIGIN pconfigcall_S.SITE,VALUE (PINT 1807),CLASS PVSCALAR,READS eps,RECEIVES eps}',
            *cast.unchanged('S_published','S_deprecated','STORE ENV ARRAYS OBJECTS OBJECTPROPS STRINGDATA EVENTS'),
            *front('S_duplicate','S_published'), 'n_object_S_duplicate = n_object_S',
            'pvalue_candidate_S_duplicate = PINT 1811', *cast.weak('S_duplicate','STRINGNULL60'), *deprecated('S_duplicate'),
            *common.step('S_duplicate_reported','S_duplicate_deprecated'),
            'S_duplicate_reported.TODO = (DYNAMIC_NULL_DEFINE_FLAG_DUPLICATE pconfigcall_converted_S_duplicate 1) :: ptask_S_duplicate*',
            'S_duplicate_reported.EVENTS = S_duplicate_deprecated.EVENTS ++ [DIAGNOSTIC "Warning" $global_constant_duplicate_message(' + text('STRINGNULL60') + ') pconfigcall_S_duplicate.LINE]',
            '$dynamic_null_define_flag_duplicate_valid(S_duplicate_reported,pconfigcall_converted_S_duplicate,1)',
            *common.step('S_duplicate_done','S_duplicate_reported','PBOOL false'),
            'S_duplicate_done.TODO = ptask_S_duplicate*', 'S_duplicate_done.USERCONSTANTS = [puserconstant_first]',
            *front('S_class','S_duplicate_done'), 'n_object_S_class = n_object_S', 'pvalue_candidate_S_class = PINT 1817',
            '$lookup(S_class.ENV,' + text('result') + ') = (n_result)', 'S_class.STORE[n_result] = DEFINED (PINT 99)',
            *cast.weak('S_class','A::NULL60'),
            '~$dynamic_null_define_flag_valid(S_class_ready,pconfigcall_converted_S_class)',
            *deprecated('S_class',True), *error('S_class','S_class_deprecated',True,None),
            'S_class_error.STORE[n_result] = DEFINED (PINT 99)', 'S_class_error.USERCONSTANTS = [puserconstant_first]',
            '$lookup(S_class_error.ENV,' + text('calls') + ') = (n_calls)', 'S_class_error.STORE[n_calls] = DEFINED (PINT 3)',
            '$test_outputs(S_class_error.EVENTS) = ' + text('B|S|T|1807|S|F|1807|S|'),
            'pconfigcall_false = pconfigcall_S[.SENT = $named_slot_set(pconfigcall_S.SENT,2,KNOWN (PBOOL false))]',
            '$dynamic_define_string_call(pconfigcall_false)', '~$dynamic_define_string_valid(S,pconfigcall_false)',
            '~$dynamic_define_string_valid(S,pconfigcall_S[.SENT = $named_slot_set(pconfigcall_S.SENT,1,KNOWN (PINT 1808))])',
            *cast.refusals('S'), *cast.budget('S'), *cast.budget('S_class_returned')]
    elif name == 'selected-stringable-null-flag-handler-installs-duplicate-after-conversion':
        values += captured()
    else:
        assert name == 'strict-stringable-null-flag-rejects-name-after-argument-effects'
        values += ['$config_strict(S,pconfigcall_S)', '~$config_string_launch(S,pconfigcall_S)',
            '~$config_string_site_valid(S,pconfigcall_S,n_object_S,porigin_child_S,z_child_S,pconfigcall_S.LINE)',
            'pvalue_candidate_S = PINT 1847', '$test_outputs(S.EVENTS) = ' + text('B|F|'),
            '$lookup(S.ENV,' + text('effects') + ') = (n_effects)', 'S.STORE[n_effects] = DEFINED (PINT 1)',
            '$lookup(S.ENV,' + text('calls') + ') = (n_calls)', 'S.STORE[n_calls] = DEFINED (PINT 0)',
            '$lookup(S.ENV,' + text('result') + ') = (n_result)', 'S.STORE[n_result] = DEFINED (PINT 99)',
            *error('S','S',False,'strictNullCaller60'), 'S_error.STORE[n_result] = DEFINED (PINT 99)',
            *cast.refusals('S'), *cast.budget('S')]
    values += ['~$dynamic_define_string_call(pconfigcall_S[.SENT = pconfigcall_S.SENT ++ [NAMED_SENT (KNOWN PNULL)]])',
        '$dynamic_define_string_call(pconfigcall_S[.SENT = $named_slot_set(pconfigcall_S.SENT,2,KNOWN (PINT 0))])']
    return values


def main():
    fingerprint = sources.family.fingerprint
    sources.family.fingerprint = lambda: dict(fingerprint(), **{
        str(Path(__file__).relative_to(driver.ROOT)): sources.family.sha(__file__),
        str(Path(cast.__file__).relative_to(driver.ROOT)): sources.family.sha(cast.__file__),
        str(Path(reception.__file__).relative_to(driver.ROOT)): sources.family.sha(reception.__file__)})
    driver.sources, driver.PREFIX, driver.checks = sources, PREFIX, checks
    driver.main()


if __name__ == '__main__':
    main()
