#!/usr/bin/env python3
"""Stringable true-flag reception preserves warning and exception phase order."""
import json
import os
from pathlib import Path

import define_stringable_name_protocol as cast
import define_stringable_name_review_protocol as throwing
import define_stringable_true_flag_sources as sources

driver, common, text, b64 = cast.driver, cast.common, cast.text, cast.b64
PREFIX = cast.PREFIX + throwing.PREFIX


def front(state, start):
    call, obj = 'pconfigcall_' + state, 'n_object_' + state
    return [*cast.reach(state, start, 0),
        state + '.TODO = (CONFIG_INVOKE ' + call + ') :: ptask_' + state + '*',
        call + '.SENT = [NAMED_SENT (KNOWN (POBJECT ' + obj + ')),NAMED_SENT (KNOWN pvalue_candidate_' + state + '),NAMED_SENT (KNOWN (PBOOL true))]',
        call + '.KIND = INTRINSIC_DEFINE', call + '.INDEX = 3',
        call + '.OWNER = eps', call + '.PACKS = eps', '~' + call + '.NAMED',
        '$dynamic_define_string_valid(' + state + ',' + call + ')', '$config_invoke_valid(' + state + ',' + call + ')',
        '~$config_string_kind(INTRINSIC_DEFINE)',
        '$config_string_source(' + state + ',' + call + ') = ((porigin_child_' + state + ',z_child_' + state + '))',
        '$config_string_object(' + call + ') = (' + obj + ')', *common.public(state)]


def default_warning(state):
    before, after = state + '_ready', state + '_warning'
    call = 'pconfigcall_converted_' + state
    return ['$dynamic_constant_case_valid(' + before + ',' + call + ')',
        '~$error_handler_eligible(' + before + ',2)', *common.step(after, before),
        after + '.TODO = (DYNAMIC_CONSTANT_CASE_WARNING ' + call + ') :: ptask_' + state + '*',
        after + '.EVENTS = ' + before + '.EVENTS ++ [DIAGNOSTIC "Warning" $dynamic_constant_case_message() ' + call + '.LINE]',
        *cast.unchanged(after, before, 'STORE ENV ARRAYS OBJECTS OBJECTPROPS USERCONSTANTS STRINGDATA SELECTEDCALLS'),
        *common.public(after)]


def error(state, kind, message, caller, converted):
    before, after = (state + '_ready' if converted else state), state + '_error'
    call = 'pconfigcall_' + ('converted_' if converted else '') + state
    obj, thrown = 'n_object_' + state, 'n_error_' + state
    frames = '[ENTRY (KINT 0) (DIRECT (PARRAY n_api_' + state + '))'
    if caller:
        frames += ',ENTRY (KINT 1) (DIRECT (PARRAY n_caller_' + state + '))'
    name_value = 'pvalue_string_' + state if converted else 'POBJECT ' + obj
    values = [*common.step(after, before),
        after + '.TODO = (THROW_SEARCH ' + thrown + ') :: ptask_' + state + '*',
        after + '.OBJECTS[' + thrown + '] = THROWABLE pthrowable_' + state,
        'pthrowable_' + state + '.KIND = "' + kind + '"',
        'pthrowable_' + state + '.ORIGIN = (' + call + '.SITE)',
        '$throwable_live(' + after + ',' + thrown + ')',
        '$string_bytes($throwable_field(' + after + ',' + thrown + ',"message")) = (' + text(message) + ')',
        '$throwable_field(' + after + ',' + thrown + ',"previous") = PNULL',
        '$throwable_field(' + after + ',' + thrown + ',"line") = PINT ' + call + '.LINE',
        '$throwable_field(' + after + ',' + thrown + ',"trace") = PARRAY n_trace_' + state,
        after + '.ARRAYS[n_trace_' + state + '].ITEMS = ' + frames + ']',
        '$trace_array_field(' + after + ',n_api_' + state + ',' + text('function') + ') = PSTRING ' + text('define'),
        '$trace_array_field(' + after + ',n_api_' + state + ',' + text('args') + ') = PARRAY n_args_' + state,
        after + '.ARRAYS[n_args_' + state + '].ITEMS = [ENTRY (KINT 0) (DIRECT (' + name_value + ')),ENTRY (KINT 1) (DIRECT pvalue_candidate_' + state + '),ENTRY (KINT 2) (DIRECT (PBOOL true))]',
        '$node_children(' + after + ',HARRAY n_args_' + state + ') = ' + ('eps' if converted else '[HOBJECT ' + obj + ']'),
        after + '.OBJECTS[' + obj + '] = ' + before + '.OBJECTS[' + obj + ']',
        '$objectprops_at(' + after + '.OBJECTPROPS,' + obj + ') = $objectprops_at(' + before + '.OBJECTPROPS,' + obj + ')',
        *cast.unchanged(after, before, 'STORE ENV USERCONSTANTS STRINGDATA EVENTS SELECTEDCALLS AUTOLOAD CLASSNAMES CLASSCONSTANTCACHE'),
        *common.public(after)]
    if caller:
        values += ['$trace_array_field(' + after + ',n_caller_' + state + ',' + text('function') + ') = PSTRING ' + text(caller)]
    return values


