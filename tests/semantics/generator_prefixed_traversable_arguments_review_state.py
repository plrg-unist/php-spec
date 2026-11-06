#!/usr/bin/env python3
"""Check positional SENT ownership through terminal Traversable argument cursors."""
import base64
import hashlib
import json
import os
from pathlib import Path
import subprocess
import tempfile

from exception_handler_review import recorded
from recorded_worker import Worker

ROOT = Path(__file__).resolve().parents[2]
CATALOG = Path(__file__).with_name('generator_prefixed_traversable_arguments_review_cases.json')
EXPECTED = {
    'i129-computed-prefix-empty-iterator-send': 'd1d2aa51ef5b1a29bc1633f2509f67f1127407963483d9355fe6f885ff918bdb',
    'i129-aggregate-prefix-mapping-cleanup': 'e5a8eed2f882f1601f14a687a0353d22b6381cda04449753af73e082714ff210',
    'i129-nullsafe-prefix-generator-source-throw-cache': 'f8efccc8ce8e039785dc205be597e240ed32d5e6d58341506f4c784194945d50',
    'i129-iterator-prefix-owning-count-trace': '2f35479c7e776bf9fdabcf20506269cd14720a6eabcf2a3074bc261ccfbd5181',
    'i129-scalar-prefix-empty-iterator-send': '5eccc3d8707c6c8aa8c6cc2efeaba13379876fd1f124fd2d59f4fa1d5b284e45',
}
PREFIX = r'''
dec $test_i129_echo(pstate, ptbytes) : bool
def $test_i129_echo(S, ptbytes) = true
  -- if S.TODO = (STMT (NStmtEcho (SEQUENCE ((NScalarString (BYTES text) metadata_string) :: expression_tail*)) metadata)) :: ptask*
  -- if $base64(text) = ptbytes
def $test_i129_echo(S, ptbytes) = false -- otherwise
dec $test_i129_front(pstate, nat) : bool
def $test_i129_front(S, 0) = true
  -- if S.TODO = (METHOD_NAME poperand phpType7* z) :: ptask*
def $test_i129_front(S, 1) = true
  -- if S.TODO = (CONFIG_UNPACK_PREP pconfigcall) :: ptask*
  -- if $generator_api_kind(pconfigcall.KIND)
def $test_i129_front(S, 2) = true
  -- if S.TODO = (CONFIG_ITERATOR pconfigiterator "ready") :: ptask*
  -- if ~((HOBJECT pconfigiterator.OBJECT) <- S.ALLOCATIONS)
def $test_i129_front(S, 3) = true
  -- if S.TODO = (RETURN_VALUE z) :: ptask*
  -- if S.CURRENT = (pcallcontext)
  -- if pcallcontext.TARGET = AGGREGATE_METHOD_TARGET n porigin
def $test_i129_front(S, 4) = true
  -- if S.TODO = (CONFIG_AGGREGATE pconfigaggregate) :: ptask*
  -- if S.RESULT = KNOWN (POBJECT n)
def $test_i129_front(S, 5) = true
  -- if S.TODO = (THROW_SEARCH n) :: (CONFIG_ITERATOR pconfigiterator "send") :: ptask*
def $test_i129_front(S, 6) = $test_i129_echo(S, $ptascii("AFTER-3|"))
def $test_i129_front(S, 7) = true
  -- if S.TODO = (THROW_SEARCH n) :: (GENERATOR_RESUME pgeneratorop) :: ptask*
  -- if pgeneratorop.STARTPACK /\ pgeneratorop.BORROWED
  -- if S.OBJECTS[pgeneratorop.OBJECT] = GENERATOR pgenerator
  -- if pgenerator.PHASE = GENERATOR_CLOSED
def $test_i129_front(S, 8) = $test_i129_echo(S, $ptascii("CACHED|"))
def $test_i129_front(S, 9) = $test_i129_echo(S, $ptascii("RELEASED|"))
def $test_i129_front(S, n_stage) = false -- otherwise
dec $test_i129_seek(pstate, nat, nat) : pstate
def $test_i129_seek(S, n_stage, 0) = S
def $test_i129_seek(S, n_stage, n) = S
  -- if $(n > 0)
  -- if $test_i129_front(S, n_stage) \/ (S.COMPLETION =/= NORMAL /\ S.COMPLETION =/= BUDGET) \/ (S.TODO = eps /\ S.CURRENT = eps /\ S.FRAMES = eps)
def $test_i129_seek(S, n_stage, n) = $test_i129_seek($drive_steps(S[.COMPLETION = NORMAL], 1), n_stage, $nabs($(n - 1)))
  -- if $(n > 0)
  -- if ~$test_i129_front(S, n_stage)
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
  -- if ~(S.TODO = eps /\ S.CURRENT = eps /\ S.FRAMES = eps)
'''


