#!/usr/bin/env python3
"""Check actual borrowed source resumes, DATA and native receiver/argv roots."""
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
CATALOG = Path(__file__).with_name('generator_source_arguments_review_cases.json')
EXPECTED = {
    'i126-generator-scalar-normal': '96af6c2d2b63232ccc52601f1fac5f6ed74996bc893151a5c837b4846eae662a',
    'i126-generator-retained-quiet-cache-body-type': '9b4df7165f9012f37dcd9134d5edebab723964ee97b131ab05b02e394f79b896',
    'i126-generator-mapping': '5bf69801236e99d5d6b8740ea92dcc97c22cda1f58699cef4200be184ae659f8',
}
PREFIX = r'''
dec $test_i126_echo(pstate, ptbytes) : bool
def $test_i126_echo(S, ptbytes) = true
  -- if S.TODO = (STMT (NStmtEcho (SEQUENCE ((NScalarString (BYTES text) metadata_string) :: expression_tail*)) metadata)) :: ptask*
  -- if $base64(text) = ptbytes
def $test_i126_echo(S, ptbytes) = false -- otherwise
dec $test_i126_front(pstate, nat) : bool
def $test_i126_front(S, 0) = true
  -- if S.TODO = (CONFIG_UNPACK_PREP pconfigcall) :: ptask*
  -- if pconfigcall.KIND = INTRINSIC_GENERATOR_METHOD "send" eps
def $test_i126_front(S, 1) = $test_i126_echo(S, $ptascii("HELD|"))
def $test_i126_front(S, 2) = true
  -- if S.TODO = (CONFIG_GENERATOR pconfiggenerator "finish") :: ptask*
def $test_i126_front(S, 3) = true
  -- if S.TODO = (CONFIG_GENERATOR pconfiggenerator "invoke") :: ptask*
def $test_i126_front(S, 4) = true
  -- if S.TODO = (THROW_SEARCH n) :: (GENERATOR_RESUME pgeneratorop) :: ptask*
  -- if ~pgeneratorop.BORROWED /\ ~pgeneratorop.STARTPACK
  -- if S.OBJECTS[pgeneratorop.OBJECT] = GENERATOR pgenerator
  -- if pgenerator.PHASE = GENERATOR_CLOSED
def $test_i126_front(S, 5) = $test_i126_echo(S, $ptascii("CACHED|"))
def $test_i126_front(S, 6) = true
  -- if S.TODO = (THROW_SEARCH n) :: (CONFIG_GENERATOR pconfiggenerator "ready") :: ptask*
def $test_i126_front(S, 7) = true
  -- if S.TODO = (THROW_SEARCH n) :: (CONFIG_INVOKE pconfigcall) :: ptask*
  -- if pconfigcall.KIND = INTRINSIC_GENERATOR_METHOD "send" eps
  -- if S.DESTRUCTION.OPERATIONS = eps
def $test_i126_front(S, n_stage) = false -- otherwise
dec $test_i126_seek(pstate, nat, nat) : pstate
def $test_i126_seek(S, n_stage, 0) = S
def $test_i126_seek(S, n_stage, n) = S
  -- if $(n > 0)
  -- if $test_i126_front(S, n_stage) \/ (S.COMPLETION =/= NORMAL /\ S.COMPLETION =/= BUDGET) \/ (S.TODO = eps /\ S.CURRENT = eps /\ S.FRAMES = eps)
def $test_i126_seek(S, n_stage, n) = $test_i126_seek($drive_steps(S[.COMPLETION = NORMAL], 1), n_stage, $nabs($(n - 1)))
  -- if $(n > 0)
  -- if ~$test_i126_front(S, n_stage)
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
  -- if ~(S.TODO = eps /\ S.CURRENT = eps /\ S.FRAMES = eps)
'''


def lines(text):
    return [line.strip() for line in text.splitlines() if line.strip()]


