#!/usr/bin/env python3
"""Reached closed storage queues, child owners and destructor exception priority."""
import os

import generator_request_finally_protocol as base
import generator_storage_order_sources as source
from reference_yield_protocol import valid

driver = base.driver
CASES = {name: row for name, row in source.CASES.items()
         if name != 'peer-reacquired-generator-releases-closure-before-cache'}
PREFIX = r'''
def $request_finally_phase(S,70) = true
  -- if S.TODO = (DESTRUCTOR_RELEASE pdestructionrelease) :: ptask*
  -- if pdestructionrelease.JOBS = (DESTRUCTION_VALUE (HOBJECT n)) :: pdestructionjob*
  -- if S.OBJECTS[n] = GENERATOR pgenerator
  -- if pgenerator.PHASE = GENERATOR_CLOSED
  -- if pgenerator.CLOSURE =/= eps /\ pgenerator.RETURN =/= eps
  -- if $close_outputs(S.EVENTS) = $ptascii("C|")
def $request_finally_phase(S,71) = true
  -- if S.CURRENT = (pcallcontext)
  -- if pcallcontext.TARGET = METHOD_TARGET n porigin
  -- if $object_name(S,n) = $ptascii("Capture349")
  -- if $trace_context_function(S,pcallcontext) = $ptascii("__destruct")
  -- if $close_outputs(S.EVENTS) = $ptascii("C|")
def $request_finally_phase(S,72) = true
  -- if S.CURRENT = (pcallcontext)
  -- if pcallcontext.TARGET = METHOD_TARGET n porigin
  -- if $object_name(S,n) = $ptascii("Value349")
  -- if $trace_context_function(S,pcallcontext) = $ptascii("__destruct")
  -- if $close_outputs(S.EVENTS) = $ptascii("C|C")
'''


