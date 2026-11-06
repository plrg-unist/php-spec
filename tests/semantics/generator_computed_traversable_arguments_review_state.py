#!/usr/bin/env python3
"""Check frozen computed selections through actual Traversable argument cursors."""
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
CATALOG = Path(__file__).with_name('generator_computed_traversable_arguments_review_cases.json')
EXPECTED = {
    'i127-computed-iterator-rebinding': '81f8735a5d7e4e38a24391bc33624edb424385bb9025a0756a6e4b5b1ade1bb4',
    'i127-nullsafe-computed-aggregate-body-type': 'd12f691e379b845d6adab535c1d10b907466e0f97f2e66b1bbf9e7df75be3f9d',
    'i127-computed-generator-count': '008ccf942955c33fa1e3b1bcaef2cd2ab4f3adce3eb9640f87cff9c786a02b55',
    'i127-computed-iterator-mapping': '241cd01ec71282fee508810a5392136240ef4f2b720ee3a33b64521d401d7812',
}
PREFIX = r'''
dec $test_i127_front(pstate, nat) : bool
def $test_i127_front(S, 0) = true
  -- if S.TODO = (METHOD_NAME poperand phpType7* z) :: ptask*
def $test_i127_front(S, 1) = true
  -- if S.TODO = (CONFIG_UNPACK_PREP pconfigcall) :: ptask*
  -- if pconfigcall.KIND = INTRINSIC_GENERATOR_METHOD text (pgeneratormethodselection)
def $test_i127_front(S, 2) = true
  -- if S.TODO = (CONFIG_ITERATOR pconfigiterator "send") :: ptask*
def $test_i127_front(S, 3) = true
  -- if S.TODO = (CONFIG_ITERATOR pconfigiterator "ready") :: ptask*
  -- if ~((HOBJECT pconfigiterator.OBJECT) <- S.ALLOCATIONS)
def $test_i127_front(S, 4) = true
  -- if S.TODO = (RETURN_VALUE z) :: ptask*
  -- if S.CURRENT = (pcallcontext)
  -- if pcallcontext.TARGET = AGGREGATE_METHOD_TARGET n porigin
def $test_i127_front(S, 5) = true
  -- if S.TODO = (CONFIG_AGGREGATE pconfigaggregate) :: ptask*
  -- if S.RESULT = KNOWN (POBJECT n)
def $test_i127_front(S, 6) = true
  -- if S.TODO = (STMT (NStmtEcho (SEQUENCE ((NScalarString (BYTES text) metadata_string) :: expression_tail*)) metadata)) :: ptask*
  -- if $base64(text) = $ptascii("HELD|")
def $test_i127_front(S, 7) = true
  -- if S.TODO = (CONFIG_GENERATOR pconfiggenerator "finish") :: ptask*
def $test_i127_front(S, 8) = true
  -- if S.TODO = (CONFIG_GENERATOR pconfiggenerator "invoke") :: ptask*
def $test_i127_front(S, 9) = true
  -- if S.TODO = (THROW_SEARCH n) :: (GENERATOR_RESUME pgeneratorop) :: ptask*
  -- if pgeneratorop.NAME = "send" /\ ~pgeneratorop.BORROWED
  -- if S.OBJECTS[pgeneratorop.OBJECT] = GENERATOR pgenerator
  -- if pgenerator.PHASE = GENERATOR_CLOSED
def $test_i127_front(S, 10) = true
  -- if S.TODO = (THROW_SEARCH n) :: (CONFIG_ITERATOR pconfigiterator "send") :: ptask*
  -- if pconfigiterator.CALL.KIND = INTRINSIC_GENERATOR_METHOD "send" (pgeneratormethodselection)
def $test_i127_front(S, n_stage) = false -- otherwise
dec $test_i127_seek(pstate, nat, nat) : pstate
def $test_i127_seek(S, n_stage, 0) = S
def $test_i127_seek(S, n_stage, n) = S
  -- if $(n > 0)
  -- if $test_i127_front(S, n_stage) \/ (S.COMPLETION =/= NORMAL /\ S.COMPLETION =/= BUDGET) \/ (S.TODO = eps /\ S.CURRENT = eps /\ S.FRAMES = eps)
def $test_i127_seek(S, n_stage, n) = $test_i127_seek($drive_steps(S[.COMPLETION = NORMAL], 1), n_stage, $nabs($(n - 1)))
  -- if $(n > 0)
  -- if ~$test_i127_front(S, n_stage)
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
  -- if ~(S.TODO = eps /\ S.CURRENT = eps /\ S.FRAMES = eps)
'''