def reach(state, start, stage):
    return [state + '_found = $test_i126_seek(' + start + ', ' + str(stage) + ', 4000)',
        state + r'_found.COMPLETION = NORMAL \/ ' + state + '_found.COMPLETION = BUDGET',
        state + ' = ' + state + '_found[.COMPLETION = NORMAL]',
        '$test_i126_front(' + state + ', ' + str(stage) + ')']


def public(state):
    return ['$call_descriptors_valid(' + state + ')', '$heap_valid($heap_graph(' + state + '))']


def budget(state):
    return [state + '_pause = $drive(' + state + ', 0)',
        state + '_pause = ' + state + '[.COMPLETION = BUDGET]',
        '$call_descriptors_valid(' + state + '_pause)',
        state + '_one = $drive(' + state + ', 1)',
        state + '_one.COMPLETION = BUDGET',
        '$drive(' + state + '_pause[.COMPLETION = NORMAL], 1) = ' + state + '_one',
        *public(state + '_one')]


def invoke_checks(state, value):
    return [
        state + '.TODO = (CONFIG_GENERATOR pconfiggenerator_copied "invoke") :: ptask_tail*',
        '$config_generator_valid(' + state + ', pconfiggenerator_copied, "invoke")',
        '$heap_owners($heap_graph(' + state + '), HOBJECT n_target) = 1',
        'PhpStep: ' + state + ' ~> S_call',
        'S_call.TODO = (CONFIG_INVOKE pconfigcall_copied) :: ptask_tail*',
        'pconfigcall_copied = pconfigcall[.INDEX = 1][.SENT = [NAMED_SENT (KNOWN (' + value + '))]]',
        '$config_invoke_valid(S_call, pconfigcall_copied)',
        'PhpStep: S_call ~> S_args',
        'S_args.TODO = (GENERATOR_ARGS pgeneratorop eps ([KNOWN (' + value + ')])) :: ptask_tail*',
        'pgeneratorop.OBJECT = n_target', 'pgeneratorop.NAME = "send"',
        'pgeneratorop.SITE = pconfigcall.SITE', 'pgeneratorop.LINE = pconfigcall.LINE',
        'pgeneratorop.ARGUMENTS = eps', 'pgeneratorop.SELECTION = eps',
        'pgeneratorop.LOOP = eps', '~pgeneratorop.STARTPACK',
        '~pgeneratorop.BORROWED', '~pgeneratorop.ADVANCE',
        'S_args.STORE = S_call.STORE', 'S_args.ALLOCATIONS = S_call.ALLOCATIONS',
        'S_args.EVENTS = S_call.EVENTS', *public('S_args')]


