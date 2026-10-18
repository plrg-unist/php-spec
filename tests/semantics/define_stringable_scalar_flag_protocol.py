#!/usr/bin/env python3
"""Actual Stringable name conversion precedes captured quiet flag reception."""
import json
import os
from pathlib import Path

import define_stringable_name_protocol as cast
import define_scalar_flag_protocol as reception
import define_stringable_scalar_flag_sources as sources

driver, common, text, b64 = cast.driver, cast.common, cast.text, cast.b64
PREFIX = cast.PREFIX + reception.PREFIX
CASE = 'define(): Argument #3 ($case_insensitive) is ignored since declaration of case-insensitive constants is no longer supported'
DUPLICATE = 'Constant CAPTUREQUIET61 already defined, this will be an error in PHP 9'


def front(state, start):
    call, obj = 'pconfigcall_' + state, 'n_object_' + state
    return [*cast.reach(state, start, 0),
        state + '.TODO = (CONFIG_INVOKE ' + call + ') :: ptask_' + state + '*',
        call + '.SENT = [NAMED_SENT (KNOWN (POBJECT ' + obj + ')),NAMED_SENT (KNOWN pvalue_candidate_' + state + '),NAMED_SENT (KNOWN pvalue_flag_' + state + ')]',
        call + '.KIND = INTRINSIC_DEFINE', call + '.INDEX = 3',
        call + '.OWNER = eps', call + '.PACKS = eps', '~' + call + '.NAMED',
        '$dynamic_define_string_valid(' + state + ',' + call + ')', '$config_invoke_valid(' + state + ',' + call + ')',
        '$dynamic_define_quiet_flag(pvalue_flag_' + state + ')', '~$config_string_kind(INTRINSIC_DEFINE)',
        '$config_string_source(' + state + ',' + call + ') = ((porigin_child_' + state + ',z_child_' + state + '))',
        '$config_string_object(' + call + ') = (' + obj + ')', *common.public(state)]


def duplicate(state):
    ready, warning, done = [state + suffix for suffix in ('_ready', '_warning', '_done')]
    call = 'pconfigcall_converted_' + state
    return ['$dynamic_scalar_define_flag_valid(' + ready + ',' + call + ')',
        '~$dynamic_scalar_define_flag_case_valid(' + ready + ',' + call + ')',
        '$dynamic_scalar_define_flag_duplicate_valid(' + ready + ',' + call + ',1)',
        '~$error_handler_eligible(' + ready + ',2)', *common.step(warning, ready),
        warning + '.TODO = (DYNAMIC_SCALAR_DEFINE_FLAG_DUPLICATE ' + call + ' 1) :: ptask_' + state + '*',
        warning + '.EVENTS = ' + ready + '.EVENTS ++ [DIAGNOSTIC "Warning" $global_constant_duplicate_message(' + text('STRINGQUIET61') + ') ' + call + '.LINE]',
        *cast.unchanged(warning, ready, 'STORE ENV USERCONSTANTS STRINGDATA ARRAYS OBJECTS SELECTEDCALLS'),
        '$call_task_valid(' + warning + ',DYNAMIC_SCALAR_DEFINE_FLAG_DUPLICATE ' + call + ' 1)',
        *common.public(warning), *common.step(done, warning, 'PBOOL false'),
        done + '.TODO = ptask_' + state + '*', done + '.USERCONSTANTS = [puserconstant_first]']