def lines(text):
    return [line.strip() for line in text.splitlines() if line.strip()]


def reach(state, start, stage):
    return [state + '_found = $test_i127_seek(' + start + ', ' + str(stage) + ', 4000)',
        state + r'_found.COMPLETION = NORMAL \/ ' + state + '_found.COMPLETION = BUDGET',
        state + ' = ' + state + '_found[.COMPLETION = NORMAL]',
        '$test_i127_front(' + state + ', ' + str(stage) + ')']


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


def selected_checks(method):
    return reach('S_name', 'S_initial', 0) + lines(r'''
S_name.TODO = (METHOD_NAME poperand phpType7* z_call) :: ptask_name_tail*
S_name.ORIGIN = (porigin_call)
$method_name_task(S_name, poperand, phpType7*, z_call)
$generator_computed_method_node($origin_node(S_name.SOURCES, porigin_call))
S_name.RESULT = VARIABLE $ptascii("method") z_name
S_method = $resolve_at(S_name, S_name.RESULT, z_call)
S_method.COMPLETION = NORMAL
S_method.RESULT = KNOWN pvalue_method
$string_bytes(pvalue_method) = (ptbytes_method)
S_lookup = $resolve_at(S_name, poperand, z_call)
S_lookup.COMPLETION = NORMAL
S_lookup.RESULT = KNOWN (POBJECT n_target)
$lookup(S_name.ENV, $ptascii("target")) = (n_target_cv)
S_name.STORE[n_target_cv] = DEFINED (POBJECT n_target)
$lookup(S_name.ENV, $ptascii("method")) = (n_method_cv)
S_name.STORE[n_method_cv] = DEFINED pvalue_method
pgeneratormethodselection = {SITE porigin_call, OBJECT n_target, NAME ptbytes_method, LINE z_call, CAPTURE eps, TEMPORARY false}
$generator_method_selection(S_method, poperand, ptbytes_method, phpType7*, z_call) = (pgeneratormethodselection)
$heap_owners($heap_graph(S_name), HOBJECT n_target) = 1
PhpStep: S_name ~> S_frozen
S_frozen.TODO = (CONFIG_ARGS pconfigcall) :: $generator_method_return_tasks(S_name, porigin_call, ptask_name_tail*)
pconfigcall.OWNER = (n_target)
pconfigcall.SITE = porigin_call
pconfigcall.LINE = z_call
pconfigcall.INDEX = 0
pconfigcall.SENT = eps
~pconfigcall.NAMED
pconfigcall.PACKS = eps
pconfigcall.SELECTION = eps
S_frozen.STORE = S_name.STORE
S_frozen.ALLOCATIONS = S_name.ALLOCATIONS
S_frozen.EVENTS = S_name.EVENTS
$config_nodes(pconfigcall) = [HOBJECT n_target]
$heap_owners($heap_graph(S_frozen), HOBJECT n_target) = 2
$call_task_valid(S_frozen, CONFIG_ARGS pconfigcall)
~$call_task_valid(S_frozen, CONFIG_ARGS pconfigcall[.LINE = $(z_call + 1)])
''') + [
        '$generator_method(ptbytes_method) = "' + method + '"',
        'pconfigcall.KIND = INTRINSIC_GENERATOR_METHOD "' + method + '" (pgeneratormethodselection)',
        '~$call_task_valid(S_frozen, CONFIG_ARGS pconfigcall[.KIND = INTRINSIC_GENERATOR_METHOD "' + method + '" eps])',
        '~$call_task_valid(S_frozen, CONFIG_ARGS pconfigcall[.KIND = INTRINSIC_GENERATOR_METHOD "' + method + '" (pgeneratormethodselection[.OBJECT = $(n_target + 1)])])',
        '~$call_task_valid(S_frozen, CONFIG_ARGS pconfigcall[.KIND = INTRINSIC_GENERATOR_METHOD "' + method + '" (pgeneratormethodselection[.NAME = $ptascii("throw")])])',
        '~$call_task_valid(S_frozen, CONFIG_ARGS pconfigcall[.KIND = INTRINSIC_GENERATOR_METHOD "' + method + '" (pgeneratormethodselection[.LINE = $(z_call + 1)])])',
        *public('S_frozen'), *reach('S', 'S_frozen', 1)]


