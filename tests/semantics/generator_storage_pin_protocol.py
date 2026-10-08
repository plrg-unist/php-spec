#!/usr/bin/env python3
"""Reached physical Generator storage pins and one-at-a-time field transfers."""
import os

import generator_request_finally_protocol as base
import generator_storage_pin_sources as author
import generator_storage_pin_peer_sources as peer
from reference_yield_protocol import reject, valid

driver = base.driver
CASES = {name: row for name, row in author.CASES.items()
         if name != 'closed-storage-weak-target-live-through-children'}
CASES.update(peer.CASES)
PREFIX = r'''
def $request_finally_phase(S,89) = true
  -- if S.TODO = (DESTRUCTOR_RELEASE pdestructionrelease) :: ptask_tail*
  -- if pdestructionrelease.JOBS = (DESTRUCTION_VALUE (HOBJECT n)) :: pdestructionjob_tail*
  -- if S.OBJECTS[n] = GENERATOR pgenerator
  -- if pgenerator.PHASE = GENERATOR_CLOSED /\ pgenerator.CLOSURE =/= eps
  -- if $close_outputs(S.EVENTS) = $ptascii("C|")
def $request_finally_phase(S,90) = true
  -- if S.TODO = (GENERATOR_STORAGE_STEP pgenstorage) :: ptask_tail*
  -- if pgenstorage.NEXT = 0
def $request_finally_phase(S,91) = true
  -- if S.CURRENT = (pcallcontext)
  -- if pcallcontext.TARGET = METHOD_TARGET n porigin
  -- if $object_name(S,n) <- [$ptascii("CaptureReturn349"),$ptascii("CaptureFields355"),$ptascii("CaptureReference355"),$ptascii("CapturePaused355"),$ptascii("CapturePinThrow355")]
  -- if $trace_context_function(S,pcallcontext) = $ptascii("__destruct")
def $request_finally_phase(S,92) = true
  -- if S.CURRENT = (pcallcontext)
  -- if pcallcontext.TARGET = METHOD_TARGET n porigin
  -- if $object_name(S,n) <- [$ptascii("ValueReturn349"),$ptascii("ValueFields355"),$ptascii("ValueReference355"),$ptascii("ValuePaused355"),$ptascii("ValuePinThrow355")]
  -- if $trace_context_function(S,pcallcontext) = $ptascii("__destruct")
def $request_finally_phase(S,93) = true
  -- if S.TODO = (GENERATOR_STORAGE_STEP pgenstorage) :: ptask_tail*
  -- if pgenstorage.NEXT = 4
def $request_finally_phase(S,94) = true
  -- if S.CURRENT = (pcallcontext)
  -- if pcallcontext.TARGET = METHOD_TARGET n porigin
  -- if $object_name(S,n) = $ptascii("KeyFields355")
  -- if $trace_context_function(S,pcallcontext) = $ptascii("__destruct")
def $request_finally_phase(S,95) = true
  -- if S.TODO = (GENERATOR_STORAGE_STEP pgenstorage) :: ptask_tail*
  -- if pgenstorage.NEXT = 2
  -- if S.OBJECTS[pgenstorage.OBJECT] = GENERATOR pgenerator
  -- if pgenerator.REFCELL =/= eps
def $request_finally_phase(S,96) = true
  -- if S.TODO = (GENERATOR_CLOSE_RELEASE pgenrelease) :: ptask_tail*
  -- if pgenrelease.JOBS = (DESTRUCTION_VALUE (HOBJECT n)) :: pdestructionjob_tail*
  -- if S.OBJECTS[n] = GENERATOR pgenerator
  -- if pgenerator.PHASE = GENERATOR_CLOSED /\ pgenerator.CLOSURE =/= eps
  -- if $close_outputs(S.EVENTS) = $ptascii("C|F")
'''