def lines(text):
    return [line.strip() for line in text.splitlines() if line.strip()]


def reach(state, start, stage):
    return [state + '_found = $test_i129_seek(' + start + ', ' + str(stage) + ', 4000)',
        state + r'_found.COMPLETION = NORMAL \/ ' + state + '_found.COMPLETION = BUDGET',
        state + ' = ' + state + '_found[.COMPLETION = NORMAL]',
        '$test_i129_front(' + state + ', ' + str(stage) + ')']


def public(state):
    return ['$call_descriptors_valid(' + state + ')', '$heap_valid($heap_graph(' + state + '))']


def budget(state):
    return [state + '_pause = $drive(' + state + ', 0)',
        state + '_pause = ' + state + '[.COMPLETION = BUDGET]',
        *public(state + '_pause'),
        state + '_one = $drive(' + state + ', 1)',
        state + '_one.COMPLETION = BUDGET',
        '$drive(' + state + '_pause[.COMPLETION = NORMAL], 1) = ' + state + '_one',
        *public(state + '_one')]


def prefix_header(method, count=1, selected=False, start='S_initial'):
    sent = '[NAMED_SENT (KNOWN (POBJECT n_prefix))' + (', NAMED_SENT (KNOWN (PINT 5))' if count == 2 else '') + ']'
    selection = '(pgeneratormethodselection)' if selected else 'eps'
    return reach('S', start, 1) + lines(r'''
S.TODO = (CONFIG_UNPACK_PREP pconfigcall) :: ptask_tail*
pconfigcall.OWNER = (n_target)
pconfigcall.SITE = porigin_call
pconfigcall.LINE = z_call
pconfigcall.PACKS = eps
pconfigcall.SELECTION = eps
~pconfigcall.NAMED
$lookup(S.ENV, $ptascii("target")) = (n_target_cv)
S.STORE[n_target_cv] = DEFINED (POBJECT n_target)
$lookup(S.ENV, $ptascii("value")) = (n_value_cv)
S.STORE[n_value_cv] = DEFINED (POBJECT n_prefix)
$heap_owners($heap_graph(S), HOBJECT n_prefix) = 2
$heap_owners($heap_graph(S), HOBJECT n_target) = 2
''') + [
        'pconfigcall.KIND = INTRINSIC_GENERATOR_METHOD "' + method + '" ' + selection,
        'pconfigcall.INDEX = ' + str(count), 'pconfigcall.SENT = ' + sent,
        '$intrinsic_count(S, porigin_call) = (' + str(count + 1) + ')',
        '$generator_traversable_source_index(S, pconfigcall) = (' + str(count) + ')',
        '$config_traversable_argument(S, pconfigcall) = ((expression_input, true, eps, porigin_input, z_input))',
        '$intrinsic_argument(S, porigin_call, ' + str(count) + ') = ((expression_input, true, eps, porigin_input, z_input))',
        '$config_traversable_prefix(S, pconfigcall)',
        '$config_source_replay(S, pconfigcall, pconfigcall[.INDEX = 0][.SENT = eps][.NAMED = false], eps) = ((pconfigcall, eps))',
        '~$config_traversable_prefix(S, pconfigcall[.INDEX = 0])',
        '~$config_traversable_prefix(S, pconfigcall[.SENT = eps])',
        '~$config_traversable_prefix(S, pconfigcall[.NAMED = true])',
        '~$config_traversable_prefix(S, pconfigcall[.KIND = INTRINSIC_INI_SET])',
        *public('S')]