def input_checks(name):
    return lines(r'''
S.TODO = (CONFIG_UNPACK_PREP pconfigcall) :: ptask_tail*
$intrinsic_argument(S, porigin_call, 0) = ((expression_input, true, eps, porigin_input, z_input))
$generator_iterator_site(S, pconfigcall)
$heap_owners($heap_graph(S), HOBJECT n_target) = 2
S.OBJECTS[n_target] = GENERATOR pgenerator_target
pgenerator_target.PHASE = GENERATOR_PAUSED
~pgenerator_target.PENDING_INIT
pgenerator_target.DELEGATE = eps
''') + [
        'S.RESULT = VARIABLE $ptascii("' + name + '") z_input',
        '$lookup(S.ENV, $ptascii("' + name + '")) = (n_input_cv)',
        'S.STORE[n_input_cv] = DEFINED (POBJECT n_input)',
        '$heap_owners($heap_graph(S), HOBJECT n_input) = 1',
        *public('S')]


def collected_checks(method):
    # Selection minting is checked once above; the other producers keep its
    # actual runtime certificate at their first argument-read continuation.
    return reach('S', 'S_initial', 1) + lines(r'''
S.TODO = (CONFIG_UNPACK_PREP pconfigcall) :: ptask_tail*
pconfigcall.OWNER = (n_target)
pconfigcall.SITE = porigin_call
pconfigcall.LINE = z_call
pconfigcall.INDEX = 0
pconfigcall.SENT = eps
pconfigcall.PACKS = eps
pconfigcall.SELECTION = eps
$lookup(S.ENV, $ptascii("target")) = (n_target_cv)
S.STORE[n_target_cv] = DEFINED (POBJECT n_target)
$lookup(S.ENV, $ptascii("method")) = (n_method_cv)
''') + [
        'pconfigcall.KIND = INTRINSIC_GENERATOR_METHOD "' + method + '" (pgeneratormethodselection)',
        'pgeneratormethodselection.NAME = $ptascii("' + method + '")',
        'S.STORE[n_method_cv] = DEFINED (PSTRING_CARRIER INTERNED_STRING $ptascii("' + method + '"))']


def dispatch_checks(state, value, method):
    return [
        state + '.TODO = (CONFIG_INVOKE pconfigcall_copied) :: ptask_tail*',
        'pconfigcall_copied = pconfigcall[.INDEX = 1][.SENT = [NAMED_SENT (KNOWN (' + value + '))]]',
        '$config_invoke_valid(' + state + ', pconfigcall_copied)',
        'PhpStep: ' + state + ' ~> S_args',
        'S_args.TODO = (GENERATOR_ARGS pgeneratorop eps ([KNOWN (' + value + ')])) :: ptask_tail*',
        'pgeneratorop.OBJECT = n_target', 'pgeneratorop.NAME = "' + method + '"',
        'pgeneratorop.SELECTION = (pgeneratormethodselection)',
        'pgeneratorop.SITE = porigin_call', 'pgeneratorop.LINE = z_call',
        'pgeneratorop.ARGUMENTS = eps', 'pgeneratorop.LOOP = eps',
        '~pgeneratorop.ADVANCE', '~pgeneratorop.STARTPACK', '~pgeneratorop.BORROWED',
        '$task_nodes(GENERATOR_ARGS pgeneratorop eps ([KNOWN (' + value + ')])) = $config_nodes(pconfigcall_copied)',
        'S_args.STORE = ' + state + '.STORE', 'S_args.ALLOCATIONS = ' + state + '.ALLOCATIONS',
        'S_args.EVENTS = ' + state + '.EVENTS',
        '$heap_owners($heap_graph(S_args), HOBJECT n_target) = 1',
        *public('S_args')]


