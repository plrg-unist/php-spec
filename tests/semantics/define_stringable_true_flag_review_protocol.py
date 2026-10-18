#!/usr/bin/env python3
"""An actual ignored-warning throw publishes after the Stringable conversion."""
import json
import os
from pathlib import Path

import define_stringable_name_protocol as cast
import define_stringable_true_flag_review_sources as sources

driver, common, text, b64 = cast.driver, cast.common, cast.text, cast.b64
MESSAGE = 'define(): Argument #3 ($case_insensitive) is ignored since declaration of case-insensitive constants is no longer supported'
PREFIX = cast.PREFIX + r"""
dec $test_string_true_pending_front(pstate, nat) : bool
def $test_string_true_pending_front(S, 0) = true
  -- if S.CURRENT = (pcallcontext)
  -- if $error_context_call(S,pcallcontext) = (perrorcall)
  -- if perrorcall.RESUME = DYNAMIC_CONSTANT_CASE_WARNING pconfigcall
def $test_string_true_pending_front(S, 1) = true
  -- if S.TODO = (THROW_VALUE porigin z) :: ptask_body*
  -- if S.CURRENT = (pcallcontext)
  -- if $error_context_call(S,pcallcontext) = (perrorcall)
  -- if perrorcall.RESUME = DYNAMIC_CONSTANT_CASE_WARNING pconfigcall
def $test_string_true_pending_front(S, 2) = true
  -- if S.TODO = (THROW_SEARCH n) :: (ERROR_HANDLER_RESULT perrorcall) :: ptask_tail*
  -- if perrorcall.RESUME = DYNAMIC_CONSTANT_CASE_WARNING pconfigcall
def $test_string_true_pending_front(S, n_stage) = false -- otherwise
dec $test_string_true_pending_seek(pstate, nat, nat) : pstate
def $test_string_true_pending_seek(S, n_stage, 0) = S
def $test_string_true_pending_seek(S, n_stage, n) = S
  -- if $(n > 0)
  -- if $test_string_true_pending_front(S,n_stage) \/ (S.COMPLETION =/= NORMAL /\ S.COMPLETION =/= BUDGET)
def $test_string_true_pending_seek(S, n_stage, n) = $test_string_true_pending_seek($drive_steps($test_running(S),1),n_stage,$nabs($(n - 1)))
  -- if $(n > 0)
  -- if ~$test_string_true_pending_front(S,n_stage)
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
"""


def reach(state, start, stage):
    return [state + '_found = $test_string_true_pending_seek(' + start + ',' + str(stage) + ',3000)',
        state + '_found.COMPLETION = NORMAL \\/ ' + state + '_found.COMPLETION = BUDGET',
        state + ' = ' + state + '_found[.COMPLETION = NORMAL]',
        '$test_string_true_pending_front(' + state + ',' + str(stage) + ')']


