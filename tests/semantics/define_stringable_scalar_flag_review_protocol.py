#!/usr/bin/env python3
"""A captured request-zero flag reaches an actual post-conversion duplicate throw."""
import json
import os
from pathlib import Path

import define_stringable_name_protocol as cast
import define_stringable_scalar_flag_review_sources as sources

driver, common, text, b64 = cast.driver, cast.common, cast.text, cast.b64
MESSAGE = 'Constant STRINGQUIET61PEER already defined, this will be an error in PHP 9'
PREFIX = cast.PREFIX + r"""
dec $test_string_scalar_duplicate_front(pstate, nat) : bool
def $test_string_scalar_duplicate_front(S, 0) = true
  -- if S.CURRENT = (pcallcontext)
  -- if $error_context_call(S,pcallcontext) = (perrorcall)
  -- if perrorcall.RESUME = DYNAMIC_SCALAR_DEFINE_FLAG_DUPLICATE pconfigcall n_prefix
def $test_string_scalar_duplicate_front(S, 1) = true
  -- if S.TODO = (THROW_VALUE porigin z) :: ptask_body*
  -- if S.CURRENT = (pcallcontext)
  -- if $error_context_call(S,pcallcontext) = (perrorcall)
  -- if perrorcall.RESUME = DYNAMIC_SCALAR_DEFINE_FLAG_DUPLICATE pconfigcall n_prefix
def $test_string_scalar_duplicate_front(S, 2) = true
  -- if S.TODO = (THROW_SEARCH n) :: (ERROR_HANDLER_RESULT perrorcall) :: ptask_tail*
  -- if perrorcall.RESUME = DYNAMIC_SCALAR_DEFINE_FLAG_DUPLICATE pconfigcall n_prefix
def $test_string_scalar_duplicate_front(S, n_stage) = false -- otherwise
dec $test_string_scalar_duplicate_seek(pstate, nat, nat) : pstate
def $test_string_scalar_duplicate_seek(S, n_stage, 0) = S
def $test_string_scalar_duplicate_seek(S, n_stage, n) = S
  -- if $(n > 0)
  -- if $test_string_scalar_duplicate_front(S,n_stage) \/ (S.COMPLETION =/= NORMAL /\ S.COMPLETION =/= BUDGET)
def $test_string_scalar_duplicate_seek(S, n_stage, n) = $test_string_scalar_duplicate_seek($drive_steps($test_running(S),1),n_stage,$nabs($(n - 1)))
  -- if $(n > 0)
  -- if ~$test_string_scalar_duplicate_front(S,n_stage)
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
"""


def reach(state, start, stage):
    return [state + '_found = $test_string_scalar_duplicate_seek(' + start + ',' + str(stage) + ',3000)',
        state + '_found.COMPLETION = NORMAL \\/ ' + state + '_found.COMPLETION = BUDGET',
        state + ' = ' + state + '_found[.COMPLETION = NORMAL]',
        '$test_string_scalar_duplicate_front(' + state + ',' + str(stage) + ')']