def iterator_checks():
    values = selected_checks('send') + input_checks('pack') + lines(r'''
$config_iterator_start(S, pconfigcall, S.RESULT, n_input)
S_fresh = S[.OBJECTS[n_target] = GENERATOR pgenerator_target[.PHASE = GENERATOR_FRESH]]
~$config_iterator_start(S_fresh, pconfigcall, S_fresh.RESULT, n_input)
S_pending = S[.OBJECTS[n_target] = GENERATOR pgenerator_target[.PENDING_INIT = true]]
~$config_iterator_start(S_pending, pconfigcall, S_pending.RESULT, n_input)
~$generator_iterator_site(S, pconfigcall[.KIND = INTRINSIC_GENERATOR_METHOD "throw" (pgeneratormethodselection[.NAME = $ptascii("throw")])])
S.OBJECTS[n_input] = INSTANCE porigin_data
$class_at(S.CLASSES, porigin_data) = (pclassdesc_data)
pmethoddesc_current = pclassdesc_data.METHODS[3]
pmethoddesc_current.NAME = $ptascii("current")
pmethoddesc_reference = pmethoddesc_current[.FUNCTION = pmethoddesc_current.FUNCTION[.SIGNATURE = pmethoddesc_current.FUNCTION.SIGNATURE[.BYREF = true]]]
S_reference = S[.CLASSES = $trait_class_set(S.CLASSES, pclassdesc_data[.METHODS[3] = pmethoddesc_reference])]
$effective_method(S_reference, porigin_data, $ptascii("current"), |S_reference.CLASSES|) = (pmethoddesc_reference)
~$generator_aggregate_current(S_reference, n_input)
~$config_iterator_start(S_reference, pconfigcall, S_reference.RESULT, n_input)
PhpStep: S ~> S_data
S_data.TODO = (CONFIG_ITERATOR pconfigiterator_initial "rewind-start") :: ptask_tail*
pconfigiterator_initial.CALL = pconfigcall
pconfigiterator_initial.OBJECT = n_input
pconfigiterator_initial.INPUT = S.RESULT
pconfigiterator_initial.PRODUCER = eps
$task_nodes(CONFIG_ITERATOR pconfigiterator_initial "rewind-start") = [HOBJECT n_input, HOBJECT n_target]
$heap_owners($heap_graph(S_data), HOBJECT n_input) = 2
''')
    values += reach('S_send', 'S_data', 2) + lines(r'''
S_send.TODO = (CONFIG_ITERATOR pconfigiterator_send "send") :: ptask_tail*
pconfigiterator_send.CALL = pconfigcall
pconfigiterator_send.OBJECT = n_input
pconfigiterator_send.CURRENT = KNOWN (POBJECT n_token)
pconfigiterator_send.KEY = KNOWN (PINT 0)
pconfigiterator_send.ITEMS = eps
S_send.STORE[n_target_cv] = DEFINED (POBJECT n_other)
n_other =/= n_target
S_send.STORE[n_method_cv] = DEFINED (PSTRING_CARRIER INTERNED_STRING $ptascii("next"))
S_send.STORE[n_input_cv] = DEFINED PNULL
$objectprops_record_at(S_send.OBJECTPROPS, n_input) = (pobjectprops_data)
$property_slot_at(pobjectprops_data.SLOTS, $ptascii("value")) = (ppropertyslot_value)
ppropertyslot_value.STATE = PROP_VALUE (DIRECT (PINT 17))
$object_name(S_send, n_token) = $ptascii("Token127I")
$generator_selected_method(S_send, porigin_call, n_target, ptbytes_method, z_call, (pgeneratormethodselection))
$config_iterator_valid(S_send, pconfigiterator_send, "send")
$heap_owners($heap_graph(S_send), HOBJECT n_target) = 1
$heap_owners($heap_graph(S_send), HOBJECT n_input) = 1
$heap_owners($heap_graph(S_send), HOBJECT n_token) = 1
''')
    values += public('S_send') + budget('S_send') + reach('S_ready', 'S_send_one[.COMPLETION = NORMAL]', 3) + lines(r'''
S_ready.TODO = (CONFIG_ITERATOR pconfigiterator_ready "ready") :: ptask_tail*
pconfigiterator_ready.CALL = pconfigcall
pconfigiterator_ready.ITEMS = [ENTRY (KINT 0) (DIRECT (POBJECT n_token))]
~((HOBJECT n_input) <- S_ready.ALLOCATIONS)
$config_iterator_valid(S_ready, pconfigiterator_ready, "ready")
$task_nodes(CONFIG_ITERATOR pconfigiterator_ready "ready") = [HOBJECT n_target, HOBJECT n_token]
PhpStep: S_ready ~> S_invoke
''')
    return values + public('S_ready') + budget('S_ready') + dispatch_checks('S_invoke', 'POBJECT n_token', 'send')