def dispatch(state, values, method, selection='eps', output='S_invoke'):
    sent = '[' + ', '.join('NAMED_SENT (KNOWN (' + value + '))' for value in values) + ']'
    operands = '[' + ', '.join('KNOWN (' + value + ')' for value in values) + ']'
    return [
        'PhpStep: ' + state + ' ~> ' + output,
        output + '.TODO = (CONFIG_INVOKE pconfigcall_copied) :: ptask_tail*',
        'pconfigcall_copied = pconfigcall[.INDEX = $(pconfigcall.INDEX + 1)][.SENT = ' + sent + ']',
        '$config_invoke_valid(' + output + ', pconfigcall_copied)',
        '$generator_traversable_copied_prefix(' + output + ', pconfigcall_copied)',
        'PhpStep: ' + output + ' ~> S_args',
        'S_args.TODO = (GENERATOR_ARGS pgeneratorop eps (' + operands + ')) :: ptask_tail*',
        'pgeneratorop.OBJECT = n_target', 'pgeneratorop.NAME = "' + method + '"',
        'pgeneratorop.SITE = porigin_call', 'pgeneratorop.LINE = z_call',
        'pgeneratorop.SELECTION = ' + selection,
        'pgeneratorop.ARGUMENTS = eps', '~pgeneratorop.BORROWED', '~pgeneratorop.STARTPACK',
        '$task_nodes(GENERATOR_ARGS pgeneratorop eps (' + operands + ')) = $config_nodes(pconfigcall_copied)',
        *public('S_args')]


def iterator_checks():
    values = reach('S_name', 'S_initial', 0) + lines(r'''
S_name.TODO = (METHOD_NAME poperand phpType7* z_call) :: ptask_name_tail*
S_name.ORIGIN = (porigin_call)
S_name.RESULT = VARIABLE $ptascii("method") z_name
S_method = $resolve_at(S_name, S_name.RESULT, z_call)
S_method.RESULT = KNOWN pvalue_method
$string_bytes(pvalue_method) = ($ptascii("send"))
S_lookup = $resolve_at(S_name, poperand, z_call)
S_lookup.RESULT = KNOWN (POBJECT n_target)
pgeneratormethodselection = {SITE porigin_call, OBJECT n_target, NAME $ptascii("send"), LINE z_call, CAPTURE eps, TEMPORARY false}
$generator_method_selection(S_method, poperand, $ptascii("send"), phpType7*, z_call) = (pgeneratormethodselection)
PhpStep: S_name ~> S_frozen
S_frozen.TODO = (CONFIG_ARGS pconfigcall_initial) :: $generator_method_return_tasks(S_name, porigin_call, ptask_name_tail*)
pconfigcall_initial.KIND = INTRINSIC_GENERATOR_METHOD "send" (pgeneratormethodselection)
pconfigcall_initial.INDEX = 0
pconfigcall_initial.SENT = eps
S_frozen.STORE = S_name.STORE
S_frozen.EVENTS = S_name.EVENTS
$heap_owners($heap_graph(S_frozen), HOBJECT n_target) = 2
''')
    values += public('S_frozen') + prefix_header('send', selected=True, start='S_frozen') + lines(r'''
pconfigcall = pconfigcall_initial[.INDEX = 1][.SENT = [NAMED_SENT (KNOWN (POBJECT n_prefix))]]
S.RESULT = VARIABLE $ptascii("pack") z_input
$lookup(S.ENV, $ptascii("pack")) = (n_input_cv)
S.STORE[n_input_cv] = DEFINED (POBJECT n_data)
$config_iterator_start(S, pconfigcall, S.RESULT, n_data)
PhpStep: S ~> S_data
S_data.TODO = (CONFIG_ITERATOR pconfigiterator_initial "rewind-start") :: ptask_tail*
pconfigiterator_initial.CALL = pconfigcall
pconfigiterator_initial.OBJECT = n_data
$config_iterator_argument_nodes(pconfigiterator_initial) = [HOBJECT n_prefix]
$task_nodes(CONFIG_ITERATOR pconfigiterator_initial "rewind-start") = [HOBJECT n_data, HOBJECT n_target, HOBJECT n_prefix]
''')
    values += reach('S_ready', 'S_data', 2) + lines(r'''
S_ready.TODO = (CONFIG_ITERATOR pconfigiterator_ready "ready") :: ptask_tail*
pconfigiterator_ready.CALL = pconfigcall
pconfigiterator_ready.OBJECT = n_data
pconfigiterator_ready.ITEMS = eps
S_ready.STORE[n_value_cv] = DEFINED PNULL
S_ready.STORE[n_target_cv] = DEFINED PNULL
S_ready.STORE[n_input_cv] = DEFINED PNULL
$lookup(S_ready.ENV, $ptascii("method")) = (n_method_cv)
S_ready.STORE[n_method_cv] = DEFINED (PSTRING_CARRIER INTERNED_STRING $ptascii("next"))
$config_iterator_valid(S_ready, pconfigiterator_ready, "ready")
$config_iterator_argument_nodes(pconfigiterator_ready) = [HOBJECT n_prefix]
$task_nodes(CONFIG_ITERATOR pconfigiterator_ready "ready") = [HOBJECT n_target, HOBJECT n_prefix]
$heap_owners($heap_graph(S_ready), HOBJECT n_target) = 1
$heap_owners($heap_graph(S_ready), HOBJECT n_prefix) = 1
$heap_owners($heap_graph(S_ready), HOBJECT n_data) = 0
$config_traversable_prefix(S_ready, pconfigcall)
''')
    return values + public('S_ready') + budget('S_ready') + dispatch('S_ready', ['POBJECT n_prefix'], 'send', '(pgeneratormethodselection)') + budget('S_args')


