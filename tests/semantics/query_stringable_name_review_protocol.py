#!/usr/bin/env python3
"""A real Stringable query throw keeps its receiver and cancels both consumers."""
import json
import os
from pathlib import Path

import global_constant_scalar_name_protocol as driver
import query_stringable_name_review_sources as sources

common, text, b64 = driver.common, driver.text, driver.b64

PREFIX = r"""
dec $test_query_string_throw_front(pstate, nat) : bool
def $test_query_string_throw_front(S, 0) = true
  -- if S.TODO = (CONFIG_INVOKE pconfigcall) :: ptask_tail*
  -- if pconfigcall.KIND = INTRINSIC_CONSTANT
  -- if pconfigcall.SENT = [NAMED_SENT (KNOWN (POBJECT n_object))]
def $test_query_string_throw_front(S, 1) = true
  -- if S.TODO = (THROW_VALUE porigin z) :: ptask_method*
  -- if S.CURRENT = (pcallcontext)
  -- if $context_target(pcallcontext) = METHOD_TARGET n_object porigin_method
  -- if S.FRAMES = pframe :: pframe_tail*
  -- if pframe.TODO = (STRINGIFY_RESULT n_object porigin_child z_call) :: (CONFIG_STRING_RESULT pconfigcall n_object porigin_child z_child z_call) :: ptask_tail*
  -- if pconfigcall.KIND = INTRINSIC_CONSTANT
def $test_query_string_throw_front(S, 2) = true
  -- if S.TODO = (THROW_SEARCH n_throw) :: (STRINGIFY_RESULT n_object porigin_child z_call) :: (CONFIG_STRING_RESULT pconfigcall n_object porigin_child z_child z_call) :: ptask_tail*
  -- if pconfigcall.KIND = INTRINSIC_CONSTANT
def $test_query_string_throw_front(S, n_stage) = false -- otherwise
dec $test_query_string_throw_seek(pstate, nat, nat) : pstate
def $test_query_string_throw_seek(S, n_stage, 0) = S
def $test_query_string_throw_seek(S, n_stage, n) = S
  -- if $(n > 0)
  -- if $test_query_string_throw_front(S,n_stage) \/ (S.COMPLETION =/= NORMAL /\ S.COMPLETION =/= BUDGET)
def $test_query_string_throw_seek(S, n_stage, n) = $test_query_string_throw_seek($drive_steps($test_running(S),1),n_stage,$nabs($(n - 1)))
  -- if $(n > 0)
  -- if ~$test_query_string_throw_front(S,n_stage)
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
"""


def reach(state, start, stage):
    return [state + '_found = $test_query_string_throw_seek(' + start + ',' + str(stage) + ',3000)',
        state + '_found.COMPLETION = NORMAL \\/ ' + state + '_found.COMPLETION = BUDGET',
        state + ' = ' + state + '_found[.COMPLETION = NORMAL]',
        '$test_query_string_throw_front(' + state + ',' + str(stage) + ')']


def budget(state):
    return [state + '_pause = $drive_steps(' + state + ',0)', state + '_pause = ' + state + '[.COMPLETION = BUDGET]',
        state + '_one = $drive_steps(' + state + ',1)', state + '_one = $drive_steps(' + state + '_pause[.COMPLETION = NORMAL],1)']


