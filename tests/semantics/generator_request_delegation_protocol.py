#!/usr/bin/env python3
"""Reached request delegation input, CV, cache and handler ownership."""
import os

import generator_request_finally_protocol as base
import generator_request_delegation_sources as author
import generator_request_delegation_peer_sources as peer
from reference_yield_protocol import valid, reject

driver = base.driver
CASES = {name: peer.CASES[name] for name in [
    'peer-request-delegate-temporary-child-before-outer',
    'peer-request-delegate-parameter-retains-child-through-outer',
    'peer-request-delegate-shared-reference-globals-store-order',
    'peer-request-delegate-inner-handler-cache-before-outer',
]}
CASES['request-reference-current-keeps-closure-before-value'] = author.CASES[
    'request-reference-current-keeps-closure-before-value']
PREFIX = r'''
def $request_finally_phase(S,100) = (S.TODO = [DESTRUCTOR_GLOBALS])
def $request_finally_phase(S,101) = true
  -- if S.TODO = [DESTRUCTOR_RELEASE pdestructionrelease,DESTRUCTOR_GLOBALS]
  -- if pdestructionrelease.JOBS = (DESTRUCTION_VALUE (HOBJECT n)) :: pdestructionjob_tail*
  -- if S.OBJECTS[n] = GENERATOR pgenerator
  -- if pgenerator.PHASE = GENERATOR_DELEGATING
def $request_finally_phase(S,102) = true
  -- if S.TODO = (GENERATOR_CLOSE_RELEASE pgenrelease) :: (GENERATOR_CLOSE_ENTER pgenclose) :: ptask_tail*
  -- if $trace_context_function(S,pgenclose.CONTEXT) = $ptascii("outerPeerRequest")
  -- if pgenrelease.JOBS =/= eps
def $request_finally_phase(S,103) = true
  -- if S.TODO = (GENERATOR_CLOSE_ENTER pgenclose) :: ptask_tail*
  -- if $trace_context_function(S,pgenclose.CONTEXT) = $ptascii("outerPeerRequest")
def $request_finally_phase(S,120) = true
  -- if S.TODO = [DESTRUCTOR_STORE]
  -- if $trace_slot(S,S.ENV,$ptascii("inner")) = POBJECT n
  -- if $destructor_handle(S,S.DESTRUCTION.INDEX,0) = (n)
def $request_finally_phase(S,121) = true
  -- if S.TODO = [DESTRUCTOR_STORE]
  -- if $trace_slot(S,S.ENV,$ptascii("a")) = POBJECT n
  -- if $destructor_handle(S,S.DESTRUCTION.INDEX,0) = (n)
def $request_finally_phase(S,130) = true
  -- if S.TODO = (GENERATOR_CLOSE_RELEASE pgenrelease) :: (GENERATOR_CLOSE_ENTER pgenclose) :: ptask_tail*
  -- if S.OBJECTS[pgenclose.OBJECT] = GENERATOR pgenerator
  -- if pgenerator.DELEGATE = (pgeneratorfrom)
  -- if pgeneratorfrom.CURRENT = (REFERENCE n)
  -- if pgenrelease.JOBS =/= eps
def $request_finally_phase(S,131) = true
  -- if S.TODO = (GENERATOR_CLOSE_ENTER pgenclose) :: ptask_tail*
  -- if S.OBJECTS[pgenclose.OBJECT] = GENERATOR pgenerator
  -- if pgenerator.DELEGATE = (pgeneratorfrom)
  -- if pgeneratorfrom.CURRENT = (REFERENCE n)
def $request_finally_phase(S,132) = true
  -- if S.TODO = (GENERATOR_STORAGE_STEP pgenstorage) :: ptask_tail*
  -- if pgenstorage.NEXT = 0
def $request_finally_phase(S,133) = true
  -- if S.CURRENT = (pcallcontext)
  -- if pcallcontext.TARGET = METHOD_TARGET n porigin
  -- if $object_name(S,n) = $ptascii("CaptureRequest360")
  -- if $trace_context_function(S,pcallcontext) = $ptascii("__destruct")
def $request_finally_phase(S,134) = true
  -- if S.CURRENT = (pcallcontext)
  -- if pcallcontext.TARGET = METHOD_TARGET n porigin
  -- if $object_name(S,n) = $ptascii("ValueRequest360")
  -- if $trace_context_function(S,pcallcontext) = $ptascii("__destruct")
def $request_finally_phase(S,140) = true
  -- if S.CURRENT = (pcallcontext)
  -- if $trace_context_function(S,pcallcontext) = $ptascii("caughtPeerRequest")
  -- if $exception_context_call(S,pcallcontext) = (pexceptioncall)
def $request_finally_phase(S,141) = true
  -- if S.CURRENT = (pcallcontext)
  -- if pcallcontext.TARGET = METHOD_TARGET n porigin
  -- if $object_name(S,n) = $ptascii("PayloadPeerRequest")
  -- if $trace_context_function(S,pcallcontext) = $ptascii("__destruct")
'''