def aggregate_checks():
    values = prefix_header('send') + lines(r'''
S.RESULT = VARIABLE $ptascii("pack") z_input
$lookup(S.ENV, $ptascii("pack")) = (n_input_cv)
S.STORE[n_input_cv] = DEFINED (POBJECT n_input)
$config_aggregate_start(S, pconfigcall, S.RESULT, n_input)
PhpStep: S ~> S_getter
S_getter.TODO = (CALL_ARGS pcalltarget eps 0 eps (porigin_input) z_input) :: (CONFIG_AGGREGATE pconfigaggregate) :: ptask_tail*
pconfigaggregate = {CALL pconfigcall, OBJECT n_input, INPUT S.RESULT}
pcalltarget = AGGREGATE_METHOD_TARGET n_input porigin_method
$target_nodes(pcalltarget) = eps
$task_nodes(CONFIG_AGGREGATE pconfigaggregate) = [HOBJECT n_target, HOBJECT n_prefix]
''')
    values += reach('S_get', 'S_getter', 3) + lines(r'''
S_get.CURRENT = (pcallcontext_get)
pcallcontext_get.TARGET = pcalltarget
pcallcontext_get.RECEIVER = (n_input)
pcallcontext_get.CALLSITE = (porigin_input)
pcallcontext_get.LINE = z_input
$call_context_roots((pcallcontext_get)) = eps
S_get.FRAMES = pframe_get :: pframe_get_tail*
pframe_get.TODO = (CONFIG_AGGREGATE pconfigaggregate) :: ptask_tail*
pframe_get.ORIGIN = (porigin_input)
$config_aggregate_frame(S_get, pcallcontext_get, pframe_get)
$heap_owners($heap_graph(S_get), HOBJECT n_input) = 1
$heap_owners($heap_graph(S_get), HOBJECT n_prefix) = 2
$heap_owners($heap_graph(S_get), HOBJECT n_target) = 2
''')
    values += public('S_get') + budget('S_get') + reach('S_return', 'S_get', 4) + lines(r'''
S_return.TODO = (CONFIG_AGGREGATE pconfigaggregate) :: ptask_tail*
S_return.RESULT = KNOWN (POBJECT n_data)
$config_aggregate_return_allowed(S_return, pconfigaggregate)
PhpStep: S_return ~> S_data
S_data.TODO = (CONFIG_ITERATOR pconfigiterator_initial "rewind-start") :: ptask_tail*
pconfigiterator_initial.CALL = pconfigcall
pconfigiterator_initial.OBJECT = n_data
pconfigiterator_initial.PRODUCER = (n_input)
$task_nodes(CONFIG_ITERATOR pconfigiterator_initial "rewind-start") = [HOBJECT n_data, HOBJECT n_target, HOBJECT n_prefix]
''')
    values += reach('S_error', 'S_data', 5) + lines(r'''
S_error.TODO = (THROW_SEARCH n_error) :: (CONFIG_ITERATOR pconfigiterator_send "send") :: ptask_tail*
pconfigiterator_send.CALL = pconfigcall
pconfigiterator_send.OBJECT = n_data
pconfigiterator_send.PRODUCER = (n_input)
pconfigiterator_send.ITEMS = eps
pconfigiterator_send.CURRENT = KNOWN (PINT 17)
S_error.STORE[n_target_cv] = DEFINED PNULL
S_error.STORE[n_value_cv] = DEFINED PNULL
S_error.STORE[n_input_cv] = DEFINED PNULL
~((HOBJECT n_input) <- S_error.ALLOCATIONS)
$config_iterator_argument_nodes(pconfigiterator_send) = [HOBJECT n_prefix]
$heap_owners($heap_graph(S_error), HOBJECT n_target) = 1
$heap_owners($heap_graph(S_error), HOBJECT n_prefix) = 1
$heap_owners($heap_graph(S_error), HOBJECT n_data) = 1
$object_name(S_error, n_error) = $ptascii("Error")
$string_bytes($throwable_field(S_error, n_error, "message")) = ($ptascii("Unknown named parameter $extra"))
$throwable_field(S_error, n_error, "previous") = PNULL
$throwable_field(S_error, n_error, "trace") = PARRAY n_trace
S_error.ARRAYS[n_trace].ITEMS = [ENTRY (KINT 0) (DIRECT (PARRAY n_caller_trace))]
$trace_array_field(S_error, n_caller_trace, $ptascii("function")) = PSTRING $ptascii("run129A")
PhpStep: S_error ~> S_clean
S_clean.TODO = (THROW_SEARCH n_error) :: (CONFIG_ITERATOR pconfigiterator_ready "ready") :: ptask_tail*
pconfigiterator_ready = pconfigiterator_send[.CURRENT = KNOWN PNULL][.KEY = KNOWN PNULL]
$heap_owners($heap_graph(S_clean), HOBJECT n_target) = 1
$heap_owners($heap_graph(S_clean), HOBJECT n_prefix) = 1
$heap_owners($heap_graph(S_clean), HOBJECT n_data) = 0
''')
    values += public('S_error') + public('S_clean') + budget('S_clean') + lines(r'''
S_clean_one.TODO = (THROW_SEARCH n_error) :: (CONFIG_INVOKE pconfigcall_copied) :: ptask_tail*
pconfigcall_copied = pconfigcall[.INDEX = 2]
$heap_owners($heap_graph(S_clean_one), HOBJECT n_target) = 1
$heap_owners($heap_graph(S_clean_one), HOBJECT n_prefix) = 1
''')
    return values