def error(state, before, converted, caller):
    after, call, obj = state + '_error', 'pconfigcall_' + ('converted_' if converted else '') + state, 'n_object_' + state
    frames = '[ENTRY (KINT 0) (DIRECT (PARRAY n_api_' + state + '))'
    if caller:
        frames += ',ENTRY (KINT 1) (DIRECT (PARRAY n_caller_' + state + '))'
    raw = 'pvalue_string_' + state if converted else 'POBJECT ' + obj
    message = 'define(): Argument #1 ($constant_name) cannot be a class constant' if converted else 'define(): Argument #1 ($constant_name) must be of type string, StrictScalarFlagName61 given'
    values = [*common.step(after, before),
        after + '.TODO = (THROW_SEARCH n_error_' + state + ') :: ptask_' + state + '*',
        after + '.OBJECTS[n_error_' + state + '] = THROWABLE pthrowable_' + state,
        'pthrowable_' + state + '.KIND = ' + json.dumps('ValueError' if converted else 'TypeError'),
        'pthrowable_' + state + '.ORIGIN = (' + call + '.SITE)', '$throwable_live(' + after + ',n_error_' + state + ')',
        '$string_bytes($throwable_field(' + after + ',n_error_' + state + ',"message")) = (' + text(message) + ')',
        '$throwable_field(' + after + ',n_error_' + state + ',"previous") = PNULL',
        '$throwable_field(' + after + ',n_error_' + state + ',"line") = PINT ' + call + '.LINE',
        '$throwable_field(' + after + ',n_error_' + state + ',"trace") = PARRAY n_trace_' + state,
        after + '.ARRAYS[n_trace_' + state + '].ITEMS = ' + frames + ']',
        '$trace_array_field(' + after + ',n_api_' + state + ',' + text('function') + ') = PSTRING ' + text('define'),
        '$trace_array_field(' + after + ',n_api_' + state + ',' + text('args') + ') = PARRAY n_args_' + state,
        after + '.ARRAYS[n_args_' + state + '].ITEMS = [ENTRY (KINT 0) (DIRECT (' + raw + ')),ENTRY (KINT 1) (DIRECT pvalue_candidate_' + state + '),ENTRY (KINT 2) (DIRECT pvalue_flag_' + state + ')]',
        '$node_children(' + after + ',HARRAY n_args_' + state + ') = ' + ('eps' if converted else '[HOBJECT ' + obj + ']'),
        after + '.OBJECTS[' + obj + '] = ' + before + '.OBJECTS[' + obj + ']',
        '$objectprops_at(' + after + '.OBJECTPROPS,' + obj + ') = $objectprops_at(' + before + '.OBJECTPROPS,' + obj + ')',
        *cast.unchanged(after, before, 'STORE ENV USERCONSTANTS STRINGDATA EVENTS SELECTEDCALLS AUTOLOAD CLASSNAMES CLASSCONSTANTCACHE'),
        *common.public(after)]
    if caller:
        values += ['$trace_array_field(' + after + ',n_caller_' + state + ',' + text('function') + ') = PSTRING ' + text(caller)]
    return values