def scalar_checks():
    values = reach('S', 'S_initial', 0) + lines(r'''
S.TODO = (CONFIG_UNPACK_PREP pconfigcall) :: ptask_tail*
S.CURRENT = (pcallcontext_caller)
pcallcontext_caller.NAME = $ptascii("run126N")
pconfigcall.OWNER = (n_target)
pconfigcall.INDEX = 0
pconfigcall.SENT = eps
pconfigcall.PACKS = eps
pconfigcall.SELECTION = eps
~pconfigcall.NAMED
$intrinsic_argument(S, pconfigcall.SITE, 0) = ((expression, true, eps, porigin_argument, z_argument))
S.RESULT = VARIABLE $ptascii("source") z_argument
$lookup(S.ENV, $ptascii("target")) = (n_target_cv)
$lookup(S.ENV, $ptascii("source")) = (n_source_cv)
S.STORE[n_target_cv] = DEFINED (POBJECT n_target)
S.STORE[n_source_cv] = DEFINED (POBJECT n_source)
n_source =/= n_target
S.OBJECTS[n_target] = GENERATOR pgenerator_target
pgenerator_target.PHASE = GENERATOR_PAUSED
~pgenerator_target.PENDING_INIT
pgenerator_target.DELEGATE = eps
S.OBJECTS[n_source] = GENERATOR pgenerator_source
pgenerator_source.PHASE = GENERATOR_PAUSED
pgenerator_source.FIRST
~pgenerator_source.PENDING_INIT
pgenerator_source.VALUE = (PINT 17)
pgenerator_source.KEY = (PINT 0)
pgenerator_source.REFCELL = eps
pgenerator_source.DELEGATE = eps
pgenerator_source.CLOSURE = eps
pgenerator_source.ACCESS = eps
pgenerator_source.CREATION = eps
$function_at($all_functions(S), pgenerator_source.FUNCTION) = (pfunction_source)
pfunction_source.NAME = $ptascii("source126N")
pfunction_source.SIGNATURE.PARAMETERS = eps
~pfunction_source.SIGNATURE.BYREF
$origin_node(S.SOURCES, pfunction_source.ORIGIN) = (NStmtFunction phpType14 (BOOLEAN false) phpType11 phpType16 phpType18 phpType23 metadata)
$config_generator_start(S, pconfigcall, S.RESULT, n_source)
$heap_owners($heap_graph(S), HOBJECT n_source) = 1
$heap_owners($heap_graph(S), HOBJECT n_target) = 2
~$config_generator_start(S, pconfigcall[.OWNER = (n_source)], S.RESULT, n_source)
~$config_generator_start(S, pconfigcall[.OWNER = eps], S.RESULT, n_source)
~$config_generator_start(S, pconfigcall[.KIND = INTRINSIC_GENERATOR_METHOD "throw" eps], S.RESULT, n_source)
~$config_generator_start(S, pconfigcall[.LINE = $(pconfigcall.LINE + 1)], S.RESULT, n_source)
~$config_generator_start(S, pconfigcall, KNOWN (POBJECT n_source), n_source)
S_fresh_source = S[.OBJECTS[n_source] = GENERATOR pgenerator_source[.PHASE = GENERATOR_FRESH]]
~$config_generator_start(S_fresh_source, pconfigcall, S.RESULT, n_source)
S_fresh_target = S[.OBJECTS[n_target] = GENERATOR pgenerator_target[.PHASE = GENERATOR_FRESH]]
~$config_generator_start(S_fresh_target, pconfigcall, S.RESULT, n_source)
S_pending = S[.OBJECTS[n_source] = GENERATOR pgenerator_source[.PENDING_INIT = true]]
~$config_generator_start(S_pending, pconfigcall, S.RESULT, n_source)
S_delegate = S[.OBJECTS[n_source] = GENERATOR pgenerator_source[.DELEGATE = ({SITE porigin_argument, INPUT (POBJECT n_target), POSITION 0, CURRENT eps, ACQUISITION eps})]]
~$config_generator_start(S_delegate, pconfigcall, S.RESULT, n_source)
PhpStep: S ~> S_data
S_data.TODO = (CONFIG_GENERATOR pconfiggenerator_initial "rewind") :: ptask_tail*
pconfiggenerator_initial = {CALL pconfigcall, OBJECT n_source, INPUT S.RESULT, ITEMS eps, PRODUCER eps}
$task_nodes(CONFIG_GENERATOR pconfiggenerator_initial "rewind") = [HOBJECT n_source, HOBJECT n_target]
$config_generator_input_nodes(pconfiggenerator_initial) = eps
$config_generator_valid(S_data, pconfiggenerator_initial, "rewind")
$heap_owners($heap_graph(S_data), HOBJECT n_source) = 2
$heap_owners($heap_graph(S_data), HOBJECT n_target) = 2
pgeneratorop_rewind = {OBJECT n_source, NAME "rewind", SITE porigin_argument, LINE z_argument, LOOP eps, ADVANCE false, ARGUMENTS eps, STARTPACK true, BORROWED true, SELECTION eps}
$config_generator_header(S_data, pgeneratorop_rewind, pconfiggenerator_initial, "rewind")
$generator_operation_nodes(pgeneratorop_rewind) = eps
$generator_operation_trace(S_data, pgeneratorop_rewind) = eps
PhpStep: S_data ~> S_ready
S_ready.TODO = (CONFIG_GENERATOR pconfiggenerator_initial "ready") :: ptask_tail*
S_ready.OBJECTS[n_source] = GENERATOR pgenerator_source
$config_generator_value(S_ready, pconfiggenerator_initial) = (PINT 17)
PhpStep: S_ready ~> S_copied
S_copied.TODO = (CONFIG_GENERATOR pconfiggenerator_copied "next") :: ptask_tail*
pconfiggenerator_copied = pconfiggenerator_initial[.ITEMS = [ENTRY (KINT 0) (DIRECT (PINT 17))]]
$config_generator_argument_nodes(pconfiggenerator_copied) = eps
~$config_generator_history(S_copied, pconfiggenerator_copied[.ITEMS = [ENTRY (KINT 0) (DIRECT (PINT 17)), ENTRY (KINT 1) (DIRECT (PINT 17)), ENTRY (KINT 2) (DIRECT (PINT 17))]])
''')
    values += public('S_copied') + reach('S_body', 'S_copied', 1)
    values += lines(r'''
S_body.CURRENT = (pcallcontext_source)
pcallcontext_source.FUNCTION = pfunction_source.ORIGIN
pcallcontext_source.TARGET = pfunction_source.ORIGIN
pcallcontext_source.ARGC = 0
pcallcontext_source.RECEIVER = eps
$call_context_roots((pcallcontext_source)) = eps
S_body.FRAMES = pframe_source :: pframe_source_tail*
pframe_source.TODO = (GENERATOR_RESUME pgeneratorop_source) :: (CONFIG_GENERATOR pconfiggenerator_copied "next") :: ptask_tail*
pgeneratorop_source = pgeneratorop_rewind[.NAME = "next"]
$generator_operation_valid(S_body, pgeneratorop_source)
$generator_operation_nodes(pgeneratorop_source) = eps
$generator_operation_trace(S_body, pgeneratorop_source) = eps
~$generator_operation_valid(S_body, pgeneratorop_source[.OBJECT = n_target])
~$generator_operation_valid(S_body, pgeneratorop_source[.BORROWED = false])
~$generator_operation_valid(S_body, pgeneratorop_source[.SITE = pconfigcall.SITE])
S_body.OBJECTS[n_source] = GENERATOR pgenerator_running
pgenerator_running.PHASE = GENERATOR_RUNNING
pgenerator_running.FRAME = eps
pgenerator_running.VALUE = (PINT 17)
pgenerator_running.REFCELL = eps
S_body.STORE[n_target_cv] = DEFINED PNULL
S_body.STORE[n_source_cv] = DEFINED PNULL
$heap_owners($heap_graph(S_body), HOBJECT n_target) = 1
$heap_owners($heap_graph(S_body), HOBJECT n_source) = 1
S_boundary = $constant_frame_scope(S_body, pframe_source, pframe_source_tail*)
$config_generator_valid(S_boundary, pconfiggenerator_copied, "next")
$task_nodes(CONFIG_GENERATOR pconfiggenerator_copied "next") = [HOBJECT n_source, HOBJECT n_target]
''')
    values += public('S_body') + budget('S_body') + reach('S_finish', 'S_body', 2)
    values += lines(r'''
S_finish.TODO = (CONFIG_GENERATOR pconfiggenerator_copied "finish") :: ptask_tail*
S_finish.CURRENT = (pcallcontext_caller)
S_finish.OBJECTS[n_source] = GENERATOR pgenerator_closed
pgenerator_closed.PHASE = GENERATOR_CLOSED
pgenerator_closed.FRAME = eps
pgenerator_closed.VALUE = (PINT 17)
pgenerator_closed.REFCELL = eps
$node_children(S_finish, HOBJECT n_source) = eps
$config_generator_quiet_closed(S_finish, pconfiggenerator_copied)
~$config_generator_callee(S_finish, pconfigcall.OWNER, 1)
$generator_source_live_callee(S_finish, pconfiggenerator_copied)
$config_generator_live_callee(S_finish, pconfiggenerator_copied)
$config_generator_finish_allowed(S_finish, pconfiggenerator_copied)
$heap_owners($heap_graph(S_finish), HOBJECT n_source) = 1
$heap_owners($heap_graph(S_finish), HOBJECT n_target) = 1
S_no_marker = S_finish[.TODO = ptask_tail*]
$heap_owners($heap_graph(S_no_marker), HOBJECT n_target) = 0
~$generator_source_live_callee(S_no_marker, pconfiggenerator_copied)
~$config_generator_finish_allowed(S_no_marker, pconfiggenerator_copied)
~$destructor_operational(S_finish)
''')
    values += public('S_finish') + budget('S_finish') + lines(r'''
S_finish_one.TODO = (CONFIG_GENERATOR pconfiggenerator_copied "invoke") :: ptask_tail*
$task_nodes(CONFIG_GENERATOR pconfiggenerator_copied "invoke") = [HOBJECT n_target]
$heap_owners($heap_graph(S_finish_one), HOBJECT n_source) = 0
~((HOBJECT n_source) <- S_finish_one.ALLOCATIONS)
$heap_owners($heap_graph(S_finish_one), HOBJECT n_target) = 1
''')
    values += reach('S_invoke', 'S_finish_one[.COMPLETION = NORMAL]', 3) + lines(r'''
~((HOBJECT n_source) <- S_invoke.ALLOCATIONS)
~$generator_storage_active(S_invoke, n_source)
$config_generator_retired_scope(S_invoke, pconfiggenerator_copied)
$heap_owners($heap_graph(S_invoke), HOBJECT n_source) = 0
S_invoke.ITERATORS = S.ITERATORS
S_invoke.NEXTITER = S.NEXTITER
''')
    values += public('S_invoke') + budget('S_invoke') + invoke_checks('S_invoke', 'PINT 17')
    return values + ['S_invoke_one = S_call[.COMPLETION = BUDGET]',
        '$task_nodes(CONFIG_INVOKE pconfigcall_copied) = [HOBJECT n_target]',
        '$task_nodes(GENERATOR_ARGS pgeneratorop eps ([KNOWN (PINT 17)])) = [HOBJECT n_target]']