def generator_checks():
    values = prefix_header('send', count=2, selected=True) + lines(r'''
S.RESULT = VARIABLE $ptascii("source") z_input
$lookup(S.ENV, $ptascii("source")) = (n_source_cv)
S.STORE[n_source_cv] = DEFINED (POBJECT n_source)
$config_generator_start(S, pconfigcall, S.RESULT, n_source)
''')
    values += reach('S_body', 'S', 6) + lines(r'''
S_body.CURRENT = (pcallcontext_source)
S_body.FRAMES = pframe_source :: pframe_source_tail*
pframe_source.TODO = (GENERATOR_RESUME pgeneratorop_source) :: (CONFIG_GENERATOR pconfiggenerator "next") :: ptask_tail*
pconfiggenerator.CALL = pconfigcall
pconfiggenerator.OBJECT = n_source
pconfiggenerator.INPUT = VARIABLE $ptascii("source") z_input
pconfiggenerator.PRODUCER = eps
pconfiggenerator.ITEMS = [ENTRY (KINT 0) (DIRECT (POBJECT n_cache)), ENTRY (KINT 1) (DIRECT (POBJECT n_cache)), ENTRY (KINT 2) (DIRECT (POBJECT n_cache))]
S_body.OBJECTS[n_source] = GENERATOR pgenerator_running
pgenerator_running.PHASE = GENERATOR_RUNNING
pgenerator_running.FRAME = eps
pgenerator_running.VALUE = (POBJECT n_cache)
pgenerator_running.REFCELL = eps
S_body.STORE[n_value_cv] = DEFINED PNULL
S_body.STORE[n_target_cv] = DEFINED PNULL
pgeneratorop_source = {OBJECT n_source, NAME "next", SITE porigin_input, LINE z_input, LOOP eps, ADVANCE false, ARGUMENTS eps, STARTPACK true, BORROWED true, SELECTION eps}
$generator_operation_valid(S_body, pgeneratorop_source)
$generator_operation_nodes(pgeneratorop_source) = eps
$generator_operation_trace(S_body, pgeneratorop_source) = eps
$call_context_roots((pcallcontext_source)) = eps
$config_generator_argument_nodes(pconfiggenerator) = [HOBJECT n_prefix, HOBJECT n_cache, HOBJECT n_cache, HOBJECT n_cache]
$task_nodes(CONFIG_GENERATOR pconfiggenerator "next") = [HOBJECT n_source, HOBJECT n_prefix, HOBJECT n_cache, HOBJECT n_cache, HOBJECT n_cache, HOBJECT n_target]
$heap_owners($heap_graph(S_body), HOBJECT n_prefix) = 1
$heap_owners($heap_graph(S_body), HOBJECT n_cache) = 4
$heap_owners($heap_graph(S_body), HOBJECT n_source) = 2
$heap_owners($heap_graph(S_body), HOBJECT n_target) = 1
S_boundary = $constant_frame_scope(S_body, pframe_source, pframe_source_tail*)
$config_generator_valid(S_boundary, pconfiggenerator, "next")
$config_traversable_prefix(S_boundary, pconfigcall)
''')
    values += public('S_body') + budget('S_body') + reach('S_error', 'S_body', 7) + lines(r'''
S_error.TODO = (THROW_SEARCH n_error) :: (GENERATOR_RESUME pgeneratorop_source) :: (CONFIG_GENERATOR pconfiggenerator "next") :: ptask_tail*
S_error.OBJECTS[n_source] = GENERATOR pgenerator_closed
pgenerator_closed.PHASE = GENERATOR_CLOSED
pgenerator_closed.FRAME = eps
pgenerator_closed.VALUE = (POBJECT n_cache)
$object_name(S_error, n_error) = $ptascii("Exception")
$string_bytes($throwable_field(S_error, n_error, "message")) = ($ptascii("source"))
$throwable_field(S_error, n_error, "previous") = PNULL
$throwable_field(S_error, n_error, "trace") = PARRAY n_trace
S_error.ARRAYS[n_trace].ITEMS = [ENTRY (KINT 0) (DIRECT (PARRAY n_source_trace)), ENTRY (KINT 1) (DIRECT (PARRAY n_caller_trace))]
$trace_array_field(S_error, n_source_trace, $ptascii("function")) = PSTRING $ptascii("source129G")
$trace_array_field(S_error, n_caller_trace, $ptascii("function")) = PSTRING $ptascii("run129G")
PhpStep: S_error ~> S_cursor
S_cursor.TODO = (THROW_SEARCH n_error) :: (CONFIG_GENERATOR pconfiggenerator "next") :: ptask_tail*
S_popped = S_cursor[.TODO = (THROW_SEARCH n_error) :: ptask_tail*]
$heap_owners($heap_graph(S_popped), HOBJECT n_target) = 0
$heap_owners($heap_graph(S_popped), HOBJECT n_prefix) = 0
$heap_owners($heap_graph(S_popped), HOBJECT n_cache) = 1
$generator_source_discard_state(S_popped, pconfiggenerator, "next") = (S_hold)
$config_pack_prefix(pconfigcall, pconfiggenerator.ITEMS, false) = (pconfigcall_full)
pconfigcall_copied = pconfigcall_full[.INDEX = 3]
|pconfigcall_copied.SENT| = 5
S_hold.TODO = (THROW_SEARCH n_error) :: (CONFIG_INVOKE pconfigcall_copied) :: ptask_tail*
$config_nodes(pconfigcall_copied) = [HOBJECT n_target, HOBJECT n_prefix, HOBJECT n_cache, HOBJECT n_cache, HOBJECT n_cache]
$heap_owners($heap_graph(S_hold), HOBJECT n_prefix) = 1
$heap_owners($heap_graph(S_hold), HOBJECT n_cache) = 4
$heap_owners($heap_graph(S_hold), HOBJECT n_target) = 1
~$destructor_operational(S_cursor)
PhpStep: S_cursor ~> S_staged
S_staged = S_hold
''')
    values += public('S_error') + public('S_staged') + budget('S_cursor') + reach('S_cached', 'S_staged', 8) + lines(r'''
$heap_owners($heap_graph(S_cached), HOBJECT n_prefix) = 0
$heap_owners($heap_graph(S_cached), HOBJECT n_target) = 0
$heap_owners($heap_graph(S_cached), HOBJECT n_source) = 1
$heap_owners($heap_graph(S_cached), HOBJECT n_cache) = 1
~((HOBJECT n_prefix) <- S_cached.ALLOCATIONS)
~((HOBJECT n_target) <- S_cached.ALLOCATIONS)
S_cached.OBJECTS[n_source] = GENERATOR pgenerator_closed
''')
    return values + public('S_cached')