def method_throw():
    values = ['pconfigcall_S.SELECTION = (n_selection)', 'S.SELECTEDCALLS[n_selection].KIND = INTRINSIC_DEFINE',
        'pvalue_candidate_S = PSTRING_CARRIER (REQUEST_STRING n_candidate) ' + text('captured-candidate59'),
        '$string_carrier_valid(S,pvalue_candidate_S)', '~$config_strict(S,pconfigcall_S)',
        '$config_string_site_valid(S,pconfigcall_S,n_object_S,porigin_child_S,z_child_S,pconfigcall_S.LINE)',
        '$config_string_launch(S,pconfigcall_S)',
        '$lookup(S.ENV,' + text('keep') + ') = (n_keep)', 'S.STORE[n_keep] = DEFINED (POBJECT n_object_S)',
        '$lookup(S.ENV,' + text('result') + ') = (n_result)', 'S.STORE[n_result] = DEFINED (PINT 99)',
        '$lookup(S.ENV,' + text('calls') + ') = (n_calls)', 'S.STORE[n_calls] = DEFINED (PINT 0)',
        '$lookup(S.ENV,' + text('effects') + ') = (n_effects)', 'S.STORE[n_effects] = DEFINED (PINT 2)',
        '$lookup(S.ENV,' + text('warnings') + ') = (n_warnings)', 'S.STORE[n_warnings] = DEFINED (PINT 0)',
        '$lookup(S.ENV,' + text('saved') + ') = (n_saved)', 'S.STORE[n_saved] = DEFINED PNULL',
        '$lookup(S.ENV,' + text('flag') + ') = (n_flag)', 'S.STORE[n_flag] = DEFINED (PBOOL false)',
        'S.USERCONSTANTS = eps', '$test_outputs(S.EVENTS) = ' + text('B|V|F|'),
        *common.step('S_launch', 'S'),
        'S_launch.TODO = (CALL_ARGS (METHOD_TARGET n_object_S porigin_method) eps 0 eps (porigin_child_S) pconfigcall_S.LINE) :: (STRINGIFY_RESULT n_object_S porigin_child_S pconfigcall_S.LINE) :: (CONFIG_STRING_RESULT pconfigcall_S n_object_S porigin_child_S z_child_S pconfigcall_S.LINE) :: ptask_S*',
        *throwing.reach('S_throw', 'S_launch', 1),
        'S_throw.TODO = (THROW_VALUE porigin_throw z_throw) :: ptask_body*',
        'S_throw.CURRENT = (pcallcontext_method)',
        '$context_target(pcallcontext_method) = METHOD_TARGET n_object_S porigin_method',
        'S_throw.FRAMES = pframe_call :: pframe_outer*',
        'pframe_call.CONTEXT = S.CURRENT', 'pframe_call.LOCALS = ($active_table(S))',
        'pframe_call.TODO = (STRINGIFY_RESULT n_object_S porigin_child_S pconfigcall_S.LINE) :: (CONFIG_STRING_RESULT pconfigcall_S n_object_S porigin_child_S z_child_S pconfigcall_S.LINE) :: ptask_S*',
        '$config_string_trace_context(S_throw,pcallcontext_method)',
        '$config_string_site_valid(S_throw,pconfigcall_S,n_object_S,porigin_child_S,z_child_S,pconfigcall_S.LINE)',
        'S_throw.STORE[n_saved] = DEFINED (POBJECT n_exception)',
        'S_throw.OBJECTS[n_exception] = THROWABLE pthrowable', 'pthrowable.KIND = "Exception"',
        '$string_bytes($throwable_field(S_throw,n_exception,"message")) = (' + text('cast59-stop') + ')',
        '$throwable_field(S_throw,n_exception,"previous") = PNULL',
        '$throwable_field(S_throw,n_exception,"trace") = PARRAY n_trace',
        'S_throw.ARRAYS[n_trace].ITEMS = [ENTRY (KINT 0) (DIRECT (PARRAY n_method)),ENTRY (KINT 1) (DIRECT (PARRAY n_api)),ENTRY (KINT 2) (DIRECT (PARRAY n_caller))]',
        '$trace_array_field(S_throw,n_method,' + text('function') + ') = PSTRING ' + text('__toString'),
        '$trace_array_field(S_throw,n_method,' + text('class') + ') = PSTRING ' + text('CancelTrueFlagName59'),
        '$trace_array_field(S_throw,n_method,' + text('type') + ') = PSTRING ' + text('->'),
        '$trace_array_field(S_throw,n_api,' + text('function') + ') = PSTRING ' + text('define'),
        '$trace_array_field(S_throw,n_api,' + text('args') + ') = PARRAY n_args',
        'S_throw.ARRAYS[n_args].ITEMS = [ENTRY (KINT 0) (DIRECT (POBJECT n_object_S)),ENTRY (KINT 1) (DIRECT pvalue_candidate_S),ENTRY (KINT 2) (DIRECT (PBOOL true))]',
        '$node_children(S_throw,HARRAY n_args) = [HOBJECT n_object_S]',
        '$trace_array_field(S_throw,n_caller,' + text('function') + ') = PSTRING ' + text('cancelTrueCaller59'),
        'S_throw.STORE[n_result] = DEFINED (PINT 99)', 'S_throw.STORE[n_calls] = DEFINED (PINT 1)',
        'S_throw.STORE[n_effects] = DEFINED (PINT 2)', 'S_throw.STORE[n_warnings] = DEFINED (PINT 0)',
        'S_throw.STORE[n_keep] = DEFINED (POBJECT n_object_S)', 'S_throw.STORE[n_flag] = DEFINED (PBOOL false)',
        'S_throw.USERCONSTANTS = [puserconstant_sibling]',
        'puserconstant_sibling.NAME = ' + text('SOURCE59CAST'), 'puserconstant_sibling.VALUE = PINT 1789',
        'puserconstant_sibling.CLASS = PVSCALAR',
        '$source_constant_lookup(S_throw,' + text('STRINGTRUECANCEL59') + ') = eps',
        '$test_outputs(S_throw.EVENTS) = ' + text('B|V|F|S|'), *common.public('S_throw'),
        *common.step('S_throwing', 'S_throw'),
        'S_throwing.TODO = (THROW_SEARCH n_exception) :: ptask_body*',
        *throwing.reach('S_unwind', 'S_throwing', 2),
        'S_unwind.TODO = (THROW_SEARCH n_exception) :: (STRINGIFY_RESULT n_object_S porigin_child_S pconfigcall_S.LINE) :: (CONFIG_STRING_RESULT pconfigcall_S n_object_S porigin_child_S z_child_S pconfigcall_S.LINE) :: ptask_S*',
        'S_unwind.CURRENT = S.CURRENT', 'S_unwind.ENV = S.ENV',
        'S_unwind.OBJECTS[n_exception] = THROWABLE pthrowable',
        'S_unwind.STORE[n_saved] = DEFINED (POBJECT n_exception)',
        'S_unwind.STORE[n_result] = DEFINED (PINT 99)', 'S_unwind.USERCONSTANTS = [puserconstant_sibling]',
        *common.public('S_unwind'), *common.step('S_discard_string', 'S_unwind'),
        'S_discard_string = S_unwind[.TODO = (THROW_SEARCH n_exception) :: (CONFIG_STRING_RESULT pconfigcall_S n_object_S porigin_child_S z_child_S pconfigcall_S.LINE) :: ptask_S*]',
        *common.step('S_discard_define', 'S_discard_string'),
        'S_discard_define = S_discard_string[.TODO = (THROW_SEARCH n_exception) :: ptask_S*]',
        '$source_constant_lookup(S_discard_define,' + text('STRINGTRUECANCEL59') + ') = eps',
        'S_discard_define.USERCONSTANTS = [puserconstant_sibling]',
        'S_discard_define.STORE[n_result] = DEFINED (PINT 99)', *common.public('S_discard_define'),
        *cast.refusals('S'), *cast.budget('S'), *cast.budget('S_unwind'),
        'pvalue_bad_candidate = PSTRING_CARRIER (REQUEST_STRING (|S.STRINGDATA|)) ' + text('captured-candidate59'),
        '~$dynamic_define_string_valid(S,pconfigcall_S[.SENT = $named_slot_set(pconfigcall_S.SENT,1,KNOWN pvalue_bad_candidate)])']
    for variable, expected in [('call', 'constant'), ('name', 'STRINGTRUECANCEL59')]:
        values += ['$lookup(S_throw.ENV,' + text(variable) + ') = (n_live_' + variable + ')',
            'S_throw.STORE[n_live_' + variable + '] = DEFINED pvalue_live_' + variable,
            '$string_bytes(pvalue_live_' + variable + ') = (' + text(expected) + ')']
    values += ['$lookup(S_throw.ENV,' + text('value') + ') = (n_live_value)',
        'S_throw.STORE[n_live_value] = DEFINED (PINT 997)',
        'S_final = $drive_steps(S_discard_define,3000)', 'S_final.COMPLETION = NORMAL',
        'S_final.TODO = eps', 'S_final.CURRENT = eps', 'S_final.FRAMES = eps',
        'S_final.USERCONSTANTS = [puserconstant_sibling]', 'S_final.ERRORHANDLER.CALLBACK = eps',
        '$test_outputs(S_final.EVENTS) = ' + text('B|V|F|S|I|99|1|2|0|constant|STRINGTRUECANCEL59|997|F|A|1789|Z'),
        *common.public('S_final')]
    return values