def assertions(checked, path, directory, name):
    paused = name == 'paused-storage-parent-retains-pin-through-children'
    fields = name == 'closed-storage-owned-value-and-key-order'
    reference = name == 'closed-storage-consumed-reference-cell-retains-return'
    throwing = name == 'closed-storage-pin-return-throw-priority'
    initial = ('$php_file_run(' + checked['fixture'] + ',0,'
               + driver.driver.byte_expr(os.fsencode(path)) + ','
               + driver.driver.byte_expr(os.fsencode(driver.ROOT)) + ')')
    checks = ['S_initial = ' + initial, '~S_initial.COMPILESTOP']
    checks += base.seek('S_release', 'S_initial', 96 if paused else 89) + valid('S_release')
    if paused:
        checks += r'''
S_release.TODO = (GENERATOR_CLOSE_RELEASE pgenrelease) :: ptask_after*
pgenrelease.JOBS = (DESTRUCTION_VALUE (HOBJECT n_generator)) :: pdestructionjob_tail*
$generator_close_release_valid(S_release,pgenrelease)
ptask_parent = GENERATOR_CLOSE_RELEASE pgenrelease[.JOBS = pdestructionjob_tail*]
'''.strip().splitlines()
    else:
        checks += r'''
S_release.TODO = (DESTRUCTOR_RELEASE pdestructionrelease) :: ptask_after*
pdestructionrelease.JOBS = (DESTRUCTION_VALUE (HOBJECT n_generator)) :: pdestructionjob_tail*
pdestructionrelease.USER
ptask_parent = DESTRUCTOR_RELEASE pdestructionrelease[.JOBS = pdestructionjob_tail*]
'''.strip().splitlines()
    checks += r'''
S_release.OBJECTS[n_generator] = GENERATOR pgenerator
pgenerator.PHASE = GENERATOR_CLOSED /\ pgenerator.FRAME = eps
pgenerator.CLOSURE = (n_closure)
$node_children(S_release,HOBJECT n_closure) = [HCELL n_capture]
S_release.STORE[n_capture] = DEFINED (POBJECT n_capture_object)
$trace_slot(S_release,S_release.ENV,$ptascii("wg")) = POBJECT n_weak
$weakref_get(S_release,n_weak) = POBJECT n_generator
$heap_owners($heap_graph(S_release),HOBJECT n_generator) = 1
$heap_owners($heap_graph(S_release),HOBJECT n_closure) = 1
$heap_owners($heap_graph(S_release),HCELL n_capture) = 1
'''.strip().splitlines()
    if fields:
        checks += ['pgenerator.VALUE = (POBJECT n_value)',
                   'pgenerator.REFCELL = eps', 'pgenerator.KEY = (POBJECT n_key)',
                   'pgenerator.RETURN = (PINT 0)']
    elif paused:
        checks += ['pgenerator.VALUE = (POBJECT n_value)',
                   'pgenerator.REFCELL = eps', 'pgenerator.KEY = (PINT 0)',
                   'pgenerator.RETURN = eps']
    elif reference:
        checks += ['pgenerator.VALUE = eps', 'pgenerator.REFCELL = (n_cell)',
                   'pgenerator.KEY = (PINT 0)', 'pgenerator.RETURN = (POBJECT n_value)',
                   'S_release.STORE[n_cell] = DEFINED (POBJECT n_value)',
                   '$heap_owners($heap_graph(S_release),HCELL n_cell) = 1',
                   '$heap_owners($heap_graph(S_release),HOBJECT n_value) = 2']
    else:
        checks += ['pgenerator.VALUE = (PINT 1)', 'pgenerator.REFCELL = eps',
                   'pgenerator.KEY = (PINT 0)', 'pgenerator.RETURN = (POBJECT n_value)']
    checks += base.seek('S_pinned', 'S_release', 90) + valid('S_pinned')
    checks += r'''
S_pinned_budget = $drive_steps(S_release,1)
S_pinned_budget = S_pinned[.COMPLETION = BUDGET]
S_pinned.TODO = (GENERATOR_STORAGE_STEP pgenstorage) :: ptask_parent :: ptask_after*
pgenstorage.OBJECT = n_generator /\ pgenstorage.NEXT = 0
pgenstorage.HANDLE = S_pinned.DESTRUCTION.HANDLES[n_generator]
pgenstorage.USER
$generator_storage_valid(S_pinned,pgenstorage)
$generator_storage_state_valid(S_pinned)
$node_children(S_pinned,HOBJECT n_generator) = $generator_storage_remaining(pgenerator,0)
$task_nodes(GENERATOR_STORAGE_STEP pgenstorage) = [HOBJECT n_generator]
$heap_owners($heap_graph(S_pinned),HOBJECT n_generator) = 1
$heap_owners($heap_graph(S_pinned),HOBJECT n_closure) = 1
$weakref_get(S_pinned,n_weak) = POBJECT n_generator
n_generator <- S_pinned.DESTRUCTION.CALLED
~$generator_storage_transfer(S_pinned)
S_slot_budget = $drive_steps(S_pinned,1)
S_slot_budget.COMPLETION = BUDGET
S_slot = S_slot_budget[.COMPLETION = NORMAL]
S_slot.TODO = (DESTRUCTOR_RELEASE pdestructionrelease_slot) :: (GENERATOR_STORAGE_STEP pgenstorage[.NEXT = 1]) :: ptask_parent :: ptask_after*
pdestructionrelease_slot.JOBS = [DESTRUCTION_VALUE (HOBJECT n_closure)]
$heap_owners($heap_graph(S_slot),HOBJECT n_generator) = 1
$heap_owners($heap_graph(S_slot),HOBJECT n_closure) = 1
$node_children(S_slot,HOBJECT n_generator) = $generator_storage_remaining(pgenerator,1)
'''.strip().splitlines()
    checks += valid('S_slot')
    if name == 'closed-storage-return-readable-through-children':
        reject(checks, 'handle', 'S_pinned[.TODO = (GENERATOR_STORAGE_STEP pgenstorage[.HANDLE = $(pgenstorage.HANDLE + 1)]) :: ptask_parent :: ptask_after*]', 'S_pinned')
        reject(checks, 'scope', 'S_pinned[.TODO = (GENERATOR_STORAGE_STEP pgenstorage[.USER = false]) :: ptask_parent :: ptask_after*]', 'S_pinned')
        reject(checks, 'called', 'S_pinned[.DESTRUCTION.CALLED = $request_called_drop(S_pinned.DESTRUCTION.CALLED,n_generator)]', 'S_pinned')
        reject(checks, 'duplicate', 'S_pinned[.TODO = (GENERATOR_STORAGE_STEP pgenstorage) :: S_pinned.TODO]', 'S_pinned', same_heap=False)
        reject(checks, 'hidden', 'S_pinned[.TODO = (CHOOSE ([GENERATOR_STORAGE_STEP pgenstorage]) eps 3) :: ptask_parent :: ptask_after*]', 'S_pinned', same_heap=False)
        checks += ['S_dead_future = S_pinned[.ALLOCATIONS = $destruction_node_delete(S_pinned.ALLOCATIONS,HOBJECT n_value)]',
                   '~$generator_storage_basic(S_dead_future,pgenstorage)',
                   '~$call_descriptors_valid(S_dead_future)',
                   '~$generator_storage_basic(S_pinned,pgenstorage[.NEXT = 5])']
    checks += base.seek('S_capture', 'S_slot', 91) + valid('S_capture')
    checks += r'''
$generator_storage_for(S_capture,n_generator) = (pgenstorage_capture)
pgenstorage_capture = pgenstorage[.NEXT = 1]
S_capture.OBJECTS[n_generator] = GENERATOR pgenerator
(HOBJECT n_generator) <- S_capture.ALLOCATIONS
~((HOBJECT n_closure) <- S_capture.ALLOCATIONS)
$generator_storage_closure_borrowed(S_capture,pgenerator)
$generator_closure_valid(S_capture,pgenerator)
$generator_record_valid(S_capture,pgenerator)
$weakref_get(S_capture,n_weak) = POBJECT n_generator
$heap_owners($heap_graph(S_capture),HOBJECT n_generator) = 1
$heap_owners($heap_graph(S_capture),HOBJECT n_value) = 1
'''.strip().splitlines()
    if reference:
        checks[-1] = '$heap_owners($heap_graph(S_capture),HOBJECT n_value) = 2'
        checks += base.seek('S_cell_released', 'S_capture', 95) + valid('S_cell_released')
        checks += r'''
$generator_storage_for(S_cell_released,n_generator) = (pgenstorage[.NEXT = 2])
~((HCELL n_cell) <- S_cell_released.ALLOCATIONS)
S_cell_released.STORE[n_cell] = DEFINED (POBJECT n_value)
~$call_reference_operand_valid(S_cell_released,REFERENCE n_cell)
$generator_storage_reference_borrowed(S_cell_released,pgenerator,n_cell)
$generator_record_valid(S_cell_released,pgenerator)
$heap_owners($heap_graph(S_cell_released),HOBJECT n_value) = 1
'''.strip().splitlines()
        previous = 'S_cell_released'
    else:
        previous = 'S_capture'
    checks += base.seek('S_value', previous, 92) + valid('S_value')
    checks += r'''
$generator_storage_for(S_value,n_generator) = (pgenstorage_value)
S_value.OBJECTS[n_generator] = GENERATOR pgenerator
$weakref_get(S_value,n_weak) = POBJECT n_generator
$heap_owners($heap_graph(S_value),HOBJECT n_generator) = 1
$generator_record_valid(S_value,pgenerator)
S_value.DESTRUCTION.CALLS = pdestructorcall_value :: pdestructorcall_tail*
pdestructorcall_value.OBJECT = n_value /\ pdestructorcall_value.USER
'''.strip().splitlines()
    checks += [f'pgenstorage_value.NEXT = {2 if fields or paused else 4}']
    if throwing:
        checks += ['pdestructorcall_value.PENDING = (n_capture_exception)',
                   '$throwable_field(S_value,n_capture_exception,"message") = PSTRING ($ptascii("capture"))',
                   '(HOBJECT n_capture_exception) <- S_value.ALLOCATIONS',
                   '$heap_owners($heap_graph(S_value),HOBJECT n_capture_exception) = 1']
    else:
        checks += ['pdestructorcall_value.PENDING = eps']
    if fields:
        checks += ['$node_children(S_value,HOBJECT n_generator) = [HOBJECT n_key]',
                   '$heap_owners($heap_graph(S_value),HOBJECT n_key) = 1']
        checks += base.seek('S_key', 'S_value', 94) + valid('S_key')
        checks += ['$generator_storage_for(S_key,n_generator) = (pgenstorage[.NEXT = 3])',
                   '$weakref_get(S_key,n_weak) = POBJECT n_generator',
                   '~((HOBJECT n_value) <- S_key.ALLOCATIONS)',
                   '$node_children(S_key,HOBJECT n_generator) = eps']
        previous = 'S_key'
    else:
        previous = 'S_value'
    checks += base.seek('S_finish', previous, 93) + valid('S_finish')
    checks += r'''
S_finish.TODO = (GENERATOR_STORAGE_STEP pgenstorage_finish) :: ptask_finish*
pgenstorage_finish = pgenstorage[.NEXT = 4]
$heap_owners($heap_graph(S_finish),HOBJECT n_generator) = 1
$node_children(S_finish,HOBJECT n_generator) = eps
$weakref_get(S_finish,n_weak) = POBJECT n_generator
~((HOBJECT n_closure) <- S_finish.ALLOCATIONS)
~((HOBJECT n_value) <- S_finish.ALLOCATIONS)
S_retired_budget = $drive_steps(S_finish,1)
S_retired_budget.COMPLETION = BUDGET
S_retired = S_retired_budget[.COMPLETION = NORMAL]
~((HOBJECT n_generator) <- S_retired.ALLOCATIONS)
$weakref_get(S_retired,n_weak) = PNULL
$heap_owners($heap_graph(S_retired),HOBJECT n_generator) = 0
$generator_storage_for(S_retired,n_generator) = eps
'''.strip().splitlines()
    checks += valid('S_retired')
    base.finish(checks, 'S_pinned', name)
    checks += ['~((HOBJECT n_generator) <- S_resumed.ALLOCATIONS)',
               'pgenstorage.HANDLE <- S_resumed.DESTRUCTION.FREE',
               '$weakref_get(S_resumed,n_weak) = PNULL']
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
        'spec/semantics/296-weak-references.watsup',
        'spec/semantics/328-generator-reference-yields.watsup',
        'spec/semantics/340-generator-request-finally.watsup',
        'spec/semantics/346-typed-property-slot-retirement.watsup',
        'spec/semantics/349-generator-request-fresh.watsup',
        'spec/semantics/355-generator-storage-pin.watsup',
        'tests/semantics/generator_request_finally_protocol.py',
        'tests/semantics/reference_yield_protocol.py',
        'tests/semantics/generator_storage_pin_sources.py',
        'tests/semantics/generator_storage_pin_peer_sources.py',
        'tests/semantics/generator_storage_pin_protocol.py',
    ]
    return driver.main()


if __name__ == '__main__':
    raise SystemExit(main())