def count_checks():
    values = prefix_header('current') + reach('S_ready', 'S', 2) + lines(r'''
S_ready.TODO = (CONFIG_ITERATOR pconfigiterator_ready "ready") :: ptask_tail*
pconfigiterator_ready.CALL = pconfigcall
pconfigiterator_ready.OBJECT = n_data
pconfigiterator_ready.ITEMS = [ENTRY (KINT 0) (DIRECT (POBJECT n_first)), ENTRY (KINT 1) (DIRECT (POBJECT n_middle)), ENTRY (KINT 2) (DIRECT (POBJECT n_last))]
$config_iterator_argument_nodes(pconfigiterator_ready) = [HOBJECT n_prefix, HOBJECT n_first, HOBJECT n_middle, HOBJECT n_last]
$heap_owners($heap_graph(S_ready), HOBJECT n_target) = 1
$heap_owners($heap_graph(S_ready), HOBJECT n_prefix) = 1
$heap_owners($heap_graph(S_ready), HOBJECT n_first) = 1
$heap_owners($heap_graph(S_ready), HOBJECT n_middle) = 1
$heap_owners($heap_graph(S_ready), HOBJECT n_last) = 1
$heap_owners($heap_graph(S_ready), HOBJECT n_data) = 0
''')
    values += public('S_ready') + dispatch('S_ready', ['POBJECT n_prefix', 'POBJECT n_first', 'POBJECT n_middle', 'POBJECT n_last'], 'current') + budget('S_args') + lines(r'''
pconfigcall_copied.INDEX = 2
|pconfigcall_copied.SENT| = 4
PhpStep: S_args ~> S_count
S_count.COMPLETION = THROWING n_error
S_count.TODO = ptask_tail*
$object_name(S_count, n_error) = $ptascii("ArgumentCountError")
$string_bytes($throwable_field(S_count, n_error, "message")) = ($ptascii("Generator::current() expects exactly 0 arguments, 4 given"))
$throwable_field(S_count, n_error, "previous") = PNULL
$throwable_field(S_count, n_error, "trace") = PARRAY n_trace
S_count.ARRAYS[n_trace].ITEMS = [ENTRY (KINT 0) (DIRECT (PARRAY n_api_trace)), ENTRY (KINT 1) (DIRECT (PARRAY n_caller_trace))]
$trace_array_field(S_count, n_api_trace, $ptascii("function")) = PSTRING $ptascii("current")
$trace_array_field(S_count, n_api_trace, $ptascii("args")) = PARRAY n_arguments
S_count.ARRAYS[n_arguments].ITEMS = [ENTRY (KINT 0) (DIRECT (POBJECT n_prefix)), ENTRY (KINT 1) (DIRECT (POBJECT n_first)), ENTRY (KINT 2) (DIRECT (POBJECT n_middle)), ENTRY (KINT 3) (DIRECT (POBJECT n_last))]
''')
    values += reach('S_released', 'S_args_one[.COMPLETION = NORMAL]', 9) + lines(r'''
$heap_owners($heap_graph(S_released), HOBJECT n_prefix) = 0
$heap_owners($heap_graph(S_released), HOBJECT n_first) = 0
$heap_owners($heap_graph(S_released), HOBJECT n_middle) = 0
$heap_owners($heap_graph(S_released), HOBJECT n_last) = 0
~((HOBJECT n_target) <- S_released.ALLOCATIONS)
''')
    return values + public('S_released')