def assertions(checked, path, directory, name):
    initial = ('$php_file_run(' + checked['fixture'] + ',0,'
               + driver.driver.byte_expr(os.fsencode(path)) + ','
               + driver.driver.byte_expr(os.fsencode(driver.ROOT)) + ')')
    checks = ['S_initial = ' + initial, '~S_initial.COMPILESTOP']
    checks += base.seek('S_release', 'S_initial', 70) + valid('S_release')
    checks += r'''
S_release.TODO = (DESTRUCTOR_RELEASE pdestructionrelease) :: ptask_tail*
pdestructionrelease.JOBS = (DESTRUCTION_VALUE (HOBJECT n_generator)) :: pdestructionjob_tail*
pdestructionrelease.USER
S_release.OBJECTS[n_generator] = GENERATOR pgenerator
pgenerator.PHASE = GENERATOR_CLOSED /\ pgenerator.FRAME = eps
pgenerator.CLOSURE = (n_closure)
pgenerator.RETURN = (POBJECT n_value)
pgenerator.VALUE = (PINT 1)
pgenerator.REFCELL = eps
pgenerator.KEY = (PINT 0)
$node_children(S_release,HOBJECT n_generator) = [HOBJECT n_value,HOBJECT n_closure]
$node_children(S_release,HOBJECT n_closure) = [HCELL n_capture]
n_capture <- S_release.REFCELLS
S_release.STORE[n_capture] = DEFINED (POBJECT n_capture_object)
$object_name(S_release,n_capture_object) = $ptascii("Capture349")
$object_name(S_release,n_value) = $ptascii("Value349")
$heap_owners($heap_graph(S_release),HOBJECT n_generator) = 1
$heap_owners($heap_graph(S_release),HOBJECT n_closure) = 1
$heap_owners($heap_graph(S_release),HOBJECT n_value) = 1
$heap_owners($heap_graph(S_release),HCELL n_capture) = 1
S_unheld = $destructor_release_replace(S_release,pdestructionrelease[.JOBS = pdestructionjob_tail*])
$heap_owners($heap_graph(S_unheld),HOBJECT n_generator) = 0
S_freed_budget = $drive_steps(S_release,1)
S_freed_budget.COMPLETION = BUDGET
S_freed = S_freed_budget[.COMPLETION = NORMAL]
S_freed.TODO = (GENERATOR_STORAGE_STEP pgenstorage) :: (DESTRUCTOR_RELEASE pdestructionrelease[.JOBS = pdestructionjob_tail*]) :: ptask_tail*
pgenstorage.OBJECT = n_generator /\ pgenstorage.NEXT = 0
pgenstorage.USER
$generator_storage_valid(S_freed,pgenstorage)
(HOBJECT n_generator) <- S_freed.ALLOCATIONS
$heap_owners($heap_graph(S_freed),HOBJECT n_generator) = 1
$node_children(S_freed,HOBJECT n_generator) = [HOBJECT n_closure,HOBJECT n_value]
$close_outputs(S_freed.EVENTS) = $ptascii("C|")
$heap_owners($heap_graph(S_freed),HOBJECT n_closure) = 1
$heap_owners($heap_graph(S_freed),HOBJECT n_value) = 1
'''.strip().splitlines()
    checks += valid('S_freed')
    checks += base.seek('S_capture', 'S_freed', 71) + valid('S_capture')
    checks += r'''
S_capture.CURRENT = (pcallcontext_capture)
pcallcontext_capture.TARGET = METHOD_TARGET n_capture_object porigin_capture
S_capture.DESTRUCTION.CALLS = pdestructorcall_capture :: pdestructorcall_tail*
pdestructorcall_capture.OBJECT = n_capture_object /\ pdestructorcall_capture.USER
pdestructorcall_capture.PENDING = eps
n_capture_object <- S_capture.DESTRUCTION.CALLED
~(n_value <- S_capture.DESTRUCTION.CALLED)
(HOBJECT n_value) <- S_capture.ALLOCATIONS
$heap_owners($heap_graph(S_capture),HOBJECT n_value) = 1
'''.strip().splitlines()
    checks += base.seek('S_value', 'S_capture', 72) + valid('S_value')
    checks += r'''
S_value.CURRENT = (pcallcontext_value)
pcallcontext_value.TARGET = METHOD_TARGET n_value porigin_value
S_value.DESTRUCTION.CALLS = pdestructorcall_value :: pdestructorcall_tail_value*
pdestructorcall_value.OBJECT = n_value /\ pdestructorcall_value.USER
n_value <- S_value.DESTRUCTION.CALLED
~((HOBJECT n_closure) <- S_value.ALLOCATIONS)
~((HCELL n_capture) <- S_value.ALLOCATIONS)
'''.strip().splitlines()
    if name == 'closed-generator-cache-throw-replaces-capture-throw':
        checks += ['pdestructorcall_value.PENDING = (n_capture_exception)',
                   '$throwable_field(S_value,n_capture_exception,"message") = PSTRING ($ptascii("capture"))',
                   '(HOBJECT n_capture_exception) <- S_value.ALLOCATIONS',
                   '$heap_owners($heap_graph(S_value),HOBJECT n_capture_exception) = 1']
    else:
        checks += ['pdestructorcall_value.PENDING = eps']
    base.finish(checks, 'S_freed', name)
    checks += ['~((HOBJECT n_generator) <- S_resumed.ALLOCATIONS)',
               '~((HOBJECT n_closure) <- S_resumed.ALLOCATIONS)',
               '~((HOBJECT n_value) <- S_resumed.ALLOCATIONS)',
               '~((HOBJECT n_capture_object) <- S_resumed.ALLOCATIONS)',
               '~((HCELL n_capture) <- S_resumed.ALLOCATIONS)']
    return checks


def main():
    base.CASES = CASES
    driver.CASES = CASES
    driver.PREFIX += base.PREFIX + PREFIX
    driver.assertions = assertions
    driver.source.WATCHED = source.driver.WATCHED + [
        'spec/semantics/222-exception-handlers.watsup',
        'spec/semantics/270-eager-destructors.watsup',
        'spec/semantics/281-fibers.watsup',
        'spec/semantics/296-weak-references.watsup',
        'spec/semantics/328-generator-reference-yields.watsup',
        'spec/semantics/340-generator-request-finally.watsup',
        'spec/semantics/346-typed-property-slot-retirement.watsup',
        'spec/semantics/349-generator-request-fresh.watsup',
        'spec/semantics/355-generator-storage-pin.watsup',
        'tests/semantics/generator_request_finally_protocol.py',
        'tests/semantics/generator_request_fresh_peer_sources.py',
        'tests/semantics/generator_storage_order_sources.py',
        'tests/semantics/generator_storage_order_protocol.py',
        'tests/semantics/reference_yield_protocol.py',
    ]
    return driver.main()


if __name__ == '__main__':
    raise SystemExit(main())