def aggregate_checks():
    values = collected_checks('send') + input_checks('pack') + lines(r'''
ptask_tail* = METHOD_RESULT :: ptask_after*
$task_nodes(METHOD_RESULT) = eps
$config_aggregate_start(S, pconfigcall, S.RESULT, n_input)
PhpStep: S ~> S_getter
S_getter.TODO = (CALL_ARGS pcalltarget eps 0 eps (porigin_input) z_input) :: (CONFIG_AGGREGATE pconfigaggregate) :: ptask_tail*
pconfigaggregate = {CALL pconfigcall, OBJECT n_input, INPUT S.RESULT}
pcalltarget = AGGREGATE_METHOD_TARGET n_input porigin_method
$target_nodes(pcalltarget) = eps
$target_instance(pcalltarget) = eps
$task_nodes(CONFIG_AGGREGATE pconfigaggregate) = [HOBJECT n_target]
''')
    values += reach('S_get', 'S_getter', 4) + lines(r'''
S_get.CURRENT = (pcallcontext_get)
pcallcontext_get.TARGET = pcalltarget
pcallcontext_get.RECEIVER = (n_input)
$call_context_roots((pcallcontext_get)) = eps
S_get.FRAMES = pframe_get :: pframe_get_tail*
pframe_get.TODO = (CONFIG_AGGREGATE pconfigaggregate) :: ptask_tail*
$config_aggregate_frame(S_get, pcallcontext_get, pframe_get)
$heap_owners($heap_graph(S_get), HOBJECT n_input) = 1
$heap_owners($heap_graph(S_get), HOBJECT n_target) = 2
S_get_scope = $constant_frame_scope(S_get, pframe_get, pframe_get_tail*)
S_get_scope.ORIGIN = (porigin_input)
$call_task_valid(S_get_scope, CONFIG_AGGREGATE pconfigaggregate)
S_get_after = $call_after_origin(S_get_scope, CONFIG_AGGREGATE pconfigaggregate)
S_get_after = S_get_scope[.ORIGIN = (pconfigcall.SITE)]
$call_task_valid(S_get_after, METHOD_RESULT)
''')
    values += public('S_get') + budget('S_get') + reach('S_return', 'S_get', 5) + lines(r'''
S_return.TODO = (CONFIG_AGGREGATE pconfigaggregate) :: ptask_tail*
S_return.RESULT = KNOWN (POBJECT n_data)
$config_aggregate_iterator_admitted(S_return, pconfigaggregate, n_data)
$config_aggregate_return_allowed(S_return, pconfigaggregate)
$heap_owners($heap_graph(S_return), HOBJECT n_data) = 1
PhpStep: S_return ~> S_data
S_data.TODO = (CONFIG_ITERATOR pconfigiterator_initial "rewind-start") :: ptask_tail*
pconfigiterator_initial.CALL = pconfigcall
pconfigiterator_initial.OBJECT = n_data
pconfigiterator_initial.PRODUCER = (n_input)
$task_nodes(CONFIG_ITERATOR pconfigiterator_initial "rewind-start") = [HOBJECT n_data, HOBJECT n_target]
''')
    values += reach('S_send', 'S_data', 2) + lines(r'''
S_send.TODO = (CONFIG_ITERATOR pconfigiterator_send "send") :: ptask_tail*
pconfigiterator_send.CALL = pconfigcall
pconfigiterator_send.OBJECT = n_data
pconfigiterator_send.PRODUCER = (n_input)
pconfigiterator_send.CURRENT = KNOWN (POBJECT n_token)
S_send.STORE[n_target_cv] = DEFINED PNULL
S_send.STORE[n_method_cv] = DEFINED (PSTRING_CARRIER INTERNED_STRING $ptascii("valid"))
S_send.STORE[n_input_cv] = DEFINED PNULL
~((HOBJECT n_input) <- S_send.ALLOCATIONS)
$config_iterator_producer_valid(S_send, pconfigiterator_send)
$config_iterator_valid(S_send, pconfigiterator_send, "send")
$heap_owners($heap_graph(S_send), HOBJECT n_target) = 1
$heap_owners($heap_graph(S_send), HOBJECT n_data) = 1
$heap_owners($heap_graph(S_send), HOBJECT n_token) = 1
''')
    values += public('S_send') + budget('S_send') + reach('S_ready', 'S_send_one[.COMPLETION = NORMAL]', 3) + lines(r'''
S_ready.TODO = (CONFIG_ITERATOR pconfigiterator_ready "ready") :: ptask_tail*
pconfigiterator_ready.CALL = pconfigcall
~((HOBJECT n_data) <- S_ready.ALLOCATIONS)
~((HOBJECT n_input) <- S_ready.ALLOCATIONS)
$config_iterator_valid(S_ready, pconfigiterator_ready, "ready")
PhpStep: S_ready ~> S_invoke
''')
    values += public('S_ready') + budget('S_ready') + dispatch_checks('S_invoke', 'POBJECT n_token', 'send')
    values += reach('S_closed', 'S_args', 9) + lines(r'''
S_closed.TODO = (THROW_SEARCH n_error) :: (GENERATOR_RESUME pgeneratorop_closed) :: ptask_tail*
pgeneratorop_closed = pgeneratorop[.ARGUMENTS = [POBJECT n_token]]
S_closed.OBJECTS[n_target] = GENERATOR pgenerator_closed
pgenerator_closed.PHASE = GENERATOR_CLOSED
pgenerator_closed.FRAME = eps
$generator_api_body_throw(S_closed, pgeneratorop_closed)
$object_name(S_closed, n_error) = $ptascii("TypeError")
$throwable_field(S_closed, n_error, "previous") = PNULL
$throwable_field(S_closed, n_error, "trace") = PARRAY n_trace
|S_closed.ARRAYS[n_trace].ITEMS| = 4
$heap_owners($heap_graph(S_closed), HOBJECT n_target) = 1
$heap_owners($heap_graph(S_closed), HOBJECT n_token) = 3
$lookup(S_closed.ENV, $ptascii("result")) = (n_result_cv)
S_closed.STORE[n_result_cv] = DEFINED (PSTRING_CARRIER INTERNED_STRING $ptascii("sentinel"))
''')
    return values + public('S_closed') + budget('S_closed')