def retained_checks():
    values = reach('S_finish', 'S_initial', 2) + lines(r'''
S_finish.TODO = (CONFIG_GENERATOR pconfiggenerator_copied "finish") :: ptask_tail*
S_finish.CURRENT = (pcallcontext_caller)
pcallcontext_caller.NAME = $ptascii("run126T")
pconfiggenerator_copied.CALL = pconfigcall
pconfigcall.KIND = INTRINSIC_GENERATOR_METHOD "send" eps
pconfigcall.OWNER = (n_target)
pconfigcall.INDEX = 0
pconfigcall.SENT = eps
pconfigcall.PACKS = eps
pconfigcall.SELECTION = eps
~pconfigcall.NAMED
pconfiggenerator_copied.OBJECT = n_source
pconfiggenerator_copied.PRODUCER = eps
pconfiggenerator_copied.ITEMS = [ENTRY (KINT 0) (DIRECT (POBJECT n_token))]
$intrinsic_argument(S_finish, pconfigcall.SITE, 0) = ((expression, true, eps, porigin_argument, z_argument))
pconfiggenerator_copied.INPUT = VARIABLE $ptascii("source") z_argument
n_source =/= n_target
$lookup(S_finish.ENV, $ptascii("source")) = (n_source_cv)
S_finish.STORE[n_source_cv] = DEFINED (POBJECT n_source)
S_finish.OBJECTS[n_source] = GENERATOR pgenerator_source
pgenerator_source.PHASE = GENERATOR_CLOSED
pgenerator_source.FRAME = eps
pgenerator_source.VALUE = (POBJECT n_token)
pgenerator_source.KEY = (PINT 0)
pgenerator_source.REFCELL = eps
pgenerator_source.DELEGATE = eps
pgenerator_source.CLOSURE = eps
pgenerator_source.ACCESS = eps
pgenerator_source.CREATION = eps
~pgenerator_source.PENDING_INIT
$config_generator_owning_value_source(S_finish, pconfiggenerator_copied)
$node_children(S_finish, HOBJECT n_source) = [HOBJECT n_token]
$object_name(S_finish, n_token) = $ptascii("Token126T")
$config_generator_argument_nodes(pconfiggenerator_copied) = [HOBJECT n_token]
$heap_owners($heap_graph(S_finish), HOBJECT n_source) = 2
$heap_owners($heap_graph(S_finish), HOBJECT n_token) = 2
$heap_owners($heap_graph(S_finish), HOBJECT n_target) = 1
~$config_generator_callee(S_finish, pconfigcall.OWNER, 1)
$config_generator_finish_allowed(S_finish, pconfiggenerator_copied)
S_lost_source = S_finish[.STORE[n_source_cv] = DEFINED PNULL]
$heap_owners($heap_graph(S_lost_source), HOBJECT n_source) = 1
~$config_generator_finish_allowed(S_lost_source, pconfiggenerator_copied)
PhpStep: S_lost_source ~> S_held
S_held = S_lost_source[.COMPLETION = UNSUPPORTED "CONFIG Generator unpack last DATA or callee owner"]
''')
    values += public('S_finish') + reach('S_invoke', 'S_finish', 3) + lines(r'''
S_invoke.OBJECTS[n_source] = GENERATOR pgenerator_source
$node_children(S_invoke, HOBJECT n_source) = [HOBJECT n_token]
$heap_owners($heap_graph(S_invoke), HOBJECT n_source) = 1
$heap_owners($heap_graph(S_invoke), HOBJECT n_token) = 2
$task_nodes(CONFIG_GENERATOR pconfiggenerator_copied "invoke") = [HOBJECT n_token, HOBJECT n_target]
''')
    values += invoke_checks('S_invoke', 'POBJECT n_token') + reach('S_closed', 'S_args', 4)
    values += lines(r'''
S_closed.TODO = (THROW_SEARCH n_error) :: (GENERATOR_RESUME pgeneratorop_closed) :: ptask_tail*
pgeneratorop_closed = pgeneratorop[.ARGUMENTS = [POBJECT n_token]]
S_closed.CURRENT = (pcallcontext_caller)
$generator_api_body_throw(S_closed, pgeneratorop_closed)
$object_name(S_closed, n_error) = $ptascii("TypeError")
$throwable_field(S_closed, n_error, "previous") = PNULL
$throwable_field(S_closed, n_error, "trace") = PARRAY n_trace
S_closed.ARRAYS[n_trace].ITEMS = [ENTRY (KINT 0) (DIRECT (PARRAY n_typed)), ENTRY (KINT 1) (DIRECT (PARRAY n_body)), ENTRY (KINT 2) (DIRECT (PARRAY n_api)), ENTRY (KINT 3) (DIRECT (PARRAY n_caller))]
$trace_array_field(S_closed, n_typed, $ptascii("function")) = PSTRING $ptascii("typed126T")
$trace_array_field(S_closed, n_body, $ptascii("function")) = PSTRING $ptascii("flow126T")
$trace_array_field(S_closed, n_api, $ptascii("function")) = PSTRING $ptascii("send")
$trace_array_field(S_closed, n_api, $ptascii("class")) = PSTRING $ptascii("Generator")
$trace_array_field(S_closed, n_api, $ptascii("line")) = PINT pconfigcall.LINE
$trace_array_field(S_closed, n_caller, $ptascii("function")) = PSTRING $ptascii("run126T")
$trace_array_field(S_closed, n_typed, $ptascii("args")) = PARRAY n_typed_args
S_closed.ARRAYS[n_typed_args].ITEMS = [ENTRY (KINT 0) (DIRECT (POBJECT n_token))]
$trace_array_field(S_closed, n_api, $ptascii("args")) = PARRAY n_api_args
S_closed.ARRAYS[n_api_args].ITEMS = [ENTRY (KINT 0) (DIRECT (POBJECT n_token))]
S_closed.OBJECTS[n_source] = GENERATOR pgenerator_source
$node_children(S_closed, HOBJECT n_source) = [HOBJECT n_token]
$heap_owners($heap_graph(S_closed), HOBJECT n_source) = 1
$heap_owners($heap_graph(S_closed), HOBJECT n_token) = 4
$heap_owners($heap_graph(S_closed), HOBJECT n_target) = 1
$lookup(S_closed.ENV, $ptascii("result")) = (n_result_cv)
S_closed.STORE[n_result_cv] = DEFINED pvalue_result
$string_bytes(pvalue_result) = ($ptascii("sentinel"))
''')
    values += public('S_closed') + reach('S_cached', 'S_closed', 5) + lines(r'''
S_cached.CURRENT = (pcallcontext_caller)
S_cached.STORE[n_source_cv] = DEFINED (POBJECT n_source)
S_cached.OBJECTS[n_source] = GENERATOR pgenerator_source
$node_children(S_cached, HOBJECT n_source) = [HOBJECT n_token]
$heap_owners($heap_graph(S_cached), HOBJECT n_source) = 1
$heap_owners($heap_graph(S_cached), HOBJECT n_token) = 1
$heap_owners($heap_graph(S_cached), HOBJECT n_target) = 0
~((HOBJECT n_target) <- S_cached.ALLOCATIONS)
$lookup(S_cached.ENV, $ptascii("weakToken")) = (n_weak_cv)
S_cached.STORE[n_weak_cv] = DEFINED (POBJECT n_weak_token)
$weakref_get(S_cached, n_weak_token) = POBJECT n_token
''')
    return values + public('S_cached')