def captured():
    call, args = 'pconfigcall_converted_S', '[pvalue_string_S,pvalue_candidate_S,pvalue_flag_S]'
    values = ['pconfigcall_S.SELECTION = (n_selection)', 'S.SELECTEDCALLS[n_selection].KIND = INTRINSIC_DEFINE',
        'pvalue_candidate_S = PSTRING_CARRIER (REQUEST_STRING n_candidate) ' + text('captured-candidate61'),
        'pvalue_flag_S = PSTRING_CARRIER (REQUEST_STRING n_flag_string) ' + text('false'),
        '$string_carrier_valid(S,pvalue_candidate_S)', '$string_carrier_valid(S,pvalue_flag_S)',
        '$truth(S,pvalue_flag_S)', 'S.USERCONSTANTS = eps', '$test_outputs(S.EVENTS) = ' + text('B|V|F|'),
        '$lookup(S.ENV,' + text('flag') + ') = (n_flag)', 'S.STORE[n_flag] = DEFINED pvalue_live_flag',
        '$string_bytes(pvalue_live_flag) = (' + text('0') + ')', '~$truth(S,pvalue_live_flag)',
        '$lookup(S.ENV,' + text('effects') + ') = (n_effects)', 'S.STORE[n_effects] = DEFINED (PINT 2)',
        '$lookup(S.ENV,' + text('result') + ') = (n_result)', 'S.STORE[n_result] = DEFINED (PINT 99)',
        '$lookup(S.ENV,' + text('warnings') + ') = (n_warnings)', 'S.STORE[n_warnings] = DEFINED (PINT 0)',
        *cast.weak('S', 'CAPTUREQUIET61'),
        'pvalue_string_S = PSTRING_CARRIER (REQUEST_STRING n_name) ' + text('CAPTUREQUIET61'),
        'S_ready.USERCONSTANTS = eps', '$dynamic_scalar_define_flag_case_valid(S_ready,' + call + ')',
        *reception.warning('S_warning', 'S_ready', call, 'DYNAMIC_SCALAR_DEFINE_FLAG_RESULT ' + call, '$dynamic_constant_case_message()'),
        *reception.handler('S_handler', 'S_warning', 3, 'CAPTUREQUIET61', call, args),
        'perrorcall_S_handler.RESUME = DYNAMIC_SCALAR_DEFINE_FLAG_RESULT ' + call,
        *reception.reach('S_resume', 'S_handler', 1, 'CAPTUREQUIET61'),
        'S_resume.TODO = (DYNAMIC_SCALAR_DEFINE_FLAG_RESULT ' + call + ') :: ptask_S*',
        'S_resume.USERCONSTANTS = [puserconstant_inner]',
        'puserconstant_inner.NAME = ' + text('CAPTUREQUIET61'), 'puserconstant_inner.VALUE = PINT 1931',
        'puserconstant_inner.ORIGIN =/= pconfigcall_S.SITE', 'puserconstant_inner.CLASS = PVSCALAR',
        'S_resume.STORE[n_warnings] = DEFINED (PINT 1)', 'S_resume.STORE[n_result] = DEFINED (PINT 99)',
        '$test_outputs(S_resume.EVENTS) = ' + text('B|V|F|S|W|2|' + CASE + '|'),
        '$call_task_valid(S_resume,DYNAMIC_SCALAR_DEFINE_FLAG_RESULT ' + call + ')',
        '$dynamic_scalar_define_flag_duplicate_valid(S_resume,' + call + ',1)',
        '~$dynamic_scalar_define_flag_duplicate_valid(S_resume,' + call + ',0)',
        '~$dynamic_scalar_define_flag_duplicate_valid(S_resume,' + call + ',2)',
        *reception.warning('S_duplicate_warning', 'S_resume', call, 'DYNAMIC_SCALAR_DEFINE_FLAG_DUPLICATE ' + call + ' 1', '$global_constant_duplicate_message(' + text('CAPTUREQUIET61') + ')'),
        *reception.handler('S_duplicate_handler', 'S_duplicate_warning', 4, 'CAPTUREQUIET61', call, args),
        'perrorcall_S_duplicate_handler.RESUME = DYNAMIC_SCALAR_DEFINE_FLAG_DUPLICATE ' + call + ' 1',
        *reception.reach('S_duplicate_resume', 'S_duplicate_handler', 2, 'CAPTUREQUIET61'),
        'S_duplicate_resume.TODO = (DYNAMIC_SCALAR_DEFINE_FLAG_DUPLICATE ' + call + ' 1) :: ptask_S*',
        'S_duplicate_resume.USERCONSTANTS = [puserconstant_inner]', 'S_duplicate_resume.STORE[n_warnings] = DEFINED (PINT 2)',
        'S_duplicate_resume.EVENTS[$nabs($(|S_duplicate_resume.EVENTS| - 1))] = DIAGNOSTIC "Warning" ' + text(DUPLICATE) + ' pconfigcall_S.LINE',
        *common.step('S_done', 'S_duplicate_resume', 'PBOOL false'),
        'S_done.TODO = ptask_S*', 'S_done.USERCONSTANTS = [puserconstant_inner]']
    for variable, expected in [('call', 'defined'), ('name', 'handler-live61'), ('flag', '0')]:
        values += ['$lookup(S_resume.ENV,' + text(variable) + ') = (n_live_' + variable + ')',
            'S_resume.STORE[n_live_' + variable + '] = DEFINED pvalue_live_' + variable + '_resume',
            '$string_bytes(pvalue_live_' + variable + '_resume) = (' + text(expected) + ')']
    values += ['$lookup(S_resume.ENV,' + text('value') + ') = (n_live_value)', 'S_resume.STORE[n_live_value] = DEFINED (PINT 991)']
    for slot, label, payload in [(0, 'name', 'CAPTUREQUIET61'), (1, 'candidate', 'captured-candidate61'), (2, 'flag', 'false')]:
        values += ['pvalue_invalid_' + label + ' = PSTRING_CARRIER (REQUEST_STRING (|S_ready.STRINGDATA|)) ' + text(payload),
            '~$dynamic_scalar_define_flag_valid(S_ready,' + call + '[.SENT = $named_slot_set(' + call + '.SENT,' + str(slot) + ',KNOWN pvalue_invalid_' + label + ')])']
    values += ['pconfigcall_legacy = pconfigcall_S[.SENT = $named_slot_set(pconfigcall_S.SENT,2,KNOWN (PSTRING ' + text('false') + '))]',
        '$dynamic_define_string_call(pconfigcall_legacy)', '~$dynamic_define_string_valid(S,pconfigcall_legacy)',
        *cast.refusals('S'), *cast.budget('S'), *cast.budget('S_returned'), *cast.budget('S_resume'),
        'S_final = $drive_steps(S_done,3000)', 'S_final.COMPLETION = NORMAL',
        'S_final.TODO = eps', 'S_final.CURRENT = eps', 'S_final.FRAMES = eps',
        'S_final.USERCONSTANTS = [puserconstant_inner]', 'S_final.ERRORHANDLER.CALLBACK = eps',
        '$test_outputs(S_final.EVENTS) = ' + text('B|V|F|S|W|2|' + CASE + '|W|2|' + DUPLICATE + '|F|1931|1|2|2|defined|handler-live61|991|S0|Z'),
        *common.public('S_final')]
    return values