def generator_checks():
    values = collected_checks('current') + input_checks('source') + lines(r'''
S.OBJECTS[n_input] = GENERATOR pgenerator_source
pgenerator_source.PHASE = GENERATOR_PAUSED
pgenerator_source.FIRST
pgenerator_source.REFCELL = eps
pgenerator_source.VALUE = (PINT 17)
$config_generator_start(S, pconfigcall, S.RESULT, n_input)
PhpStep: S ~> S_data
S_data.TODO = (CONFIG_GENERATOR pconfiggenerator_initial "rewind") :: ptask_tail*
pconfiggenerator_initial = {CALL pconfigcall, OBJECT n_input, INPUT S.RESULT, ITEMS eps, PRODUCER eps}
$heap_owners($heap_graph(S_data), HOBJECT n_input) = 2
$task_nodes(CONFIG_GENERATOR pconfiggenerator_initial "rewind") = [HOBJECT n_input, HOBJECT n_target]
PhpStep: S_data ~> S_ready
S_ready.TODO = (CONFIG_GENERATOR pconfiggenerator_initial "ready") :: ptask_tail*
PhpStep: S_ready ~> S_copied
S_copied.TODO = (CONFIG_GENERATOR pconfiggenerator_copied "next") :: ptask_tail*
pconfiggenerator_copied = pconfiggenerator_initial[.ITEMS = [ENTRY (KINT 0) (DIRECT (PINT 17))]]
''')
    values += reach('S_body', 'S_copied', 6) + lines(r'''
S_body.CURRENT = (pcallcontext_source)
pcallcontext_source.RECEIVER = eps
$call_context_roots((pcallcontext_source)) = eps
S_body.FRAMES = pframe_source :: pframe_source_tail*
pframe_source.TODO = (GENERATOR_RESUME pgeneratorop_source) :: (CONFIG_GENERATOR pconfiggenerator_copied "next") :: ptask_tail*
pgeneratorop_source = {OBJECT n_input, NAME "next", SITE porigin_input, LINE z_input, LOOP eps, ADVANCE false, ARGUMENTS eps, STARTPACK true, BORROWED true, SELECTION eps}
$generator_operation_valid(S_body, pgeneratorop_source)
$generator_operation_nodes(pgeneratorop_source) = eps
$generator_operation_trace(S_body, pgeneratorop_source) = eps
S_body.OBJECTS[n_input] = GENERATOR pgenerator_running
pgenerator_running.PHASE = GENERATOR_RUNNING
pgenerator_running.FRAME = eps
S_body.STORE[n_target_cv] = DEFINED PNULL
S_body.STORE[n_method_cv] = DEFINED (PSTRING_CARRIER INTERNED_STRING $ptascii("send"))
S_body.STORE[n_input_cv] = DEFINED PNULL
$heap_owners($heap_graph(S_body), HOBJECT n_target) = 1
$heap_owners($heap_graph(S_body), HOBJECT n_input) = 1
S_boundary = $constant_frame_scope(S_body, pframe_source, pframe_source_tail*)
$config_generator_valid(S_boundary, pconfiggenerator_copied, "next")
''')
    values += public('S_body') + budget('S_body') + reach('S_finish', 'S_body', 7) + lines(r'''
S_finish.TODO = (CONFIG_GENERATOR pconfiggenerator_copied "finish") :: ptask_tail*
S_finish.OBJECTS[n_input] = GENERATOR pgenerator_closed
pgenerator_closed.PHASE = GENERATOR_CLOSED
$config_generator_quiet_closed(S_finish, pconfiggenerator_copied)
$generator_source_live_callee(S_finish, pconfiggenerator_copied)
$heap_owners($heap_graph(S_finish), HOBJECT n_target) = 1
$heap_owners($heap_graph(S_finish), HOBJECT n_input) = 1
~$destructor_operational(S_finish)
''')
    values += public('S_finish') + budget('S_finish') + lines(r'''
S_finish_one.TODO = (CONFIG_GENERATOR pconfiggenerator_copied "invoke") :: ptask_tail*
~((HOBJECT n_input) <- S_finish_one.ALLOCATIONS)
$heap_owners($heap_graph(S_finish_one), HOBJECT n_input) = 0
$heap_owners($heap_graph(S_finish_one), HOBJECT n_target) = 1
''')
    values += reach('S_invoke', 'S_finish_one[.COMPLETION = NORMAL]', 8) + lines(r'''
S_invoke.TODO = (CONFIG_GENERATOR pconfiggenerator_copied "invoke") :: ptask_tail*
$config_generator_retired_scope(S_invoke, pconfiggenerator_copied)
PhpStep: S_invoke ~> S_call
''')
    return values + public('S_invoke') + budget('S_invoke') + dispatch_checks('S_call', 'PINT 17', 'current') + budget('S_args')