def scalar_checks():
    values = reach('S', 'S_initial', 1) + lines(r'''
S.TODO = (CONFIG_UNPACK_PREP pconfigcall) :: ptask_tail*
pconfigcall.KIND = INTRINSIC_GENERATOR_METHOD "send" eps
pconfigcall.OWNER = (n_target)
pconfigcall.SITE = porigin_call
pconfigcall.LINE = z_call
pconfigcall.INDEX = 1
pconfigcall.SENT = [NAMED_SENT (KNOWN (PINT 17))]
$config_traversable_prefix(S, pconfigcall)
''')
    values += reach('S_ready', 'S', 2) + lines(r'''
S_ready.TODO = (CONFIG_ITERATOR pconfigiterator_ready "ready") :: ptask_tail*
pconfigiterator_ready.CALL = pconfigcall
pconfigiterator_ready.ITEMS = eps
$config_iterator_argument_nodes(pconfigiterator_ready) = eps
$heap_owners($heap_graph(S_ready), HOBJECT n_target) = 1
''')
    return values + public('S_ready') + budget('S_ready') + dispatch('S_ready', ['PINT 17'], 'send') + lines(r'''
pconfigcall_copied.INDEX = 2
|pconfigcall_copied.SENT| = 1
''') + budget('S_args')