def checks(program, path, name):
    values = ['S_initial = $php_run(' + program + ',0,' + json.dumps(b64(os.fsencode(path))) + ')',
        'S_initial.COMPLETION = BUDGET', *front('S', 'S_initial')]
    if name == 'stringable-quiet-flags-fresh-duplicates-and-infinite-class-priority':
        values += ['pvalue_candidate_S = PINT 1907', 'pvalue_flag_S = PINT 0', 'S.USERCONSTANTS = eps',
            *cast.weak('S', 'STRINGQUIET61'), '$dynamic_scalar_define_flag_valid(S_ready,pconfigcall_converted_S)',
            '~$dynamic_scalar_define_flag_case_valid(S_ready,pconfigcall_converted_S)',
            *common.step('S_published', 'S_ready', 'PBOOL true'), 'S_published.TODO = ptask_S*',
            'S_published.USERCONSTANTS = [puserconstant_first]',
            'puserconstant_first = {NAME ' + text('STRINGQUIET61') + ',ORIGIN pconfigcall_S.SITE,VALUE (PINT 1907),CLASS PVSCALAR,READS eps,RECEIVES eps}',
            *cast.unchanged('S_published', 'S_ready', 'STORE ENV ARRAYS OBJECTS OBJECTPROPS STRINGDATA EVENTS'),
            *front('S_minus', 'S_published'), 'n_object_S_minus = n_object_S',
            'pvalue_candidate_S_minus = PINT 1913', 'pvalue_flag_S_minus = PFLOAT 9223372036854775808',
            '~$truth(S_minus,pvalue_flag_S_minus)', *cast.weak('S_minus', 'STRINGQUIET61'), *duplicate('S_minus'),
            *front('S_zero', 'S_minus_done'), 'n_object_S_zero = n_object_S',
            'pvalue_candidate_S_zero = PINT 1919', 'pvalue_flag_S_zero = PSTRING_CARRIER INTERNED_STRING ' + text('0'),
            '~$truth(S_zero,pvalue_flag_S_zero)', *cast.weak('S_zero', 'STRINGQUIET61'), *duplicate('S_zero'),
            *front('S_class', 'S_zero_done'), 'n_object_S_class = n_object_S',
            'pvalue_candidate_S_class = PINT 1921', 'pvalue_flag_S_class = PFLOAT 9218868437227405312',
            '$truth(S_class,pvalue_flag_S_class)',
            '$lookup(S_class.ENV,' + text('result') + ') = (n_result)', 'S_class.STORE[n_result] = DEFINED (PINT 99)',
            *cast.weak('S_class', 'A::QUIET61'),
            '$dynamic_class_define_scalar_valid(S_class_ready,pconfigcall_converted_S_class)',
            '~$dynamic_scalar_define_flag_valid(S_class_ready,pconfigcall_converted_S_class)',
            *error('S_class', 'S_class_ready', True, None), 'S_class_error.STORE[n_result] = DEFINED (PINT 99)',
            'S_class_error.USERCONSTANTS = [puserconstant_first]',
            '$lookup(S_class_error.ENV,' + text('calls') + ') = (n_calls)', 'S_class_error.STORE[n_calls] = DEFINED (PINT 4)',
            '$test_outputs(S_class_error.EVENTS) = ' + text('B|S|T|1907|S|F|1907|S|F|1907|S|'),
            '$dynamic_define_string_call(pconfigcall_S[.SENT = $named_slot_set(pconfigcall_S.SENT,2,KNOWN (PINT 1))])',
            '~$dynamic_define_string_valid(S,pconfigcall_S[.SENT = $named_slot_set(pconfigcall_S.SENT,2,KNOWN (PINT 1))])',
            '~$dynamic_define_string_valid(S,pconfigcall_S[.SENT = $named_slot_set(pconfigcall_S.SENT,1,KNOWN (PINT 1908))])',
            *cast.refusals('S'), *cast.budget('S'), *cast.budget('S_class_returned')]
        for flag in ('PNULL', 'PBOOL false', 'PBOOL true', 'PFLOAT 9221120237041090560', 'PARRAY 0', 'POBJECT 0'):
            values += ['~$dynamic_define_quiet_flag(' + flag + ')']
        for flag in ('PFLOAT 9221120237041090560', 'PARRAY 0', 'POBJECT 0'):
            values += ['~$dynamic_define_string_call(pconfigcall_S[.SENT = $named_slot_set(pconfigcall_S.SENT,2,KNOWN (' + flag + '))])']
    elif name == 'selected-stringable-truthy-request-flag-before-live-zero-and-duplicate':
        values += captured()
    else:
        assert name == 'strict-stringable-quiet-flag-rejects-name-before-nonbool-flag'
        values += ['$config_strict(S,pconfigcall_S)', '~$config_string_launch(S,pconfigcall_S)',
            '~$config_string_site_valid(S,pconfigcall_S,n_object_S,porigin_child_S,z_child_S,pconfigcall_S.LINE)',
            'pvalue_candidate_S = PINT 1961', 'pvalue_flag_S = PINT 1', '$test_outputs(S.EVENTS) = ' + text('B|F|'),
            '$lookup(S.ENV,' + text('effects') + ') = (n_effects)', 'S.STORE[n_effects] = DEFINED (PINT 1)',
            '$lookup(S.ENV,' + text('calls') + ') = (n_calls)', 'S.STORE[n_calls] = DEFINED (PINT 0)',
            '$lookup(S.ENV,' + text('result') + ') = (n_result)', 'S.STORE[n_result] = DEFINED (PINT 99)',
            '$lookup(S.ENV,' + text('flag') + ') = (n_flag)', 'S.STORE[n_flag] = DEFINED (PINT 0)',
            *error('S', 'S', False, 'strictScalarCaller61'), 'S_error.STORE[n_result] = DEFINED (PINT 99)',
            *cast.refusals('S'), *cast.budget('S')]
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