def checks(program, path, name):
    values = ['S_initial = $php_run(' + program + ',0,' + json.dumps(b64(os.fsencode(path))) + ')',
        'S_initial.COMPLETION = BUDGET', *front('S', 'S_initial')]
    if name == 'stringable-true-flag-fresh-duplicate-and-class-priority':
        values += ['pvalue_candidate_S = PINT 1733', 'S.USERCONSTANTS = eps',
            *cast.weak('S', 'STRINGTRUE59'), *default_warning('S'),
            *common.step('S_published', 'S_warning', 'PBOOL true'),
            'S_published.TODO = ptask_S*',
            'S_published.USERCONSTANTS = [puserconstant_first]',
            'puserconstant_first = {NAME ' + text('STRINGTRUE59') + ',ORIGIN pconfigcall_S.SITE,VALUE (PINT 1733),CLASS PVSCALAR,READS eps,RECEIVES eps}',
            *cast.unchanged('S_published', 'S_warning', 'STORE ENV ARRAYS OBJECTS OBJECTPROPS STRINGDATA EVENTS'),
            *common.public('S_published'),
            *front('S_duplicate', 'S_published'), 'n_object_S_duplicate = n_object_S',
            'pvalue_candidate_S_duplicate = PINT 1747', *cast.weak('S_duplicate', 'STRINGTRUE59'),
            *default_warning('S_duplicate'),
            '$dynamic_constant_duplicate_valid(S_duplicate_warning,pconfigcall_converted_S_duplicate,1)',
            *common.step('S_duplicate_reported', 'S_duplicate_warning'),
            'S_duplicate_reported.TODO = (DYNAMIC_CONSTANT_DUPLICATE pconfigcall_converted_S_duplicate 1) :: ptask_S_duplicate*',
            'S_duplicate_reported.EVENTS = S_duplicate_warning.EVENTS ++ [DIAGNOSTIC "Warning" $global_constant_duplicate_message(' + text('STRINGTRUE59') + ') pconfigcall_S_duplicate.LINE]',
            'S_duplicate_reported.USERCONSTANTS = [puserconstant_first]',
            *common.step('S_duplicate_done', 'S_duplicate_reported', 'PBOOL false'),
            'S_duplicate_done.TODO = ptask_S_duplicate*', 'S_duplicate_done.USERCONSTANTS = [puserconstant_first]',
            '$source_constant_lookup(S_duplicate_done,' + text('STRINGTRUE59') + ') = (VALUE (PINT 1733))',
            *front('S_class', 'S_duplicate_done'), 'n_object_S_class = n_object_S',
            'pvalue_candidate_S_class = PINT 1769',
            '$lookup(S_class.ENV,' + text('result') + ') = (n_result)', 'S_class.STORE[n_result] = DEFINED (PINT 99)',
            *cast.weak('S_class', 'A::B59'),
            '$dynamic_class_define_call(pconfigcall_converted_S_class)',
            '$dynamic_class_define_valid(S_class_ready,pconfigcall_converted_S_class)',
            '~$dynamic_constant_case_valid(S_class_ready,pconfigcall_converted_S_class)',
            '$lookup(S_class_ready.ENV,' + text('calls') + ') = (n_calls)', 'S_class_ready.STORE[n_calls] = DEFINED (PINT 3)',
            '$test_outputs(S_class_ready.EVENTS) = ' + text('B|S|T|1733|S|F|1733S|'),
            *error('S_class', 'ValueError', 'define(): Argument #1 ($constant_name) cannot be a class constant', None, True),
            'S_class_error.STORE[n_result] = DEFINED (PINT 99)',
            'S_class_error.USERCONSTANTS = [puserconstant_first]',
            'pconfigcall_false = pconfigcall_S[.SENT = $named_slot_set(pconfigcall_S.SENT,2,KNOWN (PBOOL false))]',
            '$dynamic_define_string_call(pconfigcall_false)', '~$dynamic_define_string_valid(S,pconfigcall_false)',
            '~$dynamic_define_string_valid(S,pconfigcall_S[.SENT = $named_slot_set(pconfigcall_S.SENT,1,KNOWN (PINT 1734))])',
            *cast.refusals('S'), *cast.budget('S'), *cast.budget('S_class_returned')]
    elif name == 'stringable-throw-cancels-before-captured-true-flag-warning':
        values += method_throw()
    else:
        assert name == 'strict-stringable-true-flag-rejects-name-after-argument-effects'
        values += ['$config_strict(S,pconfigcall_S)', '~$config_string_launch(S,pconfigcall_S)',
            '~$config_string_site_valid(S,pconfigcall_S,n_object_S,porigin_child_S,z_child_S,pconfigcall_S.LINE)',
            'pvalue_candidate_S = PINT 1801', '$test_outputs(S.EVENTS) = ' + text('B|F|'),
            '$lookup(S.ENV,' + text('effects') + ') = (n_effects)', 'S.STORE[n_effects] = DEFINED (PINT 1)',
            '$lookup(S.ENV,' + text('calls') + ') = (n_calls)', 'S.STORE[n_calls] = DEFINED (PINT 0)',
            '$lookup(S.ENV,' + text('flag') + ') = (n_flag)', 'S.STORE[n_flag] = DEFINED (PBOOL false)',
            '$lookup(S.ENV,' + text('result') + ') = (n_result)', 'S.STORE[n_result] = DEFINED (PINT 99)',
            *error('S', 'TypeError', 'define(): Argument #1 ($constant_name) must be of type string, StrictTrueFlagName59 given', 'strictTrueCaller59', False),
            'S_error.STORE[n_result] = DEFINED (PINT 99)', 'S_error.STORE[n_calls] = DEFINED (PINT 0)',
            *cast.refusals('S'), *cast.budget('S')]
    return values


def main():
    fingerprint = sources.family.fingerprint
    sources.family.fingerprint = lambda: dict(fingerprint(), **{
        str(Path(__file__).relative_to(driver.ROOT)): sources.family.sha(__file__),
        str(Path(cast.__file__).relative_to(driver.ROOT)): sources.family.sha(cast.__file__),
        str(Path(throwing.__file__).relative_to(driver.ROOT)): sources.family.sha(throwing.__file__)})
    driver.sources, driver.PREFIX, driver.checks = sources, PREFIX, checks
    driver.main()


if __name__ == '__main__':
    main()