def mapping_checks():
    values = reach('S_error', 'S_initial', 10) + lines(r'''
S_error.TODO = (THROW_SEARCH n_error) :: (CONFIG_ITERATOR pconfigiterator "send") :: ptask_tail*
S_error.CURRENT = (pcallcontext_caller)
pcallcontext_caller.NAME = $ptascii("run127M")
pconfigiterator.CALL = pconfigcall
pconfigcall.KIND = INTRINSIC_GENERATOR_METHOD "send" (pgeneratormethodselection)
pconfigcall.OWNER = (n_target)
pconfigcall.INDEX = 0
pconfigcall.SENT = eps
pconfigcall.PACKS = eps
pconfigcall.SELECTION = eps
~pconfigcall.NAMED
pconfigiterator.OBJECT = n_data
pconfigiterator.PRODUCER = eps
pconfigiterator.ITEMS = eps
pconfigiterator.CURRENT = KNOWN (PINT 17)
pconfigiterator.KEY = KNOWN pvalue_key
$string_bytes(pvalue_key) = ($ptascii("extra"))
$config_iterator_valid(S_error, pconfigiterator, "send")
$config_iterator_argument_nodes(pconfigiterator) = eps
$lookup(S_error.ENV, $ptascii("target")) = (n_target_cv)
$lookup(S_error.ENV, $ptascii("pack")) = (n_pack_cv)
$lookup(S_error.ENV, $ptascii("method")) = (n_method_cv)
S_error.STORE[n_target_cv] = DEFINED PNULL
S_error.STORE[n_pack_cv] = DEFINED PNULL
S_error.STORE[n_method_cv] = DEFINED (PSTRING_CARRIER INTERNED_STRING $ptascii("key"))
$heap_owners($heap_graph(S_error), HOBJECT n_target) = 1
$heap_owners($heap_graph(S_error), HOBJECT n_data) = 1
$object_name(S_error, n_error) = $ptascii("Error")
$string_bytes($throwable_field(S_error, n_error, "message")) = ($ptascii("Unknown named parameter $extra"))
$throwable_field(S_error, n_error, "previous") = PNULL
$throwable_field(S_error, n_error, "trace") = PARRAY n_trace
S_error.ARRAYS[n_trace].ITEMS = [ENTRY (KINT 0) (DIRECT (PARRAY n_caller))]
$trace_array_field(S_error, n_caller, $ptascii("function")) = PSTRING $ptascii("run127M")
S_popped = S_error[.TODO = (THROW_SEARCH n_error) :: ptask_tail*]
$heap_owners($heap_graph(S_popped), HOBJECT n_target) = 0
$heap_owners($heap_graph(S_popped), HOBJECT n_data) = 0
pconfigcall_copied = pconfigcall[.INDEX = 1]
pconfigcall_copied.SENT = eps
$config_nodes(pconfigcall_copied) = [HOBJECT n_target]
S_hold = S_popped[.TODO = (THROW_SEARCH n_error) :: (CONFIG_INVOKE pconfigcall_copied) :: ptask_tail*][.ORIGIN = (pconfigcall.SITE)][.RESULT = KNOWN PNULL][.BASE = BASE_VALUE (KNOWN PNULL)][.ITERATORS = $iterator_remove(S_popped.ITERATORS, pconfigiterator.ITERATOR)]
$generator_iterator_cancel_state(S_popped, pconfigiterator, "send") = (S_hold)
$generator_iterator_cancel_state(S_popped, pconfigiterator, "ready") = eps
$generator_iterator_cancel_state(S_popped, pconfigiterator[.CALL = pconfigcall[.OWNER = (n_data)]], "send") = eps
pconfigiterator_owning = pconfigiterator[.ITEMS = [ENTRY (KINT 0) (DIRECT (POBJECT n_error))]]
$config_iterator_argument_nodes(pconfigiterator_owning) = [HOBJECT n_error]
$generator_iterator_cancel_state(S_popped, pconfigiterator_owning, "send") = eps
$config_invoke_valid(S_hold, pconfigcall_copied)
$heap_owners($heap_graph(S_hold), HOBJECT n_target) = 1
$heap_owners($heap_graph(S_hold), HOBJECT n_data) = 0
$config_iterator_discard_nodes(pconfigiterator, "send") = [HOBJECT n_data, HOBJECT n_target]
~$destructor_operational(S_error)
PhpStep: S_error ~> S_staged
S_staged = S_hold
$task_nodes(THROW_SEARCH n_error) = [HOBJECT n_error]
$task_nodes(CONFIG_INVOKE pconfigcall_copied) = [HOBJECT n_target]
S_staged.EVENTS = S_error.EVENTS
S_staged.OBJECTS[n_target] = GENERATOR pgenerator_target
pgenerator_target.PHASE = GENERATOR_PAUSED
''')
    values += public('S_error') + public('S_staged') + budget('S_error') + lines(r'''
S_clean = S_error_one[.COMPLETION = NORMAL]
S_clean.TODO = (THROW_SEARCH n_error) :: (CONFIG_INVOKE pconfigcall_copied) :: ptask_tail*
S_clean.CURRENT = (pcallcontext_caller)
~((HOBJECT n_data) <- S_clean.ALLOCATIONS)
$heap_owners($heap_graph(S_clean), HOBJECT n_data) = 0
$heap_owners($heap_graph(S_clean), HOBJECT n_target) = 1
$heap_owners($heap_graph(S_clean), HOBJECT n_error) = 1
S_clean.OBJECTS[n_target] = GENERATOR pgenerator_target
S_clean.EVENTS = S_error.EVENTS
$lookup(S_clean.ENV, $ptascii("weakData")) = (n_weak_cv)
S_clean.STORE[n_weak_cv] = DEFINED (POBJECT n_weak_data)
$weakref_get(S_clean, n_weak_data) = PNULL
$throwable_field(S_clean, n_error, "previous") = PNULL
$throwable_field(S_clean, n_error, "trace") = PARRAY n_trace
''')
    return values + public('S_clean') + budget('S_clean') + lines(r'''
~((HOBJECT n_data) <- S_clean_one.ALLOCATIONS)
$weakref_get(S_clean_one, n_weak_data) = PNULL
''')


def checks(name, program, path):
    encoded = json.dumps(base64.b64encode(os.fsencode(path)).decode())
    initial = ['S_initial = $php_run(' + program + ', 0, ' + encoded + ')',
        'S_initial.COMPLETION = BUDGET']
    if name == 'i127-computed-iterator-rebinding':
        return initial + iterator_checks()
    if name == 'i127-nullsafe-computed-aggregate-body-type':
        return initial + aggregate_checks()
    if name == 'i127-computed-iterator-mapping':
        return initial + mapping_checks()
    assert name == 'i127-computed-generator-count'
    return initial + generator_checks()

def run(out=None, process_seconds=600):
    catalog = {row['id']: row for row in json.loads(CATALOG.read_bytes())}
    rows = [catalog[name] for name in EXPECTED]
    out = Path(out) if out else Path(tempfile.mkdtemp(prefix='generator-computed-traversable-arguments-state-', dir=ROOT / '.tools'))
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
