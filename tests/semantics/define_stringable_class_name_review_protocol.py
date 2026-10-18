#!/usr/bin/env python3
"""An actual malformed returned name reaches ValueError with converted API slots."""
import json
import os
from pathlib import Path

import define_stringable_name_protocol as cast
import define_stringable_class_name_review_sources as sources

driver, common, text, b64 = cast.driver, cast.common, cast.text, cast.b64
PREFIX = cast.PREFIX


def checks(program, path, name):
    assert name == 'selected-stringable-malformed-class-name-preserves-converted-captures'
    values = ['S_initial = $php_run(' + program + ',0,' + json.dumps(b64(os.fsencode(path))) + ')',
        'S_initial.COMPLETION = BUDGET', *cast.front('S', 'S_initial', True),
        'pconfigcall_S.INDEX = 3', '$intrinsic_count(S,pconfigcall_S.SITE) = (3)',
        'pconfigcall_S.SELECTION = (n_selection)', 'S.SELECTEDCALLS[n_selection].KIND = INTRINSIC_DEFINE',
        'pvalue_candidate_S = PSTRING_CARRIER (REQUEST_STRING n_candidate) ' + text('captured-value57'),
        '$string_carrier_valid(S,pvalue_candidate_S)',
        '$lookup(S.ENV,' + text('keep') + ') = (n_keep)', 'S.STORE[n_keep] = DEFINED (POBJECT n_object_S)',
        '$lookup(S.ENV,' + text('result') + ') = (n_result)', 'S.STORE[n_result] = DEFINED (PINT 99)',
        '$lookup(S.ENV,' + text('calls') + ') = (n_calls)', 'S.STORE[n_calls] = DEFINED (PINT 0)',
        '$lookup(S.ENV,' + text('effects') + ') = (n_effects)', 'S.STORE[n_effects] = DEFINED (PINT 1)',
        '$lookup(S.ENV,' + text('flag') + ') = (n_flag)', 'S.STORE[n_flag] = DEFINED (PBOOL false)',
        '$lookup(S.ENV,' + text('value') + ') = (n_value)', 'S.STORE[n_value] = DEFINED pvalue_candidate_S',
        '$lookup(S.ENV,' + text('name') + ') = (n_name)', 'S.STORE[n_name] = DEFINED pvalue_before_name',
        '$string_bytes(pvalue_before_name) = (' + text('argument-name57') + ')',
        '$lookup(S.ENV,' + text('call') + ') = (n_call)', 'S.STORE[n_call] = DEFINED pvalue_before_call',
        '$string_bytes(pvalue_before_call) = (' + text('defined') + ')',
        'S.USERCONSTANTS = eps', '$test_outputs(S.EVENTS) = ' + text('B|V|'),
        *cast.weak('S', 'A:::B'),
        'pvalue_string_S = PSTRING_CARRIER (REQUEST_STRING n_converted) ' + text('A:::B'),
        '~$dynamic_constant_global_name(' + text('A:::B') + ')',
        '$dynamic_constant_class_name(' + text('A:::B') + ')',
        '$dynamic_class_define_call(pconfigcall_converted_S)',
        '$dynamic_class_define_valid(S_ready,pconfigcall_converted_S)',
        '$named_slot_at(pconfigcall_converted_S.SENT,1) = NAMED_SENT (KNOWN pvalue_candidate_S)',
        '$named_slot_at(pconfigcall_converted_S.SENT,2) = NAMED_SENT (KNOWN (PBOOL false))',
        'S_ready.STORE[n_keep] = DEFINED (POBJECT n_object_S)',
        'S_ready.STORE[n_result] = DEFINED (PINT 99)',
        'S_ready.STORE[n_calls] = DEFINED (PINT 1)', 'S_ready.STORE[n_effects] = DEFINED (PINT 1)',
        'S_ready.STORE[n_flag] = DEFINED (PBOOL true)',
        'S_ready.STORE[n_call] = DEFINED pvalue_after_call',
        '$string_bytes(pvalue_after_call) = (' + text('constant') + ')',
        'S_ready.STORE[n_name] = DEFINED pvalue_after_name',
        '$string_bytes(pvalue_after_name) = (' + text('cast-name57') + ')',
        'S_ready.STORE[n_value] = DEFINED pvalue_after_value',
        '$string_bytes(pvalue_after_value) = (' + text('cast-value57') + ')',
        'S_ready.USERCONSTANTS = [puserconstant_sibling]',
        'puserconstant_sibling.NAME = ' + text('SOURCE57PEER'), 'puserconstant_sibling.VALUE = PINT 1657',
        '$source_constant_lookup(S_ready,' + text('SOURCE57PEER') + ') = (VALUE (PINT 1657))',
        '$test_outputs(S_ready.EVENTS) = ' + text('B|V|S|'), *common.step('S_error', 'S_ready'),
        'S_error.TODO = (THROW_SEARCH n_error) :: ptask_S*',
        'S_error.OBJECTS[n_error] = THROWABLE pthrowable', 'pthrowable.KIND = "ValueError"',
        'pthrowable.ORIGIN = (pconfigcall_S.SITE)',
        '$string_bytes($throwable_field(S_error,n_error,"message")) = (' + text('define(): Argument #1 ($constant_name) cannot be a class constant') + ')',
        '$throwable_field(S_error,n_error,"previous") = PNULL',
        '$throwable_field(S_error,n_error,"line") = PINT pconfigcall_S.LINE',
        '$string_bytes($throwable_field(S_error,n_error,"file")) = ($call_sourcefile(S_error.FILES,pconfigcall_S.SITE))',
        '$throwable_field(S_error,n_error,"trace") = PARRAY n_trace',
        'S_error.ARRAYS[n_trace].ITEMS = [ENTRY (KINT 0) (DIRECT (PARRAY n_api)),ENTRY (KINT 1) (DIRECT (PARRAY n_caller))]',
        '$trace_array_field(S_error,n_api,' + text('function') + ') = PSTRING ' + text('define'),
        '$trace_array_field(S_error,n_api,' + text('line') + ') = PINT pconfigcall_S.LINE',
        '$trace_array_field(S_error,n_api,' + text('args') + ') = PARRAY n_args',
        'S_error.ARRAYS[n_args].ITEMS = [ENTRY (KINT 0) (DIRECT pvalue_string_S),ENTRY (KINT 1) (DIRECT pvalue_candidate_S),ENTRY (KINT 2) (DIRECT (PBOOL false))]',
        '$node_children(S_error,HARRAY n_args) = eps',
        '$trace_array_field(S_error,n_caller,' + text('function') + ') = PSTRING ' + text('defineStringClassReviewCaller57'),
        'S_error.OBJECTS[n_object_S] = S_ready.OBJECTS[n_object_S]',
        '$objectprops_at(S_error.OBJECTPROPS,n_object_S) = $objectprops_at(S_ready.OBJECTPROPS,n_object_S)',
        'S_error.STORE[n_result] = DEFINED (PINT 99)',
        *cast.unchanged('S_error', 'S_ready', 'STORE ENV USERCONSTANTS STRINGDATA EVENTS SELECTEDCALLS AUTOLOAD CLASSNAMES CLASSCONSTANTCACHE SOURCES POOLS FILES REFCELLS ERRORHANDLER CLASSES'),
        *common.public('S_error'), *cast.refusals('S'),
        'pvalue_bad_candidate = PSTRING_CARRIER (REQUEST_STRING (|S.STRINGDATA|)) ' + text('captured-value57'),
        '~$dynamic_define_string_valid(S,pconfigcall_S[.SENT = $named_slot_set(pconfigcall_S.SENT,1,KNOWN pvalue_bad_candidate)])',
        *cast.budget('S'), *cast.budget('S_returned'), *cast.budget('S_ready')]
    for i, value in enumerate((
            'PSTRING (' + text('A::B') + ' ++ [0])',
            'PSTRING ' + text('__COMPILER_HALT_OFFSET__'),
            'PSTRING_CARRIER (REQUEST_STRING (|S_returned.STRINGDATA|)) ' + text('A:::B'))):
        state = 'S_refused_' + str(i)
        values += [state + ' = $dynamic_define_string_finish(S_returned,pconfigcall_S,' + value + ')',
            state + '.COMPLETION = UNSUPPORTED "Stringable define global name"']
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