def lines(text):
    return text.strip().splitlines()


def assertions(checked, path, directory, name):
    initial = ('$php_file_run(' + checked['fixture'] + ',0,'
               + driver.driver.byte_expr(os.fsencode(path)) + ','
               + driver.driver.byte_expr(os.fsencode(driver.ROOT)) + ')')
    checks = ['S_initial = ' + initial, '~S_initial.COMPILESTOP']
    store = name == 'peer-request-delegate-shared-reference-globals-store-order'
    reference = name == 'request-reference-current-keeps-closure-before-value'
    handler = name == 'peer-request-delegate-inner-handler-cache-before-outer'
    parameter = name == 'peer-request-delegate-parameter-retains-child-through-outer'
    if store:
        checks += base.seek('S_store', 'S_initial', 120) + valid('S_store')
        checks += lines(r'''
$trace_slot(S_store,S_store.ENV,$ptascii("inner")) = POBJECT n_inner
$trace_slot(S_store,S_store.ENV,$ptascii("a")) = POBJECT n_a
$trace_slot(S_store,S_store.ENV,$ptascii("b")) = POBJECT n_b
S_store.OBJECTS[n_a] = GENERATOR pgenerator_a
S_store.OBJECTS[n_b] = GENERATOR pgenerator_b
pgenerator_a.DELEGATE = (pgeneratorfrom_a)
pgenerator_b.DELEGATE = (pgeneratorfrom_b)
pgeneratorfrom_a.INPUT = (POBJECT n_inner)
pgeneratorfrom_b.INPUT = (POBJECT n_inner)
$heap_owners($heap_graph(S_store),HOBJECT n_inner) = 5
$generator_request_store_ready(S_store,n_inner)
n_handle_inner = S_store.DESTRUCTION.INDEX
''')
        checks += base.seek('S_a', 'S_store', 121) + valid('S_a')
        checks += lines(r'''
S_a.OBJECTS[n_inner] = GENERATOR pgenerator_inner_closed
pgenerator_inner_closed.PHASE = GENERATOR_CLOSED
pgenerator_inner_closed.FRAME = eps
n_inner <- S_a.DESTRUCTION.CALLED
$heap_owners($heap_graph(S_a),HOBJECT n_inner) = 5
$generator_request_store_ready(S_a,n_a)
$close_outputs(S_a.EVENTS) = $ptascii("C|7:7|I")
S_a.OBJECTS[n_a] = GENERATOR pgenerator_a
S_a.OBJECTS[n_b] = GENERATOR pgenerator_b
$generator_from_record_valid(S_a,n_a,pgenerator_a)
$generator_from_record_valid(S_a,n_b,pgenerator_b)
n_handle_a = S_a.DESTRUCTION.INDEX
''')
        checks += base.seek('S_enter', 'S_a', 103) + valid('S_enter')
        checks += lines(r'''
S_enter.TODO = (GENERATOR_CLOSE_ENTER pgenclose_a) :: ptask_after*
pgenclose_a.OBJECT = n_a /\ pgenclose_a.STORE = (n_handle_a)
$generator_close_enter_valid(S_enter,pgenclose_a)
$generator_request_store_valid(S_enter,pgenclose_a)
$heap_owners($heap_graph(S_enter),HOBJECT n_inner) = 4
$heap_owners($heap_graph(S_enter),HOBJECT n_a) = 2
S_enter.OBJECTS[n_b] = GENERATOR pgenerator_b
pgeneratorfrom_b.INPUT = (POBJECT n_inner)
$close_outputs(S_enter.EVENTS) = $ptascii("C|7:7|I")
''')
        reject(checks, 'wrong_store', 'S_enter[.TODO = (GENERATOR_CLOSE_ENTER pgenclose_a[.STORE = (n_handle_inner)]) :: ptask_after*]', 'S_enter')
        reject(checks, 'uncalled', 'S_enter[.DESTRUCTION.CALLED = $request_called_drop(S_enter.DESTRUCTION.CALLED,n_a)]', 'S_enter')
        base.finish(checks, 'S_enter', name)
        checks += ['S_resumed.OBJECTS[n_a] = GENERATOR pgenerator_a_closed',
                   'S_resumed.OBJECTS[n_b] = GENERATOR pgenerator_b_closed',
                   'pgenerator_a_closed.PHASE = GENERATOR_CLOSED',
                   'pgenerator_b_closed.PHASE = GENERATOR_CLOSED',
                   '$generator_from_input_of(pgenerator_a_closed.DELEGATE) = eps',
                   '$generator_from_input_of(pgenerator_b_closed.DELEGATE) = eps']
        return checks

    checks += base.seek('S_globals', 'S_initial', 100) + valid('S_globals')
    checks += lines(r'''
$trace_slot(S_globals,S_globals.ENV,$ptascii("g")) = POBJECT n_outer
S_globals.OBJECTS[n_outer] = GENERATOR pgenerator_outer
pgenerator_outer.PHASE = GENERATOR_DELEGATING
pgenerator_outer.DELEGATE = (pgeneratorfrom_outer)
pgenerator_outer.FRAME = (pframe_outer)
pframe_outer.ORIGIN = (pgeneratorfrom_outer.SITE)
$generator_request_frame_valid(S_globals,pgenerator_outer)
$generator_from_code(S_globals,pgenerator_outer,pgeneratorfrom_outer.SITE)
$heap_owners($heap_graph(S_globals),HOBJECT n_outer) = 1
''')
    if reference:
        checks += lines(r'''
pgeneratorfrom_outer.INPUT = (PARRAY n_input)
pgeneratorfrom_outer.CURRENT = (REFERENCE n_cell)
S_globals.STORE[n_cell] = DEFINED (POBJECT n_value)
$heap_owners($heap_graph(S_globals),HCELL n_cell) = 2
pgenerator_outer.CLOSURE = (n_closure)
$trace_slot(S_globals,S_globals.ENV,$ptascii("wg")) = POBJECT n_weak
$trace_slot(S_globals,S_globals.ENV,$ptascii("other")) = POBJECT n_other
S_globals.OBJECTS[n_other] = GENERATOR pgenerator_other
pgenerator_other.PHASE = GENERATOR_CLOSED /\ pgenerator_other.FRAME = eps
''')
    else:
        checks += ['pgeneratorfrom_outer.INPUT = (POBJECT n_inner)',
                   'pgeneratorfrom_outer.CURRENT = eps',
                   f'$heap_owners($heap_graph(S_globals),HOBJECT n_inner) = {2 if parameter else 1}']
        if handler:
            checks += ['S_globals.OBJECTS[n_inner] = GENERATOR pgenerator_inner',
                       'pgenerator_inner.VALUE = (POBJECT n_payload)']
    checks += base.seek('S_release', 'S_globals', 101) + valid('S_release')
    checks += lines(r'''
S_release.TODO = [DESTRUCTOR_RELEASE pdestructionrelease,DESTRUCTOR_GLOBALS]
pdestructionrelease.JOBS = [DESTRUCTION_VALUE (HOBJECT n_outer)]
~pdestructionrelease.USER
$generator_destructor_request_ready(S_release,pdestructionrelease,HOBJECT n_outer)
S_unheld = $destructor_release_replace(S_release,pdestructionrelease[.JOBS = eps])
$heap_owners($heap_graph(S_unheld),HOBJECT n_outer) = 0
''')
    checks += base.seek('S_input', 'S_release', 130 if reference else 102) + valid('S_input')
    checks += lines(r'''
S_input.TODO = (GENERATOR_CLOSE_RELEASE pgenrelease_input) :: (GENERATOR_CLOSE_ENTER pgenclose_outer) :: ptask_after*
pgenclose_outer.OBJECT = n_outer /\ pgenclose_outer.STORE = eps
S_input.OBJECTS[n_outer] = GENERATOR pgenerator_detached
pgenerator_detached.PHASE = GENERATOR_CLOSING /\ pgenerator_detached.FRAME = eps
pgenerator_detached.DELEGATE = (pgeneratorfrom_outer[.INPUT = eps])
$generator_close_enter_valid(S_input,pgenclose_outer)
$heap_owners($heap_graph(S_input),HOBJECT n_outer) = 1
''')
    if reference:
        checks += ['pgenrelease_input.JOBS = [DESTRUCTION_VALUE (HARRAY n_input)]',
                   '$heap_owners($heap_graph(S_input),HCELL n_cell) = 2']
        checks += base.seek('S_enter', 'S_input', 131) + valid('S_enter')
        checks += ['~((HARRAY n_input) <- S_enter.ALLOCATIONS)',
                   '$heap_owners($heap_graph(S_enter),HCELL n_cell) = 1']
        checks += base.seek('S_pinned', 'S_enter', 132) + valid('S_pinned')
        checks += lines(r'''
S_pinned.TODO = (GENERATOR_STORAGE_STEP pgenstorage) :: ptask_parent*
pgenstorage.OBJECT = n_outer /\ pgenstorage.NEXT = 0
~pgenstorage.USER
$generator_storage_valid(S_pinned,pgenstorage)
$generator_storage_slot(pgenerator_detached,1) = [HCELL n_cell]
$heap_owners($heap_graph(S_pinned),HCELL n_cell) = 1
$heap_owners($heap_graph(S_pinned),HOBJECT n_outer) = 1
S_pinned.OBJECTS[n_outer] = GENERATOR pgenerator_pinned
S_two_values = $generator_set(S_pinned,n_outer,pgenerator_pinned[.VALUE = (POBJECT n_value)])
$heap_valid($heap_graph(S_two_values))
~$generator_storage_value_shape(pgenerator_pinned[.VALUE = (POBJECT n_value)])
~$generator_storage_basic(S_two_values,pgenstorage)
~$call_descriptors_valid(S_two_values)
''')
        checks += base.seek('S_capture', 'S_pinned', 133) + valid('S_capture')
        checks += ['$generator_storage_for(S_capture,n_outer) = (pgenstorage[.NEXT = 1])',
                   '~((HOBJECT n_closure) <- S_capture.ALLOCATIONS)',
                   '$heap_owners($heap_graph(S_capture),HCELL n_cell) = 1',
                   '$weakref_get(S_capture,n_weak) = POBJECT n_outer']
        checks += base.seek('S_value', 'S_capture', 134) + valid('S_value')
        checks += lines(r'''
S_value.OBJECTS[n_outer] = GENERATOR pgenerator_value
pgenerator_value.DELEGATE = (pgeneratorfrom_value)
pgeneratorfrom_value.CURRENT = (REFERENCE n_cell) /\ pgeneratorfrom_value.INPUT = eps
$generator_storage_for(S_value,n_outer) = (pgenstorage[.NEXT = 2])
~((HCELL n_cell) <- S_value.ALLOCATIONS)
S_value.STORE[n_cell] = DEFINED (POBJECT n_value)
~$generator_from_cached_operand(S_value,pgeneratorfrom_value.CURRENT)
$generator_storage_current_borrowed(S_value,pgeneratorfrom_value)
$generator_from_cache_valid(S_value,pgeneratorfrom_value)
$generator_from_record_valid(S_value,n_outer,pgenerator_value)
$generator_storage_node_valid(S_value,n_outer)
$weakref_get(S_value,n_weak) = POBJECT n_outer
$heap_owners($heap_graph(S_value),HOBJECT n_outer) = 1
S_value.CURRENT = (pcallcontext_value)
pcallcontext_value.RECEIVER = (n_value)
$heap_owners($heap_graph(S_value[.CURRENT = eps]),HOBJECT n_value) = 1
$heap_owners($heap_graph(S_value),HOBJECT n_value) = 2
S_value.OBJECTS[n_other] = GENERATOR pgenerator_other
(HOBJECT n_other) <- S_value.ALLOCATIONS
$generator_storage_for(S_value,n_other) = eps
S_copy = S_value[.OBJECTS[n_other] = GENERATOR pgenerator_value]
$generator_record_valid(S_copy,pgenerator_value)
$generator_from_record_valid(S_copy,n_other,pgenerator_value)
~$generator_storage_node_valid(S_copy,n_other)
~$generator_state_valid(S_copy)
~$call_descriptors_valid(S_copy)
$call_entry_check(S_copy).COMPLETION = UNSUPPORTED "invalid compiled function descriptor"
''')
        base.finish(checks, 'S_value', name)
        checks += ['~((HOBJECT n_outer) <- S_resumed.ALLOCATIONS)',
                   '$weakref_get(S_resumed,n_weak) = PNULL']
        return checks

    checks += ['pgenrelease_input.JOBS = [DESTRUCTION_VALUE (HOBJECT n_inner)]',
               f'$heap_owners($heap_graph(S_input),HOBJECT n_inner) = {2 if parameter else 1}']
    if handler:
        checks += base.seek('S_handler', 'S_input', 140) + valid('S_handler')
        checks += lines(r'''
S_handler.CURRENT = (pcallcontext_handler)
$exception_context_call(S_handler,pcallcontext_handler) = (pexceptioncall)
S_handler.FRAMES = [pframe_handler_root]
S_root = $constant_frame_scope(S_handler,pframe_handler_root,eps)
pgenclose_outer.FRAME = (pframe_outer)
pframe_outer.CONTEXT = (pcallcontext_outer)
S_outer_view = $generator_frame_scope(S_root,pframe_outer)[.FRAMES = $save_frame(S_root).FRAMES]
$exception_context_source_view(S_outer_view,pcallcontext_outer)
$exception_context_call(S_outer_view,pcallcontext_outer) = eps
$call_saved_context_valid(S_outer_view,pframe_outer)
$generator_close_enter_valid(S_root,pgenclose_outer)
S_bad_handler = S_handler[.CURRENT = (pcallcontext_handler[.TARGET = pcallcontext_outer.TARGET][.CALLSITE = pcallcontext_outer.CALLSITE])]
S_bad_handler.CURRENT = (pcallcontext_bad_handler)
~$exception_context_source_view(S_bad_handler,pcallcontext_bad_handler)
$exception_context_call(S_bad_handler,pcallcontext_bad_handler) = (pexceptioncall)
~$exception_context_valid(S_bad_handler,pcallcontext_bad_handler)
$heap_graph(S_bad_handler) = $heap_graph(S_handler)
~$call_descriptors_valid(S_bad_handler)
$throwable_field(S_handler,pexceptioncall.OBJECT,"message") = PSTRING ($ptascii("inner"))
S_handler.OBJECTS[n_inner] = GENERATOR pgenerator_inner_closed
pgenerator_inner_closed.PHASE = GENERATOR_CLOSED /\ pgenerator_inner_closed.FRAME = eps
pgenerator_inner_closed.VALUE = (POBJECT n_payload)
$generator_storage_for(S_handler,n_inner) = eps
$heap_owners($heap_graph(S_handler),HOBJECT n_inner) = 1
$heap_owners($heap_graph(S_handler),HOBJECT n_payload) = 1
$heap_owners($heap_graph(S_handler),HOBJECT n_outer) = 1
$generator_id_count($generator_close_frame_claims(S_handler.FRAMES),n_inner) = 1
$generator_id_count($generator_close_frame_claims(S_handler.FRAMES),n_outer) = 1
$close_outputs(S_handler.EVENTS) = $ptascii("C|I")
''')
        checks += base.seek('S_payload', 'S_handler', 141) + valid('S_payload')
        checks += ['$generator_storage_for(S_payload,n_inner) = (pgenstorage_inner)',
                   'pgenstorage_inner.NEXT = 2',
                   '$heap_owners($heap_graph(S_payload),HOBJECT n_inner) = 1',
                   '$heap_owners($heap_graph(S_payload),HOBJECT n_outer) = 1',
                   '$close_outputs(S_payload.EVENTS) = $ptascii("C|IH")']
        previous = 'S_payload'
    else:
        previous = 'S_input'
    checks += base.seek('S_enter', previous, 103) + valid('S_enter')
    checks += lines(r'''
S_enter.TODO = (GENERATOR_CLOSE_ENTER pgenclose_outer) :: ptask_enter*
$generator_close_enter_valid(S_enter,pgenclose_outer)
$heap_owners($heap_graph(S_enter),HOBJECT n_outer) = 1
''')
    if parameter:
        checks += ['(HOBJECT n_inner) <- S_enter.ALLOCATIONS',
                   '$heap_owners($heap_graph(S_enter),HOBJECT n_inner) = 1',
                   'S_enter.OBJECTS[n_inner] = GENERATOR pgenerator_inner',
                   'pgenerator_inner.PHASE = GENERATOR_PAUSED',
                   '$close_outputs(S_enter.EVENTS) = $ptascii("C|7|")']
    else:
        checks += ['~((HOBJECT n_inner) <- S_enter.ALLOCATIONS)',
                   '$close_outputs(S_enter.EVENTS) = $ptascii("C|IHD")' if handler
                   else '$close_outputs(S_enter.EVENTS) = $ptascii("C|7|I")']
    base.finish(checks, 'S_input', name)
    checks += ['~((HOBJECT n_inner) <- S_resumed.ALLOCATIONS)',
               '~((HOBJECT n_outer) <- S_resumed.ALLOCATIONS)']
    return checks


def main():
    base.CASES = CASES
    driver.CASES = CASES
    driver.PREFIX += base.PREFIX + PREFIX
    driver.assertions = assertions
    driver.source.WATCHED += [
        'spec/semantics/222-exception-handlers.watsup',
        'spec/semantics/257-request-destructors.watsup',
        'spec/semantics/270-eager-destructors.watsup',
        'spec/semantics/281-fibers.watsup',
        'spec/semantics/289-generator-delegation.watsup',
        'spec/semantics/296-weak-references.watsup',
        'spec/semantics/328-generator-reference-yields.watsup',
        'spec/semantics/340-generator-request-finally.watsup',
        'spec/semantics/349-generator-request-fresh.watsup',
        'spec/semantics/355-generator-storage-pin.watsup',
        'spec/semantics/360-generator-request-delegation.watsup',
        'tests/semantics/generator_request_finally_protocol.py',
        'tests/semantics/reference_yield_protocol.py',
        'tests/semantics/generator_request_delegation_sources.py',
        'tests/semantics/generator_request_delegation_peer_sources.py',
        'tests/semantics/generator_request_delegation_protocol.py',
    ]
    return driver.main()


if __name__ == '__main__':
    raise SystemExit(main())