def checks(program, path, name):
    assert name == 'selected-stringable-true-warning-throw-still-registers-captured-value'
    values = ['S_initial = $php_run(' + program + ',0,' + json.dumps(b64(os.fsencode(path))) + ')',
        'S_initial.COMPLETION = BUDGET', *cast.reach('S', 'S_initial', 0),
        'S.TODO = (CONFIG_INVOKE pconfigcall_S) :: ptask_S*',
        'pconfigcall_S.KIND = INTRINSIC_DEFINE', 'pconfigcall_S.INDEX = 3',
        'pconfigcall_S.OWNER = eps', 'pconfigcall_S.PACKS = eps', '~pconfigcall_S.NAMED',
        'pconfigcall_S.SENT = [NAMED_SENT (KNOWN (POBJECT n_object_S)),NAMED_SENT (KNOWN pvalue_candidate_S),NAMED_SENT (KNOWN (PBOOL true))]',
        'pconfigcall_S.SELECTION = (n_selection)', 'S.SELECTEDCALLS[n_selection].KIND = INTRINSIC_DEFINE',
        '$dynamic_define_string_valid(S,pconfigcall_S)', '$config_invoke_valid(S,pconfigcall_S)',
        '~$config_string_kind(INTRINSIC_DEFINE)',
        '$config_string_source(S,pconfigcall_S) = ((porigin_child_S,z_child_S))',
        '$config_string_object(pconfigcall_S) = (n_object_S)',
        'pvalue_candidate_S = PSTRING_CARRIER (REQUEST_STRING n_candidate) ' + text('captured-value59'),
        '$string_carrier_valid(S,pvalue_candidate_S)',
        '$lookup(S.ENV,' + text('keep') + ') = (n_keep)', 'S.STORE[n_keep] = DEFINED (POBJECT n_object_S)',
        '$lookup(S.ENV,' + text('name') + ') = (n_name)', 'S.STORE[n_name] = DEFINED (POBJECT n_object_S)',
        '$lookup(S.ENV,' + text('call') + ') = (n_call)', 'S.STORE[n_call] = DEFINED pvalue_call_before',
        '$string_bytes(pvalue_call_before) = (' + text('DeFiNe') + ')',
        '$lookup(S.ENV,' + text('value') + ') = (n_value)', 'S.STORE[n_value] = DEFINED pvalue_candidate_S',
        '$lookup(S.ENV,' + text('flag') + ') = (n_flag)', 'S.STORE[n_flag] = DEFINED (PBOOL true)',
        '$lookup(S.ENV,' + text('result') + ') = (n_result)', 'S.STORE[n_result] = DEFINED (PINT 99)',
        '$lookup(S.ENV,' + text('casts') + ') = (n_casts)', 'S.STORE[n_casts] = DEFINED (PINT 0)',
        '$lookup(S.ENV,' + text('warnings') + ') = (n_warnings)', 'S.STORE[n_warnings] = DEFINED (PINT 0)',
        '$lookup(S.ENV,' + text('saved') + ') = (n_saved)', 'S.STORE[n_saved] = DEFINED PNULL',
        'S.USERCONSTANTS = eps', '$test_outputs(S.EVENTS) = ' + text('B|'),
        *common.public('S'), *cast.weak('S', 'STRINGFLAG59PEER'),
        'pvalue_string_S = PSTRING_CARRIER (REQUEST_STRING n_converted) ' + text('STRINGFLAG59PEER'),
        '$named_slot_at(pconfigcall_converted_S.SENT,1) = NAMED_SENT (KNOWN pvalue_candidate_S)',
        '$named_slot_at(pconfigcall_converted_S.SENT,2) = NAMED_SENT (KNOWN (PBOOL true))',
        '$dynamic_constant_case_valid(S_ready,pconfigcall_converted_S)',
        'S_ready.STORE[n_flag] = DEFINED (PBOOL false)',
        'S_ready.STORE[n_casts] = DEFINED (PINT 1)', 'S_ready.STORE[n_warnings] = DEFINED (PINT 0)',
        'S_ready.STORE[n_result] = DEFINED (PINT 99)', 'S_ready.STORE[n_keep] = DEFINED (POBJECT n_object_S)',
        'S_ready.STORE[n_call] = DEFINED pvalue_cast_call', '$string_bytes(pvalue_cast_call) = (' + text('constant') + ')',
        'S_ready.STORE[n_name] = DEFINED pvalue_cast_name', '$string_bytes(pvalue_cast_name) = (' + text('cast-name59') + ')',
        'S_ready.STORE[n_value] = DEFINED pvalue_cast_value', '$string_bytes(pvalue_cast_value) = (' + text('cast-value59') + ')',
        'S_ready.USERCONSTANTS = eps', '$test_outputs(S_ready.EVENTS) = ' + text('B|S|'),
        *common.step('S_dispatch', 'S_ready'),
        'S_dispatch.TODO = (ERROR_HANDLER_INVOKE perrorcall_case) :: ptask_S*',
        'perrorcall_case.RESUME = DYNAMIC_CONSTANT_CASE_WARNING pconfigcall_converted_S',
        'perrorcall_case.LEVEL = 2', 'perrorcall_case.MESSAGE = $dynamic_constant_case_message()',
        'perrorcall_case.MESSAGE = ' + text(MESSAGE),
        'perrorcall_case.SITE = pconfigcall_S.SITE', 'perrorcall_case.LINE = pconfigcall_S.LINE',
        '$error_call_valid(S_dispatch,perrorcall_case)',
        *cast.unchanged('S_dispatch', 'S_ready', 'STORE ENV ARRAYS OBJECTS OBJECTPROPS USERCONSTANTS STRINGDATA EVENTS SELECTEDCALLS AUTOLOAD CLASSNAMES CLASSCONSTANTCACHE'),
        *common.public('S_dispatch'), *reach('S_handler', 'S_dispatch', 0),
        'S_handler.CURRENT = (pcallcontext_handler)',
        '$error_context_trigger(S_handler,pcallcontext_handler) = (pconfigcall_converted_S)',
        '$error_handler_trace_values(S_handler,pcallcontext_handler,pconfigcall_converted_S) = [PSTRING ' + text('STRINGFLAG59PEER') + ',pvalue_candidate_S,PBOOL true]',
        *common.public('S_handler'), *reach('S_throw', 'S_handler', 1),
        'S_throw.TODO = (THROW_VALUE porigin_throw z_throw) :: ptask_body*',
        'S_throw.CURRENT = (pcallcontext_handler)',
        'S_throw.FRAMES = pframe_call :: pframe_outer*',
        'pframe_call.CONTEXT = S.CURRENT', 'pframe_call.LOCALS = ($active_table(S_ready))',
        'pframe_call.TODO = (ERROR_HANDLER_RESULT perrorcall_entered) :: ptask_S*',
        'perrorcall_entered.RESUME = perrorcall_case.RESUME',
        '$error_context_trigger(S_throw,pcallcontext_handler) = (pconfigcall_converted_S)',
        'S_throw.STORE[n_saved] = DEFINED (POBJECT n_exception)',
        'S_throw.OBJECTS[n_exception] = THROWABLE pthrowable', 'pthrowable.KIND = "Exception"',
        '$string_bytes($throwable_field(S_throw,n_exception,"message")) = (' + text('ignored59-stop') + ')',
        '$throwable_field(S_throw,n_exception,"previous") = PNULL',
        '$throwable_field(S_throw,n_exception,"trace") = PARRAY n_trace',
        'S_throw.ARRAYS[n_trace].ITEMS = [ENTRY (KINT 0) (DIRECT (PARRAY n_handler)),ENTRY (KINT 1) (DIRECT (PARRAY n_api)),ENTRY (KINT 2) (DIRECT (PARRAY n_caller))]',
        '$trace_array_field(S_throw,n_handler,' + text('function') + ') = PSTRING ' + text('stringTrueReviewWarning59'),
        '$trace_array_field(S_throw,n_api,' + text('function') + ') = PSTRING ' + text('define'),
        '$trace_array_field(S_throw,n_api,' + text('line') + ') = PINT pconfigcall_S.LINE',
        '$trace_array_field(S_throw,n_api,' + text('args') + ') = PARRAY n_args',
        'S_throw.ARRAYS[n_args].ITEMS = [ENTRY (KINT 0) (DIRECT (PSTRING ' + text('STRINGFLAG59PEER') + ')),ENTRY (KINT 1) (DIRECT pvalue_candidate_S),ENTRY (KINT 2) (DIRECT (PBOOL true))]',
        '$node_children(S_throw,HARRAY n_args) = eps',
        '$trace_array_field(S_throw,n_caller,' + text('function') + ') = PSTRING ' + text('stringTrueReviewCaller59'),
        'S_throw.STORE[n_keep] = DEFINED (POBJECT n_object_S)', 'S_throw.STORE[n_result] = DEFINED (PINT 99)',
        'S_throw.STORE[n_flag] = DEFINED (PBOOL false)',
        'S_throw.STORE[n_casts] = DEFINED (PINT 1)', 'S_throw.STORE[n_warnings] = DEFINED (PINT 1)',
        'S_throw.USERCONSTANTS = [puserconstant_sibling]',
        'puserconstant_sibling.NAME = ' + text('SOURCE59PEER'), 'puserconstant_sibling.VALUE = PINT 1777',
        'puserconstant_sibling.CLASS = PVSCALAR',
        '$source_constant_lookup(S_throw,' + text('STRINGFLAG59PEER') + ') = eps',
        '$test_outputs(S_throw.EVENTS) = ' + text('B|S|W|2|' + MESSAGE + '|'),
        'S_throw.AUTOLOAD = S_ready.AUTOLOAD', 'S_throw.CLASSNAMES = S_ready.CLASSNAMES',
        'S_throw.CLASSCONSTANTCACHE = S_ready.CLASSCONSTANTCACHE',
        'S_throw.OBJECTS[n_object_S] = S_ready.OBJECTS[n_object_S]',
        '$objectprops_at(S_throw.OBJECTPROPS,n_object_S) = $objectprops_at(S_ready.OBJECTPROPS,n_object_S)',
        *common.public('S_throw'), *common.step('S_throwing', 'S_throw'),
        'S_throwing.TODO = (THROW_SEARCH n_exception) :: ptask_body*',
        *reach('S_thrown', 'S_throwing', 2),
        'S_thrown.TODO = (THROW_SEARCH n_exception) :: (ERROR_HANDLER_RESULT perrorcall_entered) :: ptask_S*',
        'S_thrown.CURRENT = S.CURRENT', 'S_thrown.ENV = S.ENV',
        'S_thrown.OBJECTS[n_exception] = THROWABLE pthrowable',
        'S_thrown.STORE[n_saved] = DEFINED (POBJECT n_exception)',
        'S_thrown.STORE[n_result] = DEFINED (PINT 99)', 'S_thrown.STORE[n_keep] = DEFINED (POBJECT n_object_S)',
        'S_thrown.USERCONSTANTS = [puserconstant_sibling]',
        '$dynamic_constant_case_valid(S_thrown,pconfigcall_converted_S)',
        '$source_constant_lookup(S_thrown,' + text('STRINGFLAG59PEER') + ') = eps',
        *common.public('S_thrown'),
        'S_discard = S_thrown[.TODO = (THROW_SEARCH n_exception) :: ptask_S*]',
        'S_before = $error_handler_restore($identity_read_discard(S_discard,perrorcall_entered.RESUME),perrorcall_entered.CALLBACK)',
        'puserconstant_published = {NAME ' + text('STRINGFLAG59PEER') + ',ORIGIN pconfigcall_S.SITE,VALUE pvalue_candidate_S,CLASS PVSTRING false,READS eps,RECEIVES eps}',
        'S_expected = S_before[.USERCONSTANTS = [puserconstant_sibling,puserconstant_published]]',
        '$dynamic_constant_case_pending(S_before,pconfigcall_converted_S) = S_expected',
        '$error_read_discard(S_before,perrorcall_entered.RESUME) = S_expected',
        *common.step('S_after', 'S_thrown'), 'S_after = S_expected',
        'S_after.TODO = (THROW_SEARCH n_exception) :: ptask_S*',
        'S_after.OBJECTS[n_exception] = THROWABLE pthrowable', '$throwable_live(S_after,n_exception)',
        'S_after.STORE[n_result] = DEFINED (PINT 99)',
        '$source_constant_lookup(S_after,' + text('STRINGFLAG59PEER') + ') = (VALUE pvalue_candidate_S)',
        '$source_constant_lookup(S_after,' + text('SOURCE59PEER') + ') = (VALUE (PINT 1777))',
        '$user_constants_valid(S_after,S_after.USERCONSTANTS)', *common.public('S_after'),
        *cast.refusals('S'),
        'pvalue_bad_candidate = PSTRING_CARRIER (REQUEST_STRING (|S.STRINGDATA|)) ' + text('captured-value59'),
        '~$dynamic_define_string_valid(S,pconfigcall_S[.SENT = $named_slot_set(pconfigcall_S.SENT,1,KNOWN pvalue_bad_candidate)])',
        'pconfigcall_bad_candidate = pconfigcall_converted_S[.SENT = $named_slot_set(pconfigcall_converted_S.SENT,1,KNOWN (PSTRING_CARRIER (REQUEST_STRING (|S_before.STRINGDATA|)) ' + text('captured-value59') + '))]',
        '~$dynamic_constant_case_valid(S_before,pconfigcall_bad_candidate)',
        'pconfigcall_bad_name = pconfigcall_converted_S[.SENT = $named_slot_set(pconfigcall_converted_S.SENT,0,KNOWN (PSTRING_CARRIER (REQUEST_STRING (|S_before.STRINGDATA|)) ' + text('STRINGFLAG59PEER') + '))]',
        'S_bad_name = $dynamic_constant_case_pending(S_before,pconfigcall_bad_name)',
        'S_bad_name.COMPLETION = UNSUPPORTED "boolean define flag pending-exception registration"',
        'S_bad_name.USERCONSTANTS = S_before.USERCONSTANTS',
        'pconfigcall_false = pconfigcall_converted_S[.SENT = $named_slot_set(pconfigcall_converted_S.SENT,2,KNOWN (PBOOL false))]',
        '~$dynamic_constant_case_valid(S_before,pconfigcall_false)',
        'S_false = $dynamic_constant_case_pending(S_before,pconfigcall_false)',
        'S_false.COMPLETION = UNSUPPORTED "boolean define flag pending-exception registration"',
        'S_false.USERCONSTANTS = S_before.USERCONSTANTS',
        *cast.budget('S'), *cast.budget('S_returned'), *cast.budget('S_thrown')]
    for variable, expected in [('call', 'defined'), ('name', 'handler-name59'), ('value', 'handler-value59')]:
        values += ['S_thrown.STORE[n_' + variable + '] = DEFINED pvalue_handler_' + variable,
            '$string_bytes(pvalue_handler_' + variable + ') = (' + text(expected) + ')']
    for field in ('.SITE = PORIGIN 0 eps', '.LINE = $(pconfigcall_S.LINE + 1)', '.SELECTION = eps'):
        values += ['~$dynamic_constant_case_valid(S_before,pconfigcall_converted_S[' + field + '])']
    values += ['S_final = $drive_steps(S_after,3000)', 'S_final.COMPLETION = NORMAL',
        'S_final.TODO = eps', 'S_final.CURRENT = eps', 'S_final.FRAMES = eps',
        'S_final.USERCONSTANTS = [puserconstant_sibling,puserconstant_published]',
        'S_final.ERRORHANDLER.CALLBACK = eps', 'S_final.AUTOLOAD = S.AUTOLOAD',
        'S_final.CLASSNAMES = S.CLASSNAMES', 'S_final.CLASSCONSTANTCACHE = S.CLASSCONSTANTCACHE',
        '$test_outputs(S_final.EVENTS) = ' + text('B|S|W|2|' + MESSAGE + '|I|99|1|1|defined|handler-name59|handler-value59|F|captured-value59|1777|Z|99'),
        *common.public('S_final')]
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