def mapping_checks():
    values = reach('S_error', 'S_initial', 6) + lines(r'''
S_error.TODO = (THROW_SEARCH n_error) :: (CONFIG_GENERATOR pconfiggenerator "ready") :: ptask_tail*
S_error.CURRENT = (pcallcontext_caller)
pcallcontext_caller.NAME = $ptascii("run126M")
pconfiggenerator.CALL = pconfigcall
pconfigcall.KIND = INTRINSIC_GENERATOR_METHOD "send" eps
pconfigcall.OWNER = (n_target)
pconfigcall.INDEX = 0
pconfigcall.SENT = eps
pconfigcall.PACKS = eps
pconfigcall.SELECTION = eps
~pconfigcall.NAMED
pconfiggenerator.OBJECT = n_source
pconfiggenerator.PRODUCER = eps
pconfiggenerator.ITEMS = [ENTRY (KINT 0) (DIRECT (PINT 17))]
$config_generator_valid(S_error, pconfiggenerator, "ready")
$lookup(S_error.ENV, $ptascii("source")) = (n_source_cv)
$lookup(S_error.ENV, $ptascii("target")) = (n_target_cv)
S_error.STORE[n_source_cv] = DEFINED (POBJECT n_source)
S_error.STORE[n_target_cv] = DEFINED PNULL
S_error.OBJECTS[n_source] = GENERATOR pgenerator_source
pgenerator_source.PHASE = GENERATOR_PAUSED
pgenerator_source.VALUE = (PINT 23)
pgenerator_source.KEY = (pvalue_key)
$string_bytes(pvalue_key) = ($ptascii("extra"))
$config_generator_key(S_error, pvalue_key) = (KSTRING $ptascii("extra"))
$heap_owners($heap_graph(S_error), HOBJECT n_source) = 2
$heap_owners($heap_graph(S_error), HOBJECT n_target) = 1
$object_name(S_error, n_error) = $ptascii("Error")
$string_bytes($throwable_field(S_error, n_error, "message")) = ($ptascii("Unknown named parameter $extra"))
$throwable_field(S_error, n_error, "previous") = PNULL
$throwable_field(S_error, n_error, "trace") = PARRAY n_trace
S_error.ARRAYS[n_trace].ITEMS = [ENTRY (KINT 0) (DIRECT (PARRAY n_caller))]
$trace_array_field(S_error, n_caller, $ptascii("function")) = PSTRING $ptascii("run126M")
S_popped = S_error[.TODO = (THROW_SEARCH n_error) :: ptask_tail*]
$heap_owners($heap_graph(S_popped), HOBJECT n_target) = 0
$heap_owners($heap_graph(S_popped), HOBJECT n_source) = 1
~$config_generator_callee(S_popped, pconfigcall.OWNER, 0)
~$config_generator_discard_allowed(S_popped, pconfiggenerator)
$generator_source_discard_state(S_popped, pconfiggenerator, "ready") = (S_hold)
pconfigcall_copied = pconfigcall[.INDEX = 1][.SENT = [NAMED_SENT (KNOWN (PINT 17))]]
S_hold = S_popped[.TODO = (THROW_SEARCH n_error) :: (CONFIG_INVOKE pconfigcall_copied) :: ptask_tail*][.ORIGIN = (pconfigcall.SITE)][.RESULT = KNOWN PNULL][.BASE = BASE_VALUE (KNOWN PNULL)]
$config_generator_discard_allowed(S_hold, pconfiggenerator)
$heap_owners($heap_graph(S_hold), HOBJECT n_target) = 1
$heap_owners($heap_graph(S_hold), HOBJECT n_source) = 1
$generator_source_discard_nodes(pconfiggenerator, "ready") = [HOBJECT n_source]
~$destructor_operational(S_popped)
PhpStep: S_error ~> S_staged
S_staged = S_hold
$task_nodes(THROW_SEARCH n_error) = [HOBJECT n_error]
$task_nodes(CONFIG_INVOKE pconfigcall_copied) = [HOBJECT n_target]
$heap_owners($heap_graph(S_staged), HOBJECT n_source) = 1
$heap_owners($heap_graph(S_staged), HOBJECT n_target) = 1
$heap_owners($heap_graph(S_staged), HOBJECT n_error) = 1
''')
    values += public('S_error') + public('S_staged') + budget('S_error')
    values += ['S_error_one = S_staged[.COMPLETION = BUDGET]']
    values += reach('S_released', 'S_error_one[.COMPLETION = NORMAL]', 7) + lines(r'''
S_released.TODO = (THROW_SEARCH n_error) :: (CONFIG_INVOKE pconfigcall_copied) :: ptask_tail*
S_released.CURRENT = (pcallcontext_caller)
S_released.OBJECTS[n_source] = GENERATOR pgenerator_source
$config_generator_count(S_released.TODO, pconfigcall.SITE) = 0
$heap_owners($heap_graph(S_released), HOBJECT n_source) = 1
$heap_owners($heap_graph(S_released), HOBJECT n_target) = 1
$heap_owners($heap_graph(S_released), HOBJECT n_error) = 1
$throwable_field(S_released, n_error, "previous") = PNULL
$throwable_field(S_released, n_error, "trace") = PARRAY n_trace
S_released.EVENTS = S_error.EVENTS
''')
    return values + public('S_released')


def checks(name, program, path):
    encoded = json.dumps(base64.b64encode(os.fsencode(path)).decode())
    initial = ['S_initial = $php_run(' + program + ', 0, ' + encoded + ')',
        'S_initial.COMPLETION = BUDGET']
    if name == 'i126-generator-scalar-normal':
        return initial + scalar_checks()
    if name == 'i126-generator-retained-quiet-cache-body-type':
        return initial + retained_checks()
    assert name == 'i126-generator-mapping'
    return initial + mapping_checks()


def run(out=None, process_seconds=600):
    catalog = {row['id']: row for row in json.loads(CATALOG.read_bytes())}
    rows = [catalog[name] for name in EXPECTED]
    out = Path(out) if out else Path(tempfile.mkdtemp(prefix='generator-source-arguments-state-', dir=ROOT / '.tools'))
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
    report = {'revision': subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip(), 'selection': list(EXPECTED), 'records': records, 'passed': all(row['passed'] for row in records)}
    (out / 'raw-report.json').write_text(json.dumps(report, indent=2) + '\n')
    return report['passed']


if __name__ == '__main__':
    raise SystemExit(0 if run() else 1)