def checks(name, program, path):
    encoded = json.dumps(base64.b64encode(os.fsencode(path)).decode())
    initial = ['S_initial = $php_run(' + program + ', 0, ' + encoded + ')',
        'S_initial.COMPLETION = BUDGET']
    functions = {
        'i129-computed-prefix-empty-iterator-send': iterator_checks,
        'i129-aggregate-prefix-mapping-cleanup': aggregate_checks,
        'i129-nullsafe-prefix-generator-source-throw-cache': generator_checks,
        'i129-iterator-prefix-owning-count-trace': count_checks,
        'i129-scalar-prefix-empty-iterator-send': scalar_checks,
    }
    return initial + functions[name]()


def run(out=None, process_seconds=600):
    catalog = {row['id']: row for row in json.loads(CATALOG.read_bytes())}
    rows = [catalog[name] for name in EXPECTED]
    out = Path(out) if out else Path(tempfile.mkdtemp(prefix='generator-prefixed-traversable-arguments-state-', dir=ROOT / '.tools'))
    out.mkdir(parents=True, exist_ok=True)
    environment = dict(os.environ, LC_ALL='C', TZ='UTC')
    environment.pop('PHP_SPEC_SCRIPT_ENCODING', None)
    modules = [ROOT / name for name in json.loads((ROOT / 'spec/semantics/modules.json').read_bytes())]
    records = []
    for row in rows:
        assert row['source_sha256'] == EXPECTED[row['id']]
        assert hashlib.sha256(row['source'].encode()).hexdigest() == row['source_sha256']
        directory = out / row['id']; directory.mkdir()
        source = directory / 'source.php'; source.write_text(row['source'])
        frontend = Worker([str(ROOT / '.tools/php/bin/php'), '-n', '-d', 'extension=' + str(ROOT / '.tools/php-file.so'), str(ROOT / 'frontend/worker.php')], directory / 'frontend')
        try:
            parsed = frontend.request({'op': 'parse', 'source': base64.b64encode(source.read_bytes()).decode()})
            assert parsed['accepted']
        finally:
            frontend.close()
        adapter = Worker([str(ROOT / '_build/default/adapter/main.exe'), str(ROOT)], directory / 'adapter')
        try:
            checked = adapter.request({'op': 'check', 'ast': parsed['ast'], 'fixture': True})
            assert checked['ok']
        finally:
            adapter.close()
        conditions = checks(row['id'], checked['fixture'], source)
        fixture = directory / 'test.watsup'
        fixture.write_text(PREFIX + '\ndec $main() : bool\ndef $main() = true\n' + ''.join(
            '  -- ' + (condition if condition.startswith('PhpStep:') else 'if ' + condition) + '\n'
            for condition in conditions))
        (directory / 'assertions.json').write_text(json.dumps(conditions, indent=2) + '\n')
        process = recorded([ROOT / 'tests/semantics/_build/default/numeric_runner.exe', '--sl', *modules, fixture], directory, 'model', environment, process_seconds)
        passed = not process['timeout'] and process['exit'] == 0 and (directory / 'model.stdout').read_bytes() == b'true\n' and (directory / 'model.stderr').read_bytes() == b''
        records.append({'id': row['id'], 'source_sha256': row['source_sha256'], 'assertions': len(conditions), 'process': process, 'passed': passed})
        print(row['id'], len(conditions), 'PASS' if passed else 'FAIL', flush=True)
        if not passed:
            break
    report = {'revision': subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip(), 'selection': list(EXPECTED), 'records': records, 'passed': len(records) == len(rows) and all(row['passed'] for row in records)}
    (out / 'raw-report.json').write_text(json.dumps(report, indent=2) + '\n')
    return report['passed']


if __name__ == '__main__':
    raise SystemExit(0 if run() else 1)