def checks(program, path, name):
    assert name == 'selected-stringable-query-throw-keeps-raw-object-api-trace'
    values = ['S_initial = $php_run(' + program + ',0,' + json.dumps(b64(os.fsencode(path))) + ')',
        'S_initial.COMPLETION = BUDGET', *reach('S', 'S_initial', 0),
        'S.TODO = (CONFIG_INVOKE pconfigcall) :: ptask_tail*',
        'pconfigcall.KIND = INTRINSIC_CONSTANT', 'pconfigcall.INDEX = 1',
        'pconfigcall.SENT = [NAMED_SENT (KNOWN (POBJECT n_receiver))]',
        'pconfigcall.OWNER = eps', 'pconfigcall.PACKS = eps', '~pconfigcall.NAMED',
        'pconfigcall.SELECTION = (n_selection)', 'S.SELECTEDCALLS[n_selection].KIND = INTRINSIC_CONSTANT',
        '$config_invoke_valid(S,pconfigcall)', '$dynamic_query_string_call(pconfigcall)',
        '$dynamic_query_string_valid(S,pconfigcall)', '~$config_strict(S,pconfigcall)',
        '~$config_string_kind(INTRINSIC_CONSTANT)', '$config_string_object(pconfigcall) = (n_receiver)',
        '$config_string_source(S,pconfigcall) = ((porigin_child,z_child))',
        '$config_string_site_valid(S,pconfigcall,n_receiver,porigin_child,z_child,pconfigcall.LINE)',
        '$config_string_launch(S,pconfigcall)',
        'S_file = S[.FILEINCLUDEPATH = (' + text('.') + ')]',
        '$config_string_launch(S_file,pconfigcall)',
        '$config_string_site_valid(S_file,pconfigcall,n_receiver,porigin_child,z_child,pconfigcall.LINE)',
        '$intrinsic_argument(S,pconfigcall.SITE,0) = ((expression_argument,false,eps,porigin_argument,z_argument))',
        '$compiled_read(S,porigin_argument) = eps',
        '$stringable_instance(S,n_receiver)', 'S.OBJECTS[n_receiver] = INSTANCE porigin_class',
        '$lookup(S.ENV,' + text('keep') + ') = (n_keep)', 'S.STORE[n_keep] = DEFINED (POBJECT n_receiver)',
        '$lookup(S.ENV,' + text('name') + ') = (n_name)', 'S.STORE[n_name] = DEFINED (POBJECT n_receiver)',
        '$lookup(S.ENV,' + text('call') + ') = (n_call)', 'S.STORE[n_call] = DEFINED pvalue_call',
        '$string_bytes(pvalue_call) = (' + text('CoNsTaNt') + ')',
        '$lookup(S.ENV,' + text('calls') + ') = (n_calls)', 'S.STORE[n_calls] = DEFINED (PINT 0)',
        '$lookup(S.ENV,' + text('saved') + ') = (n_saved)', 'S.STORE[n_saved] = DEFINED PNULL',
        '$lookup(S.ENV,' + text('result') + ') = (n_result)', 'S.STORE[n_result] = DEFINED (PINT 99)',
        'S.USERCONSTANTS = eps', '$test_outputs(S.EVENTS) = ' + text('B|'), *common.public('S'),
        *common.step('S_launch', 'S'),
        'S_launch.TODO = (CALL_ARGS (METHOD_TARGET n_receiver porigin_method) eps 0 eps (porigin_child) pconfigcall.LINE) :: (STRINGIFY_RESULT n_receiver porigin_child pconfigcall.LINE) :: (CONFIG_STRING_RESULT pconfigcall n_receiver porigin_child z_child pconfigcall.LINE) :: ptask_tail*',
        'S_launch.ORIGIN = (porigin_child)', 'S_launch.RESULT = KNOWN PNULL',
        'S_launch.STORE = S.STORE', 'S_launch.USERCONSTANTS = S.USERCONSTANTS',
        'S_launch.SELECTEDCALLS = S.SELECTEDCALLS', 'S_launch.EVENTS = S.EVENTS', *common.public('S_launch'),
        *reach('S_throw', 'S_launch', 1),
        'S_throw.TODO = (THROW_VALUE porigin_throw z_throw) :: ptask_method*',
        'S_throw.CURRENT = (pcallcontext_method)',
        '$context_target(pcallcontext_method) = METHOD_TARGET n_receiver porigin_method',
        'pcallcontext_method.CALLSITE = (porigin_child)', 'pcallcontext_method.LINE = pconfigcall.LINE',
        'S_throw.FRAMES = pframe_call :: pframe_outer*',
        'pframe_call.CONTEXT = S.CURRENT', 'pframe_call.LOCALS = ($active_table(S))',
        'pframe_call.TODO = (STRINGIFY_RESULT n_receiver porigin_child pconfigcall.LINE) :: (CONFIG_STRING_RESULT pconfigcall n_receiver porigin_child z_child pconfigcall.LINE) :: ptask_tail*',
        '$config_string_trace_context(S_throw,pcallcontext_method)',
        '$config_string_site_valid(S_throw,pconfigcall,n_receiver,porigin_child,z_child,pconfigcall.LINE)',
        'S_throw.STORE[n_saved] = DEFINED (POBJECT n_exception)',
        'S_throw.OBJECTS[n_exception] = THROWABLE pthrowable', 'pthrowable.KIND = "Exception"',
        '$string_bytes($throwable_field(S_throw,n_exception,"message")) = (' + text('query53-stop') + ')',
        '$throwable_field(S_throw,n_exception,"previous") = PNULL',
        '$throwable_field(S_throw,n_exception,"trace") = PARRAY n_trace',
        'S_throw.ARRAYS[n_trace].ITEMS = [ENTRY (KINT 0) (DIRECT (PARRAY n_method_frame)),ENTRY (KINT 1) (DIRECT (PARRAY n_api_frame)),ENTRY (KINT 2) (DIRECT (PARRAY n_caller_frame))]',
        '$trace_array_field(S_throw,n_method_frame,' + text('function') + ') = PSTRING ' + text('__toString'),
        '$trace_array_field(S_throw,n_method_frame,' + text('class') + ') = PSTRING ' + text('QueryStringReviewThrow53'),
        '$trace_array_field(S_throw,n_method_frame,' + text('type') + ') = PSTRING ' + text('->'),
        '$trace_array_field(S_throw,n_method_frame,' + text('args') + ') = PARRAY n_method_args',
        'S_throw.ARRAYS[n_method_args].ITEMS = eps',
        '$trace_array_field(S_throw,n_api_frame,' + text('function') + ') = PSTRING ' + text('constant'),
        '$trace_array_field(S_throw,n_api_frame,' + text('line') + ') = PINT pconfigcall.LINE',
        '$trace_array_field(S_throw,n_api_frame,' + text('args') + ') = PARRAY n_api_args',
        'S_throw.ARRAYS[n_api_args].ITEMS = [ENTRY (KINT 0) (DIRECT (POBJECT n_receiver))]',
        '$node_children(S_throw,HARRAY n_api_args) = [HOBJECT n_receiver]',
        '$trace_array_field(S_throw,n_caller_frame,' + text('function') + ') = PSTRING ' + text('queryStringReviewCaller53'),
        'S_throw.STORE[n_result] = DEFINED (PINT 99)', 'S_throw.STORE[n_calls] = DEFINED (PINT 1)',
        'S_throw.STORE[n_call] = DEFINED pvalue_live_call', '$string_bytes(pvalue_live_call) = (' + text('defined') + ')',
        'S_throw.STORE[n_name] = DEFINED pvalue_live_name', '$string_bytes(pvalue_live_name) = (' + text('live-name53') + ')',
        'S_throw.STORE[n_keep] = DEFINED (POBJECT n_receiver)',
        'S_throw.USERCONSTANTS = [puserconstant_sibling]',
        'puserconstant_sibling.NAME = ' + text('SOURCE53PEER'),
        'puserconstant_sibling.VALUE = PINT 1433', 'puserconstant_sibling.CLASS = PVSCALAR',
        '$test_outputs(S_throw.EVENTS) = ' + text('B|S|'), *common.public('S_throw'),
        *common.step('S_throwing', 'S_throw'),
        'S_throwing.TODO = (THROW_SEARCH n_exception) :: ptask_method*',
        'S_throwing.OBJECTS[n_exception] = THROWABLE pthrowable',
        *reach('S_unwind', 'S_throwing', 2),
        'S_unwind.TODO = (THROW_SEARCH n_exception) :: (STRINGIFY_RESULT n_receiver porigin_child pconfigcall.LINE) :: (CONFIG_STRING_RESULT pconfigcall n_receiver porigin_child z_child pconfigcall.LINE) :: ptask_tail*',
        'S_unwind.CURRENT = S.CURRENT', 'S_unwind.ENV = S.ENV',
        'S_unwind.OBJECTS[n_exception] = THROWABLE pthrowable',
        'S_unwind.STORE[n_saved] = DEFINED (POBJECT n_exception)',
        'S_unwind.STORE[n_keep] = DEFINED (POBJECT n_receiver)',
        'S_unwind.STORE[n_result] = DEFINED (PINT 99)', 'S_unwind.STORE[n_calls] = DEFINED (PINT 1)',
        'S_unwind.USERCONSTANTS = [puserconstant_sibling]',
        '$config_string_site_valid(S_unwind,pconfigcall,n_receiver,porigin_child,z_child,pconfigcall.LINE)',
        *common.public('S_unwind'), *common.step('S_discard_string', 'S_unwind'),
        'S_discard_string = S_unwind[.TODO = (THROW_SEARCH n_exception) :: (CONFIG_STRING_RESULT pconfigcall n_receiver porigin_child z_child pconfigcall.LINE) :: ptask_tail*]',
        *common.step('S_discard_query', 'S_discard_string'),
        'S_discard_query = S_discard_string[.TODO = (THROW_SEARCH n_exception) :: ptask_tail*]',
        'S_discard_query.STORE[n_result] = DEFINED (PINT 99)',
        'S_discard_query.STORE[n_saved] = DEFINED (POBJECT n_exception)',
        'S_discard_query.USERCONSTANTS = [puserconstant_sibling]', *common.public('S_discard_query')]
    for field in ('.SITE = PORIGIN 0 eps', '.LINE = $(pconfigcall.LINE + 1)', '.INDEX = 0', '.SELECTION = eps'):
        values += ['~$dynamic_query_string_valid(S,pconfigcall[' + field + '])']
    for field in ('.OWNER = (0)', '.NAMED = true', '.KIND = INTRINSIC_DEFINE', '.SENT = eps',
            '.SENT = pconfigcall.SENT ++ [NAMED_SENT (KNOWN PNULL)]', '.SENT = [NAMED_SENT (KNOWN PNULL)]'):
        bad = 'pconfigcall[' + field + ']'
        values += ['~$dynamic_query_string_call(' + bad + ')',
            '~$config_string_site_valid(S_throw,' + bad + ',n_receiver,porigin_child,z_child,pconfigcall.LINE)']
    values += ['pconfigcall_wrong_kind = pconfigcall[.KIND = INTRINSIC_DEFINED]',
        '$dynamic_query_string_call(pconfigcall_wrong_kind)',
        '~$config_string_site_valid(S_throw,pconfigcall_wrong_kind,n_receiver,porigin_child,z_child,pconfigcall.LINE)',
        'pconfigcall_dead = pconfigcall[.SENT = [NAMED_SENT (KNOWN (POBJECT (|S.OBJECTS|)))]]',
        '$dynamic_query_string_call(pconfigcall_dead)', '~$dynamic_query_string_valid(S,pconfigcall_dead)',
        '~$config_string_site_valid(S_throw,pconfigcall,n_receiver,PORIGIN 0 eps,z_child,pconfigcall.LINE)',
        '~$config_string_site_valid(S_throw,pconfigcall,n_receiver,porigin_child,$(z_child + 1),pconfigcall.LINE)',
        '~$config_string_site_valid(S_throw,pconfigcall,n_receiver,porigin_child,z_child,$(pconfigcall.LINE + 1))',
        *budget('S'), *budget('S_unwind')]
    return values


def main():
    fingerprint = sources.family.fingerprint
    sources.family.fingerprint = lambda: dict(fingerprint(), **{
        str(Path(__file__).relative_to(driver.ROOT)): sources.family.sha(__file__)})
    driver.sources, driver.PREFIX, driver.checks = sources, PREFIX, checks
    driver.main()


if __name__ == '__main__':
    main()