def checks(program, path, name):
    assert name == 'selected-stringable-request-zero-duplicate-throw-retains-key'
    values = ['S_initial = $php_run(' + program + ',0,' + json.dumps(b64(os.fsencode(path))) + ')',
        'S_initial.COMPLETION = BUDGET', *cast.reach('S', 'S_initial', 0),
        'S.TODO = (CONFIG_INVOKE pconfigcall_S) :: ptask_S*',
        'pconfigcall_S.KIND = INTRINSIC_DEFINE', 'pconfigcall_S.INDEX = 3',
        'pconfigcall_S.OWNER = eps', 'pconfigcall_S.PACKS = eps', '~pconfigcall_S.NAMED',
        'pconfigcall_S.SENT = [NAMED_SENT (KNOWN (POBJECT n_object_S)),NAMED_SENT (KNOWN pvalue_candidate_S),NAMED_SENT (KNOWN pvalue_flag_S)]',
        'pconfigcall_S.SELECTION = (n_selection)', 'S.SELECTEDCALLS[n_selection].KIND = INTRINSIC_DEFINE',
        '$dynamic_define_string_valid(S,pconfigcall_S)', '$config_invoke_valid(S,pconfigcall_S)',
        '~$config_string_kind(INTRINSIC_DEFINE)',
        '$config_string_source(S,pconfigcall_S) = ((porigin_child_S,z_child_S))',
        '$config_string_object(pconfigcall_S) = (n_object_S)',
        'pvalue_candidate_S = PSTRING_CARRIER (REQUEST_STRING n_candidate) ' + text('captured-value61'),
        '$string_carrier_valid(S,pvalue_candidate_S)',
        'pvalue_flag_S = PSTRING_CARRIER (REQUEST_STRING n_flag_string) ' + text('0'),
        '$string_carrier_valid(S,pvalue_flag_S)', '$dynamic_define_quiet_flag(pvalue_flag_S)', '~$truth(S,pvalue_flag_S)',
        '$lookup(S.ENV,' + text('keep') + ') = (n_keep)', 'S.STORE[n_keep] = DEFINED (POBJECT n_object_S)',
        '$lookup(S.ENV,' + text('name') + ') = (n_name)', 'S.STORE[n_name] = DEFINED (POBJECT n_object_S)',
        '$lookup(S.ENV,' + text('call') + ') = (n_call)', 'S.STORE[n_call] = DEFINED pvalue_call_before',
        '$string_bytes(pvalue_call_before) = (' + text('DeFiNe') + ')',
        '$lookup(S.ENV,' + text('value') + ') = (n_value)', 'S.STORE[n_value] = DEFINED pvalue_candidate_S',
        '$lookup(S.ENV,' + text('flag') + ') = (n_flag)', 'S.STORE[n_flag] = DEFINED pvalue_flag_S',
        '$lookup(S.ENV,' + text('result') + ') = (n_result)', 'S.STORE[n_result] = DEFINED (PINT 99)',
        '$lookup(S.ENV,' + text('casts') + ') = (n_casts)', 'S.STORE[n_casts] = DEFINED (PINT 0)',
        '$lookup(S.ENV,' + text('warnings') + ') = (n_warnings)', 'S.STORE[n_warnings] = DEFINED (PINT 0)',
        '$lookup(S.ENV,' + text('saved') + ') = (n_saved)', 'S.STORE[n_saved] = DEFINED PNULL',
        'S.USERCONSTANTS = eps', '$test_outputs(S.EVENTS) = ' + text('B|'),
        *common.public('S'), *cast.weak('S', 'STRINGQUIET61PEER'),
        'pvalue_string_S = PSTRING_CARRIER (REQUEST_STRING n_converted) ' + text('STRINGQUIET61PEER'),
        '$named_slot_at(pconfigcall_converted_S.SENT,1) = NAMED_SENT (KNOWN pvalue_candidate_S)',
        '$named_slot_at(pconfigcall_converted_S.SENT,2) = NAMED_SENT (KNOWN pvalue_flag_S)',
        '$dynamic_scalar_define_flag_valid(S_ready,pconfigcall_converted_S)',
        '~$dynamic_constant_case_valid(S_ready,pconfigcall_converted_S)',
        '~$dynamic_scalar_define_flag_case_valid(S_ready,pconfigcall_converted_S)',
        'S_ready.STORE[n_flag] = DEFINED pvalue_cast_flag', '$string_bytes(pvalue_cast_flag) = (' + text('cast-flag61') + ')',
        '$truth(S_ready,pvalue_cast_flag)', '~$truth(S_ready,pvalue_flag_S)',
        'S_ready.STORE[n_casts] = DEFINED (PINT 1)', 'S_ready.STORE[n_warnings] = DEFINED (PINT 0)',
        'S_ready.STORE[n_result] = DEFINED (PINT 99)', 'S_ready.STORE[n_keep] = DEFINED (POBJECT n_object_S)',
        'S_ready.STORE[n_call] = DEFINED pvalue_cast_call', '$string_bytes(pvalue_cast_call) = (' + text('constant') + ')',
        'S_ready.STORE[n_name] = DEFINED pvalue_cast_name', '$string_bytes(pvalue_cast_name) = (' + text('cast-name61') + ')',
        'S_ready.STORE[n_value] = DEFINED pvalue_cast_value', '$string_bytes(pvalue_cast_value) = (' + text('cast-value61') + ')',
        'S_ready.USERCONSTANTS = [puserconstant_target]',
        'puserconstant_target.NAME = ' + text('STRINGQUIET61PEER'), 'puserconstant_target.VALUE = PINT 1901',
        'puserconstant_target.CLASS = PVSCALAR', 'puserconstant_target.ORIGIN =/= pconfigcall_S.SITE',
        '$dynamic_scalar_define_flag_duplicate_valid(S_ready,pconfigcall_converted_S,1)',
        '~$dynamic_scalar_define_flag_duplicate_valid(S_ready,pconfigcall_converted_S,0)', '$test_outputs(S_ready.EVENTS) = ' + text('B|S|'),
        *common.step('S_dispatch', 'S_ready'),
        'S_dispatch.TODO = (ERROR_HANDLER_INVOKE perrorcall_duplicate) :: ptask_S*',
        'perrorcall_duplicate.RESUME = DYNAMIC_SCALAR_DEFINE_FLAG_DUPLICATE pconfigcall_converted_S 1',
        'perrorcall_duplicate.LEVEL = 2',
        'perrorcall_duplicate.MESSAGE = ' + text(MESSAGE),
        'perrorcall_duplicate.EVENT = DIAGNOSTIC "Warning" perrorcall_duplicate.MESSAGE pconfigcall_S.LINE',
        'perrorcall_duplicate.SITE = pconfigcall_S.SITE', 'perrorcall_duplicate.LINE = pconfigcall_S.LINE',
        '$error_call_valid(S_dispatch,perrorcall_duplicate)',
        *cast.unchanged('S_dispatch', 'S_ready', 'STORE ENV ARRAYS OBJECTS OBJECTPROPS USERCONSTANTS STRINGDATA EVENTS SELECTEDCALLS AUTOLOAD CLASSNAMES CLASSCONSTANTCACHE'),
        *common.public('S_dispatch'), *reach('S_handler', 'S_dispatch', 0),
        'S_handler.CURRENT = (pcallcontext_handler)',
        '$error_context_trigger(S_handler,pcallcontext_handler) = (pconfigcall_converted_S)',
        '$error_handler_trace_values(S_handler,pcallcontext_handler,pconfigcall_converted_S) = [pvalue_string_S,pvalue_candidate_S,pvalue_flag_S]',
        *common.public('S_handler'), *reach('S_throw', 'S_handler', 1),
        'S_throw.TODO = (THROW_VALUE porigin_throw z_throw) :: ptask_body*',
        'S_throw.CURRENT = (pcallcontext_handler)',
        'S_throw.FRAMES = pframe_call :: pframe_outer*',
        'pframe_call.CONTEXT = S.CURRENT', 'pframe_call.LOCALS = ($active_table(S_ready))',
        'pframe_call.TODO = (ERROR_HANDLER_RESULT perrorcall_entered) :: ptask_S*',
        'perrorcall_entered.RESUME = perrorcall_duplicate.RESUME',
        '$error_context_trigger(S_throw,pcallcontext_handler) = (pconfigcall_converted_S)',
        'S_throw.STORE[n_saved] = DEFINED (POBJECT n_exception)',
        'S_throw.OBJECTS[n_exception] = THROWABLE pthrowable', 'pthrowable.KIND = "Exception"',
        '$string_bytes($throwable_field(S_throw,n_exception,"message")) = (' + text('duplicate61-stop') + ')',
        '$throwable_field(S_throw,n_exception,"previous") = PNULL',
        '$throwable_field(S_throw,n_exception,"trace") = PARRAY n_trace',
        'S_throw.ARRAYS[n_trace].ITEMS = [ENTRY (KINT 0) (DIRECT (PARRAY n_handler)),ENTRY (KINT 1) (DIRECT (PARRAY n_api)),ENTRY (KINT 2) (DIRECT (PARRAY n_caller))]',
        '$trace_array_field(S_throw,n_handler,' + text('function') + ') = PSTRING ' + text('stringScalarReviewWarning61'),
        '$trace_array_field(S_throw,n_api,' + text('function') + ') = PSTRING ' + text('define'),
        '$trace_array_field(S_throw,n_api,' + text('line') + ') = PINT pconfigcall_S.LINE',
        '$trace_array_field(S_throw,n_api,' + text('args') + ') = PARRAY n_args',
        'S_throw.ARRAYS[n_args].ITEMS = [ENTRY (KINT 0) (DIRECT pvalue_string_S),ENTRY (KINT 1) (DIRECT pvalue_candidate_S),ENTRY (KINT 2) (DIRECT pvalue_flag_S)]',
        '$node_children(S_throw,HARRAY n_args) = eps',
        '$trace_array_field(S_throw,n_caller,' + text('function') + ') = PSTRING ' + text('stringScalarReviewCaller61'),
        'S_throw.STORE[n_keep] = DEFINED (POBJECT n_object_S)', 'S_throw.STORE[n_result] = DEFINED (PINT 99)',
        'S_throw.STORE[n_flag] = DEFINED pvalue_handler_flag',
        'S_throw.STORE[n_casts] = DEFINED (PINT 1)', 'S_throw.STORE[n_warnings] = DEFINED (PINT 1)',
        'S_throw.USERCONSTANTS = [puserconstant_target,puserconstant_sibling]',
        'puserconstant_sibling.NAME = ' + text('SOURCE61PEER'), 'puserconstant_sibling.VALUE = PINT 1957',
        'puserconstant_sibling.CLASS = PVSCALAR',
        '$source_constant_lookup(S_throw,' + text('STRINGQUIET61PEER') + ') = (VALUE (PINT 1901))',
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
        'S_thrown.USERCONSTANTS = [puserconstant_target,puserconstant_sibling]',
        '$dynamic_scalar_define_flag_valid(S_thrown,pconfigcall_converted_S)',
        '$dynamic_scalar_define_flag_duplicate_valid(S_thrown,pconfigcall_converted_S,1)',
        '$dynamic_scalar_define_flag_duplicate_valid(S_thrown,pconfigcall_converted_S,2)',
        '~$dynamic_scalar_define_flag_duplicate_valid(S_thrown,pconfigcall_converted_S,3)',
        '$source_constant_lookup(S_thrown,' + text('STRINGQUIET61PEER') + ') = (VALUE (PINT 1901))',
        *common.public('S_thrown'),
        'S_discard = S_thrown[.TODO = (THROW_SEARCH n_exception) :: ptask_S*]',
        'S_expected = $error_handler_restore($identity_read_discard(S_discard,perrorcall_entered.RESUME),perrorcall_entered.CALLBACK)',
        '$error_read_discard(S_expected,perrorcall_entered.RESUME) = S_expected',
        *common.step('S_after', 'S_thrown'), 'S_after = S_expected',
        'S_after.TODO = (THROW_SEARCH n_exception) :: ptask_S*',
        'S_after.OBJECTS[n_exception] = THROWABLE pthrowable', '$throwable_live(S_after,n_exception)',
        'S_after.STORE[n_result] = DEFINED (PINT 99)',
        'S_after.USERCONSTANTS = [puserconstant_target,puserconstant_sibling]',
        '$source_constant_lookup(S_after,' + text('STRINGQUIET61PEER') + ') = (VALUE (PINT 1901))',
        '$source_constant_lookup(S_after,' + text('SOURCE61PEER') + ') = (VALUE (PINT 1957))',
        '$user_constants_valid(S_after,S_after.USERCONSTANTS)', *common.public('S_after'),
        *cast.refusals('S'),
        'pvalue_bad_flag = PSTRING_CARRIER (REQUEST_STRING (|S.STRINGDATA|)) ' + text('0'),
        '~$dynamic_define_string_valid(S,pconfigcall_S[.SENT = $named_slot_set(pconfigcall_S.SENT,2,KNOWN pvalue_bad_flag)])',
        'pconfigcall_bad_flag = pconfigcall_converted_S[.SENT = $named_slot_set(pconfigcall_converted_S.SENT,2,KNOWN (PSTRING_CARRIER (REQUEST_STRING (|S_expected.STRINGDATA|)) ' + text('0') + '))]',
        '~$dynamic_scalar_define_flag_valid(S_expected,pconfigcall_bad_flag)',
        'pvalue_bad_candidate = PSTRING_CARRIER (REQUEST_STRING (|S.STRINGDATA|)) ' + text('captured-value61'),
        '~$dynamic_define_string_valid(S,pconfigcall_S[.SENT = $named_slot_set(pconfigcall_S.SENT,1,KNOWN pvalue_bad_candidate)])',
        'pconfigcall_bad_candidate = pconfigcall_converted_S[.SENT = $named_slot_set(pconfigcall_converted_S.SENT,1,KNOWN (PSTRING_CARRIER (REQUEST_STRING (|S_expected.STRINGDATA|)) ' + text('captured-value61') + '))]',
        '~$dynamic_scalar_define_flag_valid(S_expected,pconfigcall_bad_candidate)',
        'pconfigcall_bad_name = pconfigcall_converted_S[.SENT = $named_slot_set(pconfigcall_converted_S.SENT,0,KNOWN (PSTRING_CARRIER (REQUEST_STRING (|S_expected.STRINGDATA|)) ' + text('STRINGQUIET61PEER') + '))]',
        '~$dynamic_scalar_define_flag_valid(S_expected,pconfigcall_bad_name)',
        'pconfigcall_short = pconfigcall_S[.INDEX = 2][.SENT = [NAMED_SENT (KNOWN (POBJECT n_object_S)),NAMED_SENT (KNOWN pvalue_candidate_S)]]',
        '$dynamic_define_string_call(pconfigcall_short)', '~$dynamic_define_string_valid(S,pconfigcall_short)',
        *cast.budget('S'), *cast.budget('S_returned'), *cast.budget('S_thrown')]
    for variable, expected in [('call', 'defined'), ('name', 'handler-name61'), ('value', 'handler-value61'), ('flag', 'handler-flag61')]:
        values += ['S_thrown.STORE[n_' + variable + '] = DEFINED pvalue_handler_' + variable,
            '$string_bytes(pvalue_handler_' + variable + ') = (' + text(expected) + ')']
    for field in ('.SITE = PORIGIN 0 eps', '.LINE = $(pconfigcall_S.LINE + 1)', '.SELECTION = eps'):
        values += ['~$dynamic_scalar_define_flag_valid(S_expected,pconfigcall_converted_S[' + field + '])']
    for flag in ('PBOOL false', 'PBOOL true', 'PNULL'):
        values += ['~$dynamic_scalar_define_flag_call(pconfigcall_converted_S[.SENT = $named_slot_set(pconfigcall_converted_S.SENT,2,KNOWN (' + flag + '))])']
    for field in ('.LEVEL = 8192', '.MESSAGE = ' + text('changed'), '.LINE = $(perrorcall_duplicate.LINE + 1)',
            '.EVENT = DIAGNOSTIC "Warning" perrorcall_duplicate.MESSAGE $(perrorcall_duplicate.LINE + 1)'):
        values += ['~$error_call_valid(S_expected,perrorcall_duplicate[' + field + '])']
    values += ['S_final = $drive_steps(S_after,3000)', 'S_final.COMPLETION = NORMAL',
        'S_final.TODO = eps', 'S_final.CURRENT = eps', 'S_final.FRAMES = eps',
        'S_final.USERCONSTANTS = [puserconstant_target,puserconstant_sibling]',
        '$source_constant_lookup(S_final,' + text('STRINGQUIET61PEER') + ') = (VALUE (PINT 1901))',
        'S_final.ERRORHANDLER.CALLBACK = eps', 'S_final.AUTOLOAD = S.AUTOLOAD',
        'S_final.CLASSNAMES = S.CLASSNAMES', 'S_final.CLASSCONSTANTCACHE = S.CLASSCONSTANTCACHE',
        '$test_outputs(S_final.EVENTS) = ' + text('B|S|W|2|' + MESSAGE + '|I|99|1|1|defined|handler-name61|handler-value61|handler-flag61|1901|1957|Z|99'),
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
